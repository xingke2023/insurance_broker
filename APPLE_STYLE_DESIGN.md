# Apple Style Design - Company Comparison Page

## 设计目标
将公司对比页面改造为 Apple 风格的现代化界面，使用玻璃拟态（Glassmorphism）设计语言，打造立体、精致的视觉效果。

## 设计理念

### Apple 设计核心元素
1. **玻璃拟态 (Glassmorphism)**: 半透明背景 + 背景模糊效果
2. **精致阴影**: 多层次阴影营造深度感
3. **圆角设计**: 大圆角 (rounded-2xl, rounded-3xl)
4. **微妙边框**: 半透明白色边框
5. **流畅过渡**: 所有交互都有平滑动画
6. **渐变背景**: 柔和的渐变色彩

## 已实现的改造

### 1. 页面整体背景
```jsx
className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50"
```
- 使用柔和的蓝色渐变背景
- 从浅灰到浅蓝再到浅靛蓝的自然过渡

### 2. 主题选择器 (Theme Selector)
**按钮样式**:
```jsx
className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-white/80 backdrop-blur-xl
shadow-[0_4px_20px_rgba(0,0,0,0.08)] hover:shadow-[0_8px_30px_rgba(0,0,0,0.12)]
transition-all text-gray-900 border border-white/50 hover:scale-[1.02]"
```

**下拉菜单**:
```jsx
className="absolute right-0 top-full mt-2 w-52 py-2 bg-white/95 backdrop-blur-2xl
rounded-2xl shadow-[0_12px_40px_rgba(0,0,0,0.15)] border border-white/50"
```

特点:
- 玻璃拟态效果 (`backdrop-blur-xl`)
- 多层阴影营造深度
- 悬停缩放效果 (`hover:scale-[1.02]`)
- 半透明白色边框

### 3. 页面标题
```jsx
className="text-xl md:text-2xl lg:text-3xl font-bold text-transparent bg-clip-text
bg-gradient-to-r from-gray-800 via-blue-800 to-indigo-800 tracking-wide drop-shadow-sm"
```

特点:
- 渐变文字效果
- 文字阴影增加深度
- 响应式字体大小

### 4. 返回和对比按钮

**返回按钮** (Apple 白色玻璃风格):
```jsx
className="flex items-center gap-1.5 md:gap-2 px-4 md:px-6 py-2 md:py-3 bg-white/80
backdrop-blur-xl rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.08)]
hover:shadow-[0_8px_30px_rgba(0,0,0,0.12)] transition-all text-sm md:text-base
font-semibold text-gray-900 border border-white/50 hover:scale-[1.02]"
```

**对比按钮** (蓝色渐变，发光效果):
```jsx
className="flex items-center gap-2 md:gap-3 px-4 md:px-8 py-2 md:py-4
bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl
shadow-[0_8px_30px_rgba(59,130,246,0.4)] hover:shadow-[0_12px_40px_rgba(59,130,246,0.5)]
transition-all text-base md:text-lg font-bold hover:scale-[1.02]"
```

### 5. 客户信息卡片
```jsx
className="mb-2 md:mb-4 bg-white/80 backdrop-blur-xl rounded-3xl
shadow-[0_8px_30px_rgba(0,0,0,0.1),0_2px_8px_rgba(0,0,0,0.06)]
p-2 md:p-4 border border-white/60"
```

**输入框样式**:
```jsx
className="w-16 md:w-24 px-2 md:px-4 py-2 md:py-2.5 border border-gray-200/80
bg-white/90 rounded-xl text-gray-900 font-medium focus:outline-none
focus:ring-2 focus:ring-blue-400/50 focus:border-blue-400/50 transition-all
text-sm md:text-base shadow-sm"
```

**单选按钮标签**:
```jsx
className="flex items-center gap-1.5 cursor-pointer px-2 md:px-4 py-1.5 md:py-2
rounded-xl hover:bg-blue-50/50 transition-all text-gray-900 bg-white/50"
```

特点:
- 大圆角卡片 (`rounded-3xl`)
- 多层阴影效果
- 输入框有微妙的焦点效果
- 单选按钮有半透明背景

### 6. 保险公司卡片

**正常状态**:
```jsx
className="bg-white/80 backdrop-blur-xl
shadow-[0_4px_20px_rgba(0,0,0,0.08),0_1px_3px_rgba(0,0,0,0.06)]
hover:shadow-[0_8px_30px_rgba(0,0,0,0.12),0_2px_8px_rgba(0,0,0,0.08)]
hover:scale-[1.02] border border-white/50 hover:border-blue-200/50"
```

**选中状态** (蓝色发光 + 光环效果):
```jsx
className="bg-gradient-to-br from-blue-50/90 via-indigo-50/90 to-purple-50/90
backdrop-blur-xl border-2 border-blue-400/50
shadow-[0_8px_30px_rgb(59,130,246,0.3),0_2px_8px_rgb(99,102,241,0.15)]
scale-105 ring-4 ring-blue-400/20"
```

