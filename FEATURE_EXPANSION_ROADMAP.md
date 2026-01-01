# 保险网站功能扩展执行任务清单

## 项目目标
将现有的保险计划书分析系统扩展为全方位的保险咨询和比较平台，包括AI智能推荐、客户案例展示、产品对比、在线客服、专业论坛等功能。

---

## 第一阶段：数据库设计与模型创建

### 任务1：扩展insurance_products表，添加产品详细信息字段
**要求**：
- 在api/models.py中扩展InsuranceProduct模型，添加以下字段：
  - product_category: 产品类别（储蓄分红型/重疾险/医疗险/人寿险等）
  - target_age_group: 目标年龄段（JSON字段：最小年龄、最大年龄）
  - premium_range: 保费范围（JSON字段：最低保费、最高保费）
  - coverage_period: 保障期限（终身/定期/年数）
  - payment_period: 缴费期限（趸交/5年/10年/20年等）
  - guaranteed_return_rate: 保证回报率（百分比）
  - estimated_return_rate: 预期回报率（百分比）
  - key_features: 产品特色（JSON数组）
  - suitable_for: 适合人群（JSON数组：人生阶段、收入水平、家庭状况）
  - is_flagship: 是否为主打产品（布尔值）
  - ranking_score: 综合评分（1-100）
- 运行makemigrations和migrate
- 使用Django admin界面测试新字段

===

### 任务2：创建ClientCase（客户案例）模型
**要求**：
- 在api/models.py中创建ClientCase模型，包含字段：
  - title: 案例标题
  - life_stage: 人生阶段（扶幼保障期/收入成长期/责任高峰期/责任递减期/退休期）
  - age: 客户年龄
  - annual_income: 年收入
  - family_situation: 家庭状况（JSON：配偶、子女数量、父母赡养等）
  - insurance_needs: 保险需求（JSON数组）
  - recommended_products: 推荐产品（ManyToMany关联InsuranceProduct）
  - total_annual_premium: 年度总保费
  - case_description: 案例描述（文本）
  - solution_explanation: 解决方案说明（文本）
  - case_image: 案例配图（ImageField）
  - created_at, updated_at: 时间戳
  - is_published: 是否发布
  - view_count: 浏览次数
- 创建序列化器ClientCaseSerializer
- 运行迁移并创建5-10个示例案例数据

===

### 任务5：创建Article（资讯文章）模型
**要求**：
- 在api/models.py中创建Article模型：
  - title: 文章标题
  - category: 文章分类（税务规划/产品解读/行业资讯/客户FAQ等）
  - author: 作者（外键关联User或OnlineAgent）
  - content: 文章内容（富文本，TextField）
  - summary: 文章摘要
  - featured_image: 特色图片
  - tags: 标签（JSON数组）
  - view_count: 浏览次数
  - is_featured: 是否精选
  - published_at: 发布时间
  - created_at, updated_at
- 创建序列化器ArticleSerializer
- 运行迁移

===

### 任务6：创建ForumPost（论坛帖子）和ForumReply（论坛回复）模型
**要求**：
- 创建ForumPost模型：
  - title: 帖子标题
  - category: 板块分类（产品咨询/理财规划/税务问题/行业交流等）
  - author: 发帖人（外键关联User）
  - content: 帖子内容
  - tags: 标签（JSON数组）
  - view_count: 浏览次数
  - reply_count: 回复数
  - is_pinned: 是否置顶
  - is_locked: 是否锁定
  - created_at, updated_at
- 创建ForumReply模型：
  - post: 所属帖子（外键关联ForumPost）
  - author: 回复人（外键关联User）
  - content: 回复内容
  - is_expert_reply: 是否为专家回复
  - expert_badge: 专家标识（精算师/理财师等）
  - created_at
- 创建对应的序列化器
- 运行迁移

===

### 任务7：创建CompanyNews（保险公司新闻）模型
**要求**：
- 在api/models.py中创建CompanyNews模型：
  - company: 所属公司（外键关联InsuranceCompany）
  - title: 新闻标题
  - content: 新闻内容
  - news_type: 新闻类型（产品发布/政策变更/业绩公告/企业动态等）
  - source: 新闻来源
  - source_url: 原文链接
  - published_at: 发布时间
  - created_at
- 创建序列化器CompanyNewsSerializer
- 运行迁移

