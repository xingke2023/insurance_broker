/**
 * 会员权限辅助工具
 */

/**
 * 处理API错误响应，检查是否为会员权限问题
 * @param {Error} error - Axios错误对象
 * @param {Function} navigate - 导航函数
 * @returns {boolean} - 如果是会员权限问题返回true，否则返回false
 */
export const handleMembershipError = (error, navigate) => {
  if (error.response?.status === 403) {
    const data = error.response.data;

    // 检查是否为会员过期或无会员
    if (data.error === 'membership_expired' || data.error === 'no_membership') {
      const message = data.message || '请加入会员计划以使用此功能';

      // 显示提示
      if (window.confirm(`${message}\n\n是否前往会员计划页面？`)) {
        navigate('membership-plans');
      }

      return true;
    }
  }

  return false;
};

/**
 * 显示会员权限提示对话框
 * @param {string} message - 提示信息
 * @param {Function} navigate - 导航函数
 */
export const showMembershipAlert = (message, navigate) => {
  const defaultMessage = '您的会员已过期，请续费以继续使用此功能';
  const displayMessage = message || defaultMessage;

  if (window.confirm(`${displayMessage}\n\n是否前往会员计划页面？`)) {
    navigate('membership-plans');
  }
};

/**
 * 检查错误是否为会员权限错误
 * @param {Error} error - Axios错误对象
 * @returns {boolean}
 */
export const isMembershipError = (error) => {
  if (error.response?.status === 403) {
    const errorType = error.response.data?.error;
    return errorType === 'membership_expired' || errorType === 'no_membership';
  }
  return false;
};

/**
 * 从错误对象中获取会员权限相关信息
 * @param {Error} error - Axios错误对象
 * @returns {Object|null} - 会员权限错误信息，如果不是会员错误则返回null
 */
export const getMembershipErrorInfo = (error) => {
  if (isMembershipError(error)) {
    return {
      error: error.response.data.error,
      message: error.response.data.message,
      redirect: error.response.data.redirect,
      endDate: error.response.data.end_date
    };
  }
  return null;
};
