#!/usr/bin/env python3
"""
测试PDF页脚移除功能的字体支持
"""
import fitz
import io

def test_chinese_fonts():
    """测试中文字体支持"""
    print("🔍 测试PyMuPDF中文字体支持...\n")

    # 创建一个简单的PDF
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4尺寸

    # 测试不同的中文字体
    fonts_to_test = [
        "china-s",      # 简体中文
        "china-ss",     # 简体中文（Song体）
        "china-t",      # 繁体中文
        "china-ts",     # 繁体中文（Song体）
        "cjk",          # CJK统一字体
    ]

    test_text = "第 1 頁，共 10 頁\n测试中文字体"

    y_position = 50
    results = []

    for font_name in fonts_to_test:
        try:
            rect = fitz.Rect(50, y_position, 500, y_position + 100)
            page.insert_textbox(
                rect,
                f"字体 '{font_name}':\n{test_text}",
                fontsize=12,
                fontname=font_name,
                color=(0, 0, 0),
                align=fitz.TEXT_ALIGN_LEFT
            )
            results.append(f"✅ {font_name}: 成功")
            y_position += 120
        except Exception as e:
            results.append(f"❌ {font_name}: 失败 - {str(e)}")
            y_position += 120

    # 保存测试PDF
    output = io.BytesIO()
    try:
        doc.save(output)
        doc.close()
        print("✅ PDF生成成功！")
        print(f"   大小: {len(output.getvalue())} bytes\n")
    except Exception as e:
        print(f"❌ PDF保存失败: {e}\n")
        doc.close()
        return False

    # 输出测试结果
    print("字体测试结果:")
    print("-" * 50)
    for result in results:
        print(f"  {result}")
    print("-" * 50)

    # 检查是否有成功的字体
    success_count = sum(1 for r in results if r.startswith("✅"))
    print(f"\n总结: {success_count}/{len(fonts_to_test)} 个字体可用")

    return success_count > 0

def test_pdf_footer_removal():
    """测试PDF页脚移除核心功能"""
    print("\n🔍 测试PDF页脚移除核心功能...\n")

    try:
        # 创建一个带有页脚的测试PDF
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)  # A4尺寸

        # 添加一些内容
        page.insert_text((100, 100), "这是测试内容", fontsize=14)

        # 获取页面尺寸
        page_rect = page.rect
        page_width = page_rect.width
        page_height = page_rect.height

        # 模拟页脚移除：用白色矩形覆盖底部
        footer_height = 50
        rect = fitz.Rect(0, page_height - footer_height, page_width, page_height)
        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

        # 添加新的页码（使用china-s字体）
        text_rect = fitz.Rect(0, page_height - footer_height, page_width, page_height)
        page.insert_textbox(
            text_rect,
            "第 1 頁，共 1 頁",
            fontsize=10,
            fontname="china-s",
            color=(0, 0, 0),
            align=fitz.TEXT_ALIGN_CENTER
        )

        # 保存PDF
        output = io.BytesIO()
        doc.save(
            output,
            garbage=4,
            deflate=True,
            clean=True
        )
        doc.close()

        print("✅ PDF页脚移除功能测试成功！")
        print(f"   生成的PDF大小: {len(output.getvalue())} bytes")
        return True

    except Exception as e:
        print(f"❌ PDF页脚移除功能测试失败:")
        print(f"   错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PDF生成功能诊断工具")
    print("=" * 60)
    print(f"PyMuPDF版本: {fitz.__version__}\n")

    # 测试1: 中文字体支持
    font_test_passed = test_chinese_fonts()

    # 测试2: PDF页脚移除核心功能
    removal_test_passed = test_pdf_footer_removal()

    # 最终结果
    print("\n" + "=" * 60)
    print("诊断结果:")
    print("=" * 60)
    print(f"  中文字体支持: {'✅ 通过' if font_test_passed else '❌ 失败'}")
    print(f"  页脚移除功能: {'✅ 通过' if removal_test_passed else '❌ 失败'}")
    print("=" * 60)

    if font_test_passed and removal_test_passed:
        print("\n🎉 所有测试通过！PDF生成功能正常。")
        print("   如果Web API仍然失败，请检查:")
        print("   1. 上传的PDF文件是否损坏")
        print("   2. PDF文件权限或加密状态")
        print("   3. 服务器内存和磁盘空间")
        print("   4. Django日志中的详细错误信息")
    else:
        print("\n⚠️  发现问题，请参考上述错误信息修复。")