===

### 任务8：创建PremiumCalculator（保费计算器记录）模型
**要求**：
- 在api/models.py中创建PremiumCalculator模型，记录用户的计算历史：
  - user: 用户（外键，可为空）
  - product: 关联产品（外键关联InsuranceProduct）
  - annual_premium: 年缴保费
  - payment_years: 缴费年数
  - insured_age: 投保年龄
  - calculation_result: 计算结果（JSON：每年的现金价值、回报率等）
  - created_at
- 创建序列化器
- 运行迁移

===

## 第二阶段：AI智能推荐系统后端开发

### 任务9：创建AI产品推荐服务（api/ai_recommendation_service.py）
**要求**：
- 创建新文件api/ai_recommendation_service.py
- 实现函数analyze_customer_needs(customer_info)：
  - 输入参数：年收入、年龄、家庭状况、保险需求、预算等
  - 调用Google Gemini API或通义千问API
  - 分析客户的人生阶段和保险需求优先级
  - 返回结构化的需求分析结果
- 实现函数recommend_products(customer_info, needs_analysis)：
  - 基于需求分析结果，从数据库查询suitable_for字段匹配的产品
  - 按照ranking_score和匹配度排序
  - 返回推荐产品列表（包含推荐理由）
- 实现函数calculate_premium_plan(recommended_products, budget)：
  - 根据客户预算，组合推荐产品
  - 计算总保费和保障覆盖率
  - 返回完整的保险规划方案
- 添加错误处理和日志记录

===

### 任务10：创建AI咨询API视图（api/ai_consultation_views.py）
**要求**：
- 创建新文件api/ai_consultation_views.py
- 实现POST /api/ai-consultation/ask/接口：
  - 接收参数：customer_question（客户问题文本）、customer_info（可选的客户基本信息）
  - 调用ai_recommendation_service中的函数
  - 返回AI分析结果和推荐产品
  - 保存咨询记录到数据库（创建ConsultationRecord模型）
- 实现GET /api/ai-consultation/history/接口：
  - 返回当前用户的咨询历史记录
- 在api/urls.py中注册路由
- 编写单元测试（使用mock模拟AI API调用）

===

### 任务11：创建产品对比API（api/product_comparison_views.py）
**要求**：
- 创建新文件api/product_comparison_views.py
- 实现GET /api/products/compare/?ids=1,2,3接口：
  - 接收多个产品ID（最多5个）
  - 从数据库获取产品详细信息
  - 返回标准化的对比数据结构（表格形式）
  - 包含对比维度：保费、回报率、保障期限、缴费期限、特色功能等
- 实现GET /api/products/by-category/{category}/接口：
  - 按类别（储蓄分红型/重疾险等）返回产品列表
  - 支持排序（按评分/按保费/按回报率）
  - 支持筛选（保费范围/保险公司/保障期限等）
- 在api/urls.py中注册路由

===

### 任务12：创建保费计算器API（api/calculator_views.py）
**要求**：
- 创建新文件api/calculator_views.py
- 实现POST /api/calculator/savings/接口（储蓄险计算器）：
  - 接收参数：annual_premium（年缴保费）、payment_years（缴费年数）、insured_age（投保年龄）、product_id
  - 根据产品的guaranteed_return_rate和estimated_return_rate计算每年的现金价值
  - 返回JSON数据：每年的保证现金价值、非保证现金价值、总回报率
  - 保存计算记录到PremiumCalculator表
- 实现POST /api/calculator/critical-illness/接口（重疾险计算器）：
  - 接收参数：coverage_amount（保额）、insured_age、payment_years、product_id
  - 计算年缴保费和保障范围
  - 返回计算结果
- 在api/urls.py中注册路由

===

## 第三阶段：客户案例与内容管理后端开发

### 任务13：创建客户案例API（api/case_views.py）
**要求**：
- 创建新文件api/case_views.py
- 实现GET /api/cases/接口：
  - 返回所有已发布的客户案例
  - 支持按life_stage筛选
  - 支持分页
  - 增加view_count计数
- 实现GET /api/cases/{id}/接口：
  - 返回单个案例的详细信息
  - 包含推荐产品的完整信息
- 实现GET /api/cases/by-stage/{stage}/接口：
  - 按人生阶段返回案例列表
  - 阶段包括：youth（扶幼保障期）、growth（收入成长期）、peak（责任高峰期）、decline（责任递减期）、retirement（退休期）
