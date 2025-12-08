import { useEffect } from 'react';
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

  useEffect(() => {
    // 等待加载完成
    if (loading) return;

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
      console.log('🔒 [ProtectedRoute] 用户未登录');

      // 如果是登录失败的情况，避免立即重定向（防止循环）
      if (hasLoginFailed) {
        console.log('🔒 [ProtectedRoute] 检测到登录失败标志，延迟1秒后重定向');
        const timer = setTimeout(() => {
          if (isInMiniProgram()) {
            redirectToMiniProgramLogin(() => {
              navigate('/', { replace: true });
            });
          } else {
            navigate('/', { replace: true });
          }
        }, 1000);
        return () => clearTimeout(timer);
      }

      if (isInMiniProgram()) {
        console.log('🔒 [ProtectedRoute] 在小程序环境中，跳转到小程序登录页');

        // 使用工具函数处理小程序登录跳转
        redirectToMiniProgramLogin(() => {
          // 如果跳转失败，回退到 Web 端首页
          console.log('🔒 [ProtectedRoute] 小程序跳转失败，重定向到首页');
          navigate('/', { replace: true });
        });
      } else {
        console.log('🔒 [ProtectedRoute] 在普通浏览器中，重定向到首页');
        navigate('/', { replace: true });
      }
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

  // 如果用户未登录，不渲染子组件（防止闪烁）
  if (!user) {
    return null;
  }

  // 用户已登录，渲染子组件
  return children;
}

export default ProtectedRoute;
