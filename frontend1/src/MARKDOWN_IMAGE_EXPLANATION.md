# Markdown 图片和 PDF 渲染问题解析

## 📌 问题概述

您提到的 Markdown 渲染图片和 PDF 的问题，涉及到**前端渲染**和**后端资源访问**两个方面。

---

## 🖼️ 一、Markdown 中的图片渲染

### 问题根源

当 DeepSeek OCR 解析文档后，生成的 Markdown 文件中可能包含图片引用，例如：

```markdown
![图片描述](./images/screenshot.png)
```

这里的问题是：
- ✅ **Markdown 语法支持图片**：`![alt](url)` 是标准语法
- ❌ **相对路径无法访问**：浏览器不知道 `./images/screenshot.png` 相对于哪里
- ❌ **本地文件系统隔离**：浏览器无法直接访问后端服务器的文件系统

---

### 当前实现方案

我们已经在代码中做了以下优化：

#### 1️⃣ **前端能做的**：渲染图片标签
```typescript
// FilePreview.tsx
img: ({ node, ...props }) => (
  <img
    {...props}
    className="max-w-full h-auto rounded-lg shadow-md my-4"
    loading="lazy"
    alt={props.alt || ''}
  />
)
```
✅ 这段代码可以正确渲染 `<img>` 标签，**但图片能否显示取决于路径是否正确**。

---

#### 2️⃣ **需要后端支持的**：提供图片访问接口

**问题示例**：
```markdown
![示例](./images/pic.png)
```

**浏览器看到的路径**：`./images/pic.png`（❌ 无法访问）

**需要转换成**：`http://127.0.0.1:8002/api/file/content?path=/完整路径/images/pic.png`（✅ 可以访问）

---

### 解决方案（需要后端配合）

#### 方案一：后端自动转换 Markdown 中的图片路径
后端在返回 Markdown 内容时，将相对路径替换为完整的 API URL：

```python
# 后端示例代码（伪代码）
def convert_image_paths(markdown_content, result_dir):
    import re
    
    # 查找所有图片引用 ![alt](path)
    def replace_image_path(match):
        alt_text = match.group(1)
        relative_path = match.group(2)
        
        # 构建完整路径
        full_path = os.path.join(result_dir, relative_path)
        # 转换为 API URL
        api_url = f"http://127.0.0.1:8002/api/file/content?path={urllib.parse.quote(full_path)}"
        
        return f"![{alt_text}]({api_url})"
    
    # 替换所有图片路径
    converted = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_image_path, markdown_content)
    return converted
```

**转换效果**：
```diff
- ![示例](./images/pic.png)
+ ![示例](http://127.0.0.1:8002/api/file/content?path=/output/task123/images/pic.png)
```

---

#### 方案二：前端拦截并转换路径
如果后端不方便修改，前端也可以自己转换：

```typescript
// FilePreview.tsx（高级版本）
img: ({ node, src, ...props }) => {
  // 如果是相对路径，转换成完整 API URL
  let imgSrc = src || '';
  
  if (file.resultDir && imgSrc && !imgSrc.startsWith('http')) {
    // 解析相对路径
    const cleanPath = imgSrc.replace(/^\.\//, ''); // 去掉 ./
    const fullPath = `${file.resultDir}/${cleanPath}`;
    imgSrc = `${API_BASE_URL}/api/file/content?path=${encodeURIComponent(fullPath)}`;
  }
  
  return (
    <img
      {...props}
      src={imgSrc}
      className="max-w-full h-auto rounded-lg shadow-md my-4"
      loading="lazy"
      alt={props.alt || ''}
    />
  );
}
```

**注意**：这需要后端返回文件时包含 `resultDir` 信息。

---

## 📄 二、Markdown 中的 PDF 渲染

### 问题根源

Markdown **本身不支持嵌入 PDF**。标准 Markdown 只能：
- ✅ 链接到 PDF：`[查看 PDF](file.pdf)`
- ❌ 直接显示 PDF（无标准语法）

---

### 解决方案

#### 方案一：使用 HTML 嵌入（需要后端转换）
如果 DeepSeek OCR 生成的 Markdown 包含 PDF，后端可以转换成 HTML 代码：