- 在api/urls.py中注册路由
- 使用Django admin创建10-15个示例案例

===

### 任务14：创建文章资讯API（api/article_views.py）
**要求**：
- 创建新文件api/article_views.py
- 实现GET /api/articles/接口：
  - 返回所有文章列表
  - 支持按category筛选
  - 支持按is_featured筛选精选文章
  - 支持按tags搜索
  - 支持分页
- 实现GET /api/articles/{id}/接口：
  - 返回文章详情
  - 增加view_count计数
- 实现GET /api/articles/featured/接口：
  - 返回首页精选文章（最多6篇）
- 在api/urls.py中注册路由
- 创建15-20篇示例文章（税务、产品解读、FAQ等）

===

### 任务15：创建在线客服API（api/agent_views.py）
**要求**：
- 创建新文件api/agent_views.py
- 实现GET /api/agents/online/接口：
  - 返回所有在线客服列表
  - 按display_order排序
  - 包含头像URL、姓名、职称、专长等信息
- 实现GET /api/agents/{id}/接口：
  - 返回客服详细信息
  - 包含联系方式（WhatsApp、微信、邮箱）
- 在api/urls.py中注册路由
- 在Django admin中创建6-8个客服数据

===

### 任务16：创建保险公司信息API（api/company_views.py）
**要求**：
- 创建新文件api/company_views.py
- 实现GET /api/companies/接口：
  - 返回所有保险公司列表
  - 包含公司基本信息、排名、评分
  - 支持按排名排序
- 实现GET /api/companies/{id}/接口：
  - 返回公司详细信息
  - 包含公司简介、主打产品、历史业绩
- 实现GET /api/companies/{id}/news/接口：
  - 返回公司最新新闻（最多10条）
- 实现GET /api/companies/{id}/products/接口：
  - 返回公司的所有产品列表
- 在api/urls.py中注册路由

===

### 任务17：创建论坛API（api/forum_views.py）
**要求**：
- 创建新文件api/forum_views.py
- 实现GET /api/forum/posts/接口：
  - 返回论坛帖子列表
  - 支持按category筛选
  - 支持按热度（回复数、浏览数）排序
  - 支持分页
- 实现POST /api/forum/posts/接口：
  - 创建新帖子（需要登录）
  - 验证用户权限
- 实现GET /api/forum/posts/{id}/接口：
  - 返回帖子详情和所有回复
  - 增加view_count
- 实现POST /api/forum/posts/{id}/reply/接口：
  - 发表回复（需要登录）
- 在api/urls.py中注册路由

===

## 第四阶段：前端页面开发

### 任务18：创建AI咨询页面（frontend/src/components/AIConsultation.jsx）
**要求**：
- 创建新组件AIConsultation.jsx
- 页面布局：
  - 顶部：标题"AI智能保险顾问"和简介
  - 左侧：客户信息输入表单（年收入、年龄、家庭状况、保险需求、预算）
  - 右侧：对话区域（显示客户问题和AI回答）
  - 底部：问题输入框和发送按钮
- 功能实现：
  - 支持快速填写表单或直接输入问题
  - 调用POST /api/ai-consultation/ask/
  - 显示加载动画（AI思考中）
  - 展示AI推荐结果：需求分析、推荐产品卡片、保费方案
  - 产品卡片可点击查看详情或添加到对比列表
- 样式：使用Tailwind CSS，参考现代聊天界面设计
- 添加到Dashboard菜单，路由为/ai-consultation
- 添加i18n多语言支持（中文/英文）

===

### 任务19：创建客户案例页面（frontend/src/components/ClientCases.jsx）
**要求**：
- 创建新组件ClientCases.jsx
- 页面布局：
  - 顶部：标题"客户案例"和人生阶段分类标签（5个阶段）
  - 主体：案例卡片网格布局（每行3个卡片）
  - 每个卡片包含：案例配图、标题、客户基本信息、年度保费、查看详情按钮
- 实现Tab切换功能，点击不同阶段显示对应案例
- 调用GET /api/cases/by-stage/{stage}/
- 点击"查看详情"打开Modal弹窗：
  - 显示完整的案例描述和解决方案
  - 显示推荐产品列表（带产品详情链接）
