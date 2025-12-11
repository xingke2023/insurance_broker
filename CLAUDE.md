# 保险计划书智能分析系统 - 项目分析

## 项目概述

这是一个**保险计划书智能分析系统**（Insurance Plan Analyzer），使用全栈技术构建的现代化Web应用。主要用于自动化处理和分析保险计划书文档。

## 核心功能

### 1. OCR文档识别与保存
- 上传保险计划书文档（PDF/图片）
- 使用阿里云通义千问进行OCR识别
- 保存识别结果到数据库
- 实现位置：`api/ocr_views.py`

### 2. AI智能提取
- 提取受保人信息（姓名、年龄、性别）
- 提取保险产品信息（产品名、保险公司）
- 提取保费信息（年缴保费、缴费年数、总保费）
- 提取保险期限和基本保额
- AI服务：`api/qwen_service.py`

### 3. 年度价值表分析
- 使用DeepSeek AI分析保单年度价值表
- 提取每年的保证现金价值、非保证现金价值
- 存储多年度数据用于对比分析
- 实现位置：`api/deepseek_service.py`

### 4. 用户认证系统
- JWT token认证
- 用户注册/登录功能
- 多语言支持（中文/英文）
- 认证视图：`api/auth_views.py`

### 5. 文档管理
- 查看已保存的文档列表
- 查看文档详情和分析结果
- 批量删除文档
- 前端组件：`frontend/src/components/PlanDocumentManagement.jsx`

### 6. 海报分析工具
- 上传海报图片（JPG、PNG、WebP、GIF，最大10MB）
- AI智能分析海报的视觉设计、内容解读、营销要素
- 提供8种预设分析模板：产品分析、客户视角分析、朋友圈文案、全面分析、文案提取、设计分析、营销效果评估、竞品对比
- 支持自定义分析提示词
- 一键复制分析结果
- AI服务：Google Gemini 3 Pro Preview (`api/gemini_service.py`)
- 前端页面：`frontend/src/components/PosterAnalyzer.jsx`
- 访问路径：Dashboard → 海报分析工具 → `/poster-analyzer`

#### 海报分析功能详细说明

**技术架构**：
- **后端服务**：`api/gemini_service.py` - 封装Gemini API调用
- **视图层**：`api/poster_views.py` - 处理图片上传和分析请求
- **路由**：`POST /api/poster/analyze` - 分析接口，`GET /api/poster/templates` - 获取模板
- **AI模型**：Google Gemini 3 Pro Preview (`gemini-3-pro-preview`)
- **SDK版本**：`google-genai` 1.41.0（新版SDK，使用 `genai.Client`）

**分析模板**：
1. **产品分析**：深度理解海报传达的产品定位、核心价值、信息传达、情感共鸣和品牌印象
2. **客户视角分析**：站在客户角度分析产品吸引力、列举客户可能的疑问、并从专业角度给出满意答复
3. **朋友圈文案**：生成5种不同角度的营销文案（痛点切入、利益驱动、故事叙述、数据说话、情感共鸣），包含emoji和话题标签
4. **全面分析**：视觉设计、内容解读、营销要素、改进建议
5. **文案提取**：识别并提取海报中的所有文字内容
6. **设计分析**：配色方案、排版布局、字体选择、视觉层次
7. **营销效果评估**：目标受众定位、核心卖点、转化率预估
8. **竞品对比**：与行业标准对比，分析优劣势和创新点

**API实现细节**：
```python
# 使用新版Gemini SDK
from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)

# 构建请求
parts = [
    types.Part.from_text(text=prompt_text),
    types.Part.from_bytes(data=image_bytes, mime_type=content_type)
]

# 调用API
response = client.models.generate_content(
    model='gemini-3-pro-preview',
    contents=[types.Content(role="user", parts=parts)]
)
```

**前端特性**：
- 左右分栏布局：左侧上传和选择模板，右侧显示结果
- 渐变背景设计（黄色→橙色→红色）
- 图片实时预览
- 分析过程loading动画
- 结果展示支持换行和格式化
- 返回Dashboard按钮

**文件大小限制**：
- 最大10MB
- 支持格式：image/jpeg, image/jpg, image/png, image/webp, image/gif
- 前后端双重验证

## 技术架构

### 后端技术栈
- **框架**: Django 5.2.7
- **API**: Django REST Framework 3.16.1
- **数据库**: MySQL（端口8510，数据库名：insurancetools）
- **数据库连接**: PyMySQL
- **认证**: JWT (djangorestframework-simplejwt)
- **跨域**: django-cors-headers
- **配置**: python-dotenv

### 前端技术栈
- **框架**: React 19.1.1
- **构建工具**: Vite 7.1.7
- **样式**: Tailwind CSS 3.4.17
- **HTTP客户端**: Axios 1.13.1
- **国际化**: react-i18next 16.2.4
- **图标**: Heroicons, Lucide React

