# 文案制作功能 - 快速开始

## ✅ 功能已部署成功!

所有组件已安装并配置完成,功能已经可以使用。

## 📋 功能清单

- ✅ 前端页面: ContentCreator 组件
- ✅ 后端 API: `/api/content/extract-subtitle`
- ✅ Dashboard 入口: "文案制作" 快捷按钮
- ✅ Gemini API: 已配置并测试通过
- ✅ YouTube 字幕库: 已安装
- ✅ 依赖包: 全部安装完成

## 🚀 立即使用

### 1. 访问页面
```
http://your-domain.com/dashboard
```

### 2. 点击快捷入口
在 Dashboard 页面找到 **"文案制作"** 卡片(紫色图标),点击进入。

### 3. 提取字幕
1. 在输入框粘贴 YouTube 视频链接
   - 例如: `https://www.youtube.com/watch?v=xxxxx`
   - 或: `https://youtu.be/xxxxx`
2. 点击 **"提取字幕"** 按钮
3. 等待 10-20 秒(AI 处理中)
4. 字幕显示后,点击 **"复制"** 按钮

## 🎯 支持的功能

### YouTube 视频格式
- ✅ 标准链接: `https://www.youtube.com/watch?v=VIDEO_ID`
- ✅ 短链接: `https://youtu.be/VIDEO_ID`
- ✅ Shorts 链接: `https://www.youtube.com/shorts/VIDEO_ID`
- ✅ 嵌入链接: `https://www.youtube.com/embed/VIDEO_ID`
- ✅ 移动端链接: `https://m.youtube.com/watch?v=VIDEO_ID`

### 字幕语言支持
- 🇨🇳 中文(简体/繁体) - 优先
- 🇺🇸 英文
- 🇯🇵 日文
- 🇰🇷 韩文
- 🌍 其他语言

### AI 优化功能
使用 Google Gemini 2.0 Flash 模型:
- 删除重复内容
- 合理分段
- 修正明显错误
- 保持原意不变

## 📊 测试结果

```
✅ 视频 ID 提取: 正常
✅ Gemini API: 正常
✅ YouTube API 库: 已安装

🎉 所有功能测试通过!
```

## 🔧 技术配置

### 环境变量 (.env)
```bash
GEMINI_API_KEY=AIzaSyC6_Lp7D2RLFTDtWoKz6-eSerX6oNDdjdM
```

### API 端点
```
POST /api/content/extract-subtitle
Authorization: Bearer <token>
Content-Type: application/json

{
  "video_url": "https://www.youtube.com/watch?v=xxxxx"
}
```

### 响应格式
```json
{
  "code": 200,
  "message": "字幕提取成功",
  "data": {
    "subtitle": "提取并优化后的字幕内容...",
    "video_id": "xxxxx"
  }
}
```

## 💡 使用提示

1. **选择有字幕的视频**
   - 确保视频有公开字幕
   - 私有视频无法提取

2. **网络要求**
   - 服务器需要能访问 YouTube
   - 如果无法访问,可能需要配置代理

3. **处理时间**
   - 一般 10-20 秒完成
   - 较长视频可能需要更多时间

4. **字幕质量**
   - AI 会自动优化格式
   - 中文字幕效果最佳

## 🎨 页面特色

- 🎯 现代化 UI 设计
- 📱 完全响应式布局
- ⚡ 实时加载状态
- 🎨 渐变色彩方案
- 📋 一键复制功能
- ⚠️  友好的错误提示

## 📁 文件位置

### 前端
- 组件: `/frontend/src/components/ContentCreator.jsx`
- 路由: `/frontend/src/App.jsx` (line 11, 28)
- 入口: `/frontend/src/components/Dashboard.jsx` (line 142)

### 后端
- 视图: `/api/content_creator_views.py`
- 路由: `/api/urls.py` (line 9, 64)
- 环境: `/.env` (line 22)

### 文档
- 详细指南: `/CONTENT_CREATOR_GUIDE.md`
- 快速开始: `/CONTENT_CREATOR_QUICKSTART.md` (本文件)
- 测试脚本: `/test_content_creator_simple.py`

## 🐛 常见问题

### Q: 提示"该视频没有可用的字幕"
**A:** 确保选择有公开字幕的视频

### Q: 提取速度很慢
**A:** 这是正常的,AI 处理需要时间,请耐心等待

### Q: 无法访问 YouTube
**A:** 检查服务器网络,可能需要配置代理

### Q: Gemini API 报错
**A:** 检查 API Key 是否正确配置在 .env 文件中

## 🔄 重启服务

如果修改了配置,需要重启服务:

```bash
cd /var/www/harry-insurance2
./stop_all.sh
./start_all.sh
```

## 📞 技术支持

- 查看日志: `tail -f logs/django.log`
- 运行测试: `python3 test_content_creator_simple.py`
- 详细文档: `CONTENT_CREATOR_GUIDE.md`

---

**部署时间**: 2025-11-22
**状态**: ✅ 生产就绪
**版本**: 1.0.0
