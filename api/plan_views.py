from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from pypdf import PdfReader
import os
from .models import PlanDocument
from .qwen_service import extract_plan_data_from_pdf, extract_plan_data_from_text
from .insurance_company_configs import get_company_list


@api_view(['GET'])
@permission_classes([AllowAny])
def get_insurance_companies(request):
    """获取保险公司列表"""
    companies = get_company_list()
    return Response(companies)


@api_view(['POST'])
@permission_classes([AllowAny])  # 暂时允许所有用户，后续可改为IsAuthenticated
@parser_classes([MultiPartParser, FormParser])
def upload_plan_document(request):
    """上传计划书PDF并提取数据"""

    if 'file' not in request.FILES:
        return Response(
            {'error': '请上传文件'},
            status=status.HTTP_400_BAD_REQUEST
        )

    uploaded_file = request.FILES['file']
    company_code = request.data.get('company_code', 'other')  # 获取保险公司代码

    print(f"\n🏢 选择的保险公司: {company_code}")
    print("="*80)

    # 验证文件类型
    if not uploaded_file.name.endswith('.pdf'):
        return Response(
            {'error': '只支持PDF文件'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 验证文件大小（最大10MB）
    if uploaded_file.size > 10 * 1024 * 1024:
        return Response(
            {'error': '文件大小不能超过10MB'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 验证会员状态
    if request.user.is_authenticated:
        from .models import Membership
        try:
            membership = Membership.objects.get(user=request.user)
            if not membership.is_valid():
                return Response(
                    {
                        'error': '您的会员已过期，请续费后继续使用',
                        'membership_expired': True,
                        'expired_at': membership.end_date.isoformat()
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            print(f"✅ 会员验证通过: {request.user.username} ({membership.get_plan_type_display()})")
        except Membership.DoesNotExist:
            return Response(
                {
                    'error': '您还不是会员，请购买会员后使用',
                    'membership_required': True
                },
                status=status.HTTP_403_FORBIDDEN
            )
    else:
        return Response(
            {
                'error': '请先登录',
                'login_required': True
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        # 创建文档记录
        plan_doc = PlanDocument.objects.create(
            user=request.user if request.user.is_authenticated else None,
            file_name=uploaded_file.name,
            file_path=uploaded_file,
            file_size=uploaded_file.size,
            status='processing'
        )

        # 使用文本提取+千问分析（PDF文件不支持直接视觉识别）
        try:
            # 提取PDF文本
            pdf_text = extract_text_from_pdf(uploaded_file)

            # 使用千问分析文本（传入保险公司代码）
            result = extract_plan_data_from_text(pdf_text, company_code)
        except Exception as e:
            plan_doc.status = 'failed'
            plan_doc.error_message = f'PDF处理失败: {str(e)}'
            plan_doc.save()
            return Response(
                {'error': f'PDF处理失败: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if result['success']:
            # 更新文档记录
            extracted = result['data']
            plan_doc.insured_name = extracted.get('customer_name', '')
            plan_doc.insured_age = extracted.get('customer_age')
            plan_doc.insured_gender = extracted.get('customer_gender', '')
            plan_doc.insurance_product = extracted.get('insurance_product', '')
            plan_doc.insurance_company = extracted.get('insurance_company', '')
            plan_doc.sum_assured = extracted.get('insurance_amount')
            plan_doc.annual_premium = extracted.get('premium_amount')
            plan_doc.payment_years = extracted.get('payment_years')
            plan_doc.total_premium = extracted.get('total_premium')
            plan_doc.insurance_period = extracted.get('insurance_period', '')
            plan_doc.extracted_data = extracted
            plan_doc.status = 'completed'
            plan_doc.save()

            # 更新会员使用统计
            if request.user.is_authenticated:
                from .models import Membership
                try:
                    membership = Membership.objects.get(user=request.user)
                    membership.documents_created += 1
                    membership.save()
                    print(f"📊 会员已创建计划书数: {membership.documents_created}")
                except Membership.DoesNotExist:
                    pass

            # 保存年度价值表
            annual_values = extracted.get('annual_values', [])
            if annual_values and isinstance(annual_values, list):
                from .models import AnnualValue
                print(f"\n📊 保存年度价值表: 共{len(annual_values)}条记录")

                for av_data in annual_values:
                    try:
                        AnnualValue.objects.create(
                            plan_document=plan_doc,
                            policy_year=av_data.get('policy_year'),
                            guaranteed_cash_value=av_data.get('guaranteed_value'),
                            non_guaranteed_cash_value=av_data.get('non_guaranteed_value'),
                            total_cash_value=av_data.get('total_value')
                        )
                        print(f"  ✓ 第{av_data.get('policy_year')}年数据已保存")
                    except Exception as e:
                        print(f"  ✗ 第{av_data.get('policy_year')}年数据保存失败: {e}")

                print(f"✅ 年度价值表保存完成\n")

            return Response({
                'message': '文件上传并处理成功',
                'document_id': plan_doc.id,
                'extracted_data': extracted,
                'file_info': {
                    'name': plan_doc.file_name,
                    'size': plan_doc.file_size,
                    'status': plan_doc.status
                }
            }, status=status.HTTP_201_CREATED)
        else:
            # 提取失败
            plan_doc.status = 'failed'
            plan_doc.error_message = result.get('error', '数据提取失败')
            plan_doc.save()

            return Response({
                'error': result.get('error', '数据提取失败'),
                'document_id': plan_doc.id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response(
            {'error': f'处理失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_plan_documents(request):
    """获取所有计划书文档列表"""
    if request.user.is_authenticated:
        documents = PlanDocument.objects.filter(user=request.user)
    else:
        # 未登录用户只能看到所有文档（可以根据需求调整）
        documents = PlanDocument.objects.all()[:20]

    data = []
    for doc in documents:
        data.append({
            'id': doc.id,
            'file_name': doc.file_name,
            'file_size': doc.file_size,
            'status': doc.status,
            'customer_name': doc.insured_name,
            'insurance_product': doc.insurance_product,
            'premium_amount': str(doc.annual_premium) if doc.annual_premium else None,
            'created_at': doc.created_at.isoformat(),
            'extracted_data': doc.extracted_data
        })

    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_plan_document(request, pk):
    """获取单个计划书文档详情"""
    try:
        doc = PlanDocument.objects.get(pk=pk)

        # 获取年度价值数据
        annual_values = []
        for av in doc.annual_values.all():
            annual_values.append({
                'policy_year': av.policy_year,
                'guaranteed_value': str(av.guaranteed_cash_value) if av.guaranteed_cash_value else None,
                'non_guaranteed_value': str(av.non_guaranteed_cash_value) if av.non_guaranteed_cash_value else None,
                'total_value': str(av.total_cash_value) if av.total_cash_value else None
            })

        return Response({
            'id': doc.id,
            'file_name': doc.file_name,
            'file_size': doc.file_size,
            'status': doc.status,
            'customer_name': doc.insured_name,
            'customer_age': doc.insured_age,
            'customer_gender': doc.insured_gender,
            'insurance_product': doc.insurance_product,
            'insurance_company': doc.insurance_company,
            'insurance_amount': str(doc.sum_assured) if doc.sum_assured else None,
            'premium_amount': str(doc.annual_premium) if doc.annual_premium else None,
            'payment_years': doc.payment_years,
            'total_premium': str(doc.total_premium) if doc.total_premium else None,
            'insurance_period': doc.insurance_period,
            'extracted_data': doc.extracted_data,
            'annual_values': annual_values,
            'error_message': doc.error_message,
            'created_at': doc.created_at.isoformat(),
            'updated_at': doc.updated_at.isoformat()
        })
    except PlanDocument.DoesNotExist:
        return Response(
            {'error': '文档不存在'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_plan_document(request, pk):
    """更新计划书文档数据"""
    try:
        doc = PlanDocument.objects.get(pk=pk)
        data = request.data

        # 更新受保人信息
        if 'customer_name' in data:
            doc.insured_name = data['customer_name']
        if 'customer_age' in data:
            doc.insured_age = data['customer_age']
        if 'customer_gender' in data:
            doc.insured_gender = data['customer_gender']

        # 更新保险产品信息
        if 'insurance_product' in data:
            doc.insurance_product = data['insurance_product']
        if 'insurance_company' in data:
            doc.insurance_company = data['insurance_company']
        if 'insurance_period' in data:
            doc.insurance_period = data['insurance_period']
        if 'insurance_amount' in data:
            doc.sum_assured = data['insurance_amount']

        # 更新保费信息
        if 'premium_amount' in data:
            doc.annual_premium = data['premium_amount']
        if 'payment_years' in data:
            doc.payment_years = data['payment_years']
        if 'total_premium' in data:
            doc.total_premium = data['total_premium']

        # 更新完整数据
        if 'extracted_data' in data:
            doc.extracted_data = data['extracted_data']

        doc.save()

        # 更新年度价值数据
        if 'annual_values' in data:
            from .models import AnnualValue
            # 删除旧数据
            doc.annual_values.all().delete()

            # 创建新数据
            for av_data in data['annual_values']:
                AnnualValue.objects.create(
                    plan_document=doc,
                    policy_year=av_data['policy_year'],
                    guaranteed_cash_value=av_data.get('guaranteed_value'),
                    non_guaranteed_cash_value=av_data.get('non_guaranteed_value'),
                    total_cash_value=av_data.get('total_value')
                )

        return Response({
            'message': '数据更新成功',
            'document_id': doc.id
        })

    except PlanDocument.DoesNotExist:
        return Response(
            {'error': '文档不存在'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'更新失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_membership_status(request):
    """获取当前用户的会员状态"""
    if not request.user.is_authenticated:
        return Response({
            'has_membership': False,
            'is_active': False,
            'message': '未登录'
        })

    from .models import Membership
    try:
        membership = Membership.objects.get(user=request.user)
        is_valid = membership.is_valid()
        return Response({
            'has_membership': True,
            'is_active': is_valid,
            'plan_type': membership.plan_type,
            'plan_type_display': membership.get_plan_type_display(),
            'start_date': membership.start_date.isoformat(),
            'end_date': membership.end_date.isoformat(),
            'days_remaining': membership.days_remaining(),
            'documents_created': membership.documents_created,
            'created_at': membership.created_at.isoformat()
        })
    except Membership.DoesNotExist:
        return Response({
            'has_membership': False,
            'is_active': False,
            'message': '未开通会员'
        })


def extract_text_from_pdf(pdf_file):
    """从PDF文件提取文本"""
    print("\n" + "="*80)
    print("📄 开始提取PDF文本内容...")
    print("="*80)

    text_content = []

    # 重置文件指针
    pdf_file.seek(0)

    # 使用pypdf读取PDF
    pdf_reader = PdfReader(pdf_file)

    print(f"PDF总页数: {len(pdf_reader.pages)}")

    # 提取所有页面的文本
    for i, page in enumerate(pdf_reader.pages, 1):
        text = page.extract_text()
        if text:
            text_content.append(text)
            print(f"  ✓ 第{i}页提取成功 ({len(text)}字符)")
        else:
            print(f"  ✗ 第{i}页无文本内容")

    extracted_text = '\n\n'.join(text_content)

    print(f"\n总共提取: {len(extracted_text)} 字符")
    print("="*80)
    print("提取的文本预览 (前500字符):")
    print("="*80)
    print(extracted_text[:500])
    print("="*80 + "\n")

    return extracted_text
