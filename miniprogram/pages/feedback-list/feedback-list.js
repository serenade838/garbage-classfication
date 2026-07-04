const { get } = require('../../utils/request');

Page({
  data: {
    list: []
  },
  onShow() {
    this.loadFeedback();
  },
  async loadFeedback() {
    wx.showLoading({ title: '加载中' });
    try {
      const res = await get('/user/feedback/list');
      wx.hideLoading();
      if (res.code === 200) {
        this.setData({ list: res.data });
      } else {
        wx.showToast({ title: res.msg || '加载失败', icon: 'none' });
      }
    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '网络错误', icon: 'none' });
    }
  }
});