### AI服务集成
- **阿里云通义千问**: OCR文档识别
- **DeepSeek API**: 年度价值表格分析
- **Google Gemini 3 Pro Preview**: 海报视觉分析和营销评估

## 项目结构

```
harry-insurance/
├── backend/                          # Django配置目录
│   ├── settings.py                   # 主配置文件
│   ├── urls.py                       # 主URL配置
│   ├── wsgi.py                       # WSGI配置
│   └── asgi.py                       # ASGI配置
│
├── api/                              # Django API应用
│   ├── models.py                     # 数据模型（InsurancePolicy, PlanDocument, AnnualValue）
│   ├── serializers.py                # DRF序列化器
│   ├── urls.py                       # API路由配置
│   ├── views.py                      # 保险策略视图
│   ├── auth_views.py                 # 用户认证视图
│   ├── ocr_views.py                  # OCR识别和文档保存
│   ├── qwen_service.py               # 通义千问AI服务
│   ├── deepseek_service.py           # DeepSeek表格分析服务
│   ├── gemini_service.py             # Gemini AI海报分析服务
│   ├── poster_views.py               # 海报分析视图
│   ├── insurance_company_configs.py  # 保险公司配置
│   └── admin.py                      # Django管理后台配置
│
├── frontend/                         # React前端应用（主前端，端口8008）
│   ├── src/
│   │   ├── components/               # React组件
│   │   │   ├── HomePage.jsx          # 主页/OCR上传（19KB）
│   │   │   ├── PlanAnalyzer.jsx      # 计划书分析（31KB）
│   │   │   ├── PlanDocumentManagement.jsx  # 文档管理（52KB）
│   │   │   ├── PosterAnalyzer.jsx    # 海报分析工具
│   │   │   ├── Dashboard.jsx         # 仪表盘
│   │   │   ├── Login.jsx             # 登录页面
│   │   │   ├── Register.jsx          # 注册页面
│   │   │   └── PolicyList.jsx        # 保单列表
│   │   ├── services/                 # API服务层
│   │   ├── context/                  # React Context
│   │   ├── i18n.js                   # 国际化配置（14KB）
│   │   ├── config.js                 # 前端配置
│   │   ├── App.jsx                   # 主应用组件
│   │   └── main.jsx                  # 入口文件
│   ├── package.json                  # 依赖配置
│   ├── vite.config.js                # Vite配置
│   ├── tailwind.config.js            # Tailwind配置
│   └── postcss.config.js             # PostCSS配置
│
├── frontend1/                        # 备用前端（端口8088）
│
├── media/                            # 文件上传目录
│
├── .env                              # 环境变量配置
├── .env.example                      # 环境变量示例
├── manage.py                         # Django管理脚本
├── requirements.txt                  # Python依赖
├── start-backend.sh                  # 后端启动脚本
├── start-frontend.sh                 # 前端启动脚本
└── start-frontend1.sh                # 备用前端启动脚本
```

## 数据模型

### InsurancePolicy（保险策略）
基础保单模型，包含：
- `policy_number`: 保单号（唯一）
- `customer_name`: 客户姓名
- `policy_type`: 保险类型
- `premium`: 保费
- `start_date/end_date`: 保险期限
- `status`: 状态（active/expired/cancelled）

### PlanDocument（计划书文档）
主文档表，存储：
- 文件信息（名称、路径、大小）
- 受保人信息（姓名、年龄、性别）
- 保险产品信息（产品名、保险公司）
- 保费信息（年缴、缴费年数、总保费）
- OCR识别内容（`content`字段）
- AI提取数据（`extracted_data` JSON字段）
- 年度价值表（`table` JSON字段）
- 处理状态（uploaded/processing/completed/failed）

### AnnualValue（年度价值表）
存储每个保单年度的退保价值：
- `policy_year`: 保单年度终结
- `guaranteed_cash_value`: 保证现金价值
- `non_guaranteed_cash_value`: 非保证现金价值
- `total_cash_value`: 总现金价值
- 与PlanDocument关联（外键）

## API端点

### 保险策略管理
- `GET /api/policies/` - 获取所有保单
- `POST /api/policies/` - 创建新保单
- `GET /api/policies/{id}/` - 获取单个保单详情
- `PUT /api/policies/{id}/` - 更新保单
- `DELETE /api/policies/{id}/` - 删除保单
- `GET /api/policies/active_policies/` - 获取所有有效保单
- `POST /api/policies/{id}/cancel_policy/` - 取消保单

### 用户认证
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录
- `GET /api/auth/profile/` - 获取用户信息

