# 快速启动指南

## 方式一：使用启动脚本（推荐）

### 启动后端
打开第一个终端窗口：
```bash
cd /var/www/harry-insurance
./start-backend.sh
```

### 启动前端
打开第二个终端窗口：
```bash
cd /var/www/harry-insurance
./start-frontend.sh
```

## 方式二：手动启动

### 启动后端
```bash
cd /var/www/harry-insurance
python3 manage.py runserver 0.0.0.0:8007
```

### 启动前端
```bash
cd /var/www/harry-insurance/frontend
npm run dev
```

## 访问应用

- **前端界面**: http://localhost:8008 (或使用服务器IP:8008)
- **后端API**: http://localhost:8007/api/ (或使用服务器IP:8007)
- **Django管理后台**: http://localhost:8007/admin/

## 首次使用

1. 确保MySQL数据库服务已启动（端口8510）
2. 数据库迁移已完成（如果没有，运行 `python3 manage.py migrate`）
3. 同时启动前端和后端服务
4. 在浏览器访问前端地址开始使用

## 测试API

使用curl测试API：

```bash
# 获取所有保单
curl http://localhost:8007/api/policies/

# 创建新保单
curl -X POST http://localhost:8007/api/policies/ \
  -H "Content-Type: application/json" \
  -d '{
    "policy_number": "P001",
    "customer_name": "张三",
    "policy_type": "人寿保险",
    "premium": "5000.00",
    "start_date": "2025-01-01",
    "end_date": "2026-01-01",
    "status": "active"
  }'
```

## 常见问题

### 端口已被占用
如果8007或8008端口已被占用，可以修改端口：

**后端（修改端口为其他端口）:**
```bash
python3 manage.py runserver 0.0.0.0:8080
```

**前端（修改 frontend/vite.config.js）:**
```javascript
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 3000
  }
})
```

### 数据库连接失败
检查MySQL服务是否运行在8510端口：
```bash
mysql -h localhost -P 8510 -u root -p
```

### 前端无法连接后端
检查CORS配置是否正确，确认前端URL在 `backend/settings.py` 的 `CORS_ALLOWED_ORIGINS` 中。

## 停止服务

在相应的终端窗口按 `Ctrl + C` 即可停止服务。
