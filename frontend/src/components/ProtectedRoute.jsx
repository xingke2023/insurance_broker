import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { isInMiniProgram, redirectToMiniProgramLogin } from '../utils/miniProgramUtils';

/**
 * 受保护的路由组件
 * 只有已登录的用户才能访问，未登录用户会被重定向到首页
 */
function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  const hasRedirected = useRef(false);

  useEffect(() => {
    // 等待加载完成
    if (loading) {
      console.log('🔒 [ProtectedRoute] 等待加载完成...');
      return;
    }

    // 如果已经重定向过，避免重复
    if (hasRedirected.current) {
      console.log('🔒 [ProtectedRoute] 已经执行过重定向，跳过');
      return;
    }

    // 检查URL参数
    const urlParams = new URLSearchParams(window.location.search);
    const hasMiniappToken = urlParams.has('miniapp_token');
    const hasLoginFailed = urlParams.has('login_failed');

    // 如果URL中有miniapp_token，说明正在处理登录，不要重定向
    if (hasMiniappToken) {
      console.log('🔒 [ProtectedRoute] URL中有miniapp_token，正在处理登录，跳过重定向检查');
      return;
    }

    // 如果用户未登录，重定向到首页或小程序登录页
    if (!user) {
      console.log('🔒 [ProtectedRoute] 用户未登录，准备重定向');
      console.log('🔒 [ProtectedRoute] 当前路径:', window.location.pathname);

      // 标记已经执行过重定向
      hasRedirected.current = true;

      // 检测是否在小程序环境
      const inMiniProgram = isInMiniProgram();
      console.log('🔒 [ProtectedRoute] 是否在小程序环境:', inMiniProgram);

      if (inMiniProgram && !hasLoginFailed) {
        console.log('🔒 [ProtectedRoute] 在小程序环境中，跳转到小程序登录页');

        // 使用工具函数处理小程序登录跳转
        redirectToMiniProgramLogin(() => {
          // 如果跳转失败，回退到 Web 端首页
          console.log('🔒 [ProtectedRoute] 小程序跳转失败，使用window.location强制跳转');
          window.location.replace('/');
        });
      } else {
        console.log('🔒 [ProtectedRoute] 在普通浏览器中，立即重定向到首页');

        // 直接使用window.location.replace，确保跳转生效
        window.location.replace('/');
      }
    } else {
      console.log('🔒 [ProtectedRoute] 用户已登录，允许访问');
    }
  }, [user, loading, navigate]);

  // 加载中显示空白或加载动画
  if (loading) {
    return (
      <div className="min-h-screen bg-blue-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-600"></div>
          <p className="mt-4 text-gray-600 text-sm font-medium">加载中...</p>
        </div>
      </div>
    );
  }

  // 如果用户未登录，显示加载动画（等待重定向）
  if (!user) {
    return (
      <div className="min-h-screen bg-blue-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-600"></div>
          <p className="mt-4 text-gray-600 text-sm font-medium">正在跳转...</p>
        </div>
      </div>
    );
  }

  // 用户已登录，渲染子组件
  return children;
}

export default ProtectedRoute;
