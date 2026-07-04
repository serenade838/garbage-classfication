const { get } = require('../../utils/request');

Page({
  data: { detail: {} },
  onLoad(options) {
    const id = options.id;
    if (id) this.loadDetail(id);
  },
  async loadDetail(id) {
    try {
      const res = await get(`/user/notice/${id}`);
      if (res.code === 200) {
        this.setData({ detail: res.data });
      }
    } catch (e) {}
  }
});