### OCR与文档管理
- `POST /api/ocr/save/` - 保存OCR识别结果
- `GET /api/ocr/documents/` - 获取已保存文档列表
- `GET /api/ocr/documents/{id}/` - 获取文档详情
- `POST /api/ocr/documents/{id}/analyze/` - 分析文档年度价值表
- `POST /api/ocr/documents/{id}/basic-info/` - 分析基本信息
- `POST /api/ocr/documents/delete/` - 批量删除文档

### 海报分析
- `POST /api/poster/analyze` - 分析海报图片（multipart/form-data，字段：image, custom_prompt）
- `GET /api/poster/templates` - 获取预设分析模板列表（8种模板）

## 部署配置

### 服务端口
- **后端服务**: `0.0.0.0:8007`（Django）
- **前端服务**: `0.0.0.0:8008`（主前端）
- **备用前端**: `0.0.0.0:8088`（frontend1）
- **MySQL数据库**: `localhost:8510`

### 环境变量（.env）
```bash
# Django配置
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DB_NAME=insurance_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

# 阿里云DashScope API密钥
DASHSCOPE_API_KEY=sk-67f551815ab14c35afc14170be7dacca

# DeepSeek API密钥
# DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here

# Google Gemini API密钥 (用于海报分析)
GEMINI_API_KEY=AIzaSyC6_Lp7D2RLFTDtWoKz6-eSerX6oNDdjdM

# CORS配置
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## 安装和运行

### 前置要求
- Python 3.12+
- Node.js 24+
- MySQL 数据库

### 后端启动步骤

1. 安装Python依赖：
```bash
pip3 install django djangorestframework django-cors-headers pymysql python-dotenv google-genai
```

2. 运行数据库迁移：
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

3. 创建超级用户（可选）：
```bash
python3 manage.py createsuperuser
```

4. 启动Django服务器：Django 進程也需要重啟
```bash
sudo supervisorctl restart harry-insurance:harry-insurance-django
```

### 前端启动步骤

1. 进入前端目录并安装依赖：
```bash
cd frontend
npm install
```

2. 启动开发服务器：
```bash
./start-frontend.sh
# 或
npm run dev
```

## 关键文件说明

### 后端核心文件
- **api/ocr_views.py**: OCR识别和文档保存的核心逻辑
- **api/deepseek_service.py**: DeepSeek AI表格分析服务
- **api/qwen_service.py**: 通义千问OCR识别服务
- **api/gemini_service.py**: Google Gemini海报分析服务
- **api/poster_views.py**: 海报分析API视图（上传、分析、模板）
- **api/insurance_company_configs.py**: 各保险公司的字段映射配置
- **backend/settings.py**: Django主配置文件（数据库、JWT、CORS等）

### 前端核心组件
- **HomePage.jsx**: 主页和OCR上传界面（19KB）
- **PlanAnalyzer.jsx**: 计划书智能分析组件（31KB）
- **PlanDocumentManagement.jsx**: 文档管理和查看组件（52KB）
- **PosterAnalyzer.jsx**: 海报分析工具页面（独立页面，支持图片上传和AI分析）
- **i18n.js**: 国际化配置文件（14KB）

### 文档资源
- **DEMO_GUIDE.md**: 演示指南
- **PLAN_ANALYZER_GUIDE.md**: 计划书分析功能指南
- **PLAN_MANAGEMENT_USER_GUIDE.md**: 用户使用指南
- **DEEPSEEK_ANALYSIS_GUIDE.md**: DeepSeek分析说明
- **PROJECT_STRUCTURE.md**: 项目结构文档
- **QWEN_INTEGRATION_SUMMARY.md**: 通义千问集成总结

## 安全注意事项

### 当前需要改进的地方

⚠️ **生产环境必须修改**：

1. **数据库安全**
   - 位置：`backend/settings.py:93`
   - 问题：数据库密码硬编码
   - 建议：使用环境变量

2. **Django密钥**
   - 位置：`backend/settings.py:32`
   - 问题：使用默认不安全的SECRET_KEY
   - 建议：生成新的随机密钥

3. **调试模式**
   - 位置：`backend/settings.py:35`
   - 问题：DEBUG=True
   - 建议：生产环境设置为False

4. **跨域配置**
   - 位置：`backend/settings.py:150`
   - 问题：CORS_ALLOW_ALL_ORIGINS = True
   - 建议：限制允许的域名

5. **API密钥**
   - 位置：`.env`文件
   - 问题：包含真实API密钥
   - 建议：确保.env不上传到版本控制（已在.gitignore中）

6. **主机限制**
   - 位置：`backend/settings.py:37`
   - 问题：ALLOWED_HOSTS = ['*']
   - 建议：生产环境指定具体域名

## 开发注意事项

1. 确保MySQL服务运行在8510端口
2. 前后端需要同时运行才能正常工作
3. 修改前端代码会自动热重载
4. 修改后端代码需要重启Django服务器
5. 后端运行在0.0.0.0:8007，可从任何网络访问
6. 前端运行在0.0.0.0:8008，可从任何网络访问

## 生产部署建议

1. **安全配置**
   - 设置 `DEBUG = False`
   - 配置强密码的 `SECRET_KEY`
   - 设置具体的 `ALLOWED_HOSTS`
   - 限制CORS允许的域名
   - 使用环境变量管理所有敏感信息

2. **服务器配置**
   - 使用Gunicorn作为WSGI服务器
   - 使用Nginx作为反向代理
   - 配置HTTPS（SSL证书）
   - 配置数据库连接池

3. **性能优化**
   - 启用前端生产构建（`npm run build`）
   - 配置静态文件CDN
   - 启用数据库查询优化
   - 配置缓存策略

4. **监控与日志**
   - 配置应用日志记录
   - 设置错误监控（如Sentry）
   - 配置性能监控
   - 定期备份数据库

## Celery工作原理

### 系统架构
本项目使用 **Celery + Redis** 实现异步任务处理，自动分析保险计划书文档。

### 任务流水线

当用户上传PDF后，系统会自动执行以下流程：

```
用户上传PDF
    ↓