**选中标记**:
```jsx
<div className="absolute top-1.5 right-1.5 md:top-2 md:right-2
bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-1 md:p-1.5
shadow-[0_4px_12px_rgba(59,130,246,0.5)]">
  <Check className="w-4 h-4 md:w-6 md:h-6 text-white stroke-[3]" />
</div>
```

特点:
- **3D 立体效果**: 通过多层阴影实现
- **玻璃拟态**: 半透明背景 + 背景模糊
- **蓝色光环**: 选中时的 ring-4 ring-blue-400/20 效果
- **渐变背景**: 选中状态使用三色渐变
- **缩放动画**: 悬停和选中时的微妙缩放

### 7. 自定义年度卡片
```jsx
className="mt-3 md:mt-4 bg-white/80 backdrop-blur-xl rounded-3xl
shadow-[0_8px_30px_rgba(0,0,0,0.1),0_2px_8px_rgba(0,0,0,0.06)]
p-2 md:p-4 border border-white/60"
```

**复选框标签**:
```jsx
className="flex items-center gap-2 md:gap-3 cursor-pointer px-2 md:px-3 py-1 md:py-1.5
rounded-xl hover:bg-blue-50/50 transition-all bg-white/50"
```

## 设计细节

### 阴影系统
Apple 风格使用多层阴影营造深度:
- **基础阴影**: `shadow-[0_4px_20px_rgba(0,0,0,0.08),0_1px_3px_rgba(0,0,0,0.06)]`
- **悬停阴影**: `shadow-[0_8px_30px_rgba(0,0,0,0.12),0_2px_8px_rgba(0,0,0,0.08)]`
- **选中发光**: `shadow-[0_8px_30px_rgb(59,130,246,0.3),0_2px_8px_rgb(99,102,241,0.15)]`

### 玻璃拟态配方
```css
bg-white/80          /* 80% 不透明的白色背景 */
backdrop-blur-xl     /* 强背景模糊 */
border-white/50      /* 50% 不透明的白色边框 */
rounded-3xl          /* 大圆角 */
```

### 交互动画
所有交互元素都有:
- `transition-all` - 平滑过渡所有属性
- `hover:scale-[1.02]` - 悬停时微妙放大
- `focus:ring-2` - 焦点时的光环效果

### 渐变使用
- **页面背景**: `from-slate-50 via-blue-50 to-indigo-50`
- **标题文字**: `from-gray-800 via-blue-800 to-indigo-800`
- **按钮**: `from-blue-500 to-blue-600`
- **选中卡片**: `from-blue-50/90 via-indigo-50/90 to-purple-50/90`

## 响应式设计
- 所有元素在手机、平板、桌面都有适配
- 使用 Tailwind 响应式前缀: `md:`, `lg:`
- 间距、字体大小、图标大小都做了响应式调整

## 视觉层次
1. **最顶层**: 选中的公司卡片 (scale-105, ring-4)
2. **中层**: 悬停的元素 (hover:scale-[1.02])
3. **基础层**: 所有卡片和容器
4. **背景层**: 页面渐变背景

## 色彩系统
- **主色**: 蓝色系 (blue-50 到 blue-600)
- **辅助色**: 靛蓝色 (indigo-50 到 indigo-800)
- **强调色**: 紫色 (purple-50 用于渐变)
- **中性色**: 白色、灰色 (gray-800, gray-600)

## 对比效果

### 改造前
- 简单的白色背景
- 基础的边框和阴影
- 主题配置控制颜色

### 改造后
- 玻璃拟态设计语言
- 多层阴影营造深度
- 固定的 Apple 风格色彩（蓝色系）
- 3D 立体卡片效果
- 流畅的悬停和选中动画

## 技术要点

### Tailwind CSS 特性
- **自定义阴影**: `shadow-[...]` 语法
- **透明度**: `/80`, `/50` 等后缀
- **背景模糊**: `backdrop-blur-xl`
- **渐变**: `bg-gradient-to-br`
- **光环效果**: `ring-4`

### 性能优化
- 使用 CSS transforms (scale) 而非改变尺寸
- 使用 GPU 加速的属性 (transform, opacity)
- `transition-all` 仅用于简单属性变化

## 浏览器兼容性
- ✅ Chrome 76+ (backdrop-filter)
- ✅ Safari 9+ (backdrop-filter)
- ✅ Firefox 103+ (backdrop-filter)
- ✅ Edge 79+ (backdrop-filter)

---

**设计完成时间**: 2025-12-09
**设计风格**: Apple Glassmorphism
**主要文件**: `/var/www/harry-insurance2/frontend/src/components/CompanyComparison.jsx`
