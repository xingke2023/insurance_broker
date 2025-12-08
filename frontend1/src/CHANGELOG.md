# 更新日志

## 最新修改 - Markdown 图片路径自动修复

### ✅ 已实现功能

#### 1. **自动修复 Markdown 图片路径**
当用户点击 Markdown 文件时，系统会自动将相对路径的图片转换为完整的 API URL，确保图片能够正常显示。

**示例转换**：
```markdown
原始 Markdown：
![示例图片](images/screenshot.png)

自动转换后：
![示例图片](http://127.0.0.1:8002/api/file/view?path=%2Froot%2F...%2Fimages%2Fscreenshot.png)
```

---

### 🔧 技术实现

#### 核心函数：`fixMarkdownImages()`
位置：`/components/FileExplorer.tsx`

```typescript
function fixMarkdownImages(mdContent: string, resultDir: string): string {
  // 正则匹配所有 Markdown 图片语法：![alt](path)
  return mdContent.replace(
    /!\[(.*?)\]\((.*?)\)/g,
    (match, altText, relativePath) => {
      // 跳过已经是绝对 URL 的图片
      if (relativePath.startsWith('http://') || relativePath.startsWith('https://')) {
        return match;
      }
      
      // 构建完整路径
      const absPath = `${resultDir}/${relativePath}`.replace(/\/+/g, '/');
      // URL 编码
      const encodedPath = encodeURIComponent(absPath);
      // 返回新的图片链接
      return `![${altText}](${API_BASE_URL}/api/file/view?path=${encodedPath})`;
    }
  );
}
```

---

### 📋 处理流程

1. **用户点击 Markdown 文件** → 触发 `handleFileClick()`
2. **获取文件内容** → 调用 `/api/file/content?path=...`
3. **清理 OCR 标签** → 移除 `<|ref|>`, `<|det|>` 等
4. **修复图片路径** → 调用 `fixMarkdownImages()`
5. **渲染 Markdown** → 图片显示成功 ✅

---

### 🎯 支持的格式

#### ✅ 支持的 Markdown 图片语法：
```markdown
![](images/pic.png)                    # 无 alt text
![图片描述](images/pic.png)             # 有 alt text
![](./images/pic.png)                   # 相对路径（./）
![](subfolder/images/pic.png)           # 子文件夹
```

#### ⚠️ 跳过的格式（不处理）：
```markdown
![](http://example.com/image.png)      # 已经是绝对 URL
![](https://example.com/image.png)     # HTTPS URL
```

---

### 🔗 后端 API 要求

确保后端提供了 `/api/file/view` 接口，支持通过路径参数返回图片文件：

**接口示例**：
```
GET /api/file/view?path=/root/deepseek_output/task123/images/pic.png
```

**返回**：
- Content-Type: `image/png` / `image/jpeg` / `image/gif` 等
- 二进制图片数据

---

### 🧪 测试案例

#### 测试 Markdown 文件：
```markdown
# 测试文档

这是一张图片：
![测试图片](images/test.png)

这是另一张图片：
![](./screenshots/demo.jpg)

这是外部图片（不会修改）：
![外部](https://example.com/logo.png)
```

#### 预期渲染结果：
```markdown
# 测试文档

这是一张图片：
![测试图片](http://127.0.0.1:8002/api/file/view?path=%2Froot%2F...%2Fimages%2Ftest.png)

这是另一张图片：
![](http://127.0.0.1:8002/api/file/view?path=%2Froot%2F...%2Fscreenshots%2Fdemo.jpg)

这是外部图片（不会修改）：
![外部](https://example.com/logo.png)
```

所有本地图片都能正常显示！🎉

---

## 其他近期更新

### 1. **按钮加载状态优化** (2025-01-XX)
- ✅ 移除进度条，改为按钮转圈动画
- ✅ 解析中：灰色按钮 + `Loader2` 旋转图标
- ✅ 完成后：自动恢复原始状态

### 2. **OCR 标签清理** (2025-01-XX)
- ✅ 自动移除 `<|ref|>`, `<|det|>` 等 DeepSeek OCR 专有标签
- ✅ 保留纯净的 Markdown 文本

### 3. **文件预览增强** (2025-01-XX)
- ✅ 支持 PDF 预览（iframe 方式）
- ✅ 支持图片预览（点击全屏查看）
- ✅ 增强 Markdown 渲染（表格、代码高亮、HTML）

---

## 🚀 下一步优化建议

- [ ] 支持 Markdown 中的 PDF 链接自动转换
- [ ] 添加图片加载失败时的占位符
- [ ] 支持图片懒加载优化性能
- [ ] 添加 Markdown 导出功能（带图片打包下载）
