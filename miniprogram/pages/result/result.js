const { get } = require('../../utils/request');

Page({
  data: {
    loading: true,
    detail: {}
  },
  onLoad(options) {
    const recordId = options.id;
    if (recordId) {
      this.loadDetail(recordId);
    } else {
      wx.showToast({ title: '参数错误', icon: 'none' });
      wx.navigateBack();
    }
  },
  async loadDetail(recordId) {
    try {
      const res = await get(`/resident/recognize/${recordId}`);
      if (res.code === 200) {
        this.setData({ detail: res.data, loading: false });
      } else {
        wx.showToast({ title: res.msg, icon: 'none' });
        wx.navigateBack();
      }
    } catch (err) {
      wx.showToast({ title: '加载失败', icon: 'none' });
      wx.navigateBack();
    }
  },
  goFeedback() {
    const recordId = this.data.detail.record_id;
    wx.navigateTo({ url: `/pages/feedback/feedback?recordId=${recordId}` });
  }
});