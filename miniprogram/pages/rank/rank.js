const { get } = require('../../utils/request');

Page({
  data: {
    cycles: ['日', '周', '月', '全部'],
    cycleIndex: 2,        // 默认“月”
    rankList: []
  },

  onLoad() {
    this.loadRank();      // 页面加载时调用
  },

  // 周期切换事件（picker）
  onCycleChange(e) {
    const index = e.detail.value;
    this.setData({ cycleIndex: index });
    this.loadRank();      // 切换后重新加载
  },

  // 加载排行榜数据（方法名必须为 loadRank）
  async loadRank() {
    const cycles = ['day', 'week', 'month', 'all'];
    const cycle = cycles[this.data.cycleIndex];
    try {
      const res = await get('/user/rank', { cycle });
      console.log('排行榜响应:', res);   // 调试
      if (res.code === 200) {
        this.setData({ rankList: res.data });
        console.log('rankList:', this.data.rankList);
      } else {
        wx.showToast({ title: res.msg || '加载失败', icon: 'none' });
      }
    } catch (err) {
      console.error(err);
      wx.showToast({ title: '网络错误', icon: 'none' });
    }
  }
});