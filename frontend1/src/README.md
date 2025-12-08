# DeepSeek OCR 识别检测 - 前端

> 基于 DeepSeek-OCR 模型的 Web 界面，用于测试 OCR 识别效果

![](https://img.shields.io/badge/React-18+-blue.svg)
![](https://img.shields.io/badge/TypeScript-5+-blue.svg)
![](https://img.shields.io/badge/TailwindCSS-4.0-38bdf8.svg)

## 📖 项目简介

这是一个现代化的 OCR 文档识别 Web 应用，采用极简商务风格设计，支持 PDF、PNG、JPG 等多种格式文件的 OCR 识别，并提供实时进度展示、文件浏览和内容预览功能。

### ✨ 核心功能

- 📁 **文件上传**：支持拖拽上传 PDF、PNG、JPG 格式文件
- 🔄 **实时解析**：显示 OCR 解析进度，支持后台异步处理
- 📂 **文件浏览**：树形结构浏览解析后的文件夹和文件
- 👁️ **内容预览**：支持 Markdown、图片、PDF 文件预览
- 🖼️ **图片放大**：点击图片可全屏查看
- 💾 **批量下载**：一键下载所有解析结果文件
- 🎨 **现代 UI**：玻璃态卡片、渐变色、柔和阴影、响应式设计

---

## 🚀 快速开始

### 环境要求

- Node.js 18+ 
- 现代浏览器（Chrome、Firefox、Safari、Edge）

### 方式一：在 Figma Make 中运行（推荐）

本项目由 Figma Make 生成，可以直接在 Figma Make 中运行：

1. 在 Figma Make 中打开本项目
2. 点击"运行"或"预览"按钮
3. 应用会自动在浏览器中打开

**优势**：
- ✅ 无需安装依赖
- ✅ 自动热重载
- ✅ 零配置启动

### 方式二：本地开发环境运行

如果您需要在本地开发环境中运行，请按照以下步骤：

#### 1. 安装依赖

由于这是一个纯前端项目，您需要使用构建工具（如 Vite）来运行。

**创建 `package.json`：**

```bash
npm init -y
```

**安装必要依赖：**

```bash
# 安装 Vite 和 React
npm install vite @vitejs/plugin-react react react-dom

# 安装 TypeScript
npm install -D typescript @types/react @types/react-dom

# 安装 Tailwind CSS
npm install -D tailwindcss@next @tailwindcss/vite postcss autoprefixer

# 安装其他依赖
npm install lucide-react react-markdown rehype-raw remark-gfm react-pdf sonner@2.0.3
```

#### 2. 创建配置文件

**创建 `vite.config.ts`：**

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    open: true,
  },
});
```

**创建 `tsconfig.json`：**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["**/*.ts", "**/*.tsx"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**创建 `index.html`：**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>DeepSeek OCR 识别检测</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/main.tsx"></script>
  </body>
</html>
```

**创建 `main.tsx`：**

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/globals.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
```

#### 3. 修改 `package.json` 添加启动脚本

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

#### 4. 启动开发服务器

```bash
npm run dev
```

应用会在 `http://localhost:3000` 启动。

#### 5. 构建生产版本

```bash
npm run build
```

构建后的文件会在 `dist` 目录中。

---

## ⚙️ 后端接口配置

### 修改后端地址

前端默认连接到本地后端服务 `http://127.0.0.1:8002`。如需修改后端地址，请编辑以下文件：

```
/config/api.ts
```

修改 `BASE_URL` 配置项：

```typescript
export const API_CONFIG = {
  /**
   * 后端 API 基础地址
   */
  BASE_URL: 'http://127.0.0.1:8002',  // 修改此处
};
```

#### 配置示例

**开发环境（本地）：**
```typescript
BASE_URL: 'http://127.0.0.1:8002'
```

**局域网服务器：**
```typescript
BASE_URL: 'http://192.168.1.100:8002'
```

**生产环境（域名）：**
```typescript
BASE_URL: 'https://api.your-domain.com'
```

**生产环境（IP + 端口）：**
```typescript
BASE_URL: 'http://your-server-ip:8002'
```

> ⚠️ **注意事项**：
> - 修改后无需重启项目，刷新页面即可生效
> - 确保后端服务已启动并可访问
> - 如使用 HTTPS，前端也需部署在 HTTPS 环境下（避免混合内容警告）
> - 跨域问题请在后端配置 CORS

---

## 📡 后端 API 接口说明

前端调用以下后端接口：

### 1. 文件上传
```
POST /api/upload
Content-Type: multipart/form-data
```

### 2. 启动 OCR 任务
```
POST /api/start
Content-Type: application/json
Body: {
  "file_path": "/workspace/uploads/xxx.pdf",
  "prompt": "<image>\n<|grounding|>Convert the document to markdown."
}
```

### 3. 查询任务进度
```
GET /api/progress/{task_id}
Response: {
  "status": "success",
  "progress": 65,
  "state": "running"
}
```

