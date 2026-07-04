Component({
  properties: {
    title: {
      type: String,
      value: '智能垃圾分类'   // 默认标题
    },
    bgColor: {
      type: String,
      value: '#4CAF50'       // 默认背景色
    }
  },
  data: {
    statusBarHeight: 20      // 默认值，实际会动态获取
  },
  lifetimes: {
    attached() {
      const sysInfo = wx.getSystemInfoSync();
      this.setData({
        statusBarHeight: sysInfo.statusBarHeight || 20
      });
    }
  }
});