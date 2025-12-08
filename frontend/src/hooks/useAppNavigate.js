import { useNavigate } from 'react-router-dom';

/**
 * 自定义导航 hook，将旧的页面名称映射到新的路由路径
 * 兼容旧的 onNavigate 调用方式
 */
export function useAppNavigate() {
  const navigate = useNavigate();

  const appNavigate = (page) => {
    // 如果已经是完整路径（以 / 开头），直接使用
    if (page.startsWith('/')) {
      navigate(page);
      return;
    }

    // 映射旧的页面名称到新的路由路径
    const routeMap = {
      'home': '/',
      'dashboard': '/dashboard',
      'policies': '/policies',
      'plan-analyzer': '/plan-analyzer',
      'plan-analyzer-2': '/plan-analyzer-2',
      'plan-management': '/plan-management',
      'plan-builder': '/plan-builder',
    };

    const path = routeMap[page] || `/${page}`;
    navigate(path);
  };

  return appNavigate;
}
