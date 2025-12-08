import { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { setupAxiosInterceptors } from '../utils/axiosConfig';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('access_token'));

  // Setup axios interceptors for automatic token refresh
  useEffect(() => {
    const handleLogout = () => {
      // Clear local storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');

      // Clear axios headers
      delete axios.defaults.headers.common['Authorization'];

      // Clear state
      setToken(null);
      setUser(null);

      // Redirect to home
      window.location.href = '/';
    };

    setupAxiosInterceptors(handleLogout);
  }, []);

  useEffect(() => {
    const initAuth = async () => {
      console.log('🔐 [AuthContext] 开始初始化认证...');
      console.log('🔐 [AuthContext] 当前URL:', window.location.href);
      console.log('🔐 [AuthContext] 是否在小程序WebView:', window.__wxjs_environment === 'miniprogram');

      // 检查URL参数中是否有小程序传来的token
      const urlParams = new URLSearchParams(window.location.search);
      const miniappToken = urlParams.get('miniapp_token');
      const miniappRefreshToken = urlParams.get('miniapp_refresh_token');

      if (miniappToken) {
        console.log('🔐 [AuthContext] 检测到小程序token:', miniappToken.substring(0, 20) + '...');
        if (miniappRefreshToken) {
          console.log('🔐 [AuthContext] 检测到小程序refresh token');
        }
        // 从小程序自动登录
        const result = await loginWithToken(miniappToken, miniappRefreshToken);
        if (result.success) {
          console.log('🔐 [AuthContext] 小程序登录完成，用户ID:', result.userData?.id);
          // 只有登录成功才清除URL中的token参数
          const url = new URL(window.location);
          url.searchParams.delete('miniapp_token');
          url.searchParams.delete('miniapp_refresh_token');
          window.history.replaceState({}, '', url);
        } else {
          console.error('🔐 [AuthContext] 小程序登录失败:', result.error);
          // 登录失败，清除token参数并标记失败状态
          const url = new URL(window.location);
          url.searchParams.delete('miniapp_token');
          url.searchParams.delete('miniapp_refresh_token');
          url.searchParams.set('login_failed', '1');
          window.history.replaceState({}, '', url);
        }
      } else {
        console.log('🔐 [AuthContext] 没有小程序token，从本地存储加载');
        // 检查本地存储的token
        const storedToken = localStorage.getItem('access_token');
        const storedUser = localStorage.getItem('user');

        if (storedToken && storedUser) {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
          // 设置axios默认headers
          axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
          console.log('🔐 [AuthContext] 从缓存加载用户成功，用户ID:', JSON.parse(storedUser)?.id);
        } else {
          console.log('🔐 [AuthContext] 本地存储没有用户信息');
        }
      }
      console.log('🔐 [AuthContext] 认证初始化完成，设置loading=false');
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login/`, {
        username,
        password
      });

      const { user: userData, tokens } = response.data;

      // 保存到本地存储
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      localStorage.setItem('user', JSON.stringify(userData));

      // 更新状态
      setToken(tokens.access);
      setUser(userData);

      // 设置axios默认headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || '登录失败'
      };
    }
  };

  const register = async (username, email, password, full_name) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/register/`, {
        username,
        email,
        password,
        full_name
      });

      const { user: userData, tokens } = response.data;

      // 保存到本地存储
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      localStorage.setItem('user', JSON.stringify(userData));

      // 更新状态
      setToken(tokens.access);
      setUser(userData);

      // 设置axios默认headers
      axios.defaults.headers.common['Authorization'] = `Bearer ${tokens.access}`;

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || '注册失败'
      };
    }
  };

  const loginWithToken = async (accessToken, refreshToken = null) => {
    try {
      console.log('🔐 [loginWithToken] 开始使用token获取用户信息...');
      // 使用token获取用户信息
      axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
      const response = await axios.get(`${API_BASE_URL}/api/auth/profile/`);

      const userData = response.data;
      console.log('🔐 [loginWithToken] 获取到用户信息:', userData);

      // 保存到本地存储
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('user', JSON.stringify(userData));

      // 如果提供了 refresh token，也保存
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
        console.log('🔐 [loginWithToken] Refresh token 已保存');
      }

      // 更新状态
      setToken(accessToken);
      setUser(userData);

      console.log('🔐 [loginWithToken] 登录成功，状态已更新');
      return { success: true, userData };
    } catch (error) {
      console.error('🔐 [loginWithToken] Token登录失败:', error);
      return {
        success: false,
        error: error.response?.data?.error || 'Token登录失败'
      };
    }
  };

  const logout = () => {
    // 清除本地存储
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');

    // 清除axios headers
    delete axios.defaults.headers.common['Authorization'];

    // 清除状态
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    loading,
    login,
    loginWithToken,
    register,
    logout,
    isAuthenticated: !!user
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
