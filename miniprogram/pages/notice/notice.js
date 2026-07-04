const { get } = require('../../utils/request');

Page({
  data: { notices: [] },
  onLoad() {
    this.loadNotices();
  },
  async loadNotices() {
    try {
      const res = await get('/user/notice/list');
      if (res.code === 200) {
        this.setData({ notices: res.data });
      }
    } catch (e) {}
  },
  goDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/notice-detail/notice-detail?id=${id}` });
  }
});