- 样式：使用卡片式设计，配色温馨专业
- 添加到Dashboard菜单，路由为/client-cases
- 添加i18n多语言支持

===

### 任务20：创建产品对比页面（frontend/src/components/ProductComparison.jsx）
**要求**：
- 创建新组件ProductComparison.jsx
- 页面布局：
  - 顶部：产品类别选择（储蓄分红型/重疾险/医疗险等）
  - 左侧：产品列表（可勾选，最多5个）
  - 右侧：对比结果表格
- 对比表格包含维度：
  - 保险公司、产品名称
  - 保费范围、缴费期限
  - 保证回报率、预期回报率
  - 保障期限、保额范围
  - 产品特色（列表）
  - 综合评分
- 功能实现：
  - 选择产品后实时更新对比表格
  - 调用GET /api/products/compare/?ids=1,2,3
  - 支持导出对比结果（PDF/图片）
  - 高亮显示最优项（如最高回报率标绿）
- 添加"产品筛选"功能：按保费范围、公司、评分等筛选
- 添加到Dashboard菜单，路由为/product-comparison
- 添加i18n多语言支持

===

### 任务21：创建保费计算器页面（frontend/src/components/PremiumCalculator.jsx）
**要求**：
- 创建新组件PremiumCalculator.jsx
- 页面布局：
  - 顶部：计算器类型切换（储蓄险/重疾险）
  - 左侧：输入表单区域
  - 右侧：计算结果展示区域
- 储蓄险计算器输入：
  - 选择产品（下拉框）
  - 年缴保费（滑块+输入框）
  - 缴费年数（5/10/15/20年）
  - 投保年龄
- 储蓄险计算结果展示：
  - 图表：年度现金价值曲线（使用Chart.js或Recharts）
  - 表格：每年的保证现金价值、非保证现金价值、回报率
  - 关键指标：总缴保费、退休时价值、内部回报率（IRR）
- 重疾险计算器输入：
  - 选择产品
  - 期望保额
  - 投保年龄
  - 缴费年数
- 重疾险计算结果：年缴保费、保障范围
- 功能实现：
  - 输入变化时实时计算
  - 调用POST /api/calculator/savings/或critical-illness/
  - 支持保存计算结果（需登录）
- 添加到Dashboard菜单，路由为/calculator
- 添加i18n多语言支持

===

### 任务22：创建在线客服页面（frontend/src/components/OnlineAgents.jsx）
**要求**：
- 创建新组件OnlineAgents.jsx
- 页面布局：
  - 顶部：标题"专业理财顾问团队"和简介
  - 主体：客服卡片网格布局（每行4个）
  - 每个卡片包含：
    - 头像（圆形，带在线状态指示灯）
    - 姓名和职称
    - 专长领域标签
    - 从业年限和专业资质
    - 联系按钮（WhatsApp/微信/邮件）
- 功能实现：
  - 调用GET /api/agents/online/
  - 点击头像或"立即咨询"按钮打开Modal：
    - 显示客服详细介绍
    - 显示联系方式（二维码/链接）
    - WhatsApp按钮点击跳转到WhatsApp聊天
    - 微信按钮显示微信二维码
    - 邮件按钮打开邮件客户端
- 在线状态实时更新（使用轮询或WebSocket）
- 添加到Dashboard菜单和首页，路由为/agents
- 添加i18n多语言支持

===

### 任务23：创建文章资讯页面（frontend/src/components/Articles.jsx）
**要求**：
- 创建新组件Articles.jsx
- 页面布局：
  - 顶部：标题"保险资讯"和分类标签（税务规划/产品解读/行业资讯/客户FAQ）
  - 左侧：文章列表（每篇显示标题、摘要、发布时间、浏览数）
  - 右侧：热门文章和标签云
- 功能实现：
  - 调用GET /api/articles/
  - 支持按分类筛选
  - 支持按标签搜索
  - 点击文章进入详情页（路由为/articles/{id}）
- 创建ArticleDetail.jsx子组件（文章详情页）：
  - 显示文章完整内容（支持富文本渲染）
  - 显示作者信息
  - 相关文章推荐
- 添加到Dashboard菜单，路由为/articles
- 添加i18n多语言支持

===

