const { get } = require('../../utils/request');

Page({
  data: {
    keyword: '',
    results: [],
    searched: false
  },
  onKeywordInput(e) {
    this.setData({ keyword: e.detail.value });
  },
  async searchRules() {
    const keyword = this.data.keyword.trim();
    if (!keyword) {
      wx.showToast({ title: '请输入关键词', icon: 'none' });
      return;
    }
    wx.showLoading({ title: '搜索中...' });
    try {
      const res = await get('/user/rules', { keyword });
      wx.hideLoading();
      if (res.code === 200) {
        this.setData({ results: res.data, searched: true });
      } else {
        wx.showToast({ title: res.msg || '搜索失败', icon: 'none' });
      }
    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '网络错误', icon: 'none' });
    }
  }
});