// index.js
const request = require('../../utils/request.js')
const config = require('../../utils/config.js')

Page({
  data: {
    userInfo: null,
    payLoading: false,
    greeting: ''
  },

  onLoad() {
    // 加载用户信息
    this.loadUserInfo()
    // 设置问候语
    this.setGreeting()
  },

  onShow() {
    // 每次显示页面时检查登录状态
    this.checkLoginStatus()
  },

  /**
   * 设置问候语
   */
  setGreeting() {
    const hour = new Date().getHours()
    let greeting = ''

    if (hour >= 5 && hour < 12) {
      greeting = '早上好，开启美好的一天 ☀️'
    } else if (hour >= 12 && hour < 14) {
      greeting = '中午好，记得休息一下 🌤️'
    } else if (hour >= 14 && hour < 18) {
      greeting = '下午好，继续加油哦 ⛅'
    } else if (hour >= 18 && hour < 22) {
      greeting = '晚上好，辛苦了一天 🌙'
    } else {
      greeting = '夜深了，注意休息哦 ✨'
    }

    this.setData({
      greeting: greeting
    })
  },

  /**
   * 加载用户信息
   */
  loadUserInfo() {
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      // 处理头像URL，确保是完整的HTTPS地址
      if (userInfo.avatar) {
        userInfo.avatar = config.getFullAvatarUrl(userInfo.avatar)
      }

      this.setData({
        userInfo: userInfo
      })
    }
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    if (!token) {
      // 未登录，跳转到登录页
      wx.redirectTo({
        url: '/pages/login/login'
      })
    }
  },

  /**
   * 退出登录
   */
  handleLogout() {
    console.log('🚪 [Index] 开始执行退出登录')

    try {
      // 清除本地存储
      wx.removeStorageSync('token')
      wx.removeStorageSync('userInfo')
      console.log('🚪 [Index] 已清除本地存储')

      // 显示退出提示
      wx.showToast({
        title: '已退出登录',
        icon: 'success',
        duration: 1500
      })

      // 延迟跳转到登录页
      setTimeout(() => {
        console.log('🚪 [Index] 跳转到登录页')
        wx.redirectTo({
          url: '/pages/login/login',
          success: () => {
            console.log('🚪 [Index] 跳转成功')
          },
          fail: (err) => {
            console.error('🚪 [Index] 跳转失败:', err)
            // 如果 redirectTo 失败，尝试使用 reLaunch
            wx.reLaunch({
              url: '/pages/login/login'
            })
          }
        })
      }, 1500)
    } catch (error) {
      console.error('🚪 [Index] 退出登录出错:', error)
      // 即使出错也要跳转到登录页
      wx.reLaunch({
        url: '/pages/login/login'
      })
    }
  },

  /**
   * 发起支付
   */
  handlePay() {
    if (this.data.payLoading) return

    this.setData({
      payLoading: true
    })

    // 调用后端接口创建订单
    request.post(config.api.createOrder, {
      amount: 1,  // 支付金额（元）
      description: '微信支付测试'
    }).then(res => {
      console.log('创建订单成功', res)

      // 调起微信支付
      const paymentData = res.data.payment
      wx.requestPayment({
        timeStamp: paymentData.timeStamp,
        nonceStr: paymentData.nonceStr,
        package: paymentData.package,
        signType: paymentData.signType,
        paySign: paymentData.paySign,
        success: (res) => {
          console.log('支付成功', res)
          wx.showToast({
            title: '支付成功',
            icon: 'success',
            duration: 2000
          })
        },
        fail: (err) => {
          console.error('支付失败', err)
          if (err.errMsg === 'requestPayment:fail cancel') {
            wx.showToast({
              title: '支付已取消',
              icon: 'none',
              duration: 2000
            })
          } else {
            wx.showToast({
              title: '支付失败',
              icon: 'none',
              duration: 2000
            })
          }
        }
      })
    }).catch(err => {
      console.error('创建订单失败', err)
      wx.showToast({
        title: err.message || '创建订单失败',
        icon: 'none',
        duration: 2000
      })
    }).finally(() => {
      this.setData({
        payLoading: false
      })
    })
  },

  /**
   * 打开WebView
   */
  handleOpenWebView() {
    const token = wx.getStorageSync('token')

    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none',
        duration: 2000
      })
      return
    }

    // 跳转到WebView页面，传递token
    wx.navigateTo({
      url: `/pages/webview/webview?token=${encodeURIComponent(token)}`
    })
  },

  /**
   * 电子名片
   */
  handleBusinessCard() {
    wx.showToast({
      title: '电子名片功能开发中',
      icon: 'none',
      duration: 2000
    })
  },

  /**
   * 文案助手
   */
  handleCopywriter() {
    const token = wx.getStorageSync('token')

    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none',
        duration: 2000
      })
      return
    }

    // 跳转到WebView页面，打开文案助手
    wx.navigateTo({
      url: `/pages/webview/webview?token=${encodeURIComponent(token)}&url=${encodeURIComponent('https://write.xingke888.com/editor')}`
    })
  }
})
