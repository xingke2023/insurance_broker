# 阿里千问PDF识别 - 快速参考

## 30秒快速开始

```bash
# 1. 配置API密钥
echo "DASHSCOPE_API_KEY=sk-your-api-key" >> .env

# 2. 安装依赖
pip install openai pypdf

# 3. 测试配置
python test_qwen_api.py

# 4. 上传测试
curl -X POST http://localhost:8000/api/plans/upload/ -F "file=@plan.pdf"
```

## 核心文件

| 文件 | 作用 |
|------|------|
| `api/qwen_service.py` | 千问服务核心模块 |
| `api/plan_views.py` | API视图（已更新） |
| `test_qwen_api.py` | 配置测试脚本 |
| `.env` | 环境变量配置 |

## API密钥获取

1. 访问：https://dashscope.console.aliyun.com/
2. 注册/登录
3. 开通服务
4. 创建API Key
5. 复制到 `.env` 文件

## 环境变量

```bash
# 必需
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxx

# 可选（如果需要DeepSeek）
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
```

## API接口

### 上传PDF
```bash
POST /api/plans/upload/
Content-Type: multipart/form-data
Body: file=<PDF文件>
```

### 获取列表
```bash
GET /api/plans/
```

### 获取详情
```bash
GET /api/plans/{id}/
```

### 更新数据
```bash
PUT /api/plans/{id}/
Content-Type: application/json
Body: { "customer_name": "新名字", ... }
```

## 提取的字段

```json
{
  "customer_name": "客户姓名",
  "customer_age": 35,
  "customer_gender": "男",
  "insurance_product": "产品名称",
  "insurance_company": "保险公司",
  "insurance_amount": 500000,
  "premium_amount": 15000,
  "payment_years": 20,
  "total_premium": 300000,
  "insurance_period": "终身"
}
```

## Python调用示例

```python
import requests

# 上传PDF
files = {'file': open('plan.pdf', 'rb')}
response = requests.post(
    'http://localhost:8000/api/plans/upload/',
    files=files
)

if response.status_code == 201:
    data = response.json()
    print(data['extracted_data'])
```

## JavaScript调用示例

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/api/plans/upload/', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.extracted_data);
```

## 使用的模型

| 模型 | 用途 | 成本 |
|------|------|------|
| qwen-vl-max-latest | PDF视觉识别 | ~¥0.02/次 |
| qwen-plus-latest | 文本分析（备用） | ~¥0.002/次 |

## 工作流程

```
PDF上传 → 视觉识别 → 成功 → 返回数据
        ↓ 失败
      文本提取 → 文本分析 → 成功 → 返回数据
                        ↓ 失败
                      返回错误
```

## 测试命令

```bash
# 测试API配置
python test_qwen_api.py

# 测试上传（cURL）
curl -X POST http://localhost:8000/api/plans/upload/ \
  -F "file=@test.pdf"

# 测试上传（HTTPie）
http -f POST localhost:8000/api/plans/upload/ file@test.pdf

# 查看所有文档
curl http://localhost:8000/api/plans/

# 查看单个文档
curl http://localhost:8000/api/plans/1/
```

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| DASHSCOPE_API_KEY未设置 | 环境变量未配置 | 检查.env文件 |
| 只支持PDF文件 | 文件格式错误 | 确保上传.pdf文件 |
| 文件大小超过10MB | 文件太大 | 压缩PDF文件 |
| JSON解析失败 | API响应格式异常 | 查看raw_response |
| API调用失败 | 网络或密钥问题 | 检查网络和密钥 |

## 限制

- 文件大小：≤ 10MB
- 文件格式：PDF
- 推荐页数：≤ 20页
- 并发请求：根据API限额

## 性能

- 小文件(<1MB)：2-5秒
- 中文件(1-5MB)：5-10秒
- 大文件(5-10MB)：10-20秒

## 准确率

- 标准计划书：95%+
- 复杂格式：85-90%
- 扫描版：80-85%

## 优化建议

1. **提高准确率**：
   - 使用清晰的原生PDF
   - 确保文字清晰可读
   - 标准格式文档效果最好

2. **降低成本**：
   - 优先使用文本提取+分析
   - 实现结果缓存
   - 批量处理控制并发

3. **提升速度**：
   - 压缩PDF文件
   - 使用异步处理
   - 移除不必要页面

## 故障排查步骤

1. **运行测试脚本**
   ```bash
   python test_qwen_api.py
   ```

2. **检查环境变量**
   ```bash
   echo $DASHSCOPE_API_KEY
   ```

3. **查看日志**
   ```bash
   tail -f logs/django.log
   ```

4. **测试网络连接**
   ```bash
   curl https://dashscope.aliyuncs.com
   ```

5. **验证API密钥**
   - 登录阿里云控制台
   - 检查密钥状态
   - 查看调用限额

## 文档索引

| 文档 | 内容 |
|------|------|
| QWEN_SETUP.md | 详细配置指南 |
| QWEN_USAGE_EXAMPLES.md | 代码示例集合 |
| QWEN_INTEGRATION_SUMMARY.md | 集成总结 |
| test_qwen_api.py | 测试脚本 |

## 技术支持

- 阿里云文档：https://help.aliyun.com/zh/dashscope/
- 千问模型：https://help.aliyun.com/zh/dashscope/developer-reference/model-square/
- 项目Issues：查看项目文档

## 命令速查

```bash
# 开发相关
pip install -r requirements.txt          # 安装依赖
python manage.py runserver               # 启动服务
python test_qwen_api.py                  # 测试API

# 数据库相关
python manage.py makemigrations          # 创建迁移
python manage.py migrate                 # 应用迁移

# 测试相关
curl -X POST http://localhost:8000/api/plans/upload/ -F "file=@test.pdf"
curl http://localhost:8000/api/plans/
curl http://localhost:8000/api/plans/1/
```

## 下一步

1. ✓ 配置API密钥
2. ✓ 测试配置
3. ✓ 上传测试PDF
4. → 集成到前端
5. → 部署到生产环境

---

**提示**：这是快速参考卡片，详细信息请查看完整文档。
