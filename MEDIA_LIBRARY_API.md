# 素材库功能API文档

## 功能概述

素材库功能会自动保存用户生成的所有图片（IP形象和文案配图），并将图片下载到本地服务器存储。

### 特性
- ✅ 自动保存所有生成的图片
- ✅ 图片下载到本地服务器（`/var/www/harry-insurance2/media/generated_images/`）
- ✅ 记录图片元数据（尺寸、大小、提示词等）
- ✅ 支持收藏功能
- ✅ 支持按类型筛选
- ✅ 支持批量删除
- ✅ 提供统计信息

## 数据库表结构

### MediaLibrary 模型

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| user | ForeignKey | 用户 |
| media_type | String | 素材类型（ip_image/content_image） |
| original_url | String | Gemini生成的原始URL |
| local_path | String | 本地存储路径 |
| thumbnail_path | String | 缩略图路径（可选） |
| prompt | Text | 提示语或文案内容 |
| width | Integer | 图片宽度 |
| height | Integer | 图片高度 |
| file_size | Integer | 文件大小（字节） |
| related_ip_image_id | Integer | 关联的IP形象ID |
| is_favorite | Boolean | 是否收藏 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## API 接口

### 1. 获取素材库列表

**接口**: `GET /api/media-library/`

**认证**: 需要登录

**查询参数**:
- `media_type` (可选): 筛选类型（`ip_image` 或 `content_image`）
- `is_favorite` (可选): 筛选收藏（`true`/`false`）
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认20

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "media_type": "ip_image",
        "media_type_display": "IP形象",
        "url": "https://your-domain.com/media/generated_images/ip_images/user_1_abc123_20231123_120000.png",
        "original_url": "https://gemini-url...",
        "prompt": "卡通风格的...",
        "width": 1024,
        "height": 1024,
        "file_size": 245678,
        "is_favorite": false,
        "related_ip_image_id": null,
        "created_at": "2023-11-23 12:00:00"
      }
    ],
    "total": 50,
    "page": 1,
    "page_size": 20,
    "total_pages": 3
  }
}
```

### 2. 获取素材详情

**接口**: `GET /api/media-library/{media_id}/`

**认证**: 需要登录

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "media_type": "content_image",
    "media_type_display": "文案配图",
    "url": "https://your-domain.com/media/...",
    "original_url": "https://gemini-url...",
    "prompt": "春天的花园...",
    "width": 1024,
    "height": 1024,
    "file_size": 245678,
    "is_favorite": true,
    "related_ip_image_id": 5,
    "created_at": "2023-11-23 12:00:00",
    "updated_at": "2023-11-23 12:05:00"
  }
}
```

### 3. 切换收藏状态

**接口**: `POST /api/media-library/{media_id}/favorite/`

**认证**: 需要登录

**响应示例**:
```json
{
  "status": "success",
  "message": "收藏状态已更新",
  "is_favorite": true
}
```

### 4. 删除单个素材

**接口**: `DELETE /api/media-library/{media_id}/delete/`

**认证**: 需要登录

**响应示例**:
```json
{
  "status": "success",
  "message": "素材已删除"
}
```

### 5. 批量删除素材

**接口**: `POST /api/media-library/batch-delete/`

**认证**: 需要登录

**请求体**:
```json
{
  "media_ids": [1, 2, 3, 4, 5]
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "成功删除 5 个素材"
}
```

### 6. 获取统计信息

**接口**: `GET /api/media-library/stats/`

