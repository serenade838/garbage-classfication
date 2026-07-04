const { post } = require('../../utils/request');

Page({
  data: {
    phone: '',
    password: '',
    building: ''
  },
  onPhoneInput(e) {
    this.setData({ phone: e.detail.value });
  },
  onPwdInput(e) {
    this.setData({ password: e.detail.value });
  },
  onBuildingInput(e) {
    this.setData({ building: e.detail.value });
  },
  // 方法名必须与 wxml 中的 bindtap 一致（register）
  async register() {
    const { phone, password, building } = this.data;
    if (!phone || !password) {
      wx.showToast({ title: '请填写完整', icon: 'none' });
      return;
    }
    wx.showLoading({ title: '注册中...' });
    try {
      const res = await post('/user/register', { phone, password, building });
      wx.hideLoading();
      if (res.code === 200) {
        wx.showToast({ title: '注册成功' });
        // 注册成功后返回登录页
        wx.navigateBack();
      } else {
        wx.showToast({ title: res.msg || '注册失败', icon: 'none' });
      }
    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '网络错误', icon: 'none' });
    }
  }
});