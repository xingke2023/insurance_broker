# 🚀 快速启动指南

## 一、检查环境

### 1. 检查Python环境
```bash
python3 --version
# 应该显示 Python 3.x
```

### 2. 检查Node.js环境
```bash
node --version
npm --version
# Node.js 应该是 v16 或更高版本
```

### 3. 检查依赖是否安装

#### Python依赖
```bash
cd /var/www/harry-insurance
pip3 list | grep Django
pip3 list | grep djangorestframework
pip3 list | grep pymysql
pip3 list | grep pypdf
```

#### 前端依赖
```bash
cd /var/www/harry-insurance/frontend
ls node_modules
# 如果没有 node_modules 目录，需要运行: npm install
```

## 二、启动后端服务

### 方法1：使用启动脚本（推荐）
```bash
cd /var/www/harry-insurance
./start-backend.sh
```

### 方法2：手动启动
```bash
cd /var/www/harry-insurance
python3 manage.py runserver 0.0.0.0:8007
```

### 验证后端启动成功
打开浏览器访问：http://localhost:8007/api/
应该看到API根页面

后端日志输出示例：
```
System check identified no issues (0 silenced).
November 03, 2025 - 10:00:00
Django version 5.2.7, using settings 'backend.settings'
Starting development server at http://0.0.0.0:8007/
Quit the server with CONTROL-C.
```

## 三、启动前端服务

### 方法1：使用启动脚本（推荐）
```bash
cd /var/www/harry-insurance
./start-frontend.sh
```

### 方法2：手动启动
```bash
cd /var/www/harry-insurance/frontend
npm run dev
```

### 验证前端启动成功
前端日志输出示例：
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
  ➜  press h + enter to show help
```

打开浏览器访问：http://localhost:5173/

## 四、完整启动流程（推荐）

### 使用两个终端窗口

#### 终端1 - 启动后端
```bash
cd /var/www/harry-insurance
python3 manage.py runserver 0.0.0.0:8007
```
保持此终端运行，不要关闭

#### 终端2 - 启动前端
```bash
cd /var/www/harry-insurance/frontend
npm run dev
```
保持此终端运行，不要关闭

## 五、访问应用

1. **打开浏览器**
   - 访问：http://localhost:5173/

2. **导航到计划书提取工具**
   - 在首页点击"计划书数据提取工具"
   - 或直接在应用中切换到该页面

3. **开始使用**
   - 上传PDF文件
   - 查看提取进度
   - 编辑和保存数据

## 六、常见问题排查

### 问题1：后端无法启动
```bash
# 检查端口是否被占用
netstat -tlnp | grep 8007
# 或
lsof -i :8007

# 如果被占用，杀掉进程
kill -9 <PID>

# 检查数据库连接
python3 manage.py check
```

### 问题2：前端无法启动
```bash
# 重新安装依赖
cd /var/www/harry-insurance/frontend
rm -rf node_modules package-lock.json
npm install

# 清理缓存
npm cache clean --force
```

### 问题3：前端无法连接后端
```bash
# 检查API配置
cat frontend/src/config.js

# 确认后端服务正在运行
curl http://localhost:8007/api/

# 检查CORS设置
# 确保 backend/settings.py 中有：
# CORS_ALLOW_ALL_ORIGINS = True
```

### 问题4：数据库错误
```bash
# 运行迁移
cd /var/www/harry-insurance
python3 manage.py migrate

# 检查迁移状态
python3 manage.py showmigrations

# 查看数据库连接
python3 manage.py dbshell
```

## 七、停止服务

### 停止后端
在后端终端按 `Ctrl + C`

### 停止前端
在前端终端按 `Ctrl + C`

## 八、重启服务

### 快速重启
```bash
# 后端
Ctrl + C  # 停止
python3 manage.py runserver 0.0.0.0:8007  # 重启

# 前端
Ctrl + C  # 停止
npm run dev  # 重启
```

## 九、生产环境部署（高级）

### 后端生产部署
```bash
# 使用 gunicorn
pip3 install gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:8007

# 使用 uwsgi
pip3 install uwsgi
uwsgi --http :8007 --module backend.wsgi
```

### 前端生产部署
```bash
cd /var/www/harry-insurance/frontend
npm run build
# 构建后的文件在 dist 目录，使用 nginx 或其他服务器部署
```

## 十、快速命令参考

### 一键启动（后台运行）
```bash
# 启动后端（后台）
cd /var/www/harry-insurance
nohup python3 manage.py runserver 0.0.0.0:8007 > backend.log 2>&1 &

# 启动前端（后台）
cd /var/www/harry-insurance/frontend
nohup npm run dev > frontend.log 2>&1 &

# 查看日志
tail -f /var/www/harry-insurance/backend.log
tail -f /var/www/harry-insurance/frontend/frontend.log
```

### 查看运行状态
```bash
# 查看后端进程
ps aux | grep "manage.py runserver"

# 查看前端进程
ps aux | grep "vite"

# 查看端口占用
netstat -tlnp | grep -E "8007|5173"
```

## 十一、开发建议

### 推荐工作流
1. 启动后端（终端1）
2. 启动前端（终端2）
3. 打开浏览器并打开开发者工具（F12）
4. 开始开发和测试

### 调试技巧
- **后端调试**：查看终端输出的请求日志
- **前端调试**：使用浏览器开发者工具的Console和Network标签
- **数据库查询**：使用Django Admin或直接查询数据库

## 📞 需要帮助？

如果遇到问题：
1. 检查两个服务是否都在运行
2. 查看终端的错误信息
3. 检查浏览器控制台的错误
4. 确认网络连接和端口没有被防火墙阻止

---

**提示**: 建议使用 tmux 或 screen 来管理多个终端窗口，这样可以方便地切换和管理服务。