**认证**: 需要登录

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "total_count": 120,
    "ip_image_count": 50,
    "content_image_count": 70,
    "favorite_count": 15,
    "total_size": 52428800,
    "total_size_mb": 50.0
  }
}
```

## 自动保存机制

### IP形象生成

当用户通过 `/api/ip-image/generate-v2` 生成IP形象时，系统会自动：

1. 生成图片成功后
2. 下载图片到本地：`/media/generated_images/ip_images/`
3. 保存到素材库数据库
4. 记录元数据（尺寸、大小、提示词等）

**代码位置**: `api/ip_image_views.py:973-980`

### 文案配图生成

当用户通过 `/api/ip-image/generate-v2` 生成文案配图时，系统会自动：

1. 生成图片成功后
2. 下载图片到本地：`/media/generated_images/content_images/`
3. 如果包含IP形象，记录关联的IP形象ID
4. 保存到素材库数据库
5. 记录元数据

**代码位置**: `api/ip_image_views.py:813-832`

## 本地存储路径

```
/var/www/harry-insurance2/media/
└── generated_images/
    ├── ip_images/          # IP形象存储目录
    │   ├── user_1_abc123_20231123_120000.png
    │   └── ...
    └── content_images/     # 文案配图存储目录
        ├── user_1_def456_20231123_130000.png
        └── ...
```

### 文件命名规则

格式: `user_{user_id}_{unique_id}_{timestamp}.png`

- `user_id`: 用户ID
- `unique_id`: 8位随机UUID
- `timestamp`: 时间戳（格式：YYYYMMDD_HHMMSS）

示例: `user_5_a1b2c3d4_20231123_143022.png`

## 工具函数

### 图像存储工具

位置: `api/utils/image_storage.py`

#### download_and_save_image()
下载图片并保存到本地

```python
result = download_and_save_image(
    image_url='https://...',
    media_type='ip_image',
    user_id=1
)
```

#### save_to_media_library()
下载图片并保存到素材库数据库

```python
media = save_to_media_library(
    user=request.user,
    media_type='content_image',
    original_url='https://...',
    prompt='春天的花园',
    related_ip_image_id=5
)
```

#### delete_media_file()
删除本地媒体文件

```python
success = delete_media_file('generated_images/ip_images/user_1_abc123.png')
```

## Django Admin管理

访问 `/admin/api/medialibrary/` 可以管理素材库：

### 功能
- 查看所有素材（带缩略图预览）
- 按类型、收藏状态筛选
- 按用户、提示词搜索
- 批量标记/取消收藏
- 删除素材（同时删除本地文件）
- 查看详细信息（尺寸、大小等）

### 列表显示
- 用户信息（含微信昵称）
- 媒体类型（带颜色标签）
- 图片缩略图（60x60）
- 提示词预览
- 文件大小
- 收藏状态
- 创建时间

## 注意事项

1. **存储空间**: 图片会占用服务器存储空间，建议定期清理或设置存储限额
2. **下载失败处理**: 如果图片下载失败，只会记录原始URL，不会保存本地路径
3. **权限控制**: 用户只能查看和删除自己的素材
4. **删除操作**: 删除素材时会同时删除数据库记录和本地文件

## 前端集成示例

### 获取素材库列表

```javascript
import { API_BASE_URL } from '../config';

const getMediaLibrary = async (page = 1, mediaType = '') => {
  const token = localStorage.getItem('access_token');
  const params = new URLSearchParams({
    page: page,
    page_size: 20
  });

  if (mediaType) {
    params.append('media_type', mediaType);
  }

  const response = await fetch(`${API_BASE_URL}/api/media-library/?${params}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  return await response.json();
};
```

### 删除素材

```javascript
const deleteMedia = async (mediaId) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE_URL}/api/media-library/${mediaId}/delete/`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  return await response.json();
};
```

### 切换收藏

```javascript
const toggleFavorite = async (mediaId) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`${API_BASE_URL}/api/media-library/${mediaId}/favorite/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  return await response.json();
};
```

## 测试建议

1. 生成一个IP形象，检查是否自动保存到素材库
2. 生成一个文案配图，检查是否自动保存
3. 访问素材库API，验证数据是否正确
4. 测试删除功能，确认本地文件也被删除
5. 在Admin后台查看素材库，验证缩略图显示正常

## 后续优化建议

1. **缩略图生成**: 自动生成缩略图以减少流量
2. **CDN集成**: 将图片上传到CDN加速访问
3. **存储配额**: 为每个用户设置存储空间限制
4. **定期清理**: 自动清理超过保留期的图片
5. **图片压缩**: 保存前自动压缩图片以节省空间
6. **多格式支持**: 支持WebP等更高效的图片格式
