// API配置
const getApiUrl = () => {
  const hostname = window.location.hostname;

  console.log('当前主机名:', hostname);

  // 如果是localhost，使用localhost直连
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    console.log('使用localhost API');
    return 'http://localhost:8017';
  }

  // 生产环境使用相对路径（通过Nginx反向代理）
  const apiUrl = window.location.origin;
  console.log('使用Nginx代理 API:', apiUrl);
  return apiUrl;
};

export const API_BASE_URL = getApiUrl();
export const API_URL = `${API_BASE_URL}/api`;

console.log('API配置:', { API_BASE_URL, API_URL });
