# 文案制作功能文档

## 功能概述

在香港保险人保单分析系统的 Dashboard 中新增了"文案制作"页面,该页面可以输入 YouTube 视频链接,调用 Gemini API 提取视频字幕并进行智能优化。

## 功能特性

1. **YouTube 视频字幕提取**
   - 支持多种 YouTube URL 格式
   - **直接使用 Gemini API 的 URL 上下文功能访问视频**
   - 自动提取完整字幕内容(优先中文,其次英文或其他语言)
   - AI 智能优化:删除重复、合理分段、修正错误
   - 无需依赖第三方字幕 API

2. **智能内容生成** (扩展功能)
   - 支持 URL 上下文访问
   - 支持 Google 搜索集成
   - 使用最新的 Gemini 2.0 Flash Exp 模型

## 项目结构

### 前端文件

```
frontend1/src/
├── components/
│   └── ContentCreator.tsx          # 文案制作页面组件
├── App.tsx                          # 添加了页面导航
└── config/
    └── api.ts                       # API 配置
```

### 后端文件

```
api/
├── content_creator_views.py         # 文案制作相关视图函数
└── urls.py                          # 添加了新的 API 路由
```

## API 接口

### 1. 提取视频字幕

**端点:** `POST /api/content/extract-subtitle`

**请求头:**
```
Authorization: Token <your_token>
Content-Type: application/json
```

**请求体:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**响应:**
```json
{
  "code": 200,
  "message": "字幕提取成功",
  "data": {
    "subtitle": "优化后的字幕内容...",
    "video_id": "VIDEO_ID"
  }
}
```

### 2. 使用上下文生成内容 (扩展功能)

**端点:** `POST /api/content/generate-with-context`

**请求头:**
```
Authorization: Token <your_token>
Content-Type: application/json
```

**请求体:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "prompt": "请分析这个视频的主要观点",
  "use_url_context": true,
  "use_google_search": false
}
```

**响应:**
```json
{
  "code": 200,
  "message": "内容生成成功",
  "data": {
    "content": "生成的内容..."
  }
}
```

## Gemini API 配置

### 环境变量

需要在系统中设置以下环境变量:

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

### Python 依赖

项目已安装以下依赖:

```
google-genai==1.41.0
google-generativeai==0.8.5
```

**注意**: 不再需要 `youtube-transcript-api`,因为我们直接使用 Gemini 的 URL 上下文功能。

## 使用 Gemini SDK 示例

项目根目录包含 `gemini_example.py` 示例文件,演示了如何使用新的 Gemini SDK:

```bash
# 设置 API Key
export GEMINI_API_KEY="your_api_key"

# 运行示例
python3 gemini_example.py
```

### 示例代码特点

1. **基本文本生成**
   - 使用 `gemini-2.0-flash-exp` 模型
   - 流式响应处理

2. **使用工具增强**
   - URL 上下文访问 (`url_context`)
   - Google 搜索集成 (`google_search`)

3. **配置选项**
   - 温度参数控制
   - 自定义提示词
   - 工具选择

## 新的 Gemini SDK 特性

根据你提供的示例代码,新 SDK 的主要变化:

### 旧 SDK (google-generativeai)
```python
import google.generativeai as genai
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')
response = model.generate_content(prompt)
```

### 新 SDK (google-genai)
```python
from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)
contents = [
    types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)],
    ),
]
config = types.GenerateContentConfig(
    temperature=1.0,
    tools=[
        types.Tool(url_context=types.UrlContext()),
        types.Tool(google_search=types.GoogleSearch()),
    ]
)
for chunk in client.models.generate_content_stream(
    model="gemini-2.0-flash-exp",
    contents=contents,
    config=config,
):
    print(chunk.text, end="")
```

## 前端界面

### 页面导航

在顶部 Header 添加了两个导航按钮:
- **保单分析**: 原有的文档分析功能
- **文案制作**: 新增的视频字幕提取功能

### 文案制作页面布局

- **左侧**: 输入区域
  - YouTube 视频链接输入框
  - 提取字幕按钮
  - 状态提示

- **右侧**: 结果显示区域
  - 优化后的字幕内容
  - 复制按钮
  - 空状态提示

- **底部**: 功能说明卡片

## 部署说明

### 1. 构建前端

```bash
cd /var/www/harry-insurance2/frontend1
npm run build
```

构建后的文件位于 `frontend1/build/` 目录。

### 2. 重启后端服务

```bash
# 如果使用 systemd
sudo systemctl restart gunicorn

# 如果使用开发服务器
pkill -f "manage.py runserver"
python3 manage.py runserver 0.0.0.0:8017
```

### 3. 配置 Nginx (如需要)

确保 Nginx 配置正确代理后端 API 和提供前端静态文件。

## 注意事项

1. **认证要求**: 所有 API 接口都需要用户认证 (Token)
2. **API 限额**: 注意 Gemini API 的调用限额和配额
3. **错误处理**: 前端会显示友好的错误提示
4. **字幕可用性**: 并非所有视频都有字幕,系统会提示相应错误

## 未来扩展

可以考虑添加以下功能:

1. 批量处理多个视频
2. 自定义字幕优化提示词
3. 导出为多种格式 (PDF, Word 等)
4. 字幕翻译功能
5. 视频摘要生成
6. 关键词提取

## 技术栈

- **前端**: React, TypeScript, TailwindCSS, shadcn/ui
- **后端**: Django, Django REST Framework
- **AI**: Google Gemini 2.0 Flash, YouTube Transcript API
- **部署**: Nginx, Gunicorn

## 联系与支持

如有问题或建议,请联系开发团队。
