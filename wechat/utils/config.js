// 全局配置文件
const config = {
  // API基础地址
  apiBaseUrl: 'https://hongkong.xingke888.com',

  // API接口
  api: {
    login: '/api/login/wechat',  // 微信登录接口
    getUserInfo: '/api/user/info',  // 获取用户信息
    createOrder: '/api/payment/create',  // 创建支付订单
  },

  /**
   * 获取完整的头像URL
   * @param {String} avatarUrl 头像URL（可能是相对路径或完整URL）
   * @returns {String} 完整的HTTPS URL
   */
  getFullAvatarUrl(avatarUrl) {
    if (!avatarUrl) {
      return ''
    }

    // 如果已经是完整的URL（http或https开头），直接返回
    if (avatarUrl.startsWith('http://') || avatarUrl.startsWith('https://')) {
      return avatarUrl
    }

    // 如果是相对路径，拼接域名
    // 确保路径以 / 开头
    const path = avatarUrl.startsWith('/') ? avatarUrl : '/' + avatarUrl
    return this.apiBaseUrl + path
  }
}

module.exports = config
