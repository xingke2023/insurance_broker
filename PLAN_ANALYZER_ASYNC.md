# 计划书智能分析工具 - 异步任务功能说明

## 📋 功能概述

计划书智能分析工具现已支持完整的异步任务处理功能，用户可以在上传文件并开始分析后立即返回首页，系统会在后台继续处理任务。

## ✨ 核心功能

### 1. 异步任务处理
- ✅ 文件上传后自动开始OCR解析
- ✅ 任务在后台运行，不阻塞用户操作
- ✅ 用户可以随时返回或继续其他操作

### 2. 实时进度推送
- ✅ 使用WebSocket实时推送任务进度（0-100%）
- ✅ 进度条动态更新
- ✅ 分步显示任务状态（初始化→处理中→获取结果→完成）

### 3. 任务持久化
- ✅ 任务信息保存到localStorage
- ✅ 页面刷新后自动恢复任务状态
- ✅ 支持多个任务并行处理

### 4. 后台任务管理
- ✅ 任务列表弹窗，显示所有后台任务
- ✅ 实时显示每个任务的进度和状态
- ✅ 完成的任务可直接查看结果
- ✅ 支持删除任务记录

## 🔧 技术实现

### WebSocket连接
```javascript
// WebSocket URL格式
ws://domain.com/api-plan/ws/progress/{task_id}

// 接收消息格式
{
  "task_id": "abc123",
  "progress": 60  // 0-100
}
```

### 任务状态流转
```
running (处理中) → finished (完成) → error (失败)
```

### 本地存储结构
```javascript
{
  task_id: "unique_task_id",
  file_name: "document.pdf",
  state: "running|finished|error",
  progress: 0-100,
  result_dir: "/path/to/results",
  created_at: "2025-01-01T00:00:00.000Z",
  completed_at: "2025-01-01T00:05:00.000Z"
}
```

## 📱 用户使用流程

### 场景1: 标准流程
1. 上传PDF/图片文件
2. 点击"开始分析"
3. 系统显示进度条和实时进度
4. 2秒后弹出提示，询问是否返回首页
5. 选择"确定"返回首页，任务继续后台运行
6. 点击右上角"后台任务"按钮查看进度
7. 任务完成后点击"查看结果"

### 场景2: 持续等待
1. 上传文件后开始分析
2. 弹出提示时选择"取消"
3. 停留在当前页面等待任务完成
4. 实时看到进度更新
5. 完成后自动显示解析结果

### 场景3: 页面刷新恢复
1. 任务运行过程中刷新页面
2. 系统自动从localStorage恢复任务
3. 重新连接WebSocket继续监听
4. 进度继续更新

## 🎨 UI组件说明

### 1. 后台任务按钮
- 位置：页面右上角
- 显示条件：有后台任务时显示
- 红色徽章：显示运行中的任务数量

### 2. 进度显示
- **百分比进度条**：0-100%渐变色显示
- **步骤指示器**：4个步骤的可视化进度
- **进度消息**：文字描述当前状态

### 3. 任务列表弹窗
- **任务卡片**：显示文件名、任务ID、状态
- **进度条**：运行中的任务显示进度条
- **操作按钮**：查看结果、删除任务

## 🔌 后端接口依赖

### 必需接口
1. `POST /api-plan/api/upload` - 文件上传
2. `POST /api-plan/api/start` - 启动OCR任务
3. `WebSocket /api-plan/ws/progress/{task_id}` - 实时进度推送
4. `GET /api-plan/api/progress/{task_id}` - 查询任务进度
5. `GET /api-plan/api/result/{task_id}` - 获取任务结果
6. `GET /api-plan/api/folder?path=xxx` - 获取结果文件列表
7. `GET /api-plan/api/file/content?path=xxx` - 获取文件内容

## 🐛 常见问题

### Q1: WebSocket连接失败
**原因**: 反向代理配置未正确支持WebSocket
**解决**: 检查Nginx配置，确保包含以下配置：
```nginx
location /api-plan/ws/ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### Q2: 页面刷新后任务丢失
**原因**: localStorage未正确保存或被清除
**解决**:
- 检查浏览器localStorage是否启用
- 确保没有隐私模式
- 检查localStorage容量限制

### Q3: 进度更新不及时
**原因**: WebSocket消息推送延迟
**解决**:
- 检查网络连接
- 后端可能正在处理大文件
- 等待或使用HTTP轮询作为备选

## 📊 性能优化

1. **WebSocket管理**
   - 任务完成后自动关闭连接
   - 组件卸载时清理连接
   - 避免重复连接

2. **本地存储优化**
   - 定期清理已完成的旧任务
   - 限制任务历史记录数量
   - 使用增量更新而非全量写入

3. **并发控制**
   - 建议同时运行任务不超过5个
   - 后端有并发限制（MAX_CONCURRENCY）

## 🚀 未来改进方向

- [ ] 添加任务完成的桌面通知
- [ ] 支持任务优先级调整
- [ ] 添加任务取消功能
- [ ] 任务失败自动重试
- [ ] 批量任务管理
- [ ] 导出任务报告

## 📝 更新日志

### v1.0.0 (2025-01-06)
- ✅ 实现WebSocket实时进度推送
- ✅ 添加任务持久化到localStorage
- ✅ 创建后台任务管理界面
- ✅ 支持任务恢复和查看
- ✅ 优化用户体验，支持后台运行

---

## 📞 技术支持

如有问题，请检查：
1. 浏览器控制台是否有错误
2. 网络面板中WebSocket连接状态
3. localStorage中的任务数据

调试提示：
```javascript
// 查看本地任务
console.log(JSON.parse(localStorage.getItem('backgroundTasks')));

// 清除所有任务
localStorage.removeItem('backgroundTasks');
```
