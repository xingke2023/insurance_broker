# Markdown 文件读取流程详解

## 📋 完整流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. 用户上传文件                               │
│  FileUploader → handleFileChange() → POST /api/upload          │
│  返回: { status: 'success', file_path: '/path/to/file.pdf' }   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 2. 用户点击"开始解析"                             │
│  PromptInput → handleStartParsing() → POST /api/start          │
│  请求体: { file_path: '...', prompt: '<image>...' }            │
│  返回: { status: 'running', task_id: 'task123' }               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   3. 前端轮询任务状态                             │
│  每 2 秒请求: GET /api/progress/{task_id}                       │
│  返回: { status: 'success', state: 'running/finished' }        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    4. 任务完成，获取结果                           │
│  GET /api/result/{task_id}                                      │
│  返回: {                                                         │
│    status: 'success',                                           │
│    state: 'finished',                                           │
│    result_dir: '/root/deepseek_output/task123'                 │
│  }                                                              │
│  → setResultDir(result_dir)                                     │
│  → setParseCompleted(true)                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  5. 文件浏览器获取文件结构                         │
│  FileExplorer → fetchFolderStructure()                          │
│  GET /api/folder?path=/root/deepseek_output/task123            │
│  返回: {                                                         │
│    status: 'success',                                           │
│    name: 'task123',                                             │
│    type: 'folder',                                              │
│    children: [                                                  │
│      {                                                          │
│        name: 'output.md',                                       │
│        type: 'file',                                            │
│        path: '/root/deepseek_output/task123/output.md'         │
│      },                                                         │
│      {                                                          │
│        name: 'images',                                          │
│        type: 'folder',                                          │
│        children: [...]                                          │
│      }                                                          │
│    ]                                                            │
│  }                                                              │
│  → 渲染文件树                                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               6. 用户点击 Markdown 文件                           │
│  FileExplorer → handleFileClick(node)                           │
│  触发条件: node.fileType === 'markdown'                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 7. 读取 Markdown 文件内容                         │
│  GET /api/file/content?path=/root/.../output.md                │
│  返回: {                                                         │
│    status: 'success',                                           │
│    content: '# 标题\n\n![](images/pic.png)\n\n<|ref|>...'     │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                8. 清理 DeepSeek OCR 标签                         │
│  cleanContent = data.content                                    │
│    .replace(/<\|ref\|>.*?<\/ref\|>/g, '')  // 移除引用标签      │
│    .replace(/<\|det\|>.*?<\/det\|>/g, '')  // 移除坐标标签      │
│    .replace(/<\|ref\|>/g, '')              // 移除孤立标签      │
│    .replace(/<\/ref\|>/g, '')                                  │
│    .replace(/<\|det\|>/g, '')                                  │
│    .replace(/<\/det\|>/g, '')                                  │
│    .replace(/\n{3,}/g, '\n\n')             // 清理多余换行      │
│    .trim();                                                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                9. 修复 Markdown 图片路径                          │
│  cleanContent = fixMarkdownImages(cleanContent, resultDir)      │
│                                                                 │
│  处理逻辑:                                                       │
│  原始: ![示例](images/pic.png)                                  │
│  ↓                                                              │
│  拼接完整路径:                                                   │
│    absPath = '/root/deepseek_output/task123/images/pic.png'    │
│  ↓                                                              │
│  URL 编码:                                                      │
│    encodedPath = '%2Froot%2Fdeepseek_output%2F...'            │
│  ↓                                                              │
│  生成新链接:                                                     │
│    http://127.0.0.1:8002/api/file/view?path=encodedPath        │
│  ↓                                                              │
│  替换: ![示例](http://127.0.0.1:8002/api/file/view?path=...)   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              10. 传递给 FilePreview 组件渲染                      │
│  onFileSelect({                                                 │
│    ...node,                                                     │
│    content: cleanContent  // 已清理和修复的 Markdown            │
│  })                                                             │
│  ↓                                                              │
│  FilePreview 接收到 file.content                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              11. ReactMarkdown 渲染 Markdown                     │
│  FilePreview → ReactMarkdown                                    │
│  - remarkPlugins: [remarkGfm]  // 支持表格、删除线等            │
│  - rehypePlugins: [rehypeRaw]  // 支持 HTML                    │
│  - components: 自定义渲染器                                      │
│    • img: 渲染图片标签                                           │
│    • code: 语法高亮                                              │
│    • table: 表格样式                                             │
│    • a: 链接样式                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 12. 浏览器请求图片资源                            │
│  浏览器解析 <img src="http://127.0.0.1:8002/...">              │
│  ↓                                                              │
│  GET /api/file/view?path=/root/.../images/pic.png              │
│  ↓                                                              │
│  后端返回二进制图片数据 (Content-Type: image/png)               │
│  ↓                                                              │
│  浏览器显示图片 ✅                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 详细代码流程

### 步骤 1-4：文件上传与解析
**位置**: `/App.tsx`

```typescript
// 1. 上传文件
const handleFileChange = async (file: File | null) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });
  
  const data = await response.json();
  setUploadedFilePath(data.file_path); // 保存文件路径
};

// 2. 开始解析
const handleStartParsing = async () => {
  const response = await fetch(`${API_BASE_URL}/api/start`, {
    method: 'POST',
    body: JSON.stringify({
      file_path: uploadedFilePath,
      prompt: prompt,
    }),
  });
  
  const data = await response.json();
  setTaskId(data.task_id); // 保存任务 ID
  
  // 3. 轮询任务状态
  const pollInterval = setInterval(async () => {
    const progressRes = await fetch(`${API_BASE_URL}/api/progress/${data.task_id}`);
    const progressData = await progressRes.json();
    
    if (progressData.state === 'finished') {
      clearInterval(pollInterval);
      
      // 4. 获取结果目录
      const resultRes = await fetch(`${API_BASE_URL}/api/result/${data.task_id}`);
      const resultData = await resultRes.json();
      
      setResultDir(resultData.result_dir); // 保存结果目录路径
      setParseCompleted(true); // 触发文件浏览器
    }
  }, 2000);
};
```

---

### 步骤 5：获取文件结构
**位置**: `/components/FileExplorer.tsx`

```typescript
const fetchFolderStructure = async () => {
  // 请求文件夹结构
  const response = await fetch(
    `${API_BASE_URL}/api/folder?path=${encodeURIComponent(resultDir)}`
  );
  const data = await response.json();
  
  // 转换后端数据为前端格式
  const convertNode = (node: any): FileNode => {
    // 识别文件类型
    const ext = node.name.split('.').pop()?.toLowerCase();
    let fileType: 'markdown' | 'image' | 'pdf' | undefined;
    
    if (ext === 'md' || ext === 'mmd' || ext === 'txt') {
      fileType = 'markdown'; // 标记为 Markdown 文件
    } else if (ext === 'png' || ext === 'jpg' || ext === 'jpeg') {
      fileType = 'image';
    } else if (ext === 'pdf') {
      fileType = 'pdf';
    }
    
    return {
      name: node.name,
      type: node.type,
      fileType,
      path: node.path, // 完整的服务器路径
      resultDir: resultDir, // 结果目录
    };
  };
  
  // 渲染文件树
  setFileStructure(data.children.map(convertNode));
};
```

---

### 步骤 6-9：读取并处理 Markdown
**位置**: `/components/FileExplorer.tsx`

```typescript
const handleFileClick = async (node: FileNode) => {
  // 6. 用户点击 Markdown 文件
  if (node.fileType === 'markdown') {
    
    // 7. 请求文件内容
    const response = await fetch(
      `${API_BASE_URL}/api/file/content?path=${encodeURIComponent(node.path)}`
    );
    const data = await response.json();
    let cleanContent = data.content;
    
    // 8. 清理 OCR 标签
    cleanContent = cleanContent
      .replace(/<\|ref\|>.*?<\/ref\|>/g, '')
      .replace(/<\|det\|>.*?<\/det\|>/g, '')
      .replace(/<\|ref\|>/g, '')
      .replace(/<\/ref\|>/g, '')
      .replace(/<\|det\|>/g, '')
      .replace(/<\/det\|>/g, '')
      .replace(/\n{3,}/g, '\n\n')
      .trim();
    
    // 9. 修复图片路径
    cleanContent = fixMarkdownImages(cleanContent, node.resultDir || '');
    
    // 10. 传递给 FilePreview
    onFileSelect({
      ...node,
      content: cleanContent,
    });
  }
};

// 图片路径修复函数
function fixMarkdownImages(mdContent: string, resultDir: string): string {
  return mdContent.replace(
    /!\[(.*?)\]\((.*?)\)/g, // 匹配 ![alt](path)
    (match, altText, relativePath) => {
      // 跳过外部链接
      if (relativePath.startsWith('http://') || relativePath.startsWith('https://')) {
        return match;
      }
      
      // 拼接完整路径
      const absPath = `${resultDir}/${relativePath}`.replace(/\/+/g, '/');
      // URL 编码
      const encodedPath = encodeURIComponent(absPath);
      // 返回新的图片链接
      return `![${altText}](${API_BASE_URL}/api/file/view?path=${encodedPath})`;
    }
  );
}
```

**示例转换**：
```javascript
// 输入
resultDir = '/root/deepseek_output/task123'
mdContent = '![示例](images/pic.png)'

// 处理
absPath = '/root/deepseek_output/task123/images/pic.png'
encodedPath = '%2Froot%2Fdeepseek_output%2Ftask123%2Fimages%2Fpic.png'

// 输出
'![示例](http://127.0.0.1:8002/api/file/view?path=%2Froot%2F...)'
```

---

### 步骤 10-11：渲染 Markdown
**位置**: `/components/FilePreview.tsx`

```typescript
export function FilePreview({ file }: FilePreviewProps) {
  return (
    <div>
      {file.fileType === 'markdown' && file.content && (
        <ReactMarkdown
          remarkPlugins={[remarkGfm]} // 支持 GitHub 风格 Markdown
          rehypePlugins={[rehypeRaw]} // 支持 HTML 标签
          components={{
            // 自定义图片渲染器
            img: ({ node, ...props }) => (
              <img
                {...props}
                className="max-w-full h-auto rounded-lg shadow-md"
                loading="lazy"
                alt={props.alt || ''}
              />
            ),
            
            // 自定义代码块渲染器
            code: ({ node, inline, className, children, ...props }) => {
              return !inline ? (
                <pre className="bg-gray-900 text-gray-100 rounded-lg p-4">
                  <code {...props}>{children}</code>
                </pre>
              ) : (
                <code className="bg-gray-100 text-teal-700 px-1 rounded" {...props}>
                  {children}
                </code>
              );
            },
            
            // 自定义表格渲染器
            table: ({ node, ...props }) => (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full border" {...props} />
              </div>
            ),
          }}
        >
          {file.content}
        </ReactMarkdown>
      )}
    </div>
  );
}
```

---

### 步骤 12：浏览器加载图片
**流程**：

1. ReactMarkdown 渲染出 HTML：
   ```html
   <img src="http://127.0.0.1:8002/api/file/view?path=%2Froot%2F..." alt="示例">
   ```

2. 浏览器自动发起请求：
   ```
   GET http://127.0.0.1:8002/api/file/view?path=%2Froot%2Fdeepseek_output%2Ftask123%2Fimages%2Fpic.png
   ```

3. 后端返回图片：
   ```
   Content-Type: image/png
   [二进制图片数据]
   ```

4. 浏览器显示图片 ✅

---

## 🗂️ 关键数据结构

### FileNode 接口
```typescript
interface FileNode {
  name: string;                // 文件名：'output.md'
  type: 'folder' | 'file';     // 类型：文件或文件夹
  fileType?: 'markdown' | 'image' | 'pdf'; // 文件类型
  content?: string;            // 文件内容（处理后）
  path?: string;               // 完整路径：'/root/.../output.md'
  resultDir?: string;          // 结果目录：'/root/.../task123'
  children?: FileNode[];       // 子节点（文件夹）
}
```

---

## 📊 后端接口总结

| 接口 | 方法 | 用途 | 返回数据 |
|------|------|------|----------|
| `/api/upload` | POST | 上传文件 | `{ status, file_path }` |
| `/api/start` | POST | 开始解析 | `{ status, task_id }` |
| `/api/progress/{task_id}` | GET | 查询进度 | `{ status, state }` |
| `/api/result/{task_id}` | GET | 获取结果 | `{ status, result_dir }` |
| `/api/folder?path=...` | GET | 获取文件结构 | `{ status, children: [...] }` |
| `/api/file/content?path=...` | GET | 读取文件内容 | `{ status, content }` (JSON) |
| `/api/file/view?path=...` | GET | 获取图片/PDF | 二进制数据 |

---

## 🎯 关键点总结

1. **resultDir 非常重要**：它是拼接相对路径的基础
2. **两个读取接口**：
   - `/api/file/content`：返回 JSON，用于 Markdown
   - `/api/file/view`：返回二进制，用于图片
3. **路径处理**：自动去除多余斜杠、URL 编码
4. **异步渲染**：图片是浏览器异步加载的
5. **错误处理**：跳过外部 URL，避免重复处理

---

希望这个流程图能帮助您理解整个系统！如果还有疑问，请随时问我。 🚀
