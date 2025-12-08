/**
 * 微信小程序 WebView 工具函数
 */

/**
 * 检测是否在小程序环境中
 * @returns {boolean} 是否在小程序环境
 */
export const isInMiniProgram = () => {
  // 方法1: 检查 wx.miniProgram (需要 JS-SDK)
  const hasMiniProgram = typeof window !== 'undefined' &&
                        typeof window.wx !== 'undefined' &&
                        typeof window.wx.miniProgram !== 'undefined';

  // 方法2: 检查 __wxjs_environment
  const hasWxEnvironment = typeof window !== 'undefined' &&
                          window.__wxjs_environment === 'miniprogram';

  // 方法3: 检查 user-agent
  const userAgent = navigator.userAgent || '';
  const hasWxUserAgent = userAgent.toLowerCase().indexOf('miniprogram') > -1;

  return hasMiniProgram || hasWxEnvironment || hasWxUserAgent;
};

/**
 * 跳转到小程序登录页
 * @param {Function} fallback - 如果不在小程序环境或跳转失败时的回调函数
 */
export const redirectToMiniProgramLogin = (fallback) => {
  console.log('🔒 [miniProgramUtils] 尝试跳转到小程序登录页');

  if (typeof window.wx !== 'undefined' && window.wx.miniProgram) {
    window.wx.miniProgram.reLaunch({
      url: '/pages/login/login',
      success: () => {
        console.log('✅ [miniProgramUtils] 成功跳转到小程序登录页');
      },
      fail: (err) => {
        console.error('❌ [miniProgramUtils] 跳转到登录页失败:', err);
        if (fallback) {
          fallback();
        }
      }
    });
  } else {
    console.warn('⚠️ [miniProgramUtils] wx.miniProgram 不可用');
    if (fallback) {
      fallback();
    }
  }
};

/**
 * 处理小程序退出登录
 * 先清除 Web 端存储，然后使用 reLaunch 跳转到登录页并传递 logout 参数
 * @param {Function} webLogout - Web 端的 logout 函数，用于清除 Web 端的存储
 * @param {Function} fallback - 如果跳转失败时的回调函数
 */
export const redirectToMiniProgramLogout = (webLogout, fallback) => {
  console.log('🚪 [miniProgramUtils] 执行小程序退出登录流程');

  // 先清除 Web 端的存储
  if (webLogout && typeof webLogout === 'function') {
    console.log('🚪 [miniProgramUtils] 清除 Web 端存储');
    try {
      webLogout();
      console.log('✅ [miniProgramUtils] Web 端存储已清除');
    } catch (e) {
      console.error('❌ [miniProgramUtils] 清除 Web 端存储失败:', e);
    }
  }

  if (typeof window.wx !== 'undefined' && window.wx.miniProgram) {
    console.log('🚪 [miniProgramUtils] 使用 reLaunch 跳转到登录页');

    // 使用 reLaunch 跳转到登录页，并传递 logout=1 参数
    // reLaunch 会关闭所有页面，然后打开目标页面
    // 登录页会检测 logout=1 参数，清除小程序存储并停留在登录页
    window.wx.miniProgram.reLaunch({
      url: '/pages/login/login?logout=1',
      success: () => {
        console.log('✅ [miniProgramUtils] reLaunch 到登录页成功');
      },
      fail: (err) => {
        console.error('❌ [miniProgramUtils] reLaunch 失败:', err);
        console.error('  错误详情:', JSON.stringify(err));

        // 如果 reLaunch 失败，尝试使用 redirectTo
        console.log('🚪 [miniProgramUtils] 尝试使用 redirectTo 作为备选');
        window.wx.miniProgram.redirectTo({
          url: '/pages/login/login?logout=1',
          success: () => {
            console.log('✅ [miniProgramUtils] redirectTo 到登录页成功');
          },
          fail: (err2) => {
            console.error('❌ [miniProgramUtils] redirectTo 也失败:', err2);
            if (fallback) {
              fallback();
            }
          }
        });
      }
    });
  } else {
    console.error('❌ [miniProgramUtils] wx.miniProgram 不存在');
    console.error('  window.wx:', typeof window.wx);
    console.error('  window.wx.miniProgram:', typeof window.wx?.miniProgram);
    if (fallback) {
      fallback();
    }
  }
};
