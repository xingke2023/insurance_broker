"""
流式响应视图 - 用于实时显示PDF处理进度
"""
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt
import json
import time
from .models import PlanDocument, AnnualValue
from pypdf import PdfReader


def generate_sse_message(event_type, data):
    """生成SSE格式的消息"""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def extract_text_from_pdf_streaming(pdf_file):
    """从PDF提取文本并流式输出进度"""
    yield generate_sse_message('progress', {
        'step': 'pdf_extract_start',
        'message': '📄 开始提取PDF文本内容...'
    })

    text_content = []
    pdf_file.seek(0)
    pdf_reader = PdfReader(pdf_file)

    total_pages = len(pdf_reader.pages)
    yield generate_sse_message('progress', {
        'step': 'pdf_pages',
        'message': f'PDF总页数: {total_pages}',
        'total_pages': total_pages
    })

    for i, page in enumerate(pdf_reader.pages, 1):
        text = page.extract_text()
        if text:
            text_content.append(text)
            yield generate_sse_message('progress', {
                'step': 'pdf_page_extracted',
                'message': f'✓ 第{i}页提取成功 ({len(text)}字符)',
                'page': i,
                'chars': len(text)
            })
        else:
            yield generate_sse_message('progress', {
                'step': 'pdf_page_empty',
                'message': f'✗ 第{i}页无文本内容',
                'page': i
            })

    extracted_text = '\n\n'.join(text_content)

    yield generate_sse_message('progress', {
        'step': 'pdf_extract_complete',
        'message': f'✅ 总共提取: {len(extracted_text)} 字符',
        'total_chars': len(extracted_text),
        'preview': extracted_text[:500]
    })

    return extracted_text


