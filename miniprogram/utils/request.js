const { getToken, removeToken } = require('./auth');
const app = getApp();

const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = getToken();
    wx.request({
      url: app.globalData.baseUrl + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      success(res) {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else if (res.statusCode === 401) {
          removeToken();
          wx.redirectTo({ url: '/pages/login/login' });
          reject(res);
        } else {
          reject(res);
        }
      },
      fail(err) {
        reject(err);
      }
    });
  });
};

// 封装常用方法
const get = (url, data) => request({ url, data, method: 'GET' });
const post = (url, data) => request({ url, data, method: 'POST' });
const put = (url, data) => request({ url, data, method: 'PUT' });
const del = (url, data) => request({ url, data, method: 'DELETE' });

// 上传文件
const upload = (url, filePath, name = 'image') => {
  return new Promise((resolve, reject) => {
    const token = getToken();
    wx.uploadFile({
      url: app.globalData.baseUrl + url,
      filePath,
      name,
      header: {
        'Authorization': `Bearer ${token}`
      },
      success(res) {
        const data = JSON.parse(res.data);
        resolve(data);
      },
      fail(err) {
        reject(err);
      }
    });
  });
};

module.exports = {
  request,
  get,
  post,
  put,
  del,
  upload
};