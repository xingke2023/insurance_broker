# 保单智能分析系统内部集成指南

## 概述

保单智能分析系统已经成功集成到主系统内部，作为一个内部页面而不是外部链接。

## 集成架构

```
主系统 (http://localhost:5173)
├── 首页 (HomePage)
├── 保单管理 (PolicyList)
├── 用户后台 (Dashboard)
└── 保单智能分析 (PlanAnalyzer) ← 新增内部页面
        ↓
        调用远程OCR API (101.36.226.245:8002)
```

## 技术实现

### 1. 组件集成

**文件**: `/var/www/harry-insurance/frontend/src/components/PlanAnalyzer.jsx`

- 从frontend1提取核心功能
- 转换TypeScript为JavaScript (JSX)
- 使用主系统的UI风格
- 集成远程OCR API

### 2. 路由配置

**文件**: `/var/www/harry-insurance/frontend/src/App.jsx`

```jsx
import PlanAnalyzer from './components/PlanAnalyzer'

// 添加路由
{currentPage === 'plan-analyzer' && <PlanAnalyzer onNavigate={setCurrentPage} />}
```

### 3. 导航入口

**文件**: `/var/www/harry-insurance/frontend/src/components/HomePage.jsx`

- 添加"保单智能分析系统"工具卡片 (ID: 13)
- 配置点击事件: `onNavigate('plan-analyzer')`
- 内部页面跳转，不再打开新标签页

### 4. 依赖安装

```bash
cd /var/www/harry-insurance/frontend
npm install lucide-react
```

## 启动方式

现在只需要启动2个服务（不再需要frontend1）：

```bash
# 终端1 - 后端
cd /var/www/harry-insurance
./start-backend.sh

# 终端2 - 主前端（已包含保单分析功能）
cd /var/www/harry-insurance
./start-frontend.sh
```

## 访问地址

- **主系统**: http://localhost:5173/
- **后端API**: http://localhost:8007/api/

## 使用流程

### 1. 访问保单分析页面

1. 打开主系统: http://localhost:5173/
2. 在首页找到"保单智能分析系统"工具卡片
3. 点击"立即使用"按钮
4. 直接在当前窗口打开保单分析页面

### 2. 使用分析功能

**左侧面板 - 文件上传**

1. 点击"上传文件"按钮选择PDF/图片
2. 支持PDF、PNG、JPG格式
3. 实时预览上传的文件
4. 点击删除按钮清除文件

**右侧面板 - AI分析**

1. **设置提示词**
   - 默认: `<image>\n<|grounding|>Convert the document to markdown.`
   - 可自定义修改

2. **开始分析**
   - 点击"开始分析"按钮
   - 实时显示处理进度
   - 等待AI完成解析

3. **查看结果**
   - 解析完成后显示文件列表
   - 点击文件查看内容
   - 支持Markdown和图片预览

### 3. 返回首页

点击页面右上角的"返回首页"按钮

## API配置

### 远程OCR API

**硬编码在组件中**: `frontend/src/components/PlanAnalyzer.jsx`

```javascript
const API_BASE_URL = 'http://101.36.226.245:8002';
```

### API接口列表

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/upload` | POST | 上传文件 |
| `/api/start` | POST | 开始解析任务 |
| `/api/progress/{task_id}` | GET | 查询处理进度 |
| `/api/result/{task_id}` | GET | 获取解析结果 |
| `/api/folder?path=...` | GET | 获取文件结构 |
| `/api/file/content?path=...` | GET | 读取文件内容 |

## 功能特性

### 保单分析系统功能

1. ✅ **文件上传与预览**
   - 支持多种格式
   - 实时预览
   - 拖拽支持（可扩展）

2. ✅ **AI智能解析**
   - 远程OCR识别
   - 实时进度显示
   - 自动轮询状态

3. ✅ **结果查看**
   - 文件浏览器
   - 内容预览
   - Markdown渲染

4. ✅ **用户体验**
   - 统一UI风格
   - 响应式布局
   - 加载状态提示

## 与frontend1的区别

| 特性 | Frontend1 (独立应用) | 集成后 (内部页面) |
|------|---------------------|------------------|
| 技术栈 | TypeScript + Vite | JavaScript (JSX) |
| UI组件库 | Radix UI | Tailwind + 自定义 |
| 访问方式 | 独立端口 (3001) | 内部路由 |
| 启动方式 | 单独启动 | 随主系统启动 |
| 图标库 | Lucide React | Lucide React |
| API配置 | 配置文件 | 组件内硬编码 |

## 端口使用

| 服务 | 端口 | 说明 |
|------|------|------|
| Django后端 | 8007 | 主系统API |
| 主前端 | 5173 | 包含所有功能 |
| 远程OCR | 8002 | OCR识别服务 |

**注意**: 不再需要端口3001（frontend1已集成）

## 文件结构

```
harry-insurance/
├── frontend/                    # 主前端应用
│   ├── src/
│   │   ├── components/
│   │   │   ├── HomePage.jsx    # 首页（已添加入口）
│   │   │   ├── PlanAnalyzer.jsx # 保单分析页面（新增）✨
│   │   │   ├── PolicyList.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Login.jsx
│   │   │   └── Register.jsx
│   │   ├── App.jsx             # 路由配置（已添加）
│   │   └── main.jsx
│   └── package.json            # 已添加lucide-react依赖
│
├── frontend1/                   # 独立应用（保留但不使用）
│   └── ...
│
├── api/                         # Django API
├── backend/                     # Django配置
├── start-backend.sh
└── start-frontend.sh
```

## 故障排查

### 问题1: 找不到lucide-react图标

```bash
# 安装图标库
cd /var/www/harry-insurance/frontend
npm install lucide-react
```

### 问题2: 无法连接到远程OCR服务

```bash
# 测试连通性
curl http://101.36.226.245:8002/api/

