// pages/feedback/feedback.js
const { post } = require('../../utils/request');  // 使用封装好的请求方法

Page({
  data: {
    recordId: '',
    categories: ['可回收物', '有害垃圾', '厨余垃圾', '其他垃圾'],
    selectedCategory: ''
  },

  onLoad(options) {
    if (options.recordId) {
      this.setData({ recordId: options.recordId });
    } else {
      wx.showToast({ title: '参数错误', icon: 'none' });
      wx.navigateBack();
    }
  },

  onCategoryChange(e) {
    const index = e.detail.value;
    this.setData({
      selectedCategory: this.data.categories[index]
    });
  },

  async submitFeedback() {
    const { recordId, selectedCategory } = this.data;
    if (!selectedCategory) {
      wx.showToast({ title: '请选择正确的分类', icon: 'none' });
      return;
    }

    try {
      wx.showLoading({ title: '提交中...' });
      // 调用用户端接口，自动携带Token
      const res = await post('/user/feedback/add', {
        record_id: parseInt(recordId, 10),
        correct_category: selectedCategory   // 注意字段名与接口文档一致
      });
      wx.hideLoading();
      if (res.code === 200) {
        wx.showToast({ title: '已提交，等待管理员审核', icon: 'success' });
        setTimeout(() => wx.navigateBack(), 1500);
      } else {
        wx.showToast({ title: res.msg || '提交失败', icon: 'none' });
      }
    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '网络错误，请重试', icon: 'none' });
      console.error('提交反馈失败:', err);
    }
  }
});