### 任务24：创建保险公司页面（frontend/src/components/InsuranceCompanies.jsx）
**要求**：
- 创建新组件InsuranceCompanies.jsx
- 页面布局：
  - 顶部：标题"保险公司排名"和排序选项（按排名/按评分）
  - 主体：公司卡片列表
  - 每个卡片包含：
    - 公司Logo
    - 公司名称和排名
    - 综合评分（星级显示）
    - 主打产品（最多3个）
    - 查看详情按钮
- 功能实现：
  - 调用GET /api/companies/
  - 点击"查看详情"进入公司详情页（路由为/companies/{id}）
- 创建CompanyDetail.jsx子组件（公司详情页）：
  - 公司基本信息（成立时间、总部、业务范围）
  - 公司简介和优势
  - 主打产品列表（可点击查看产品详情）
  - 最新新闻（调用GET /api/companies/{id}/news/）
- 添加到Dashboard菜单，路由为/companies
- 添加i18n多语言支持

===

### 任务25：创建论坛页面（frontend/src/components/Forum.jsx）
**要求**：
- 创建新组件Forum.jsx
- 页面布局：
  - 顶部：标题"专业理财师论坛"和发帖按钮
  - 左侧：板块分类（产品咨询/理财规划/税务问题/行业交流）
  - 主体：帖子列表（显示标题、作者、回复数、浏览数、最后回复时间）
- 功能实现：
  - 调用GET /api/forum/posts/
  - 支持按板块筛选
  - 支持按热度排序
  - 置顶帖子显示在最上方
  - 点击帖子进入详情页（路由为/forum/posts/{id}）
- 创建ForumPostDetail.jsx子组件（帖子详情页）：
  - 显示帖子完整内容
  - 显示所有回复（分页）
  - 专家回复带特殊标识（精算师/理财师徽章）
  - 回复输入框（需登录）
  - 调用POST /api/forum/posts/{id}/reply/发表回复
- 创建NewPost.jsx子组件（发帖页面）：
  - 标题输入框
  - 选择板块
  - 内容编辑器（富文本）
  - 添加标签
  - 调用POST /api/forum/posts/
- 添加到Dashboard菜单，路由为/forum
- 添加i18n多语言支持

===

### 任务26：更新首页（frontend/src/components/HomePage.jsx）
**要求**：
- 重构HomePage.jsx，从OCR上传页面改为综合首页
- 新首页布局：
  - 顶部Banner：主标题"第三方中立保险咨询平台"、副标题、快速咨询按钮
  - 第二部分：核心价值主张（4个图标+文字）
    - "中立第三方，不偏袒任何公司"
    - "最真实的数据，实时更新"
    - "8年专业服务，数千客户案例"
    - "权威产品对比，科学推荐"
  - 第三部分：香港保险反佣报道（滚动展示新闻标题和摘要）
  - 第四部分：主打功能入口（6个大卡片）
    - AI智能咨询
    - 产品对比
    - 保费计算器
    - 客户案例
    - 在线客服
    - 专业论坛
  - 第五部分：精选文章（调用GET /api/articles/featured/）
  - 第六部分：在线客服团队（显示3-4个在线客服头像）
  - 底部：联系方式和友情链接
- 将OCR上传功能移至Dashboard内的独立页面
- 添加平滑滚动动画
- 响应式设计，适配移动端
- 添加i18n多语言支持

===

### 任务27：更新Dashboard导航菜单（frontend/src/components/Dashboard.jsx）
**要求**：
- 在Dashboard.jsx中更新左侧导航菜单，添加新页面入口：
  - AI智能咨询（/ai-consultation）
  - 客户案例（/client-cases）
  - 产品对比（/product-comparison）
  - 保费计算器（/calculator）
  - 在线客服（/agents）
  - 文章资讯（/articles）
  - 保险公司（/companies）
  - 专业论坛（/forum）
  - 保留现有的：计划书分析、文档管理、海报分析
- 将OCR上传功能作为"上传计划书"入口
- 添加菜单图标（使用Heroicons或Lucide React）
- 实现菜单项的active状态高亮
- 添加折叠/展开功能（移动端）
- 添加i18n多语言支持

===