### 4. 获取任务结果
```
GET /api/result/{task_id}
Response: {
  "status": "success",
  "state": "finished",
  "result_dir": "/workspace/results/ocr_task_xxx"
}
```

### 5. 获取文件夹结构
```
GET /api/folder?path=/workspace/results/ocr_task_xxx
Response: {
  "status": "success",
  "children": [...]
}
```

### 6. 获取文件内容
```
GET /api/file/content?path=/workspace/results/xxx/file.md
Response (文本): { "content": "..." }
Response (图片): Binary image data
```

详细的 API 文档请参考后端项目的 OpenAPI 文档。

---

## 📂 项目结构

```
.
├── App.tsx                    # 主应用组件
├── config/
│   └── api.ts                 # API 配置文件（修改后端地址）
├── components/
│   ├── FileUploader.tsx       # 文件上传组件
│   ├── PromptInput.tsx        # 提示词输入和解析控制
│   ├── FileExplorer.tsx       # 文件浏览器（树形结构）
│   ├── FilePreview.tsx        # 文件内容预览
│   ├── figma/                 # Figma 组件
│   │   └── ImageWithFallback.tsx
│   └── ui/                    # shadcn/ui 组件库
│       ├── button.tsx
│       ├── dialog.tsx
│       ├── progress.tsx
│       ├── scroll-area.tsx
│       └── ...
└── styles/
    └── globals.css            # 全局样式
```

---

## 🎨 技术栈

- **React 18+** - UI 框架
- **TypeScript** - 类型安全
- **Tailwind CSS 4.0** - 样式框架
- **shadcn/ui** - UI 组件库
- **lucide-react** - 图标库
- **react-markdown** - Markdown 渲染
- **react-pdf** - PDF 预览
- **sonner** - Toast 通知

---

## 🔧 使用说明

### 1. 上传文件
- 点击上传区域或拖拽文件到上传区
- 支持 PDF、PNG、JPG 格式
- 文件上传成功后会显示预览

### 2. 配置提示词
- 在右侧"提示词输入"区域修改提示词
- 默认提示词：`<image>\n<|grounding|>Convert the document to markdown.`
- 提示词会影响 OCR 识别的输出格式

### 3. 开始解析
- 点击"开始解析"按钮启动 OCR 任务
- 进度条会实时显示解析进度
- 解析完成后会自动加载文件列表

### 4. 浏览结果
- 在"文件浏览器"中查看解析生成的文件
- 点击文件夹可展开/折叠
- 点击文件可在右侧预览内容

### 5. 查看内容
- **Markdown 文件**：渲染后的格式化文本
- **图片文件**：点击可全屏查看
- **PDF 文件**：分页预览

### 6. 下载文件
- 点击文件浏览器右上角的下载图标
- 可一键下载所有解析结果文件

---

## 🐛 常见问题

### Q1: 提示"无法连接到后端服务"
**A:** 检查以下几点：
1. 后端服务是否已启动
2. 后端地址配置是否正确（`/config/api.ts`）
3. 网络是否可达（ping 后端 IP）
4. 防火墙是否开放端口

### Q2: 文件上传后没有反应
**A:** 
1. 打开浏览器开发者工具（F12）查看 Network 标签
2. 检查 `/api/upload` 请求是否成功
3. 查看后端日志确认是否收到请求

### Q3: 解析进度卡住不动
**A:** 
1. 检查后端 OCR 进程是否正常运行
2. 查看后端日志是否有错误信息
3. 某些大文件可能需要较长时间处理

### Q4: 跨域问题（CORS）
**A:** 
后端需要配置 CORS 允许前端域名访问，在后端添加：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定具体域名
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Q5: 图片预览加载失败
**A:** 
1. 检查图片文件路径是否正确
2. 确认 `/api/file/content` 接口返回正确的图片数据
3. 查看浏览器控制台是否有跨域或 404 错误

---

## 🎯 开发建议

### 本地开发调试

1. **修改后端地址**：在 `/config/api.ts` 中配置本地后端地址
2. **查看网络请求**：使用浏览器开发者工具监控 API 调用
3. **查看日志**：检查浏览器 Console 和后端日志

### 部署到生产环境

1. 修改 `/config/api.ts` 为生产环境后端地址
2. 确保后端配置了正确的 CORS 策略
3. 建议使用 HTTPS 协议
4. 配置 CDN 加速静态资源

---

## 📄 开源协议

本项目基于《大模型 Agent 开发实战》体验课开发，仅供学习交流使用。

---

## 👨‍💻 作者

**九天Hector**

扫码免费领取项目源码（点击右上角"领取项目源码"按钮）

---

## 📞 技术支持

如有问题，请通过以下方式联系：

- 查看完整 API 文档
- 查看后端项目 README
- 提交 Issue 反馈问题

---

**Powered by DeepSeek-OCR & Figma Make**