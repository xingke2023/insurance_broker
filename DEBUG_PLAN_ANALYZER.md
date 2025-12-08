# 保单分析器调试指南

## 问题描述

内容通过API获取到了，但没有显示在页面上。

## 已添加的调试功能

### 1. 控制台日志

打开浏览器开发者工具（F12），在Console标签中查看以下日志：

#### 文件结构获取
```
获取文件结构，目录: /path/to/result
文件结构API响应: {status: "success", children: [...]}
原始文件列表: [...]
过滤后的文件列表: [...]
找到的第一个mmd文件: {name: "xxx.mmd", path: "..."}
```

#### 文件内容加载
```
正在加载文件: xxx.mmd /path/to/xxx.mmd
文件内容API响应: {status: "success", content: "..."}
设置文件内容，长度: 1234
```

### 2. 页面调试信息

解析完成后，如果内容没有显示，会在预览区域显示：
- 加载动画
- `selectedFile: ✓/✗` - 是否选中了文件
- `fileContent length: 0` - 内容长度

## 调试步骤

### 步骤1: 打开开发者工具

1. 访问 http://localhost:5173/
2. 点击"保单智能分析系统"
3. 按 F12 打开开发者工具
4. 切换到 Console 标签

### 步骤2: 上传文件并解析

1. 上传PDF文件
2. 点击"开始分析"
3. 等待解析完成

### 步骤3: 查看控制台日志

检查以下信息：

**文件结构获取阶段**
- ✅ 是否输出了"获取文件结构，目录: xxx"
- ✅ 文件结构API响应是否成功
- ✅ 原始文件列表中是否有.mmd文件
- ✅ 过滤后是否保留了非det的mmd文件
- ✅ 是否找到了第一个mmd文件

**文件内容加载阶段**
- ✅ 是否输出了"正在加载文件: xxx.mmd"
- ✅ 文件内容API响应是否成功
- ✅ 内容长度是否大于0

### 步骤4: 检查页面状态

在页面的预览区域查看：
- 是否显示"📄 解析结果"标题
- 如果没有内容，查看调试信息
  - `selectedFile: ✓` - 文件已选中
  - `fileContent length: >0` - 内容已加载

## 常见问题排查

### 问题1: 没有找到.mmd文件

**症状**: 控制台显示"没有找到.mmd文件"

**原因**:
- 文件名可能不是.mmd结尾
- 所有mmd文件都是*det.mmd格式被过滤了

**解决**:
检查"原始文件列表"日志，确认实际的文件名

### 问题2: API返回失败

**症状**: 控制台显示"API返回失败状态"

**原因**: 远程API返回错误

**解决**:
1. 检查网络连接
2. 确认远程API服务器是否正常
3. 测试API: `curl http://101.36.226.245:8002/api/file/content?path=xxx`

### 问题3: 内容长度为0

**症状**: `fileContent length: 0`

**原因**: API返回的content字段为空

**解决**:
查看"文件内容API响应"日志中的data.content字段

### 问题4: selectedFile为✗

**症状**: `selectedFile: ✗`

**原因**: handleFileClick没有成功执行

**解决**:
检查"找到的第一个mmd文件"是否有值

## 修改内容总结

### 1. 添加详细日志
```javascript
console.log('获取文件结构，目录:', dir);
console.log('文件结构API响应:', data);
console.log('原始文件列表:', children);
console.log('过滤后的文件列表:', filteredChildren);
console.log('找到的第一个mmd文件:', firstMmdFile);
console.log('正在加载文件:', file.name, file.path);
console.log('文件内容API响应:', data);
console.log('设置文件内容，长度:', content.length);
```

### 2. 改进显示逻辑
```javascript
// 之前：需要三个条件都满足
{parseCompleted && selectedFile && fileContent && (...)}

// 现在：只要解析完成就显示区域
{parseCompleted && (...)}

// 内容区域内部判断
{fileContent ? (
  <pre>{fileContent}</pre>
) : (
  <div>正在加载...</div>
)}
```

### 3. 添加调试信息显示
- 显示selectedFile状态
- 显示fileContent长度
- 显示加载动画

## 测试清单

使用以下清单验证功能：

- [ ] 打开F12控制台
- [ ] 上传文件
- [ ] 点击"开始分析"
- [ ] 等待解析完成
- [ ] 检查控制台是否有所有日志输出
- [ ] 检查"文件结构API响应"是否成功
- [ ] 检查是否找到.mmd文件
- [ ] 检查"文件内容API响应"是否成功
- [ ] 检查内容长度是否>0
- [ ] 检查页面是否显示内容

## API响应格式参考

### /api/folder 响应
```json
{
  "status": "success",
  "children": [
    {
      "name": "result.mmd",
      "type": "file",
      "path": "/full/path/to/result.mmd",
      "fileType": "markdown"
    }
  ]
}
```

### /api/file/content 响应
```json
{
  "status": "success",
  "content": "mmd文件的完整内容..."
}
```

## 下一步

如果问题仍然存在，请：

1. 截图控制台所有日志
2. 截图页面显示状态
3. 提供具体的API响应内容
4. 检查是否有JavaScript错误

---

**重要**: 所有调试日志都会在浏览器控制台输出，请确保在测试时打开控制台！
