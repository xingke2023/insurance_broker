# React Router 路由配置说明

## 可用路由列表

应用已升级为使用 `react-router-dom` 支持真正的 URL 路由。

### 主要路由

| 路径 | 组件 | 描述 |
|------|------|------|
| `/` | HomePage | 首页（默认路由） |
| `/home` | HomePage | 首页（别名） |
| `/dashboard` | Dashboard | 用户仪表板 |
| `/policies` | PolicyList | 保单列表 |
| `/plan-analyzer` | PlanAnalyzer | 计划书分析工具（原版） |
| `/plan-analyzer-2` | PlanAnalyzer2 | 计划书分析工具 2.0（独立版本） |
| `/plan-management` | PlanDocumentManagement | 计划书文档管理 |

### 直接 URL 访问

现在可以直接通过 URL 访问任何页面，例如：

```
http://your-domain.com/plan-analyzer-2
http://your-domain.com/dashboard
http://your-domain.com/plan-management
```

## 开发环境

开发环境下，Vite 开发服务器已经自动配置了 SPA fallback，所有路由都能正常工作。

启动开发服务器：
```bash
npm run dev
```

## 生产环境配置

### 使用 Nginx

如果使用 Nginx 作为 Web 服务器，需要配置 `try_files` 指令：

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

完整的 Nginx 配置示例请查看 `nginx.conf.example` 文件。

### 部署到生产环境

1. 构建生产版本：
   ```bash
   npm run build
   ```

2. 将 `dist` 目录部署到 Web 服务器

3. 确保服务器配置支持 SPA 路由（参考 `nginx.conf.example`）

## 代码中的导航

### 使用 useAppNavigate Hook

所有组件已更新为使用自定义的 `useAppNavigate` hook，它兼容旧的导航方式：

```javascript
import { useAppNavigate } from '../hooks/useAppNavigate';

function MyComponent() {
  const navigate = useAppNavigate();

  // 使用页面名称导航（兼容旧代码）
  navigate('plan-analyzer-2');  // 会自动转换为 /plan-analyzer-2
  navigate('home');              // 会自动转换为 /
}
```

### 使用原生 react-router-dom

你也可以直接使用 react-router-dom 的 `useNavigate` hook：

```javascript
import { useNavigate } from 'react-router-dom';

function MyComponent() {
  const navigate = useNavigate();

  // 使用路径导航
  navigate('/plan-analyzer-2');
  navigate('/dashboard');

  // 返回上一页
  navigate(-1);
}
```

### 使用 Link 组件

```javascript
import { Link } from 'react-router-dom';

<Link to="/plan-analyzer-2">打开计划书分析工具 2.0</Link>
```

## 特殊说明

### PlanAnalyzer vs PlanAnalyzer2

- **PlanAnalyzer** (`/plan-analyzer`)：原始版本，返回按钮指向计划书列表
- **PlanAnalyzer2** (`/plan-analyzer-2`)：独立版本，返回按钮指向首页
- 两个版本使用不同的 localStorage 键名，数据互不干扰

### 路由守卫

如果需要添加路由守卫（如登录验证），可以在 `App.jsx` 中使用包装组件：

```javascript
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/" />;
}

// 在 Routes 中使用
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
```

## 故障排除

### 刷新页面出现 404

这表示服务器没有正确配置 SPA fallback。确保：

1. Nginx 配置了 `try_files $uri $uri/ /index.html;`
2. 或者在 `public` 目录添加了 `_redirects` 文件（用于 Netlify 等平台）

### 路由不工作

1. 检查浏览器控制台是否有错误
2. 确认所有组件都已更新为使用 `useAppNavigate` 或 `useNavigate`
3. 检查路由路径是否正确（区分大小写）

## 后续优化建议

1. **代码分割**：使用 React.lazy 和 Suspense 进行路由级代码分割
2. **路由守卫**：添加身份验证和权限检查
3. **面包屑导航**：添加面包屑组件显示当前位置
4. **404 页面**：创建专门的 404 错误页面
