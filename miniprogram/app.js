// miniprogram/app.js
App({
  onLaunch() {
    // 小程序启动时检查登录状态
    const token = wx.getStorageSync('token');
    if (token) {
      // 可以在这里请求用户信息等
    }
  },
  globalData: {
    userInfo: null,
    baseUrl: 'http://localhost:8000' // 开发环境，生产环境替换为实际域名
  }
});