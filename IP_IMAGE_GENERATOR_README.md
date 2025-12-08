# IP形象生成器 - 使用说明

## 功能概述

用户可以上传自己的照片，输入创意提示语，系统使用 Google Gemini AI 生成个性化的IP形象图片。

## 技术架构

### 前端
- **路径**: `/ip-image-generator`
- **组件**: `frontend/src/components/IPImageGenerator.jsx`
- **功能**:
  - 图片上传（支持拖拽）
  - 移动端拍照功能
  - 实时预览
  - 创意提示语输入（最多500字符）
  - 生成结果展示
  - 图片下载

### 后端
- **API端点**: `/api/ip-image/generate`
- **文件**: `api/ip_image_views.py`
- **AI模型**: Google Gemini 2.0 Flash (支持图像生成)
- **功能**:
  - 接收用户照片和提示语
  - 调用 Gemini API 生成图像
  - 保存生成的图片到服务器
  - 返回图片访问URL

## 安装依赖

### 1. 安装 Python 包

```bash
cd /var/www/harry-insurance2
pip install google-genai
```

或者更新 `requirements.txt`:

```bash
echo "google-genai" >> requirements.txt
pip install -r requirements.txt
```

### 2. 配置环境变量

在 `.env` 文件中添加 Gemini API 密钥：

```bash
# 编辑 .env 文件
nano /var/www/harry-insurance2/.env

# 添加以下行
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. 获取 Gemini API Key

1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 登录 Google 账号
3. 点击 "Get API Key" 创建新的 API 密钥
4. 复制密钥并添加到 `.env` 文件

## API 使用说明

### 生成IP形象

**请求**:
```http
POST /api/ip-image/generate
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

{
  "image": <file>,
  "prompt": "专业的商务风格，简约大气"
}
```

**响应成功**:
```json
{
  "status": "success",
  "image_url": "https://yourdomain.com/media/ip_images/ip_username_uuid.png",
  "message": "IP形象生成成功",
  "method": "gemini"
}
```

**响应失败**:
```json
{
  "status": "error",
  "message": "错误信息"
}
```

## 使用流程

### 用户端操作

1. **登录** → 进入 Dashboard
2. **点击** "打造个人IP形象" 按钮
3. **上传照片**:
   - 电脑端：点击"选择照片"或拖拽上传
   - 移动端：可以选择"拍照"直接拍摄
4. **输入提示语**:
   - 例如："可爱的卡通形象"
   - 例如："专业的商务风格"
   - 例如："科技感的未来风格"
5. **点击生成** → 等待 10-30 秒
6. **查看结果** → 下载图片或重新生成

### 提示语示例

**风格类**:
- 专业的商务风格，简约大气
- 可爱的卡通形象，活泼俏皮
- 科技感的未来风格，充满创意
- 中国风古典形象，优雅端庄
- 二次元动漫风格，精致细腻

**场景类**:
- 适合用作社交媒体头像
- 适合用作个人品牌Logo
- 适合用作名片形象
- 适合用作直播封面

**创意类**:
- 融合赛博朋克和传统文化元素
- 梦幻浪漫的童话风格
- 极简主义黑白风格

## 技术细节

### Gemini API 调用流程

```python
# 1. 创建客户端
client = genai.Client(api_key=GEMINI_API_KEY)

# 2. 准备内容（文本 + 图片）
contents = [
    types.Content(
        role="user",
        parts=[
            types.Part.from_text(text=prompt),
            types.Part.from_bytes(data=image_data, mime_type="image/jpeg"),
        ],
    ),
]

# 3. 配置生成参数
config = types.GenerateContentConfig(
    response_modalities=["IMAGE", "TEXT"],
    image_config=types.ImageConfig(image_size="1K"),
    temperature=1.0,
)

# 4. 流式生成
for chunk in client.models.generate_content_stream(
    model="gemini-2.0-flash-exp",
    contents=contents,
    config=config,
):
    # 处理返回的图片数据
    if chunk.candidates[0].content.parts[0].inline_data:
        image_data = chunk.candidates[0].content.parts[0].inline_data.data
