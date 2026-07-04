const TOKEN_KEY = 'token';

const setToken = (token) => {
  wx.setStorageSync(TOKEN_KEY, token);
};

const getToken = () => {
  return wx.getStorageSync(TOKEN_KEY) || '';
};

const removeToken = () => {
  wx.removeStorageSync(TOKEN_KEY);
};

const isLogin = () => {
  return !!getToken();
};

module.exports = {
  setToken,
  getToken,
  removeToken,
  isLogin
};