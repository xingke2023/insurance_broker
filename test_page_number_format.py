#!/usr/bin/env python3
"""测试页码格式"""
import fitz
import io

# 创建测试PDF
doc = fitz.open()
page = doc.new_page(width=595, height=842)

page_height = page.rect.height
page_width = page.rect.width
footer_height = 50

# 测试不同的页码格式
display_page_num = 2
display_total_pages = 13

# 方案1: 当前格式（无空格）
page_text1 = f"第{display_page_num}頁，共{display_total_pages}頁"

# 添加页码文本
text_rect = fitz.Rect(0, page_height - footer_height, page_width, page_height)
page.insert_textbox(
    text_rect,
    page_text1,
    fontsize=8,
    fontname="china-s",
    color=(0, 0, 0),
    align=fitz.TEXT_ALIGN_CENTER
)

# 保存测试
output = io.BytesIO()
doc.save(output)
doc.close()

print(f"✅ 测试PDF生成成功")
print(f"   页码文本: {page_text1}")
print(f"   文本长度: {len(page_text1)} 字符")
print(f"   PDF大小: {len(output.getvalue())} bytes")
print(f"\n格式分析:")
print(f"   '{page_text1}'")
for i, char in enumerate(page_text1):
    print(f"   位置{i}: '{char}' (Unicode: U+{ord(char):04X})")
