// webview.js
Page({
  data: {
    webUrl: '',
    isLoading: true  // 加载状态
  },

  onLoad(options) {
    const token = options.token || ''
    const refreshToken = options.refreshToken || ''
    const customUrl = options.url ? decodeURIComponent(options.url) : ''
    const action = options.action || ''

    // 处理退出登录操作
    if (action === 'logout') {
      console.log('收到退出登录指令')
      this.handleLogout()
      return
    }

    if (!token) {
      wx.showToast({
        title: '缺少登录信息',
        icon: 'none',
        duration: 2000
      })

      setTimeout(() => {
        wx.navigateBack()
      }, 2000)
      return
    }

    // 如果传递了自定义URL，则使用自定义URL
    let webUrl = ''
    if (customUrl) {
      // 检查URL是否已包含查询参数
      const separator = customUrl.includes('?') ? '&' : '?'
      webUrl = `${customUrl}${separator}miniapp_token=${encodeURIComponent(token)}`
      // 如果有 refresh token，也传递
      if (refreshToken) {
        webUrl += `&miniapp_refresh_token=${encodeURIComponent(refreshToken)}`
      }
    } else {
      // 默认跳转到计划书管理页面
      const baseUrl = 'https://hongkong.xingke888.com'
      webUrl = `${baseUrl}/plan-management?miniapp_token=${encodeURIComponent(token)}`
      if (refreshToken) {
        webUrl += `&miniapp_refresh_token=${encodeURIComponent(refreshToken)}`
      }
    }

    console.log('WebView URL:', webUrl)

    this.setData({
      webUrl: webUrl,
      isLoading: true
    })

    // 设置超时时间，如果加载时间过长，自动隐藏loading（作为保险）
    this.loadingTimer = setTimeout(() => {
      this.setData({
        isLoading: false
      })
    }, 10000) // 10秒超时
  },

  onShow() {
    // 页面显示时的处理
  },

  onUnload() {
    // 页面卸载时清除定时器
    if (this.loadingTimer) {
      clearTimeout(this.loadingTimer)
    }
  },

  /**
   * webview 加载完成
   */
  handleLoad(e) {
    console.log('WebView 加载完成')
    // 清除定时器
    if (this.loadingTimer) {
      clearTimeout(this.loadingTimer)
    }
    // 隐藏loading
    this.setData({
      isLoading: false
    })
  },

  /**
   * webview 加载错误
   */
  handleError(e) {
    console.error('WebView 加载失败:', e.detail)
    // 清除定时器
    if (this.loadingTimer) {
      clearTimeout(this.loadingTimer)
    }
    // 隐藏loading
    this.setData({
      isLoading: false
    })

    wx.showModal({
      title: '加载失败',
      content: '页面加载失败，请检查网络后重试',
      confirmText: '返回',
      showCancel: false,
      success: () => {
        wx.navigateBack()
      }
    })
  },

  /**
   * 接收H5页面的消息
   * H5页面需要调用: wx.miniProgram.postMessage({ data: { action: 'logout' } })
   */
  handleMessage(e) {
    console.log('收到H5页面消息:', e.detail.data)

    // 获取最后一条消息
    const messages = e.detail.data
    if (messages && messages.length > 0) {
      const lastMessage = messages[messages.length - 1]

      // 处理退出登录
      if (lastMessage.action === 'logout') {
        this.handleLogout()
      }
    }
  },

  /**
   * 退出登录
   */
  handleLogout() {
    console.log('🚪 [WebView] 开始执行退出登录')

    try {
      // 清除本地存储
      wx.removeStorageSync('token')
      wx.removeStorageSync('refreshToken')
      wx.removeStorageSync('userInfo')
      console.log('🚪 [WebView] 已清除本地存储')

      // 显示退出提示
      wx.showToast({
        title: '已退出登录',
        icon: 'success',
        duration: 1500
      })

      // 延迟跳转到登录页
      setTimeout(() => {
        console.log('🚪 [WebView] 跳转到登录页')
        wx.reLaunch({
          url: '/pages/login/login',
          success: () => {
            console.log('🚪 [WebView] 跳转成功')
          },
          fail: (err) => {
            console.error('🚪 [WebView] 跳转失败:', err)
          }
        })
      }, 1500)
    } catch (error) {
      console.error('🚪 [WebView] 退出登录出错:', error)
      // 即使出错也要跳转到登录页
      wx.reLaunch({
        url: '/pages/login/login'
      })
    }
  },

  /**
   * 用户点击右上角转发
   */
  onShareAppMessage(res) {
    const token = wx.getStorageSync('token') || ''
    const userInfo = wx.getStorageSync('userInfo') || {}

    return {
      title: '企业AI办公助手 - 智能办公新体验',
      path: `/pages/login/login`,  // 转发后打开登录页，让对方也能登录使用
      imageUrl: ''  // 可选：自定义转发图片
    }
  },

  /**
   * 用户点击右上角转发到朋友圈
   */
  onShareTimeline() {
    return {
      title: '企业AI办公助手 - 智能办公新体验',
      query: '',  // 分享到朋友圈的参数
      imageUrl: ''  // 可选：自定义分享图片
    }
  }
})
