// 网络请求封装
const config = require('./config.js')

/**
 * 封装wx.request
 * @param {String} url 请求地址
 * @param {Object} data 请求参数
 * @param {String} method 请求方法
 * @param {Boolean} showLoading 是否显示loading
 */
function request(url, data = {}, method = 'GET', showLoading = true) {
  return new Promise((resolve, reject) => {
    // 显示加载提示
    if (showLoading) {
      wx.showLoading({
        title: '加载中...',
        mask: true
      })
    }

    // 获取token
    const token = wx.getStorageSync('token') || ''

    // 发起请求
    wx.request({
      url: config.apiBaseUrl + url,
      data: data,
      method: method,
      header: {
        'content-type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        if (showLoading) {
          wx.hideLoading()
        }

        console.log('请求响应 statusCode:', res.statusCode)
        console.log('请求响应 data:', res.data)

        // 请求成功
        if (res.statusCode === 200) {
          // 根据后端返回的数据结构处理
          if (res.data.code === 200 || res.data.code === 0 || !res.data.code) {
            // 如果没有code字段，或者code是200/0，都认为成功
            resolve(res.data)
          } else {
            // 业务错误
            const errorMsg = res.data.message || res.data.msg || '请求失败'
            console.error('业务错误:', errorMsg, res.data)
            reject({
              message: errorMsg,
              ...res.data
            })
          }
        } else if (res.statusCode === 401) {
          // token过期或无效
          console.error('认证失败 401:', res.data)
          reject({
            message: res.data.detail || res.data.message || '请先登录',
            statusCode: 401,
            ...res.data
          })
        } else {
          // 其他错误
          console.error('请求失败，状态码:', res.statusCode, '数据:', res.data)
          reject({
            message: res.data.message || res.data.detail || '网络请求失败',
            statusCode: res.statusCode,
            ...res.data
          })
        }
      },
      fail: (err) => {
        if (showLoading) {
          wx.hideLoading()
        }
        console.error('wx.request fail:', err)
        reject({
          message: '网络连接失败，请检查网络设置',
          detail: err.errMsg || '未知网络错误',
          ...err
        })
      }
    })
  })
}

/**
 * GET请求
 */
function get(url, data = {}, showLoading = true) {
  return request(url, data, 'GET', showLoading)
}

/**
 * POST请求
 */
function post(url, data = {}, showLoading = true) {
  return request(url, data, 'POST', showLoading)
}

module.exports = {
  request,
  get,
  post
}