### 任务28：创建产品详情页（frontend/src/components/ProductDetail.jsx）
**要求**：
- 创建新组件ProductDetail.jsx（路由为/products/{id}）
- 页面布局：
  - 顶部：产品名称、保险公司Logo、综合评分
  - 主体分Tab展示：
    - Tab1 产品概览：保费范围、缴费期限、保障期限、回报率
    - Tab2 产品特色：key_features列表展示
    - Tab3 适合人群：suitable_for信息展示
    - Tab4 保费试算：嵌入保费计算器组件
    - Tab5 同类产品对比：推荐3-5个同类产品
  - 右侧：快速咨询栏（显示推荐客服和咨询按钮）
- 功能实现：
  - 调用GET /api/products/{id}/
  - 支持添加到对比列表
  - 支持分享链接
- 添加i18n多语言支持

===

## 第五阶段：数据准备与内容填充

### 任务29：准备香港保险反佣报道内容
**要求**：
- 在Django admin中创建Article记录，分类为"行业资讯"
- 准备3-5篇关于香港保险反佣的文章：
  - 标题示例："香港保险反佣制度解读"、"第三方平台如何确保中立性"
  - 内容要突出：合法合规、客户利益优先、透明化服务
  - 添加新闻来源和发布日期
  - 设置为精选文章（is_featured=True）
- 在首页展示这些文章的标题和摘要

===

### 任务30：填充保险产品数据
**要求**：
- 从参考网站和实际产品资料收集数据
- 在Django admin中补充insurance_products表的新字段：
  - 储蓄分红型产品（至少10个）：
    - 友邦、保诚、宏利、富通、安盛等公司的主打产品
    - 填写guaranteed_return_rate、estimated_return_rate
    - 填写key_features（如灵活提取、多重货币、保证终身等）
    - 填写suitable_for（如高收入家庭、退休规划、子女教育等）
  - 重疾险产品（至少8个）：
    - 填写保障范围、多重赔付次数、早期疾病赔付比例等
  - 为每个产品设置ranking_score（综合评分）
- 确保数据真实准确，引用官方资料

===

### 任务31：创建客户案例数据
**要求**：
- 使用Django admin创建15-20个客户案例
- 每个人生阶段至少3个案例：
  - 扶幼保障期（25-35岁，新婚或初为父母）
    - 案例1：30岁工程师，年收入60万台币，1个新生儿
    - 案例2：28岁教师夫妇，年收入100万台币，计划生育
  - 收入成长期（35-45岁，事业上升期）
    - 案例1：40岁企业主管，年收入150万台币，2个子女
    - 案例2：38岁创业者，年收入200万台币，单身
  - 责任高峰期（45-55岁，家庭责任最重）
    - 案例1：50岁企业高管，年收入300万台币，2个子女读大学
    - 案例2：48岁医生，年收入250万台币，赡养父母
  - 责任递减期（55-65岁，子女独立）
    - 案例1：60岁退休教授，关注退休金和遗产规划
    - 案例2：58岁企业家，考虑财富传承
  - 退休期（65岁以上）
    - 案例1：70岁退休人士，关注医疗保障和长期护理
- 每个案例包含：
  - 案例描述（300-500字）
  - 推荐产品（2-4个）
  - 解决方案说明（200-300字）
  - 配图（可使用AI生成或stock photo）

===

### 任务32：创建保险公司资料和新闻
**要求**：
- 在Django admin中完善insurance_companies表
- 为每个公司添加详细信息：
  - 公司简介（成立时间、总部、规模）
  - 排名和评分（根据市场份额、理赔服务、产品创新等）
  - 主打产品列表
- 为每个公司创建5-10条新闻记录（CompanyNews）：
  - 新产品发布
  - 业绩公告
  - 企业社会责任活动
  - 服务升级
- 确保新闻真实，引用官方来源

===

### 任务33：创建示例文章
**要求**：
- 在Django admin中创建25-30篇文章
- 分类覆盖：
  - 税务规划（5-8篇）：如"香港保险的税务优势"、"内地居民投保香港保险的税务问题"
  - 产品解读（8-10篇）：如"储蓄险vs投资险"、"重疾险如何选择保额"
  - 行业资讯（5-8篇）：包括反佣报道、监管政策、市场趋势
  - 客户FAQ（5-8篇）：如"理赔流程详解"、"保单如何变更受益人"
- 每篇文章1000-2000字
- 添加相关标签（如：储蓄险、税务、理赔、重疾险等）
- 部分文章设置为精选（首页展示）

===

