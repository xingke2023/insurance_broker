# 阿里千问PDF识别使用示例

## 快速开始

### 1. 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加您的API密钥
nano .env
```

在 `.env` 文件中设置：
```
DASHSCOPE_API_KEY=sk-your-actual-api-key-here
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 测试配置

```bash
python test_qwen_api.py
```

如果看到 "✓ 基础功能正常，可以开始使用！"，说明配置成功。

## API使用示例

### 使用 cURL

```bash
# 上传PDF文件进行识别
curl -X POST http://localhost:8000/api/plans/upload/ \
  -F "file=@/path/to/insurance_plan.pdf"
```

### 使用 Python requests

```python
import requests

# 上传PDF文件
url = "http://localhost:8000/api/plans/upload/"
files = {'file': open('insurance_plan.pdf', 'rb')}

response = requests.post(url, files=files)

if response.status_code == 201:
    data = response.json()
    print("上传成功！")
    print(f"文档ID: {data['document_id']}")
    print(f"提取的数据: {data['extracted_data']}")
else:
    print(f"上传失败: {response.json()}")
```

### 使用 JavaScript/Fetch

```javascript
// 在前端上传PDF文件
const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8000/api/plans/upload/', {
      method: 'POST',
      body: formData
    });

    if (response.ok) {
      const data = await response.json();
      console.log('上传成功！', data);
      return data;
    } else {
      const error = await response.json();
      console.error('上传失败：', error);
    }
  } catch (error) {
    console.error('网络错误：', error);
  }
};

// 使用示例
const fileInput = document.getElementById('pdfFile');
fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    uploadPDF(file);
  }
});
```

## 响应数据示例

### 成功响应

```json
{
  "message": "文件上传并处理成功",
  "document_id": 123,
  "extracted_data": {
    "customer_name": "张三",
    "customer_age": 35,
    "customer_gender": "男",
    "insurance_product": "平安福终身寿险",
    "insurance_company": "中国平安人寿保险股份有限公司",
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

### 失败响应

```json
{
  "error": "PDF处理失败: API调用超时",
  "document_id": 124
}
```

## 集成到前端

### React 组件示例

```jsx
import React, { useState } from 'react';
import axios from 'axios';

