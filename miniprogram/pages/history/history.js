const app = getApp();
const { get, del } = require('../../utils/request');

Page({
  data: {
    page: 1,
    size: 10,
    category: '',
    list: [],
    total: 0,
    totalPages: 1,
    loaded: false
  },

  onLoad() {
    this.loadHistory();
  },

  // 输入筛选关键词
  onCategoryInput(e) {
    this.setData({ category: e.detail.value });
  },

  // 搜索
  search() {
    this.setData({ page: 1 });
    this.loadHistory();
  },

  // 刷新
  refresh() {
    this.loadHistory();
  },

  // 加载历史记录（核心方法）
  async loadHistory() {
    const { page, size, category } = this.data;
    wx.showLoading({ title: '加载中' });
    try {
      const res = await get('/user/history/list', { page, size, category });
      wx.hideLoading();
      console.log('历史记录响应:', res);
      if (res.code === 200) {
        const { total, list } = res.data;
        const baseUrl = app.globalData.baseUrl || 'http://localhost:8000';
        const processedList = (list || []).map(item => ({
          ...item,
          // 如果 image_url 不是完整 URL，拼接 baseUrl
          image_url: item.image_url && item.image_url.startsWith('http')
            ? item.image_url
            : `${baseUrl}${item.image_url || ''}`
        }));
        this.setData({
          list: processedList,
          total: total || 0,
          totalPages: Math.ceil((total || 0) / size),
          loaded: true
        });
      } else {
        wx.showToast({ title: res.msg || '加载失败', icon: 'none' });
      }
    } catch (err) {
      console.error('loadHistory 错误:', err);
      wx.hideLoading();
      wx.showToast({ title: '网络错误', icon: 'none' });
    }
  },

  // 上一页
  prevPage() {
    if (this.data.page > 1) {
      this.setData({ page: this.data.page - 1 });
      this.loadHistory();
    }
  },

  // 下一页
  nextPage() {
    const { page, totalPages } = this.data;
    if (page < totalPages) {
      this.setData({ page: page + 1 });
      this.loadHistory();
    }
  },

  // 删除记录
  deleteRecord(e) {
    const id = e.currentTarget.dataset.id;
    wx.showModal({
      title: '提示',
      content: '确认删除该记录？',
      success: async (res) => {
        if (res.confirm) {
          try {
            const resp = await del(`/user/history/${id}`);
            if (resp.code === 200) {
              wx.showToast({ title: '删除成功' });
              this.loadHistory(); // 刷新列表
            } else {
              wx.showToast({ title: resp.msg || '删除失败', icon: 'none' });
            }
          } catch (err) {
            wx.showToast({ title: '网络错误', icon: 'none' });
          }
        }
      }
    });
  },

  // 预览图片
  previewImage(e) {
    const url = e.currentTarget.dataset.src;
    wx.previewImage({
      urls: [url]
    });
  }
});