### 任务34：创建客服和专家账号
**要求**：
- 在Django admin中创建8-10个OnlineAgent记录
- 角色分配：
  - 2个资深理财顾问（15年以上经验，全产品线）
  - 2个精算师（专长：产品设计、回报率分析）
  - 2个税务规划师（专长：税务筹划、财富传承）
  - 2个产品专员（专长：储蓄险/重疾险）
- 为每个客服准备：
  - 专业头像（商务照）
  - 详细介绍（200字）
  - 联系方式（WhatsApp、微信、邮箱）
  - 专业资质（CFP、CFA、精算师等）
- 设置部分客服为在线状态

===

### 任务35：创建论坛初始内容
**要求**：
- 创建5-10个示例帖子（ForumPost）
- 帖子类型：
  - 产品咨询类（2-3个）：如"50岁还能买储蓄险吗？"
  - 理财规划类（2-3个）：如"年收入100万如何配置保险？"
  - 税务问题类（1-2个）：如"香港保单遗产税问题"
  - 行业交流类（1-2个）：如"2024年储蓄险市场分析"
- 为每个帖子创建3-5条回复（ForumReply）
- 部分回复设置为专家回复（is_expert_reply=True）
- 添加专家徽章（精算师/理财师）

===

## 第六阶段：集成测试与优化

### 任务36：前端路由配置和导航测试
**要求**：
- 在frontend/src/App.jsx中配置所有新页面的路由
- 确保所有路由路径正确：
  - /ai-consultation
  - /client-cases
  - /product-comparison
  - /calculator
  - /agents
  - /articles
  - /articles/:id
  - /companies
  - /companies/:id
  - /forum
  - /forum/posts/:id
  - /products/:id
- 测试所有导航链接是否正常工作
- 测试浏览器前进/后退按钮
- 测试404页面
- 测试受保护路由（需登录才能访问的页面）

===

### 任务37：API接口联调测试
**要求**：
- 使用Postman或Thunder Client测试所有新增API接口
- 测试清单：
  - POST /api/ai-consultation/ask/（测试不同的客户信息输入）
  - GET /api/products/compare/?ids=1,2,3（测试不同产品组合）
  - POST /api/calculator/savings/（测试不同参数）
  - GET /api/cases/by-stage/youth/（测试5个阶段）
  - GET /api/articles/（测试筛选和分页）
  - GET /api/agents/online/
  - GET /api/companies/{id}/news/
  - POST /api/forum/posts/（测试发帖）
  - POST /api/forum/posts/{id}/reply/（测试回复）
- 验证返回数据格式正确
- 验证错误处理（如无效ID、缺少参数）
- 验证权限控制（如未登录不能发帖）

===

### 任务38：用户体验优化
**要求**：
- 所有页面添加Loading状态（骨架屏或Spinner）
- 所有API调用添加错误处理和错误提示
- 表单添加输入验证和错误提示
- 长列表添加虚拟滚动或分页加载
- 图片添加懒加载（LazyLoad）
- 添加页面过渡动画（使用Framer Motion或CSS transitions）
- 优化移动端体验：
  - 响应式布局
  - 触摸手势支持
  - 移动端菜单（汉堡菜单）
- 添加返回顶部按钮（页面滚动时显示）

===

### 任务39：SEO优化和Meta标签
**要求**：
- 为每个页面添加合适的标题和描述
- 在frontend/index.html中配置基础Meta标签：
  - og:title, og:description, og:image（用于社交分享）
  - keywords（保险、香港保险、储蓄险、重疾险等）
- 使用React Helmet或类似库动态更新Meta标签
- 添加Sitemap.xml（列出所有页面URL）
- 配置robots.txt
- 确保所有图片有alt属性
- 使用语义化HTML标签（header, nav, main, article, aside, footer）


## 注意事项

1. **数据真实性**：所有产品数据、回报率、保费等信息必须引用官方资料，确保准确性
2. **中立性声明**：在多处强调第三方中立立场，不偏袒任何公司
3. **法律合规**：确保所有内容符合香港保险监管要求，不涉及未经授权的产品推广
4. **用户隐私**：咨询记录、论坛帖子等用户数据要妥善保护
5. **性能监控**：上线后持续监控性能和错误，及时优化
6. **内容更新**：保险产品和政策经常变化，需要定期更新数据
