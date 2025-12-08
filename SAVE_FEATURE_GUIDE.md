# 保存功能使用指南

## 功能概述

保单智能分析系统现在支持将OCR解析结果保存到本地数据库。

## 功能特点

✅ **一键保存** - 点击保存按钮即可将解析结果保存到数据库
✅ **完整记录** - 保存文件名、内容、任务ID等完整信息
✅ **状态反馈** - 实时显示保存状态（保存中/已保存）
✅ **数据持久化** - 使用Django ORM存储到MySQL数据库

## 使用流程

### 1. 上传并解析文档

1. 访问保单智能分析系统
2. 上传PDF/图片文档
3. 点击"开始分析"
4. 等待OCR解析完成

### 2. 查看解析结果

解析完成后，系统会自动显示：
- 📄 解析结果标题
- 完整的文档内容
- **保存到数据库** 按钮（右上角）

### 3. 保存到数据库

点击"保存到数据库"按钮：

**按钮状态变化：**
```
[保存到数据库]
    ↓ 点击后
[保存中...] (显示加载动画)
    ↓ 保存成功
[✓ 已保存] (绿色，3秒后恢复)
```

**成功提示：**
```
保存成功！文档ID: 123
```

## 数据库结构

### 保存的数据

保存到 `plan_documents` 表，包含以下信息：

| 字段 | 说明 | 示例 |
|------|------|------|
| file_name | 原始文件名 | document.pdf |
| file_size | 内容大小（字节） | 1234 |
| extracted_data | JSON格式的完整数据 | {...} |
| status | 状态 | completed |
| created_at | 创建时间 | 2025-11-05 20:30:00 |

### extracted_data 字段内容

```json
{
  "ocr_content": "解析出的完整文本内容...",
  "task_id": "远程OCR任务ID",
  "result_dir": "远程结果目录路径",
  "content_length": 1234
}
```

## API接口

### 1. 保存OCR结果

**端点**: `POST /api/ocr/save/`

**请求体**:
```json
{
  "file_name": "document.pdf",
  "ocr_content": "解析的文本内容...",
  "task_id": "task_12345",
  "result_dir": "/path/to/result"
}
```

**响应**:
```json
{
  "status": "success",
  "message": "保存成功",
  "document_id": 123,
  "data": {
    "id": 123,
    "file_name": "document.pdf",
    "status": "completed",
    "created_at": "2025-11-05T20:30:00",
    "content_length": 1234
  }
}
```

### 2. 获取已保存文档列表

**端点**: `GET /api/ocr/documents/`

**响应**:
```json
{
  "status": "success",
  "count": 10,
  "data": [
    {
      "id": 123,
      "file_name": "document.pdf",
      "status": "completed",
      "created_at": "2025-11-05T20:30:00",
      "content_length": 1234
    }
  ]
}
```

### 3. 获取单个文档详情

**端点**: `GET /api/ocr/documents/<document_id>/`

**响应**:
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "file_name": "document.pdf",
    "file_size": 1234,
    "status": "completed",
    "extracted_data": {
      "ocr_content": "...",
      "task_id": "...",
      "result_dir": "...",
      "content_length": 1234
    },
    "created_at": "2025-11-05T20:30:00",
    "updated_at": "2025-11-05T20:30:00"
  }
}
```

## 技术实现

### 后端

**文件**: `/var/www/harry-insurance/api/ocr_views.py`

```python
@api_view(['POST'])
def save_ocr_result(request):
    # 创建 PlanDocument 记录
    plan_doc = PlanDocument()
    plan_doc.file_name = file_name
    plan_doc.file_size = len(ocr_content.encode('utf-8'))
    plan_doc.extracted_data = {
        'ocr_content': ocr_content,
        'task_id': task_id,
        'result_dir': result_dir
    }
    plan_doc.status = 'completed'
    plan_doc.save()
```

### 前端

**文件**: `/var/www/harry-insurance/frontend/src/components/PlanAnalyzer.jsx`

```javascript
const handleSave = async () => {
  const response = await fetch(`${LOCAL_API_BASE_URL}/api/ocr/save/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      file_name: uploadedFile?.name,
      ocr_content: fileContent,
      task_id: taskId,
      result_dir: resultDir
    })
  });
};
```

## 页面效果

### 保存按钮位置

```
┌─────────────────────────────────────────────────────┐
│ 📄 解析结果 - document.mmd    [💾 保存到数据库]     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  解析出的文本内容                                    │
│  ...                                                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 按钮样式

**正常状态**:
```css
蓝色背景 + 白色文字 + 💾 图标
```

**保存中**:
```css
蓝色背景 + 旋转加载图标 + "保存中..."
```

**保存成功**:
```css
绿色背景 + 白色文字 + ✓ 图标 + "已保存"
```

## 配置

### API地址

```javascript
// 远程OCR服务
const API_BASE_URL = 'http://101.36.226.245:8002';

// 本地Django后端
const LOCAL_API_BASE_URL = 'http://localhost:8007';
```

## 数据库迁移

如果是首次使用，需要确保数据库表已创建：

```bash
cd /var/www/harry-insurance
python3 manage.py makemigrations
python3 manage.py migrate
```

## 测试步骤

### 1. 测试保存功能

1. ✅ 启动后端服务
2. ✅ 启动前端服务
3. ✅ 上传文档并解析
4. ✅ 点击"保存到数据库"按钮
5. ✅ 查看成功提示

### 2. 验证数据库

```bash
# 进入Django shell
python3 manage.py shell

# 查询最新记录
from api.models import PlanDocument
doc = PlanDocument.objects.latest('created_at')
print(doc.file_name)
print(doc.status)
print(doc.extracted_data)
```

### 3. 测试API

```bash
# 获取文档列表
curl http://localhost:8007/api/ocr/documents/

# 获取单个文档
curl http://localhost:8007/api/ocr/documents/1/
```

## 故障排查

### 问题1: 保存按钮不显示

**原因**: parseCompleted状态未设置为true

**解决**: 确保解析完成，查看控制台日志

### 问题2: 点击保存无反应

**原因**: 后端服务未启动

**解决**:
```bash
cd /var/www/harry-insurance
./start-backend.sh
```

### 问题3: 保存失败

**原因**:
- 数据库连接失败
- 数据格式错误
- CORS问题

**解决**:
1. 检查Django后端日志
2. 检查浏览器控制台Network标签
3. 确认CORS配置正确

### 问题4: CORS错误

**症状**:
```
Access to fetch at 'http://localhost:8007/api/ocr/save/'
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**解决**: 确保 `backend/settings.py` 中配置了CORS

```python
CORS_ALLOW_ALL_ORIGINS = True  # 开发环境
# 或
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
```

## 后续扩展

### 可以添加的功能

- [ ] 查看已保存文档列表
- [ ] 删除已保存文档
- [ ] 编辑保存的内容
- [ ] 导出为Excel/PDF
- [ ] 添加标签和分类
- [ ] 搜索和筛选功能
- [ ] 批量操作

## 更新日志

### 2025-11-05

- ✅ 创建后端保存API (`ocr_views.py`)
- ✅ 添加API路由
- ✅ 前端添加保存按钮
- ✅ 实现保存逻辑
- ✅ 添加状态反馈
- ✅ 编写使用文档

## 相关文件

- **后端API**: `/api/ocr_views.py`
- **路由配置**: `/api/urls.py`
- **数据模型**: `/api/models.py` (PlanDocument)
- **前端组件**: `/frontend/src/components/PlanAnalyzer.jsx`

---

**提示**: 保存功能已完全集成，可以直接使用！
