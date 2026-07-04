const { get } = require('../../utils/request');

Page({
  data: {
    notices: []

  },
  onShow() {

    this.loadNotices();
  },
  async loadNotices() {
    try {
      const res = await get('/user/notice/list');
      if (res.code === 200) {
        this.setData({ notices: res.data });
      }
    } catch (e) { }
  },
  goRecognize() {
    wx.navigateTo({ url: '/pages/recognize/recognize' });
  },
  goRules() {
    wx.navigateTo({ url: '/pages/rules/rules' });
  },
  goRank() {
    wx.navigateTo({ url: '/pages/rank/rank' });
  },
  goNoticeDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/notice-detail/notice-detail?id=${id}` });
  }
});