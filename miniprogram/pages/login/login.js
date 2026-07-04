const { post } = require('../../utils/request');
const { setToken } = require('../../utils/auth');

Page({
  data: {
    phone: '',
    password: ''
  },
  onPhoneInput(e) {
    this.setData({ phone: e.detail.value });
  },
  onPwdInput(e) {
    this.setData({ password: e.detail.value });
  },
  async login() {
    const { phone, password } = this.data;
    if (!phone || !password) {
      wx.showToast({ title: '请填写完整', icon: 'none' });
      return;
    }
    try {
      const res = await post('/user/login', { phone, password });
      if (res.code === 200) {
        setToken(res.data.token);
        wx.switchTab({ url: '/pages/home/home' });
      } else {
        wx.showToast({ title: res.msg, icon: 'none' });
      }
    } catch (err) {
      wx.showToast({ title: '网络错误', icon: 'none' });
    }
  },
  goRegister() {
    wx.navigateTo({ url: '/pages/register/register' });
  }
});