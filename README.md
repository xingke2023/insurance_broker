# 保险管理系统 (Insurance Management System)

一个现代化的全栈Web应用，使用Django REST Framework后端和React + Tailwind CSS前端构建。

## 技术栈

### 后端
- **Django 5.2.7** - Python Web框架
- **Django REST Framework 3.16.1** - RESTful API
- **PyMySQL** - MySQL数据库连接器
- **django-cors-headers** - 处理跨域请求

### 前端
- **React 18** - 前端UI框架
- **Vite** - 构建工具和开发服务器
- **Tailwind CSS** - 实用优先的CSS框架
- **Axios** - HTTP客户端

### 数据库
- **MySQL** - 运行在端口8510
- 数据库名: `insurancetools`

## 项目结构

```
harry-insurance/
├── backend/              # Django配置目录
│   ├── settings.py      # 主配置文件
│   ├── urls.py          # 主URL配置
│   └── wsgi.py          # WSGI配置
├── api/                 # Django API应用
│   ├── models.py        # 数据模型
│   ├── serializers.py   # DRF序列化器
│   ├── views.py         # API视图
│   └── urls.py          # API路由
├── frontend/            # React前端应用
│   ├── src/
│   │   ├── components/  # React组件
│   │   ├── services/    # API服务
│   │   ├── App.jsx      # 主应用组件
│   │   └── main.jsx     # 入口文件
│   ├── package.json
│   └── vite.config.js
└── manage.py            # Django管理脚本
```

## 功能特性

### 保险策略管理
- 创建新保单
- 查看所有保单列表
- 更新保单信息
- 删除保单
- 取消保单
- 查看有效保单

### API端点

- `GET /api/policies/` - 获取所有保单
- `POST /api/policies/` - 创建新保单
- `GET /api/policies/{id}/` - 获取单个保单详情
- `PUT /api/policies/{id}/` - 更新保单
- `DELETE /api/policies/{id}/` - 删除保单
- `GET /api/policies/active_policies/` - 获取所有有效保单
- `POST /api/policies/{id}/cancel_policy/` - 取消保单

## 安装和运行

### 前置要求
- Python 3.12+
- Node.js 24+
- MySQL 数据库

### 后端设置

1. 安装Python依赖:
```bash
pip3 install django djangorestframework django-cors-headers pymysql python-dotenv
```

2. 配置数据库连接（已在settings.py中配置）:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'insurancetools',
        'USER': 'root',
        'PASSWORD': 'Uu8297636',
        'HOST': 'localhost',
        'PORT': '8510',
    }
}
```

3. 运行数据库迁移:
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

4. 创建超级用户（可选）:
```bash
python3 manage.py createsuperuser
```

5. 启动Django开发服务器:
```bash
python3 manage.py runserver 0.0.0.0:8007
```

后端将运行在: http://0.0.0.0:8007 (可从任何IP访问)

### 前端设置

1. 进入前端目录:
```bash
cd frontend
```

2. 安装依赖:
```bash
npm install
```

3. 启动开发服务器:
```bash
npm run dev
```

前端将运行在: http://localhost:8008 (或使用服务器IP:8008)

## 使用指南

1. 启动后端服务器（端口8007，0.0.0.0）
2. 启动前端服务器（端口8008，0.0.0.0）
3. 在浏览器访问 http://localhost:8008 或使用服务器IP
4. 使用界面进行保单管理操作

### 创建保单
- 点击"新建保单"按钮
- 填写表单信息
- 提交创建

### 管理保单
- 查看保单列表
- 取消有效保单
- 删除保单记录

## 数据模型

### InsurancePolicy (保险策略)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| policy_number | String(50) | 保单号（唯一） |
| customer_name | String(100) | 客户姓名 |
| policy_type | String(50) | 保险类型 |
| premium | Decimal | 保费 |
| start_date | Date | 起始日期 |
| end_date | Date | 结束日期 |
| status | String(20) | 状态（active/expired/cancelled） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

## 配置说明

### CORS设置
当前配置为允许所有来源访问（`CORS_ALLOW_ALL_ORIGINS = True`），适用于开发环境。

生产环境建议修改 `backend/settings.py` 中的CORS配置：
```python
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://your-domain.com",
    "https://your-domain.com",
]
```

### API认证
当前配置为开放访问 (`AllowAny`)，生产环境建议配置适当的认证机制。

## 开发注意事项

1. 确保MySQL服务运行在8510端口
2. 前后端需要同时运行才能正常工作
3. 修改前端代码会自动热重载
4. 修改后端代码需要重启Django服务器
5. 后端运行在 0.0.0.0:8007，可从任何网络访问
6. 前端运行在 0.0.0.0:8008，可从任何网络访问

## 生产部署建议

1. 设置 `DEBUG = False`
2. 配置合适的 `SECRET_KEY`
3. 设置 `ALLOWED_HOSTS`
4. 使用环境变量管理敏感信息
5. 配置HTTPS
6. 使用生产级Web服务器（如Gunicorn + Nginx）
7. 配置数据库连接池
8. 设置适当的CORS策略

## 许可证

MIT License