创建PlanDocument记录（保存OCR内容）
    ↓
触发Celery任务链 (6个任务按顺序执行)
    ↓
[步骤1] 提取表格源代码 (extract_tablecontent_task)
    ↓
[步骤2] 提取基本信息 (extract_basic_info_task)
    → 受保人信息、保险产品、保费、保额等
    ↓
[步骤3] 提取表格概要 (extract_tablesummary_task)
    → 识别所有以"保单年度终结"为坐标的表格
    ↓
[步骤4] 提取退保价值表 (extract_table_task)
    → 提取保证现金价值、非保证现金价值等数据
    ↓
[步骤5] 提取无忧选退保价值表 (extract_wellness_table_task)
    → 提取无忧选相关的年度数据
    ↓
[步骤6] 提取计划书概要 (extract_summary_task)
    → 生成Markdown格式的计划书总结
    ↓
处理完成（status: completed）
```

### 核心组件

1. **任务队列**: Redis (localhost:6379)
2. **任务处理器**: Celery Worker (4个并发)
3. **任务定义**: `api/tasks.py`
4. **任务配置**: `backend/celery.py`
5. **任务触发**: `api/ocr_views.py:122` (save_ocr_result函数)

### 任务特性

- **自动链式触发**: 每个任务完成后自动触发下一个任务
- **重试机制**: 每个任务最多重试2次（60秒间隔）
- **降级策略**: 即使某个任务失败，也会继续执行后续任务
- **状态跟踪**: 实时更新 `processing_stage` 字段
- **进度显示**: 前端可轮询状态获取处理进度

### 监控和管理

```bash
# 启动Celery Worker
./start_celery.sh

# 停止Celery Worker
./stop_celery.sh

# 查看任务日志
tail -f logs/celery.log

# 查看Redis队列
redis-cli LLEN celery
```

### 详细文档
更多配置和使用说明，请参阅：
- **CELERY_SETUP.md** - 完整的Celery安装、配置和使用指南
- **api/tasks.py** - 6个任务的详细实现代码

### 步骤5代码逻
核心逻辑（两步走）：

  第一步：判断是否存在

  - 读取 tablesummary（步骤3生成的表格概要）
  - 调用 DeepSeek API 判断是否有包含"入息"/"提取"/"无忧选"字段的表格
  - 如果不存在 → 保存空字符串，结束

  第二步：提取数据（如果存在）

  - 从 content（OCR文本）中提取该表格的具体数据
  - 调用 DeepSeek API 提取4个字段：
    - policy_year: 保单年度
    - withdraw: 该年非保证入息
    - withdraw_total: 累计已支付非保证入息
    - total: 行使无忧选后的退保价值
- 第一步OCR识别 如果失败 其他步骤就全部没有意义了
- 第一步OCR识别 如果失败 其他步骤就全部没有意义了
- /memory 页面company-comparison 文件frontend/src/components/CompanyComparison.jsx
- /memory 您的系统（可能是 AppArmor 或其他安全模块）正在杀死 esbuild 的原生二进制文件（每次运行都被 SIGKILL 信号杀死，Exit code
  137）。

  解决方案

  我使用了 esbuild-wasm（WebAssembly 版本的 esbuild）替代原生二进制版本：

  1. ✅ 安装了 esbuild-wasm
  2. ✅ 通过符号链接将 node_modules/esbuild 指向 esbuild-wasm
  3. ✅ 构建成功完成（11.94秒