```markdown
<!-- 原始 Markdown -->
[查看 PDF](./document.pdf)

<!-- 后端转换成 HTML -->
<iframe src="http://127.0.0.1:8002/api/file/content?path=/output/task123/document.pdf" 
        style="width:100%; height:600px; border:1px solid #ccc;"></iframe>
```

因为我们的前端启用了 `rehypeRaw`，所以 HTML 会被正确渲染。

---

#### 方案二：点击链接在新窗口打开
保持简单，让用户点击链接：

```markdown
[📄 查看完整 PDF 文档](./document.pdf)
```

前端拦截链接，转换成完整 URL：

```typescript
a: ({ node, href, ...props }) => {
  let linkHref = href || '';
  
  if (file.resultDir && linkHref && !linkHref.startsWith('http')) {
    const cleanPath = linkHref.replace(/^\.\//, '');
    const fullPath = `${file.resultDir}/${cleanPath}`;
    linkHref = `${API_BASE_URL}/api/file/content?path=${encodeURIComponent(fullPath)}`;
  }
  
  return (
    <a
      href={linkHref}
      target="_blank"
      rel="noopener noreferrer"
      className="text-teal-600 hover:text-teal-700 underline"
      {...props}
    />
  );
}
```

---

## 🔍 三、当前代码能力总结

### ✅ 已实现的功能
1. **图片类型文件预览**：文件浏览器中的 `.png`、`.jpg` 可以点击预览
2. **PDF 文件预览**：文件浏览器中的 `.pdf` 可以点击预览（iframe 方式）
3. **Markdown 富文本渲染**：支持标题、表格、代码块、链接等
4. **OCR 标签清理**：自动移除 `<|ref|>`、`<|det|>` 等标签

### ❌ 需要后端配合的功能
1. **Markdown 中的相对路径图片**：需要后端转换路径或前端获取 `resultDir`
2. **Markdown 中的 PDF 嵌入**：需要后端转换成 HTML iframe 代码

---

## 💡 建议与总结

### 推荐方案：后端统一处理
建议您在**后端**的 `/api/file/content` 接口中：

1. **检测文件类型**：如果是 Markdown 文件
2. **解析内容**：查找所有图片和 PDF 链接
3. **转换路径**：将相对路径替换为完整的 API URL
4. **返回处理后的内容**：前端直接渲染即可

**优势**：
- ✅ 前端代码简洁，无需复杂逻辑
- ✅ 统一管理资源路径
- ✅ 支持跨域和权限控制

---

### 临时方案：前端手动处理
如果后端暂时无法修改，可以：
1. 确保后端返回文件时包含 `resultDir` 字段
2. 在前端的 ReactMarkdown 组件中拦截 `img` 和 `a` 标签
3. 手动拼接完整的 API URL

**缺点**：
- ⚠️ 前端需要猜测文件结构
- ⚠️ 路径解析可能出错

---

## 🛠️ 测试方法

### 1. 测试图片渲染
创建一个包含图片的 Markdown：
```markdown
# 测试文档

![测试图片](./images/test.png)
```

**预期行为**：
- ❌ 当前：图片显示加载失败（路径不正确）
- ✅ 修复后：图片正常显示

### 2. 测试 PDF 链接
创建一个包含 PDF 链接的 Markdown：
```markdown
[查看 PDF 文档](./files/document.pdf)
```

**预期行为**：
- ❌ 当前：点击后 404 或无法访问
- ✅ 修复后：点击后在新窗口打开 PDF

---

## 📞 需要后端提供的信息

为了完美解决图片和 PDF 问题，请后端开发确认：

1. ✅ `/api/file/content` 接口是否支持返回二进制文件（图片、PDF）？
2. ✅ 返回 Markdown 时，是否可以包含 `resultDir` 字段？
3. ✅ 是否可以在后端统一转换 Markdown 中的相对路径？

---

**总结**：前端已经做好了渲染准备，关键在于**图片和 PDF 的路径能否正确访问**。这通常需要后端配合提供完整的 URL 或静态资源服务。
