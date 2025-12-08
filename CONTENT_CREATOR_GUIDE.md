# 文案制作功能使用指南

## 功能概述

文案制作页面是一个 AI 驱动的工具,可以从 YouTube 视频中自动提取字幕内容,帮助你快速获取视频文案。

## 功能特性

1. **YouTube 视频字幕提取**
   - 支持标准 YouTube 链接: `https://www.youtube.com/watch?v=xxxxx`
   - 支持短链接: `https://youtu.be/xxxxx`
   - 自动识别中文、英文等多语言字幕
   - 优先提取中文字幕,其次英文字幕

2. **AI 智能优化**
   - 使用 Google Gemini AI 自动优化字幕格式
   - 删除重复内容
   - 合理分段
   - 修正明显错误

3. **便捷操作**
   - 一键复制字幕内容
   - 实时显示提取进度
   - 友好的错误提示

## 安装配置

### 1. 安装 Python 依赖

依赖包已经添加到 `requirements.txt`,运行以下命令安装:

```bash
pip3 install -r requirements.txt
```

主要依赖:
- `google-generativeai>=0.3.0` - Google Gemini AI SDK
- `youtube-transcript-api>=0.6.0` - YouTube 字幕提取库

### 2. 配置 Gemini API Key

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey) 获取 API Key
2. 在 `.env` 文件中添加配置:

```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

**注意**: 如果不配置 `GEMINI_API_KEY`,功能仍可使用,但不会进行 AI 优化处理。

## 使用方法

### 1. 访问页面

- 登录后在 Dashboard 点击 **"文案制作"** 快捷入口
- 或直接访问: `/content-creator`

### 2. 提取字幕

1. 在输入框中粘贴 YouTube 视频链接
2. 点击 **"提取字幕"** 按钮
3. 等待 AI 处理(通常需要几秒到十几秒)
4. 字幕内容会显示在下方文本框中

### 3. 复制内容

点击 **"复制"** 按钮,字幕内容会自动复制到剪贴板。

## API 接口

### 提取字幕接口

**URL**: `/api/content/extract-subtitle`

**方法**: `POST`

**认证**: 需要 Bearer Token

**请求体**:
```json
{
  "video_url": "https://www.youtube.com/watch?v=xxxxx"
}
```

**成功响应** (200):
```json
{
  "code": 200,
  "message": "字幕提取成功",
  "data": {
    "subtitle": "提取的字幕内容...",
    "video_id": "xxxxx"
  }
}
```

**错误响应**:
```json
{
  "code": 400,
  "message": "无效的 YouTube 视频链接"
}
```

## 常见问题

### 1. 提示"该视频没有可用的字幕"

**原因**:
- 视频没有字幕
- 视频的字幕被禁用
- 视频是私有的

**解决方案**: 选择有公开字幕的视频

### 2. 提取速度较慢

**原因**:
- 视频字幕内容较多
- Gemini AI 处理需要时间
- 网络连接较慢

**解决方案**: 耐心等待,通常不会超过30秒

### 3. 无法访问 YouTube

**原因**: 可能需要配置代理

**解决方案**:
- 确保服务器可以访问 YouTube
- 或使用支持代理的部署环境

## 技术架构

### 前端 (React)
- **组件**: `/frontend/src/components/ContentCreator.jsx`
- **路由**: `/content-creator`
- **特性**:
  - 实时加载状态
  - 错误处理
  - 响应式设计

### 后端 (Django)
- **视图**: `/api/content_creator_views.py`
- **URL**: `/api/content/extract-subtitle`
- **认证**: JWT Token
- **流程**:
  1. 提取视频 ID
  2. 调用 YouTube Transcript API 获取字幕
  3. 使用 Gemini AI 优化格式
  4. 返回处理后的字幕

## 开发扩展

### 添加新语言支持

在 `content_creator_views.py` 中修改语言优先级:

```python
# 添加更多语言代码
transcript = transcript_list.find_transcript([
    'zh-CN', 'zh-Hans', 'zh', 'zh-TW', 'zh-Hant',  # 中文
    'en',  # 英文
    'ja',  # 日文
    'ko',  # 韩文
    # ... 添加更多语言
])
```

### 自定义 AI 优化提示词

在 `content_creator_views.py` 中修改 `prompt` 变量:

```python
prompt = f"""你的自定义提示词...

字幕内容：
{subtitle_text}

请直接输出整理后的字幕。"""
```

## 文件清单

### 前端文件
- `/frontend/src/components/ContentCreator.jsx` - 文案制作页面组件
- `/frontend/src/App.jsx` - 添加了路由配置
- `/frontend/src/components/Dashboard.jsx` - 添加了快捷入口

### 后端文件
- `/api/content_creator_views.py` - 字幕提取视图
- `/api/urls.py` - API 路由配置
- `/requirements.txt` - 添加了依赖包

### 配置文件
- `/.env.example` - 环境变量示例(添加了 GEMINI_API_KEY)

## 后续优化建议

1. **批量处理**: 支持一次提取多个视频的字幕
2. **格式导出**: 支持导出为 TXT、PDF、Word 等格式
3. **摘要生成**: 使用 AI 生成视频内容摘要
4. **翻译功能**: 将字幕翻译成其他语言
5. **关键词提取**: 自动提取视频关键词和主题
6. **缓存机制**: 缓存已提取的字幕,避免重复请求

## 支持与反馈

如有问题或建议,请联系开发团队。