def call_qwen_api_streaming(text_content, company_code):
    """调用千问API并流式输出进度"""
    import os
    from openai import OpenAI
    from .insurance_company_configs import generate_prompt_for_company

    yield generate_sse_message('progress', {
        'step': 'ai_start',
        'message': f'🏢 选择的保险公司: {company_code}'
    })

    # 获取API密钥
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        yield generate_sse_message('error', {
            'message': 'DASHSCOPE_API_KEY环境变量未设置'
        })
        return None

    # 初始化客户端
    client = OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    # 生成提示词
    prompt = generate_prompt_for_company(company_code, text_content)

    yield generate_sse_message('progress', {
        'step': 'ai_prompt',
        'message': '📤 发送提示词到千问模型...',
        'prompt': prompt[:1000] + '...' if len(prompt) > 1000 else prompt
    })

    try:
        # 调用API
        yield generate_sse_message('progress', {
            'step': 'ai_calling',
            'message': '⏳ 正在调用千问API，请稍候...'
        })

        response = client.chat.completions.create(
            model="qwen-plus-latest",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的保险文档分析助手，擅长从保险计划书中提取结构化数据。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=2000
        )

        # 获取响应
        content = response.choices[0].message.content.strip()

        yield generate_sse_message('progress', {
            'step': 'ai_response',
            'message': '📥 收到千问模型响应',
            'raw_response': content
        })

        # 解析JSON
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()

        extracted_data = json.loads(content)

        yield generate_sse_message('progress', {
            'step': 'ai_parsed',
            'message': '✅ JSON解析成功',
            'data': extracted_data
        })

        return extracted_data

    except json.JSONDecodeError as e:
        yield generate_sse_message('error', {
            'step': 'json_parse_error',
            'message': f'❌ JSON解析失败: {str(e)}'
        })
        return None
    except Exception as e:
        yield generate_sse_message('error', {
            'step': 'api_error',
            'message': f'❌ API调用失败: {str(e)}'
        })
        return None


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
@csrf_exempt
def upload_plan_document_streaming(request):
    """流式上传计划书PDF并实时返回处理进度"""

    def event_stream():
        try:
            # 验证文件
            if 'file' not in request.FILES:
                yield generate_sse_message('error', {'message': '请上传文件'})
                return

            uploaded_file = request.FILES['file']
            company_code = request.POST.get('company_code', 'other')

            yield generate_sse_message('progress', {
                'step': 'upload_start',
                'message': f'📤 开始处理文件: {uploaded_file.name}',
                'file_name': uploaded_file.name,
                'file_size': uploaded_file.size
            })

            # 验证文件类型
            if not uploaded_file.name.endswith('.pdf'):
                yield generate_sse_message('error', {'message': '只支持PDF文件'})
                return

            # 验证文件大小
            if uploaded_file.size > 10 * 1024 * 1024:
                yield generate_sse_message('error', {'message': '文件大小不能超过10MB'})
                return

            # 创建数据库记录
            yield generate_sse_message('progress', {
                'step': 'db_create',
                'message': '💾 创建数据库记录...'
            })

            plan_doc = PlanDocument.objects.create(
                user=request.user if request.user.is_authenticated else None,
                file_name=uploaded_file.name,
                file_path=uploaded_file,
                file_size=uploaded_file.size,
                status='processing'
            )

            yield generate_sse_message('progress', {
                'step': 'db_created',
                'message': f'✅ 数据库记录已创建 (ID: {plan_doc.id})',
                'document_id': plan_doc.id
            })

            # 提取PDF文本
            for progress_msg in extract_text_from_pdf_streaming(uploaded_file):
                yield progress_msg

            # 重新读取文本（因为生成器已消耗）
            uploaded_file.seek(0)
            pdf_reader = PdfReader(uploaded_file)
            text_content = '\n\n'.join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

            # 调用AI分析
            extracted_data = None
            for progress_msg in call_qwen_api_streaming(text_content, company_code):
                yield progress_msg
                # 获取最后的数据
                if '"step": "ai_parsed"' in progress_msg or '"step":"ai_parsed"' in progress_msg:
                    import json
                    msg_data = json.loads(progress_msg.split('data: ')[1].split('\n')[0])
                    if 'data' in msg_data:
                        extracted_data = msg_data['data']

            if extracted_data:
                # 保存到数据库
                yield generate_sse_message('progress', {
                    'step': 'db_update',
                    'message': '💾 保存提取的数据到数据库...'
                })

                plan_doc.insured_name = extracted_data.get('customer_name', '')
                plan_doc.insured_age = extracted_data.get('customer_age')
                plan_doc.insured_gender = extracted_data.get('customer_gender', '')
                plan_doc.insurance_product = extracted_data.get('insurance_product', '')
                plan_doc.insurance_company = extracted_data.get('insurance_company', '')
                plan_doc.sum_assured = extracted_data.get('insurance_amount')
                plan_doc.annual_premium = extracted_data.get('premium_amount')
                plan_doc.payment_years = extracted_data.get('payment_years')
                plan_doc.total_premium = extracted_data.get('total_premium')
                plan_doc.insurance_period = extracted_data.get('insurance_period', '')
                plan_doc.extracted_data = extracted_data
                plan_doc.status = 'completed'
                plan_doc.save()

                # 保存年度价值表
                annual_values = extracted_data.get('annual_values', [])
                if annual_values and isinstance(annual_values, list):
                    yield generate_sse_message('progress', {
                        'step': 'annual_values_save',
                        'message': f'📊 保存年度价值表: 共{len(annual_values)}条记录'
                    })

                    for i, av_data in enumerate(annual_values, 1):
                        AnnualValue.objects.create(
                            plan_document=plan_doc,
                            policy_year=av_data.get('policy_year'),
                            guaranteed_cash_value=av_data.get('guaranteed_value'),
                            non_guaranteed_cash_value=av_data.get('non_guaranteed_value'),
                            total_cash_value=av_data.get('total_value')
                        )
                        yield generate_sse_message('progress', {
                            'step': 'annual_value_saved',
                            'message': f'✓ 第{av_data.get("policy_year")}年数据已保存 ({i}/{len(annual_values)})'
                        })

                yield generate_sse_message('complete', {
                    'message': '🎉 处理完成！',
                    'document_id': plan_doc.id,
                    'extracted_data': extracted_data
                })
            else:
                plan_doc.status = 'failed'
                plan_doc.error_message = '数据提取失败'
                plan_doc.save()

                yield generate_sse_message('error', {
                    'message': '❌ 数据提取失败',
                    'document_id': plan_doc.id
                })

        except Exception as e:
            yield generate_sse_message('error', {
                'message': f'❌ 处理失败: {str(e)}'
            })

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response
