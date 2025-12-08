# 项目结构

## 目录树

```
harry-insurance/
├── api/                          # Django API应用
│   ├── migrations/               # 数据库迁移
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── auth_views.py            # 用户认证视图
│   ├── deepseek_service.py      # DeepSeek服务（原有）
│   ├── qwen_service.py          # 阿里千问服务（新增）⭐
│   ├── models.py                # 数据模型
│   ├── plan_views.py            # 计划书处理视图（已更新）⭐
│   ├── serializers.py           # 序列化器
│   ├── tests.py
│   ├── urls.py                  # API路由
│   └── views.py                 # 通用视图
│
├── backend/                      # Django项目配置
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py              # 项目设置
│   ├── urls.py                  # 主路由
│   └── wsgi.py
│
├── frontend/                     # React前端
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   │   ├── components/          # React组件
│   │   ├── pages/               # 页面组件
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── README.md
│
├── media/                        # 上传文件存储
│   └── plan_documents/          # PDF文件
│
├── .env                          # 环境变量（需创建）⭐
├── .env.example                  # 环境变量模板（新增）⭐
├── .gitignore
├── manage.py                     # Django管理脚本
├── requirements.txt             # Python依赖（已更新）⭐
│
├── test_qwen_api.py            # API测试脚本（新增）⭐
├── start-backend.sh            # 后端启动脚本
├── start-frontend.sh           # 前端启动脚本
│
├── README.md                    # 项目主文档
├── QUICKSTART.md               # 快速开始
├── START_GUIDE.md              # 启动指南
├── DEMO_GUIDE.md               # 演示指南
├── IMPLEMENTATION_SUMMARY.md   # 实现总结
├── PLAN_EXTRACTOR_README.md    # 计划书提取说明
│
└── 阿里千问文档（新增）⭐
    ├── QWEN_SETUP.md                    # 配置指南
    ├── QWEN_USAGE_EXAMPLES.md          # 使用示例
    ├── QWEN_INTEGRATION_SUMMARY.md     # 集成总结
    └── QWEN_QUICK_REFERENCE.md         # 快速参考
```

⭐ 标记为本次更新的新增或修改文件

## 核心模块说明

### API应用 (api/)

#### qwen_service.py（新增）
```python
# 核心功能
extract_plan_data_from_pdf(pdf_file)     # PDF直接识别
extract_plan_data_from_text(text_content) # 文本分析
```

**使用的模型：**
- qwen-vl-max-latest：视觉识别
- qwen-plus-latest：文本分析

**返回格式：**
```python
{
    'success': True/False,
    'data': {...},           # 提取的结构化数据
    'raw_response': '...'    # 原始响应
}
```

#### plan_views.py（已更新）
```python
# API端点
upload_plan_document(request)      # POST /api/plans/upload/
get_plan_documents(request)        # GET /api/plans/
get_plan_document(request, pk)     # GET /api/plans/{id}/
update_plan_document(request, pk)  # PUT /api/plans/{id}/
```

**工作流程：**
1. 接收上传的PDF文件
2. 调用 qwen_service 识别
3. 保存到数据库
4. 返回结构化数据

#### models.py
```python
# 数据模型
PlanDocument      # 计划书文档
AnnualValue       # 年度价值表
User              # 用户模型
```

### 前端应用 (frontend/)

#### 主要组件
```
src/
├── components/
│   ├── Auth/              # 认证组件
│   ├── PlanExtractor/     # 计划书提取器
│   └── Common/            # 通用组件
│
├── pages/
│   ├── HomePage.js        # 首页
│   ├── LoginPage.js       # 登录页
│   └── PlanListPage.js    # 计划书列表
│
└── services/
    └── api.js             # API调用封装
```

### 配置文件

#### .env（需创建）
```bash
# Django配置
SECRET_KEY=your-secret-key
DEBUG=True

# 数据库配置
DB_NAME=insurance_db
DB_USER=root
DB_PASSWORD=password

# API密钥
DASHSCOPE_API_KEY=sk-xxx    # 阿里千问（必需）
DEEPSEEK_API_KEY=sk-xxx     # DeepSeek（可选）
```

#### requirements.txt（已更新）
```
# 原有依赖
django==5.2.7
djangorestframework==3.16.1
djangorestframework-simplejwt==5.5.1
django-cors-headers==4.9.0
pymysql==1.1.1
python-dotenv==1.1.0

# 新增依赖
openai>=1.0.0              # 千问API客户端
pypdf>=3.0.0               # PDF文本提取
```

