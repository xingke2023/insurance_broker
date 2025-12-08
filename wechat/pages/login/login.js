// login.js
const request = require('../../utils/request.js')
const config = require('../../utils/config.js')

Page({
  data: {
    loading: false,
    agreed: false,  // 是否同意协议
    isLogout: false  // 是否是退出登录操作
  },

  onLoad(options) {
    console.log('==========================================');
    console.log('🔐 [Login] onLoad 开始');
    console.log('🔐 [Login] 接收到的参数:', JSON.stringify(options));

    // 检查是否是退出登录操作
    console.log('🔐 [Login] 检查退出登录条件:');
    console.log('  - options:', options);
    console.log('  - options.logout:', options?.logout);
    console.log('  - options.logout === "1":', options?.logout === '1');

    if (options && options.logout === '1') {
      console.log('✅ [Login] 检测到退出登录参数 logout=1');

      // 先清除本地存储
      console.log('🚪 [Login] 准备清除本地存储...');
      const tokenBefore = wx.getStorageSync('token');
      const refreshTokenBefore = wx.getStorageSync('refreshToken');
      const userInfoBefore = wx.getStorageSync('userInfo');
      console.log('  - 清除前 token:', tokenBefore ? tokenBefore.substring(0, 20) + '...' : 'null');
      console.log('  - 清除前 refreshToken:', refreshTokenBefore ? refreshTokenBefore.substring(0, 20) + '...' : 'null');
      console.log('  - 清除前 userInfo:', userInfoBefore || 'null');

      wx.removeStorageSync('token');
      wx.removeStorageSync('refreshToken');
      wx.removeStorageSync('userInfo');

      const tokenAfter = wx.getStorageSync('token');
      const refreshTokenAfter = wx.getStorageSync('refreshToken');
      const userInfoAfter = wx.getStorageSync('userInfo');
      console.log('✅ [Login] 存储已清除');
      console.log('  - 清除后 token:', tokenAfter || 'null');
      console.log('  - 清除后 refreshToken:', refreshTokenAfter || 'null');
      console.log('  - 清除后 userInfo:', userInfoAfter || 'null');

      // 设置退出登录标志
      console.log('🚪 [Login] 设置 isLogout = true');
      this.setData({
        isLogout: true
      }, () => {
        console.log('✅ [Login] isLogout 设置完成:', this.data.isLogout);
      });

      // 显示退出提示
      wx.showToast({
        title: '已退出登录',
        icon: 'success',
        duration: 1500
      });

      console.log('🚪 [Login] onLoad 完成，停留在登录页');
      console.log('==========================================');
      // 不再检查登录状态，直接停留在登录页
      return;
    }

    console.log('🔐 [Login] 非退出登录操作，检查登录状态');
    console.log('==========================================');
    // 检查是否已登录
    this.checkLoginStatus();
  },

  onShow() {
    console.log('🔐 [Login] onShow 触发');
    console.log('  - isLogout:', this.data.isLogout);

    // 如果是退出登录操作，不自动检查登录状态
    if (this.data.isLogout) {
      console.log('🚪 [Login] 退出登录状态，跳过自动登录检查');

      // 再次确认存储已清除
      const token = wx.getStorageSync('token');
      const refreshToken = wx.getStorageSync('refreshToken');
      const userInfo = wx.getStorageSync('userInfo');
      console.log('🔐 [Login] onShow 时的存储状态:');
      console.log('  - token:', token || 'null');
      console.log('  - refreshToken:', refreshToken || 'null');
      console.log('  - userInfo:', userInfo || 'null');

      // 如果存储还没清除，立即清除
      if (token || refreshToken || userInfo) {
        console.log('⚠️ [Login] 存储还未清除，立即清除');
        wx.removeStorageSync('token');
        wx.removeStorageSync('refreshToken');
        wx.removeStorageSync('userInfo');
      }

      return;
    }

    // 延迟一小段时间再检查登录状态，确保 onLoad 已经完成
    setTimeout(() => {
      console.log('🔐 [Login] onShow 延迟后检查登录状态');
      this.checkLoginStatus();
    }, 100);
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    console.log('🔐 [Login] checkLoginStatus 被调用');
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')

    console.log('🔐 [Login] 当前存储状态:');
    console.log('  - token:', token ? token.substring(0, 20) + '...' : 'null');
    console.log('  - userInfo:', userInfo || 'null');
    console.log('  - isLogout:', this.data.isLogout);

    if (token && userInfo) {
      console.log('✅ [Login] 检测到已登录，验证 token 有效性');
      // 显示加载提示
      wx.showLoading({
        title: '验证登录状态...',
        mask: true
      })

      // 验证 token 是否有效
      this.validateToken(token).then(isValid => {
        wx.hideLoading()

        if (isValid) {
          console.log('✅ [Login] Token 有效，跳转到 Dashboard');
          wx.showLoading({
            title: '正在进入...',
            mask: true
          })

          // Token 有效，跳转到 Dashboard
          const refreshToken = wx.getStorageSync('refreshToken')
          setTimeout(() => {
            wx.redirectTo({
              url: `/pages/webview/webview?token=${encodeURIComponent(token)}&refreshToken=${encodeURIComponent(refreshToken || '')}&url=${encodeURIComponent('https://hongkong.xingke888.com/dashboard')}`,
              success: () => {
                wx.hideLoading()
              },
              fail: () => {
                wx.hideLoading()
              }
            })
          }, 300)
        } else {
          console.log('❌ [Login] Token 已过期，清除本地存储');
          // Token 无效，清除本地存储
          wx.removeStorageSync('token')
          wx.removeStorageSync('refreshToken')
          wx.removeStorageSync('userInfo')
          wx.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none',
            duration: 2000
          })
        }
      }).catch(err => {
        wx.hideLoading()
        console.error('❌ [Login] 验证 token 失败:', err);
        // 验证失败，清除本地存储
        wx.removeStorageSync('token')
        wx.removeStorageSync('refreshToken')
        wx.removeStorageSync('userInfo')
        wx.showToast({
          title: '登录验证失败，请重新登录',
          icon: 'none',
          duration: 2000
        })
      })
    }
  },

  /**
   * 验证 token 是否有效
   * @param {String} token JWT token
   * @returns {Promise<Boolean>} token 是否有效
   */
  validateToken(token) {
    const request = require('../../utils/request.js')
    const config = require('../../utils/config.js')

    console.log('🔐 [Login] 开始验证 token...');

    return new Promise((resolve, reject) => {
      // 调用后端接口验证 token（使用 profile 接口）
      wx.request({
        url: config.apiBaseUrl + '/api/auth/profile/',
        method: 'GET',
        header: {
          'Authorization': 'Bearer ' + token,
          'Content-Type': 'application/json'
        },
        success: (res) => {
          console.log('🔐 [Login] Token 验证响应:', res.statusCode);
          if (res.statusCode === 200) {
            console.log('✅ [Login] Token 有效');
            resolve(true)
          } else {
            console.log('❌ [Login] Token 无效，状态码:', res.statusCode);
            resolve(false)
          }
        },
        fail: (err) => {
          console.error('❌ [Login] Token 验证请求失败:', err);
          reject(err)
        }
      })
    })
  },

  /**
   * 切换协议勾选状态
   */
  toggleAgreement() {
    this.setData({
      agreed: !this.data.agreed
    })
  },

  /**
   * 显示协议提示
   */
  showAgreementTip() {
    wx.showToast({
      title: '请阅读并同意用户协议及隐私政策',
      icon: 'none',
      duration: 2000
    })
  },

  /**
   * 处理微信登录 - 主登录入口
   */
  handleLogin() {
    if (this.data.loading) return

    // 重置退出登录标志
    this.setData({
      loading: true,
      isLogout: false
    })

    // 1. 调用wx.login获取code
    wx.login({
      success: (res) => {
        if (res.code) {
          console.log('获取到微信code:', res.code)
          // 2. 将code发送到后端（不带手机号）
          this.sendCodeToServer(res.code)
        } else {
          console.error('登录失败：' + res.errMsg)
          wx.showToast({
            title: '获取登录凭证失败',
            icon: 'none'
          })
          this.setData({
            loading: false
          })
        }
      },
      fail: (err) => {
        console.error('wx.login调用失败', err)
        wx.showToast({
          title: '登录失败，请重试',
          icon: 'none'
        })
        this.setData({
          loading: false
        })
      }
    })
  },

  /**
   * 发送code到服务器
   * @param {String} code 微信登录凭证
   */
  sendCodeToServer(code) {
    console.log('准备发送code到服务器:', code)

    const requestData = {
      code: code
    }

    request.post(config.api.login, requestData).then(res => {
      // 登录成功
      console.log('后端响应完整数据:', JSON.stringify(res))

      // 检查响应格式 - 后端返回格式是 { code: 200, message: '...', data: { token, refresh, userInfo } }
      if ((res.code === 200 || res.code === 0) && res.data) {
        const token = res.data.token
        const refreshToken = res.data.refresh
        const userInfo = res.data.userInfo || res.data.user_info || {}

        // 检查必要的登录信息
        if (!token) {
          console.error('✗ 响应中没有token字段')
          wx.showToast({
            title: '登录失败：缺少token',
            icon: 'none',
            duration: 2000
          })
          this.setData({
            loading: false
          })
          return
        }

        // 保存 access token
        if (token) {
          wx.setStorageSync('token', token)
          console.log('✓ Access Token已保存:', token.substring(0, 20) + '...')
        }

        // 保存 refresh token（用于自动刷新）
        if (refreshToken) {
          wx.setStorageSync('refreshToken', refreshToken)
          console.log('✓ Refresh Token已保存:', refreshToken.substring(0, 20) + '...')
        }

        if (userInfo && Object.keys(userInfo).length > 0) {
          wx.setStorageSync('userInfo', userInfo)
          console.log('✓ 用户信息已保存:', JSON.stringify(userInfo))
        } else {
          console.error('✗ 响应中没有userInfo字段或userInfo为空')
        }

        // 不再强制要求手机号和头像昵称，直接登录成功
        wx.showToast({
          title: '登录成功',
          icon: 'success',
          duration: 1500
        })

        // 延迟跳转到WebView Dashboard页面，传递token
        setTimeout(() => {
          // 显示加载提示
          wx.showLoading({
            title: '正在进入...',
            mask: true
          })

          wx.redirectTo({
            url: `/pages/webview/webview?token=${encodeURIComponent(token)}&refreshToken=${encodeURIComponent(refreshToken || '')}&url=${encodeURIComponent('https://hongkong.xingke888.com/dashboard')}`,
            success: () => {
              wx.hideLoading()
            },
            fail: () => {
              wx.hideLoading()
            }
          })
        }, 1500)

      } else if (res.code === 401) {
        // 用户已被禁用，清除本地存储并提示
        console.error('✗ 用户已被禁用')
        wx.removeStorageSync('token')
        wx.removeStorageSync('userInfo')
        wx.showToast({
          title: res.message || '用户已被禁用，请联系管理员',
          icon: 'none',
          duration: 3000
        })
        this.setData({
          loading: false
        })
      } else {
        // 响应格式不正确
        console.error('✗ 登录响应格式错误，期望 code=200，实际:', res)
        wx.showToast({
          title: res.message || '登录失败，请重试',
          icon: 'none',
          duration: 2000
        })
        this.setData({
          loading: false
        })
      }

    }).catch(err => {
      console.error('✗ 登录失败，错误对象:', JSON.stringify(err))
      console.error('✗ 错误详情 - message:', err.message)
      console.error('✗ 错误详情 - statusCode:', err.statusCode)
      console.error('✗ 错误详情 - detail:', err.detail)

      let errorMsg = '登录失败，请重试'
      if (err.message) {
        errorMsg = err.message
      } else if (err.detail) {
        errorMsg = err.detail
      } else if (err.statusCode) {
        errorMsg = `网络错误 (${err.statusCode})`
      }

      wx.showToast({
        title: errorMsg,
        icon: 'none',
        duration: 3000
      })

      this.setData({
        loading: false
      })
    })
  },

  /**
   * 用户协议
   */
  handleAgreement(e) {
    wx.navigateTo({
      url: '/pages/agreement/agreement'
    })
  },

  /**
   * 隐私政策
   */
  handlePrivacy(e) {
    wx.navigateTo({
      url: '/pages/privacy/privacy'
    })
  },

  /**
   * 用户点击右上角转发
   */
  onShareAppMessage(res) {
    return {
      title: '企业AI办公助手 - 智能办公新体验',
      path: '/pages/login/login',
      imageUrl: ''  // 可选：自定义转发图片
    }
  },

  /**
   * 用户点击右上角转发到朋友圈
   */
  onShareTimeline() {
    return {
      title: '企业AI办公助手 - 智能办公新体验',
      query: '',
      imageUrl: ''  // 可选：自定义分享图片
    }
  }
})
