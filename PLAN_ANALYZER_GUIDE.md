# 保单智能分析系统集成指南

## 概述

保单智能分析系统（frontend1）已成功集成到主系统中，提供基于AI的保单文档OCR识别和智能分析功能。

## 系统架构

```
主系统 (frontend - 端口5173)
    ↓
    打开新标签页 → 保单智能分析系统 (frontend1 - 端口3001)
                        ↓
                        调用远程OCR API (101.36.226.245:8002)
```

## 功能特性

### 保单智能分析系统特点

1. **文件上传**
   - 支持 PDF、PNG、JPG 格式
   - 实时文件预览
   - 拖拽上传支持

2. **AI智能解析**
   - 远程OCR识别服务
   - 实时处理进度显示
   - 自动提取关键信息

3. **结果展示**
   - 文件浏览器
   - Markdown格式报告
   - 图片查看功能

## 启动方式

### 方法1：使用启动脚本

```bash
# 终端1 - 启动后端
cd /var/www/harry-insurance
./start-backend.sh

# 终端2 - 启动主前端
cd /var/www/harry-insurance
./start-frontend.sh

# 终端3 - 启动保单分析系统
cd /var/www/harry-insurance
./start-frontend1.sh
```

### 方法2：手动启动

```bash
# 终端1 - 后端 (端口8007)
cd /var/www/harry-insurance
python3 manage.py runserver 0.0.0.0:8007

# 终端2 - 主前端 (端口5173)
cd /var/www/harry-insurance/frontend
npm run dev

# 终端3 - 保单分析系统 (端口3001)
cd /var/www/harry-insurance/frontend1
npm run dev
```

## 访问地址

- **主系统**: http://localhost:5173/
- **保单分析系统**: http://localhost:3001/
- **后端API**: http://localhost:8007/api/

## 使用流程

### 1. 从主系统访问

1. 打开主系统: http://localhost:5173/
2. 在首页找到"保单智能分析系统"工具卡片
3. 点击"打开工具"按钮
4. 系统会在新标签页打开保单分析系统

### 2. 使用保单分析功能

1. **上传文件**
   - 点击"上传文件"按钮选择PDF/图片
   - 或直接拖拽文件到上传区域
   - 系统自动上传到远程OCR服务器

2. **设置提示词**（可选）
   - 默认提示词：`<image>\n<|grounding|>Convert the document to markdown.`
   - 可根据需求自定义

3. **开始解析**
   - 点击"开始分析"按钮
   - 实时查看处理进度
   - 等待AI完成解析

4. **查看结果**
   - 解析完成后，左侧显示文件浏览器
   - 点击文件查看内容
   - 支持Markdown预览和图片查看

## API配置

### Frontend1 API配置

文件路径: `/var/www/harry-insurance/frontend1/src/config/api.ts`

```typescript
export const API_CONFIG = {
  BASE_URL: 'http://101.36.226.245:8002',  // 远程OCR服务器
};
```

### API接口说明

Frontend1调用的远程OCR API接口：

| 接口 | 方法 | 说明 | 响应 |
|------|------|------|------|
| `/api/upload` | POST | 上传文件 | `{ status, file_path }` |
| `/api/start` | POST | 开始解析 | `{ status, task_id }` |
| `/api/progress/{task_id}` | GET | 查询进度 | `{ status, state }` |
| `/api/result/{task_id}` | GET | 获取结果 | `{ status, result_dir }` |
| `/api/folder?path=...` | GET | 获取文件结构 | `{ status, children }` |
| `/api/file/content?path=...` | GET | 读取文件内容 | `{ status, content }` |
| `/api/file/view?path=...` | GET | 获取图片/PDF | 二进制数据 |

## 端口使用

| 服务 | 端口 | 说明 |
|------|------|------|
| Django后端 | 8007 | 主系统API |
| 主前端 | 5173 | 保险管理系统 |
| 保单分析系统 | 3001 | AI文档分析 |
| 远程OCR服务 | 8002 | OCR识别服务 |

## 技术栈

### 保单分析系统 (frontend1)

- **框架**: React 18 + TypeScript
- **构建工具**: Vite 6.3.5
- **UI组件**: Radix UI
- **样式**: Tailwind CSS 4
- **图标**: Lucide React
- **其他**: React Markdown、Sonner Toast

## 故障排查

### 问题1: 保单分析系统无法启动

```bash
# 检查依赖是否安装
cd /var/www/harry-insurance/frontend1
ls node_modules

# 如果没有，重新安装
npm install
```

### 问题2: 无法连接到远程OCR服务

```bash
# 测试远程服务器连通性
curl http://101.36.226.245:8002/api/

# 检查API配置
cat frontend1/src/config/api.ts
```

### 问题3: 端口被占用

```bash
# 检查端口占用
netstat -tlnp | grep -E "5173|3001|8007"

# 修改端口配置
# 编辑 frontend1/vite.config.ts 中的 server.port
```

### 问题4: 从主系统打开失败

检查以下内容：
1. 保单分析系统是否正在运行
2. 端口3001是否开放
3. 浏览器是否阻止弹出窗口

## 开发建议

### 修改远程API地址

如果需要修改远程OCR服务器地址：

1. 编辑配置文件：
```bash
vim /var/www/harry-insurance/frontend1/src/config/api.ts
```

2. 修改BASE_URL：
```typescript
export const API_CONFIG = {
  BASE_URL: 'http://your-server-ip:port',
};
```

3. 重启服务：
```bash
# Ctrl+C 停止当前服务
./start-frontend1.sh
```

### 本地开发模式

如果有本地OCR服务器：

```typescript
// frontend1/src/config/api.ts
export const API_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8002',  // 本地服务器
};
```

## 项目结构

```
harry-insurance/
├── frontend/              # 主前端 (React + Vite)
│   ├── src/
│   │   └── components/
│   │       └── HomePage.jsx   # 已添加保单分析入口
│   └── package.json
│
├── frontend1/             # 保单分析系统 (React + TypeScript)
│   ├── src/
│   │   ├── App.tsx       # 主应用
│   │   ├── components/
│   │   │   ├── FileUploader.tsx    # 文件上传
│   │   │   ├── FileExplorer.tsx    # 文件浏览
│   │   │   ├── FilePreview.tsx     # 文件预览
│   │   │   └── PromptInput.tsx     # 提示词输入
│   │   └── config/
│   │       └── api.ts    # API配置
│   ├── vite.config.ts
│   └── package.json
│
├── api/                   # Django API
├── backend/               # Django配置
├── start-backend.sh       # 后端启动脚本
├── start-frontend.sh      # 主前端启动脚本
└── start-frontend1.sh     # 保单分析系统启动脚本 (新增)
```

## 更新日志

### 2025-11-05

- ✅ 集成保单智能分析系统 (frontend1)
- ✅ 配置远程OCR API连接 (101.36.226.245:8002)
- ✅ 在主系统添加导航入口
- ✅ 创建独立启动脚本
- ✅ 编写完整集成文档

## 支持

如有问题，请检查：
1. 所有服务是否正常运行
2. 端口是否正确配置
3. 远程OCR服务是否可访问
4. 浏览器控制台错误信息

---

**提示**: 保单分析系统使用远程OCR服务，无需本地部署AI模型。