# 检查API地址配置
grep API_BASE_URL frontend/src/components/PlanAnalyzer.jsx
```

### 问题3: 页面无法跳转

检查以下内容：
1. App.jsx中是否添加了PlanAnalyzer路由
2. HomePage.jsx中是否配置了导航逻辑 (tool.id === 13)
3. 浏览器控制台是否有错误

### 问题4: 前端无法启动

```bash
# 重新安装依赖
cd /var/www/harry-insurance/frontend
rm -rf node_modules package-lock.json
npm install

# 重新启动
npm run dev
```

## 开发建议

### 修改远程API地址

如果需要更换OCR服务器：

1. 编辑组件文件：
```bash
vim /var/www/harry-insurance/frontend/src/components/PlanAnalyzer.jsx
```

2. 修改API地址：
```javascript
const API_BASE_URL = 'http://your-server-ip:port';
```

3. 重启前端（热更新会自动生效，但建议重启）：
```bash
# Ctrl+C 停止
./start-frontend.sh
```

### 添加更多功能

如需添加更多功能到PlanAnalyzer页面：
1. 编辑 `frontend/src/components/PlanAnalyzer.jsx`
2. 参考frontend1的实现 (`frontend1/src/App.tsx`)
3. 保持UI风格与主系统一致

### UI美化建议

- 使用Tailwind CSS类名
- 保持与其他页面一致的风格
- 参考HomePage、Dashboard的设计

## 优势

### 内部集成的优势

✅ **用户体验**
- 无需打开新标签页
- 统一的UI风格
- 流畅的页面切换

✅ **部署简化**
- 只需一个前端服务
- 减少端口占用
- 降低维护成本

✅ **开发效率**
- 共享依赖和配置
- 统一的开发流程
- 代码复用更容易

✅ **性能优化**
- 减少资源加载
- 共享缓存
- 更快的响应速度

## 更新日志

### 2025-11-05 - 内部集成版本

- ✅ 创建PlanAnalyzer内部组件
- ✅ 集成到主系统路由
- ✅ 添加导航入口
- ✅ 安装lucide-react依赖
- ✅ 配置远程OCR API连接
- ✅ 统一UI风格
- ✅ 编写集成文档

### 与外部链接版本的变化

- ❌ 移除外部链接跳转
- ❌ 不再需要独立启动frontend1
- ❌ 移除external和externalUrl配置
- ✅ 改为内部页面路由

## 测试清单

- [ ] 启动主系统后端和前端
- [ ] 访问首页，查看"保单智能分析系统"卡片
- [ ] 点击"立即使用"，确认在当前窗口打开
- [ ] 上传PDF文件，确认预览正常
- [ ] 点击"开始分析"，确认能连接远程API
- [ ] 查看处理进度，确认实时更新
- [ ] 查看解析结果，确认文件列表显示
- [ ] 点击文件，确认内容预览
- [ ] 点击"返回首页"，确认返回正常

## 支持

如有问题，请检查：
1. 主前端是否正常运行
2. 远程OCR服务是否可访问
3. 浏览器控制台的错误信息
4. 网络连接是否正常

---

**提示**: 保单分析功能已完全集成到主系统，无需单独启动frontend1！
