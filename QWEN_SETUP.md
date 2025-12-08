# 阿里千问PDF识别配置指南

## 概述

本项目已集成阿里千问（Qwen）视觉模型，用于直接识别保险计划书PDF文件并提取结构化数据。

## 功能特点

1. **直接PDF识别**：使用千问视觉模型 `qwen-vl-max-latest` 直接识别PDF文件
2. **文本提取备用方案**：如果直接识别失败，自动降级为文本提取+分析模式
3. **高精度提取**：智能提取保险计划书中的关键信息
4. **结构化输出**：返回标准JSON格式的数据

## 配置步骤

### 1. 获取阿里云API密钥

1. 访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)
2. 登录或注册阿里云账号
3. 开通 DashScope 服务
4. 创建 API Key

### 2. 设置环境变量

在项目根目录创建 `.env` 文件（如果不存在），添加以下配置：

```bash
# 阿里云DashScope API密钥
DASHSCOPE_API_KEY=sk-your-api-key-here
```

或者直接在系统环境变量中设置：

```bash
export DASHSCOPE_API_KEY="sk-your-api-key-here"
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包括：
- `openai>=1.0.0` - 用于调用千问API（兼容OpenAI SDK）
- `pypdf>=3.0.0` - 用于PDF文本提取（备用方案）

### 4. 重启服务

```bash
# 停止现有服务
# 然后重新启动
python manage.py runserver
```

## 使用方法

### API接口

**上传PDF文件**

```bash
POST /api/plans/upload/
Content-Type: multipart/form-data

file: <PDF文件>
```

**响应示例**

```json
{
    "message": "文件上传并处理成功",
    "document_id": 1,
    "extracted_data": {
        "customer_name": "张三",
        "customer_age": 35,
        "customer_gender": "男",
        "insurance_product": "XX终身寿险",
        "insurance_company": "XX保险公司",
        "insurance_amount": 500000,
        "premium_amount": 15000,
        "payment_years": 20,
        "total_premium": 300000,
        "insurance_period": "终身"
    },
    "file_info": {
        "name": "保险计划书.pdf",
        "size": 1048576,
        "status": "completed"
    }
}
```

### 提取的字段说明

| 字段名 | 说明 | 类型 |
|--------|------|------|
| customer_name | 客户/受保人姓名 | string |
| customer_age | 客户年龄 | integer |
| customer_gender | 性别 | string (男/女) |
| insurance_product | 保险产品名称 | string |
| insurance_company | 保险公司名称 | string |
| insurance_amount | 保额 | integer (元) |
| premium_amount | 年缴保费 | integer (元) |
| payment_years | 缴费年期 | integer (年) |
| total_premium | 总保费 | integer (元) |
| insurance_period | 保险期限 | string |

## 技术实现

### 服务模块：`api/qwen_service.py`

该模块提供两个主要函数：

1. **`extract_plan_data_from_pdf(pdf_file)`**
   - 直接识别PDF文件
   - 使用 `qwen-vl-max-latest` 视觉模型
   - 支持 base64 编码的PDF文件

2. **`extract_plan_data_from_text(text_content)`**
   - 从文本提取数据
   - 使用 `qwen-plus-latest` 文本模型
   - 作为备用方案

### 工作流程

```
上传PDF → 千问视觉识别 → 提取结构化数据 → 保存到数据库
         ↓ (失败)
    PDF文本提取 → 千问文本分析 → 提取结构化数据 → 保存到数据库
```

## 模型选择

### qwen-vl-max-latest（推荐）
- **用途**：直接识别PDF文件
- **优势**：准确率高，可以识别图片、表格等复杂内容
- **限制**：需要base64编码，文件大小有限制

### qwen-plus-latest（备用）
- **用途**：分析提取的文本内容
- **优势**：速度快，成本低
- **限制**：依赖PDF文本提取质量

## 注意事项

1. **文件大小限制**：
   - 系统限制：10MB
   - 建议：保持PDF文件小于5MB以获得最佳性能

2. **API限额**：
   - 请注意阿里云DashScope的API调用限额
   - 建议配置适当的错误处理和重试机制

3. **PDF质量**：
   - 清晰的PDF文件识别效果更好
   - 扫描版PDF也支持，但建议使用原生PDF

4. **数据准确性**：
   - 模型会尽可能提取准确数据
   - 建议在前端提供人工校验界面

## 故障排除

### 问题1：API密钥错误
```
错误信息：DASHSCOPE_API_KEY环境变量未设置
解决方案：检查.env文件或环境变量配置
```

### 问题2：JSON解析失败
```
错误信息：JSON解析失败
解决方案：检查raw_response字段查看原始响应，可能需要调整prompt
```

### 问题3：API调用失败
```
错误信息：API调用失败
解决方案：
1. 检查网络连接
2. 验证API密钥是否有效
3. 检查阿里云账户余额
```

## 成本估算

- **qwen-vl-max-latest**：约 ¥0.02/次（1页PDF）
- **qwen-plus-latest**：约 ¥0.002/次（文本分析）

实际成本取决于：
- PDF页数
- 内容复杂度
- 每月调用次数

## 扩展功能

### 批量处理

如需批量处理多个PDF文件，可以创建后台任务：

```python
# 示例代码
from celery import shared_task

@shared_task
def process_pdf_batch(file_ids):
    for file_id in file_ids:
        # 处理每个文件
        pass
```

### 自定义提取字段

修改 `qwen_service.py` 中的 prompt，可以自定义需要提取的字段。

## 相关文档

- [阿里云DashScope文档](https://help.aliyun.com/zh/dashscope/)
- [千问模型文档](https://help.aliyun.com/zh/dashscope/developer-reference/model-square/)
- [OpenAI SDK文档](https://github.com/openai/openai-python)

## 技术支持

如遇问题，请检查：
1. API密钥配置
2. 网络连接
3. 阿里云服务状态
4. 系统日志文件