function PlanUploader() {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // 验证文件类型
    if (!file.name.endsWith('.pdf')) {
      setError('请选择PDF文件');
      return;
    }

    // 验证文件大小
    if (file.size > 10 * 1024 * 1024) {
      setError('文件大小不能超过10MB');
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        'http://localhost:8000/api/plans/upload/',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      setResult(response.data);
      console.log('提取的数据：', response.data.extracted_data);
    } catch (err) {
      setError(err.response?.data?.error || '上传失败');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="plan-uploader">
      <h2>上传保险计划书</h2>

      <input
        type="file"
        accept=".pdf"
        onChange={handleFileUpload}
        disabled={uploading}
      />

      {uploading && <p>正在处理中...</p>}

      {error && (
        <div className="error">
          <p>错误：{error}</p>
        </div>
      )}

      {result && (
        <div className="result">
          <h3>提取结果</h3>
          <div className="data-grid">
            <div>客户姓名：{result.extracted_data.customer_name}</div>
            <div>年龄：{result.extracted_data.customer_age}</div>
            <div>性别：{result.extracted_data.customer_gender}</div>
            <div>产品名称：{result.extracted_data.insurance_product}</div>
            <div>保险公司：{result.extracted_data.insurance_company}</div>
            <div>保额：¥{result.extracted_data.insurance_amount?.toLocaleString()}</div>
            <div>年缴保费：¥{result.extracted_data.premium_amount?.toLocaleString()}</div>
            <div>缴费年期：{result.extracted_data.payment_years}年</div>
            <div>总保费：¥{result.extracted_data.total_premium?.toLocaleString()}</div>
            <div>保险期限：{result.extracted_data.insurance_period}</div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PlanUploader;
```

### Vue 组件示例

```vue
<template>
  <div class="plan-uploader">
    <h2>上传保险计划书</h2>

    <input
      type="file"
      accept=".pdf"
      @change="handleFileUpload"
      :disabled="uploading"
    />

    <div v-if="uploading" class="loading">
      正在处理中...
    </div>

    <div v-if="error" class="error">
      错误：{{ error }}
    </div>

    <div v-if="result" class="result">
      <h3>提取结果</h3>
      <div class="data-grid">
        <div>客户姓名：{{ result.extracted_data.customer_name }}</div>
        <div>年龄：{{ result.extracted_data.customer_age }}</div>
        <div>性别：{{ result.extracted_data.customer_gender }}</div>
        <div>产品名称：{{ result.extracted_data.insurance_product }}</div>
        <div>保险公司：{{ result.extracted_data.insurance_company }}</div>
        <div>保额：¥{{ formatNumber(result.extracted_data.insurance_amount) }}</div>
        <div>年缴保费：¥{{ formatNumber(result.extracted_data.premium_amount) }}</div>
        <div>缴费年期：{{ result.extracted_data.payment_years }}年</div>
        <div>总保费：¥{{ formatNumber(result.extracted_data.total_premium) }}</div>
        <div>保险期限：{{ result.extracted_data.insurance_period }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PlanUploader',
  data() {
    return {
      uploading: false,
      result: null,
      error: null
    };
  },
  methods: {
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file) return;

      // 验证文件
      if (!file.name.endsWith('.pdf')) {
        this.error = '请选择PDF文件';
        return;
      }

      if (file.size > 10 * 1024 * 1024) {
        this.error = '文件大小不能超过10MB';
        return;
      }

      this.uploading = true;
      this.error = null;
      this.result = null;

      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await axios.post(
          'http://localhost:8000/api/plans/upload/',
          formData
        );

        this.result = response.data;
      } catch (err) {
        this.error = err.response?.data?.error || '上传失败';
      } finally {
        this.uploading = false;
      }
    },
    formatNumber(num) {
      return num?.toLocaleString() || '未知';
    }
  }
};
</script>
```

## 高级用法

### 批量处理

```python
import os
import glob
from api.qwen_service import extract_plan_data_from_pdf

def batch_process_pdfs(directory):
    """批量处理目录下的所有PDF文件"""
    pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
    results = []

    for pdf_path in pdf_files:
        print(f"处理：{pdf_path}")

        with open(pdf_path, 'rb') as f:
            result = extract_plan_data_from_pdf(f)

            if result['success']:
                print(f"  ✓ 成功：{result['data']['customer_name']}")
                results.append({
                    'file': pdf_path,
                    'data': result['data']
                })
            else:
                print(f"  ✗ 失败：{result['error']}")

    return results

# 使用示例
results = batch_process_pdfs('./insurance_plans/')
print(f"\n共处理 {len(results)} 个文件")
```

### 自定义提取字段

如果需要提取其他字段，可以修改 `api/qwen_service.py` 中的 prompt：

```python
# 在 qwen_service.py 中修改 prompt
prompt = """请分析这份保险计划书PDF文件，提取以下关键信息：

需要提取的字段：
1. customer_name: 客户姓名
2. customer_age: 客户年龄
3. customer_gender: 性别
... (现有字段)
11. beneficiary_name: 受益人姓名  # 新增字段
12. beneficiary_relation: 受益人关系  # 新增字段
13. payment_frequency: 缴费频率（年缴/月缴）  # 新增字段

请以JSON格式返回..."""
```

### 错误处理和重试

```python
import time
from api.qwen_service import extract_plan_data_from_pdf

def extract_with_retry(pdf_file, max_retries=3):
    """带重试机制的数据提取"""
    for attempt in range(max_retries):
        try:
            result = extract_plan_data_from_pdf(pdf_file)

            if result['success']:
                return result

            print(f"尝试 {attempt + 1} 失败：{result['error']}")

            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避

        except Exception as e:
            print(f"尝试 {attempt + 1} 异常：{str(e)}")

            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

    return {'success': False, 'error': '超过最大重试次数'}

# 使用示例
with open('plan.pdf', 'rb') as f:
    result = extract_with_retry(f)
```

## 性能优化建议

1. **PDF预处理**：
   - 压缩大型PDF文件
   - 移除不必要的页面
   - 确保PDF文本可提取

2. **缓存结果**：
   - 对相同PDF文件使用缓存
   - 避免重复调用API

3. **异步处理**：
   - 对大批量处理使用后台任务
   - 使用 Celery 或类似工具

4. **错误监控**：
   - 记录所有API调用
   - 监控成功率和响应时间

## 常见问题

### Q1: 为什么提取的数据不准确？

A: 可能的原因：
- PDF质量较差（扫描版或图片模糊）
- 文档格式不标准
- 字段位置不明显

解决方案：
- 使用高质量的原生PDF
- 调整prompt增加更多上下文
- 人工校验和修正

### Q2: API调用超时怎么办？

A: 可能的原因：
- 网络连接问题
- PDF文件过大
- API服务繁忙

解决方案：
- 检查网络连接
- 压缩PDF文件
- 增加超时时间
- 实现重试机制

### Q3: 如何降低成本？

A: 建议：
- 优先使用文本提取+分析（成本更低）
- 缓存处理结果
- 批量处理时控制并发数
- 只对必要的文档使用视觉模型

## 更多资源

- [项目主文档](./README.md)
- [配置指南](./QWEN_SETUP.md)
- [API文档](./DEMO_GUIDE.md)
- [阿里云DashScope官方文档](https://help.aliyun.com/zh/dashscope/)