```

### 文件存储

- **存储路径**: `/var/www/harry-insurance2/media/ip_images/`
- **命名规则**: `ip_{username}_{uuid}.{ext}`
- **访问URL**: `https://yourdomain.com/media/ip_images/{filename}`

### 支持的图片格式

- **输入**: JPG, PNG, WEBP（最大 10MB）
- **输出**: PNG, JPEG（由 Gemini 决定）
- **尺寸**: 1024x1024

## 配置 Nginx 访问 media 文件

确保 Nginx 配置允许访问 media 文件：

```nginx
location /media/ {
    alias /var/www/harry-insurance2/media/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

## 重启服务

更新代码后需要重启服务：

```bash
# 重启 Django 应用（根据你的部署方式）
sudo systemctl restart gunicorn  # 如果使用 gunicorn
# 或
sudo systemctl restart uwsgi     # 如果使用 uwsgi
# 或
pkill -f "python manage.py runserver"  # 开发环境

# 重启 Nginx（如果修改了配置）
sudo systemctl restart nginx
```

## 成本说明

### Gemini API 定价

- **Gemini 2.0 Flash**: 免费层级提供每日配额
- **付费后**: 按生成次数计费
- **建议**:
  - 设置每日/每用户生成次数限制
  - 监控 API 使用量
  - 考虑添加会员权限控制

查看最新定价：[Google AI Pricing](https://ai.google.dev/pricing)

## 故障排查

### 1. API Key 未配置

**错误**: `暂未配置AI图像生成服务`

**解决**:
```bash
# 检查环境变量
echo $GEMINI_API_KEY

# 如果为空，添加到 .env
echo "GEMINI_API_KEY=your_key" >> .env

# 重启服务
sudo systemctl restart gunicorn
```

### 2. 依赖包未安装

**错误**: `ModuleNotFoundError: No module named 'google'`

**解决**:
```bash
pip install google-genai
```

### 3. 图片无法访问

**错误**: 生成成功但图片 404

**解决**:
```bash
# 检查目录权限
sudo chmod 755 /var/www/harry-insurance2/media/ip_images/
sudo chown -R www-data:www-data /var/www/harry-insurance2/media/

# 检查 Nginx 配置
sudo nginx -t
sudo systemctl reload nginx
```

### 4. 生成失败

**查看日志**:
```bash
# Django 日志
tail -f /var/www/harry-insurance2/logs/django.log

# Nginx 日志
tail -f /var/log/nginx/error.log
```

## 扩展建议

### 1. 数据库存储生成历史

创建 model 保存生成记录：

```python
# models.py
class IPImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_image = models.ImageField(upload_to='ip_originals/')
    generated_image = models.ImageField(upload_to='ip_images/')
    prompt = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### 2. 添加使用次数限制

```python
# 在 generate_ip_image 函数中添加
daily_count = IPImage.objects.filter(
    user=request.user,
    created_at__date=date.today()
).count()

if daily_count >= 5:  # 每日限制5次
    return Response({'message': '今日生成次数已达上限'})
```

### 3. 异步处理（推荐）

使用 Celery 异步生成：

```python
# tasks.py
@shared_task
def generate_ip_image_task(user_id, image_data, prompt):
    # 异步生成逻辑
    pass
```

### 4. 风格预设模板

提供预设风格供用户快速选择：

```javascript
const stylePresets = [
  { name: "商务风", prompt: "专业的商务风格，简约大气" },
  { name: "卡通风", prompt: "可爱的卡通形象，活泼俏皮" },
  { name: "科技风", prompt: "科技感的未来风格，充满创意" },
];
```

## 更新日志

- **2025-01-XX**: 初始版本，使用 Gemini 2.0 Flash 实现
- 支持图片上传和移动端拍照
- 支持自定义提示语生成
- 生成 1024x1024 高质量图片

## 技术支持

如有问题，请查看：
- 后端日志: `/var/www/harry-insurance2/logs/`
- 前端控制台错误
- Gemini API 状态: https://status.google.com/

---

**开发者**: Claude
**最后更新**: 2025-01-XX
