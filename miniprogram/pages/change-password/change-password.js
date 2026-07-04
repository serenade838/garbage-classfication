const { post } = require('../../utils/request');

Page({
  data: {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  },
  onOldPwdInput(e) {
    this.setData({ oldPassword: e.detail.value });
  },
  onNewPwdInput(e) {
    this.setData({ newPassword: e.detail.value });
  },
  onConfirmPwdInput(e) {
    this.setData({ confirmPassword: e.detail.value });
  },
  async submit() {
    const { oldPassword, newPassword, confirmPassword } = this.data;
    if (!oldPassword || !newPassword || !confirmPassword) {
      wx.showToast({ title: '请填写完整', icon: 'none' });
      return;
    }
    if (newPassword.length < 6) {
      wx.showToast({ title: '新密码不少于6位', icon: 'none' });
      return;
    }
    if (newPassword !== confirmPassword) {
      wx.showToast({ title: '两次密码输入不一致', icon: 'none' });
      return;
    }
    wx.showLoading({ title: '修改中' });
    try {
      const res = await post('/user/change_password', { old_password: oldPassword, new_password: newPassword });
      wx.hideLoading();
      if (res.code === 200) {
        wx.showToast({ title: '修改成功' });
        wx.navigateBack(); // 返回个人资料页
      } else {
        wx.showToast({ title: res.msg || '修改失败', icon: 'none' });
      }
    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '网络错误', icon: 'none' });
    }
  }
});