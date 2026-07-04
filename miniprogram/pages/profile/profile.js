const { get, put } = require('../../utils/request');

Page({
  data: {
    userInfo: {}
  },
  onShow() {
    this.loadUserInfo();
  },
  async loadUserInfo() {
    try {
      const res = await get('/user/info');
      if (res.code === 200) {
        this.setData({ userInfo: res.data });
      }
    } catch (e) {
      wx.showToast({ title: '加载失败', icon: 'none' });
    }
  },
  // 修改昵称
  async editNickname() {
    wx.showModal({
      title: '修改昵称',
      editable: true,
      placeholderText: '请输入新昵称',
      success: async (res) => {
        if (res.confirm && res.content) {
          const nickname = res.content.trim();
          if (!nickname) {
            wx.showToast({ title: '昵称不能为空', icon: 'none' });
            return;
          }
          wx.showLoading({ title: '保存中' });
          try {
            const result = await put('/user/nickname', { nickname });
            wx.hideLoading();
            if (result.code === 200) {
              wx.showToast({ title: '更新成功' });
              this.loadUserInfo();
            } else {
              wx.showToast({ title: result.msg, icon: 'none' });
            }
          } catch (err) {
            wx.hideLoading();
            wx.showToast({ title: '网络错误', icon: 'none' });
          }
        }
      }
    });
  },
  // 修改楼栋（修复变量声明）
  async editBuilding() {
    const current = this.data.userInfo.building || '';
    wx.showModal({
      title: '修改楼栋',
      editable: true,
      placeholderText: '请输入新楼栋（如：3栋502）',
      content: current,
      success: async (res) => {
        if (res.confirm) {
          const building = res.content.trim();   // 注意这里有 const 声明
          wx.showLoading({ title: '保存中' });
          try {
            const result = await put('/user/building', { building });
            wx.hideLoading();
            if (result.code === 200) {
              wx.showToast({ title: '更新成功' });
              this.loadUserInfo();
            } else {
              wx.showToast({ title: result.msg, icon: 'none' });
            }
          } catch (err) {
            wx.hideLoading();
            wx.showToast({ title: '网络错误', icon: 'none' });
          }
        }
      }
    });
  },
  // 跳转修改密码页
  goChangePassword() {
    // 如果页面不存在，可先弹窗提示
    wx.navigateTo({ url: '/pages/change-password/change-password' });
  },

  goFeedbackList() {
  wx.navigateTo({ url: '/pages/feedback-list/feedback-list' });
},

  // 退出登录
  logout() {
    wx.showModal({
      title: '提示',
      content: '确认退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('token');
          wx.reLaunch({ url: '/pages/login/login' });
        }
      }
    });
  }
});