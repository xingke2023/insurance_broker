from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import FileResponse, HttpResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
import fitz  # PyMuPDF
import io
import os
import tempfile


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_pdf_footer(request):
    """
    移除PDF文件指定区域

    参数:
    - pdf_file: PDF文件
    - remove_areas: JSON字符串，包含6个区域的配置
    - process_start_page: 处理开始页码，从原文件第几页开始处理（默认1）
    - page_number_start: 起始页码编号，从原文件第几页开始添加"第1页"（默认1）
    """
    try:
        # 获取上传的PDF文件
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            return Response({
                'status': 'error',
                'message': '请上传PDF文件'
            }, status=400)

        # 检查文件类型
        if not pdf_file.name.endswith('.pdf'):
            return Response({
                'status': 'error',
                'message': '只支持PDF格式文件'
            }, status=400)

        # 获取自定义文字
        custom_text = request.POST.get('custom_text', '').strip()

        # 获取处理开始页码（从第几页开始处理，默认从第1页开始）
        try:
            process_start_page = int(request.POST.get('process_start_page', 1))
            if process_start_page < 1:
                process_start_page = 1
        except (ValueError, TypeError):
            process_start_page = 1

        # 获取起始页码编号（从原文件第几页开始添加"第1页"，默认从第1页开始）
        try:
            page_number_start = int(request.POST.get('page_number_start', 1))
            if page_number_start < 1:
                page_number_start = 1
        except (ValueError, TypeError):
            page_number_start = 1

        # 获取PDF密码（如果有）
        pdf_password = request.POST.get('pdf_password', '').strip()

        # 解析擦除区域参数
        import json
        remove_areas_str = request.POST.get('remove_areas', '{}')
        try:
            remove_areas = json.loads(remove_areas_str)
        except json.JSONDecodeError:
            return Response({
                'status': 'error',
                'message': '擦除区域参数格式错误'
            }, status=400)

        # 读取PDF文件
        pdf_bytes = pdf_file.read()

        # 使用PyMuPDF处理PDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        # 检查PDF是否加密
        if pdf_document.is_encrypted:
            # 尝试解密
            if pdf_password:
                # 使用提供的密码解密
                auth_result = pdf_document.authenticate(pdf_password)
                if not auth_result:
                    pdf_document.close()
                    return Response({
                        'status': 'error',
                        'message': '密码错误，请检查后重试'
                    }, status=400)
            else:
                # 尝试空密码
                auth_result = pdf_document.authenticate("")
                if not auth_result:
                    pdf_document.close()
                    return Response({
                        'status': 'error',
                        'message': '此PDF已加密，请提供密码',
                        'requires_password': True
                    }, status=400)

        # 获取总页数
        total_pages = len(pdf_document)

        # 验证处理开始页码
        if process_start_page > total_pages:
            pdf_document.close()
            return Response({
                'status': 'error',
                'message': f'处理开始页码({process_start_page})超过PDF总页数({total_pages})'
            }, status=400)

        # 遍历每一页，从处理开始页码开始处理（索引从0开始，所以需要-1）
        for page_num in range(process_start_page - 1, total_pages):
            page = pdf_document[page_num]

            # 检查并修正页面旋转（只修正倒置的页面180度 -> 0度）
            rotation = page.rotation
            if rotation == 180:
                # 将倒置的页面旋转到正常方向（0度）
                page.set_rotation(0)

            # 获取页面尺寸
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height

            # 处理页眉-通栏
            if remove_areas.get('headerFull', {}).get('enabled', False):
                h = remove_areas['headerFull'].get('height', 50)
                rect = fitz.Rect(0, 0, page_width, h)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

            # 处理页眉-左上
            if remove_areas.get('headerLeft', {}).get('enabled', False):
                w = remove_areas['headerLeft'].get('width', 100)
                h = remove_areas['headerLeft'].get('height', 100)
                rect = fitz.Rect(0, 0, w, h)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

            # 处理页眉-右上
            if remove_areas.get('headerRight', {}).get('enabled', False):
                w = remove_areas['headerRight'].get('width', 100)
                h = remove_areas['headerRight'].get('height', 100)
                rect = fitz.Rect(page_width - w, 0, page_width, h)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

            # 处理页脚-通栏
            footer_enabled = remove_areas.get('footerFull', {}).get('enabled', False)
            footer_height = remove_areas.get('footerFull', {}).get('height', 50)

            if footer_enabled:
                rect = fitz.Rect(0, page_height - footer_height, page_width, page_height)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

            # 处理页脚-左下
            if remove_areas.get('footerLeft', {}).get('enabled', False):
                w = remove_areas['footerLeft'].get('width', 100)
                h = remove_areas['footerLeft'].get('height', 100)
                rect = fitz.Rect(0, page_height - h, w, page_height)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

            # 处理页脚-右下
            if remove_areas.get('footerRight', {}).get('enabled', False):
                w = remove_areas['footerRight'].get('width', 100)
                h = remove_areas['footerRight'].get('height', 100)
                rect = fitz.Rect(page_width - w, page_height - h, page_width, page_height)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

            # 如果页脚通栏启用，添加页码文字
            if footer_enabled:
                # 当前页码（从1开始，page_num是从0开始的索引）
                current_page_number = page_num + 1

                # 只有当当前页码 >= page_number_start 时才添加页码
                # 例如：page_number_start=3，则第1,2页不添加页码，从第3页开始显示"第1页"
                if current_page_number >= page_number_start:
                    # 显示的页码 = 当前页码 - 起始页码 + 1
                    # 例如：当前第3页，起始页码3，显示"第1页" (3-3+1=1)
                    display_page_num = current_page_number - page_number_start + 1
                    # 总页数 = 从起始页码到最后一页的数量
                    # 例如：共10页，从第3页开始编号，总数=10-3+1=8页
                    display_total_pages = total_pages - page_number_start + 1
                    page_text = f"第 {display_page_num} 頁，共 {display_total_pages} 頁"

                    # 如果有自定义文字，添加到页码下方
                    if custom_text:
                        page_text += f"\n{custom_text}"

                    # 创建文本框区域（整个页脚宽度）
                    text_rect = fitz.Rect(
                        0,  # 左边界
                        page_height - footer_height,  # 上边界
                        page_width,  # 右边界
                        page_height  # 下边界
                    )

                    # 插入居中文字（使用textbox支持中文，支持多行）
                    page.insert_textbox(
                        text_rect,
                        page_text,
                        fontsize=10,
                        fontname="china-s",  # 中文简体字体
                        color=(0, 0, 0),  # 黑色
                        align=fitz.TEXT_ALIGN_CENTER,  # 居中对齐
                    )

        # 保存到内存，使用压缩选项
        output_buffer = io.BytesIO()
        pdf_document.save(
            output_buffer,
            garbage=4,  # 最高级别的垃圾回收
            deflate=True,  # 使用deflate压缩
            clean=True,  # 清理未使用的对象
        )
        pdf_document.close()

        # 重置缓冲区指针
        output_buffer.seek(0)

        # 生成文件名
        original_name = pdf_file.name
        output_filename = original_name.replace('.pdf', '_无页脚.pdf')

        # 返回处理后的PDF文件
        response = HttpResponse(output_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'

        return response

    except Exception as e:
        print(f'❌ 处理PDF失败: {str(e)}')
        import traceback
        traceback.print_exc()

        return Response({
            'status': 'error',
            'message': f'处理PDF失败: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crop_pdf_footer(request):
    """
    通过裁剪方式移除PDF页脚

    参数:
    - pdf_file: PDF文件
    - footer_height: 要裁剪的页脚高度（像素）
    """
    try:
        # 获取上传的PDF文件
        pdf_file = request.FILES.get('pdf_file')
        if not pdf_file:
            return Response({
                'status': 'error',
                'message': '请上传PDF文件'
            }, status=400)

        # 检查文件类型
        if not pdf_file.name.endswith('.pdf'):
            return Response({
                'status': 'error',
                'message': '只支持PDF格式文件'
            }, status=400)

        # 获取页脚高度参数
        try:
            footer_height = int(request.POST.get('footer_height', 50))
            if footer_height <= 0 or footer_height > 500:
                raise ValueError('页脚高度必须在1-500像素之间')
        except ValueError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=400)

        # 获取自定义文字
        custom_text = request.POST.get('custom_text', '').strip()

        # 获取PDF密码（如果有）
        pdf_password = request.POST.get('pdf_password', '').strip()

        # 获取二维码擦除参数
        enable_qr_removal = request.POST.get('enable_qr_removal', '').lower() == 'true'
        qr_position = request.POST.get('qr_position', 'bottom-right')
        qr_width = int(request.POST.get('qr_width', 100))
        qr_height = int(request.POST.get('qr_height', 100))

        # 读取PDF文件
        pdf_bytes = pdf_file.read()

        # 使用PyMuPDF处理PDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        # 检查PDF是否加密
        if pdf_document.is_encrypted:
            # 尝试解密
            if pdf_password:
                # 使用提供的密码解密
                auth_result = pdf_document.authenticate(pdf_password)
                if not auth_result:
                    pdf_document.close()
                    return Response({
                        'status': 'error',
                        'message': '密码错误，请检查后重试'
                    }, status=400)
            else:
                # 尝试空密码
                auth_result = pdf_document.authenticate("")
                if not auth_result:
                    pdf_document.close()
                    return Response({
                        'status': 'error',
                        'message': '此PDF已加密，请提供密码',
                        'requires_password': True
                    }, status=400)

        # 遍历每一页并裁剪
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]

            # 获取当前页面尺寸
            page_rect = page.rect

            # 创建新的裁剪区域（移除底部页脚）
            new_rect = fitz.Rect(
                page_rect.x0,  # 左边界
                page_rect.y0,  # 上边界
                page_rect.x1,  # 右边界
                page_rect.y1 - footer_height  # 新的下边界（向上移动）
            )

            # 设置裁剪区域
            page.set_cropbox(new_rect)

        # 保存到内存，使用压缩选项
        output_buffer = io.BytesIO()
        pdf_document.save(
            output_buffer,
            garbage=4,  # 最高级别的垃圾回收
            deflate=True,  # 使用deflate压缩
            clean=True,  # 清理未使用的对象
        )
        pdf_document.close()

        # 重置缓冲区指针
        output_buffer.seek(0)

        # 生成文件名
        original_name = pdf_file.name
        output_filename = original_name.replace('.pdf', '_裁剪页脚.pdf')

        # 返回处理后的PDF文件
        response = HttpResponse(output_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'

        return response

    except Exception as e:
        print(f'❌ 裁剪PDF失败: {str(e)}')
        import traceback
        traceback.print_exc()

        return Response({
            'status': 'error',
            'message': f'裁剪PDF失败: {str(e)}'
        }, status=500)
