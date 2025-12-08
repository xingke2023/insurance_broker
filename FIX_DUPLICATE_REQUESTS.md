# 修复重复请求问题

## 问题描述

在计划书智能分析工具（PlanAnalyzer.jsx）中，当解析进度达到100%后，会出现以下API被重复调用两次的问题：

1. `GET /api/folder?path={result_dir}` - 调用2次
2. `GET /api/file/content?path={file_path}` - 调用2次

## 问题原因

WebSocket 后端在任务完成时可能发送多次进度为 100% 的消息，例如：
- 第1次: `{ progress: 100, state: 'running' }`
- 第2次: `{ progress: 100, state: 'finished' }`

前端代码没有防重复机制，每次收到 100% 进度消息时都会触发 `fetchTaskResult()`，导致后续的所有API调用都重复执行。

## 修复方案

采用**五层防护机制**，确保不会重复处理：

### 1. WebSocket 层防护（第一道防线）

在 `connectWebSocket()` 函数中添加 `hasCompleted` 标志位：

```javascript
const connectWebSocket = (currentTaskId) => {
    const ws = new WebSocket(wsUrl);
    let hasCompleted = false; // ← 添加标志位

    ws.onmessage = (event) => {
        const progressPercent = data.progress || 0;

        // 如果完成且未处理过，获取结果
        if (progressPercent >= 100 && !hasCompleted) {
            hasCompleted = true; // ← 防止重复
            fetchTaskResult(currentTaskId);
            ws.close();
        }
    };
};
```

**位置**: `PlanAnalyzer.jsx:120`

### 2. Task Result 层防护（第二道防线）

添加 `completedTasks` 状态，使用 Set 追踪已处理的任务：

```javascript
// 添加状态
const [completedTasks, setCompletedTasks] = useState(new Set());

// 修改 fetchTaskResult
const fetchTaskResult = async (currentTaskId) => {
    // 防止重复处理同一个任务
    if (completedTasks.has(currentTaskId)) {
        console.log('任务已处理过，跳过重复调用:', currentTaskId);
        return;
    }

    // 标记任务为正在处理
    setCompletedTasks(prev => new Set(prev).add(currentTaskId));

    try {
        // ... 原有逻辑
    } catch (error) {
        // 失败时从集合中移除，允许重试
        setCompletedTasks(prev => {
            const next = new Set(prev);
            next.delete(currentTaskId);
            return next;
        });
    }
};
```

**位置**: `PlanAnalyzer.jsx:28, 193-241`

### 3. File Structure 层防护（第三道防线）

使用 `useRef` 追踪正在获取的目录，防止同步重复调用：

```javascript
// 添加 ref
const fetchingDirsRef = useRef(new Set());

const fetchFileStructure = async (dir) => {
    // 防止重复获取同一个目录（使用 ref 追踪）
    if (fetchingDirsRef.current.has(dir)) {
        console.log('⚠️ 目录正在获取中，跳过重复请求:', dir);
        return;
    }

    // 标记开始获取
    fetchingDirsRef.current.add(dir);

    try {
        // ... 原有逻辑
    } finally {
        // 完成后移除标记（延迟移除，确保同步调用也能拦截）
        setTimeout(() => {
            fetchingDirsRef.current.delete(dir);
        }, 100);
    }
};
```

**位置**: `PlanAnalyzer.jsx:29, 359-412`

**为什么使用 useRef 而不是 useState？**
- `useState` 状态更新是异步的，无法拦截同步的重复调用
- `useRef` 的 `.current` 是同步更新的，能立即拦截重复请求

### 4. File Content 层防护（第四道防线）

使用 `useRef` 追踪正在获取的文件：

```javascript
// 添加 ref
const fetchingFilesRef = useRef(new Set());

const handleFileClick = async (file) => {
    const filePath = file.path;

    // 防止重复获取同一个文件
    if (fetchingFilesRef.current.has(filePath)) {
        console.log('⚠️ 文件正在加载中，跳过重复请求:', filePath);
        return;
    }

    // 标记开始获取
    fetchingFilesRef.current.add(filePath);

    try {
        // ... 原有逻辑
    } finally {
        setTimeout(() => {
            fetchingFilesRef.current.delete(filePath);
        }, 100);
    }
};
```

**位置**: `PlanAnalyzer.jsx:30, 415-463`

## 修改文件

- `frontend/src/components/PlanAnalyzer.jsx`

## 修改内容汇总

### 新增导入
```javascript
import { useState, useEffect, useRef } from 'react';  // 添加 useRef
```

### 新增状态变量和 Ref
```javascript
const [completedTasks, setCompletedTasks] = useState(new Set());
const fetchingDirsRef = useRef(new Set());   // 追踪正在获取的目录
const fetchingFilesRef = useRef(new Set());  // 追踪正在获取的文件
```

### 修改的函数
1. `connectWebSocket()` - 添加 `hasCompleted` 局部变量
2. `fetchTaskResult()` - 添加任务去重逻辑（useState）
3. `fetchFileStructure()` - 添加目录去重逻辑（useRef）
4. `handleFileClick()` - 添加文件去重逻辑（useRef）

## 测试验证

构建测试通过：
```bash
cd /var/www/harry-insurance/frontend
npm run build
# ✓ built in 3.74s
```

## 预期效果

修复后，当解析进度达到100%时：
- ✅ WebSocket 即使发送多次100%消息，也只会处理一次
- ✅ `/api/result/{task_id}` 只调用 **1次**（之前可能2次）
- ✅ `/api/folder?path=xxx` 只调用 **1次**（之前2次） ⭐ 主要修复
- ✅ `/api/file/content?path=xxx` 只调用 **1次**（之前2次） ⭐ 主要修复
- ✅ 避免了不必要的网络请求和服务器负载
- ✅ 同步的重复调用也能被拦截（useRef 同步更新）

## 注意事项

1. **不影响功能**：修改只是添加防重复检查，不改变原有业务逻辑
2. **失败重试**：如果任务处理失败，会从 `completedTasks` 中移除，允许重试
3. **内存管理**：`completedTasks` 使用 Set 存储，在组件生命周期内保持，不会无限增长（组件卸载时自动清理）
4. **useRef vs useState**：
   - `fetchingDirsRef` 和 `fetchingFilesRef` 使用 `useRef` 而非 `useState`
   - 原因：`useRef.current` 是**同步更新**的，能立即拦截重复调用
   - `useState` 的状态更新是**异步**的，无法拦截几乎同时发生的重复调用
5. **延迟清除**：使用 100ms 延迟清除标记，确保异步调用也能被拦截

## 部署建议

1. 备份原文件：
   ```bash
   cp frontend/src/components/PlanAnalyzer.jsx frontend/src/components/PlanAnalyzer.jsx.backup
   ```

2. 重新构建前端：
   ```bash
   cd frontend
   npm run build
   ```

3. 重启前端服务（如果已在运行）

4. 测试完整流程：
   - 上传文件
   - 点击"开始分析"
   - 观察浏览器 Network 面板
   - 确认 `/api/folder` 和 `/api/file/content` 只调用一次

## 修改日期

2025-01-06
