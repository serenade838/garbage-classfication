const { upload } = require('../../utils/request');

Page({
  data: {
    imageUrl: '',          // 用于显示原图
    imagePath: '',         // 用于上传
    result: null,
    recordId: null
  },
  chooseImage() {
    wx.chooseImage({
      count: 1,
      success: (res) => {
        const path = res.tempFilePaths[0];
        this.setData({ imageUrl: path, imagePath: path, result: null });
        this.clearCanvas();
      }
    });
  },
  takePhoto() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera'],
      success: (res) => {
        const path = res.tempFiles[0].tempFilePath;
        this.setData({ imageUrl: path, imagePath: path, result: null });
        this.clearCanvas();
      }
    });
  },
  clearCanvas() {
    const ctx = wx.createCanvasContext('resultCanvas', this);
    ctx.clearRect(0, 0, 300, 300);
    ctx.draw();
  },
  async startRecognize() {
    if (!this.data.imagePath) {
      wx.showToast({ title: '请选择图片', icon: 'none' });
      return;
    }
    wx.showLoading({ title: '识别中...' });
    try {
      const res = await upload('/user/recognize', this.data.imagePath);
      wx.hideLoading();
      if (res.code === 200) {
        this.setData({
          result: res.data,
          recordId: res.data.record_id
        });
        this.drawDetections(res.data.detections);
      } else {
        wx.showToast({ title: res.msg, icon: 'none' });
      }
    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '识别失败', icon: 'none' });
    }
  },
  // 绘制检测框（坐标需根据图片显示比例缩放）
  drawDetections(detections) {
    if (!detections || detections.length === 0) return;

    // 获取图片显示区域的尺寸
    const query = wx.createSelectorQuery().in(this);
    query.select('.preview-image').boundingClientRect((rect) => {
      if (!rect) return;
      const imgW = rect.width;
      const imgH = rect.height;
      // 获取图片实际像素尺寸，用于坐标缩放
      wx.getImageInfo({
        src: this.data.imageUrl,
        success: (info) => {
          const realW = info.width;
          const realH = info.height;
          const scaleX = imgW / realW;
          const scaleY = imgH / realH;

          const ctx = wx.createCanvasContext('resultCanvas', this);
          ctx.clearRect(0, 0, imgW, imgH);

          const colors = ['#FF0000', '#00FF00', '#0000FF', '#FFA500', '#800080'];
          const classNames = ['可回收物', '有害垃圾', '厨余垃圾', '其他垃圾'];

          detections.forEach((det, index) => {
            const { x1, y1, x2, y2, confidence, class_id } = det;
            const left = x1 * scaleX;
            const top = y1 * scaleY;
            const right = x2 * scaleX;
            const bottom = y2 * scaleY;

            ctx.setStrokeStyle(colors[index % colors.length]);
            ctx.setLineWidth(3);
            ctx.strokeRect(left, top, right - left, bottom - top);

            const label = `${classNames[class_id] || '未知'} ${confidence.toFixed(2)}`;
            ctx.setFontSize(16);
            ctx.setFillStyle(colors[index % colors.length]);
            ctx.fillText(label, left, top - 6);
          });
          ctx.draw();
        }
      });
    }).exec();
  },
  goFeedback(e) {
    const recordId = e.currentTarget.dataset.record;
    wx.navigateTo({ url: `/pages/feedback/feedback?recordId=${recordId}` });
  }
});