## 数据流

### PDF上传和识别流程

```
前端 (React)
    ↓ [POST /api/plans/upload/]
    ↓ {file: PDF}
    ↓
Django View (plan_views.py)
    ↓
    ├─→ 创建 PlanDocument 记录
    ↓
Qwen Service (qwen_service.py)
    ↓
    ├─→ 尝试视觉识别
    │   ├─→ 成功 → 返回数据
    │   └─→ 失败 ↓
    │
    └─→ 提取PDF文本
        ├─→ 文本分析
        └─→ 返回数据
    ↓
Django View
    ↓
    ├─→ 保存提取的数据
    ├─→ 更新文档状态
    └─→ 返回响应
    ↓
前端 (React)
    └─→ 显示提取结果
```

### 数据库结构

```sql
-- 计划书文档表
PlanDocument
    - id (PK)
    - user_id (FK)
    - file_name
    - file_path
    - file_size
    - status (processing/completed/failed)
    - insured_name
    - insured_age
    - insured_gender
    - insurance_product
    - insurance_company
    - sum_assured
    - annual_premium
    - payment_years
    - total_premium
    - insurance_period
    - extracted_data (JSON)
    - error_message
    - created_at
    - updated_at

-- 年度价值表
AnnualValue
    - id (PK)
    - plan_document_id (FK)
    - policy_year
    - guaranteed_cash_value
    - non_guaranteed_cash_value
    - total_cash_value
```

## 技术栈

### 后端
- **框架**: Django 5.2.7
- **API**: Django REST Framework 3.16.1
- **认证**: JWT (djangorestframework-simplejwt)
- **数据库**: MySQL (pymysql)
- **AI服务**: 阿里千问 (OpenAI SDK)
- **PDF处理**: pypdf

### 前端
- **框架**: React
- **HTTP客户端**: Axios
- **样式**: CSS/Tailwind

### AI模型
- **视觉识别**: qwen-vl-max-latest
- **文本分析**: qwen-plus-latest
- **备用**: deepseek-chat

## API端点总览

```
身份认证
├── POST   /api/auth/register/          # 用户注册
├── POST   /api/auth/login/             # 用户登录
└── POST   /api/auth/token/refresh/     # 刷新令牌

计划书管理
├── POST   /api/plans/upload/           # 上传PDF并提取
├── GET    /api/plans/                  # 获取文档列表
├── GET    /api/plans/{id}/             # 获取文档详情
└── PUT    /api/plans/{id}/             # 更新文档数据
```

## 环境要求

### 开发环境
- Python 3.8+
- Node.js 14+
- MySQL 5.7+

### 生产环境
- Python 3.8+
- Node.js 14+
- MySQL 5.7+
- Nginx (可选)
- Gunicorn (可选)

## 部署架构

```
用户浏览器
    ↓
Nginx (反向代理)
    ├─→ 静态文件 (React)
    │   └─→ /static/
    │
    └─→ Django应用
        ├─→ Gunicorn (WSGI)
        └─→ 端口: 8000
            ↓
        MySQL数据库
            └─→ 端口: 3306
            ↓
        阿里云API
            └─→ DashScope
```

## 安全考虑

1. **API密钥管理**
   - 使用环境变量
   - 不提交到版本控制
   - 定期轮换密钥

2. **文件上传**
   - 文件类型验证
   - 文件大小限制
   - 文件名清理

3. **认证授权**
   - JWT令牌
   - CORS配置
   - 权限控制

## 监控和日志

```
日志位置：
├── Django日志: logs/django.log
├── 访问日志: logs/access.log
└── 错误日志: logs/error.log

监控指标：
├── API调用次数
├── 识别成功率
├── 平均响应时间
└── 错误率
```

## 扩展方向

### 短期
- [ ] 添加更多字段提取
- [ ] 实现批量上传
- [ ] 优化错误处理
- [ ] 添加数据验证

### 中期
- [ ] 用户管理界面
- [ ] 数据统计分析
- [ ] 导出功能
- [ ] API限流

### 长期
- [ ] 自定义模型训练
- [ ] 多语言支持
- [ ] 移动端应用
- [ ] 微服务架构

## 相关链接

- [阿里云DashScope](https://dashscope.console.aliyun.com/)
- [Django文档](https://docs.djangoproject.com/)
- [React文档](https://react.dev/)
- [千问模型文档](https://help.aliyun.com/zh/dashscope/)
