from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import PlanDocument
from .deepseek_service import analyze_insurance_table, extract_plan_data_from_text, extract_plan_summary
from .tasks import process_document_pipeline  # 使用Celery任务替代线程
from .permissions import IsMemberActive
import json
import base64
import logging
import os
from openai import OpenAI

logger = logging.getLogger(__name__)


@api_view(['POST'])
def save_ocr_result(request):
    """
    保存OCR解析结果到数据库

    请求体：
    {
        "file_name": "xxx.pdf",
        "file_content": "base64编码的文件内容（可选）",
        "ocr_content": "解析出的文本内容",
        "task_id": "任务ID（可选）",
        "result_dir": "结果目录（可选）",
        "user_id": "用户ID（可选）"
    }
    """
    try:
        # 获取请求数据
        file_name = request.data.get('file_name', 'unknown.pdf')
        file_content = request.data.get('file_content', None)
        ocr_content = request.data.get('ocr_content', '')
        task_id = request.data.get('task_id', '')
        result_dir = request.data.get('result_dir', '')
        user_id = request.data.get('user_id', None)

        # 如果提供了task_id，先尝试查找已存在的文档记录（避免重复创建）
        plan_doc = None
        if task_id:
            try:
                document_id = int(task_id)
                plan_doc = PlanDocument.objects.get(id=document_id)
                logger.info(f"✅ 找到已存在的文档记录 ID: {document_id}，将更新该记录")
            except (ValueError, PlanDocument.DoesNotExist):
                logger.info(f"⚠️ 未找到文档记录 {task_id}，将创建新记录")
                pass

        # 如果没有找到现有记录，创建新的 PlanDocument 记录
        if not plan_doc:
            plan_doc = PlanDocument()
            plan_doc.file_name = file_name
            logger.info(f"📝 创建新的文档记录")

        # 更新基本信息
        plan_doc.file_name = file_name
        plan_doc.file_size = len(ocr_content.encode('utf-8'))

        # 设置用户ID（如果提供了）
        user_obj = None
        if user_id:
            from django.contrib.auth.models import User
            try:
                user_obj = User.objects.get(id=user_id)
                plan_doc.user = user_obj
            except User.DoesNotExist:
                pass  # 如果用户不存在，就不设置user字段

        # 验证会员状态
        if user_obj:
            from .models import Membership
            try:
                membership = Membership.objects.get(user=user_obj)
                if not membership.is_valid():
                    return Response({
                        'status': 'error',
                        'error': '您的会员已过期，请续费后继续使用',
                        'membership_expired': True,
                        'expired_at': membership.end_date.isoformat()
                    }, status=status.HTTP_403_FORBIDDEN)
                logger.info(f"✅ 会员验证通过: {user_obj.username} ({membership.get_plan_type_display()})")
            except Membership.DoesNotExist:
                return Response({
                    'status': 'error',
                    'error': '您还不是会员，请购买会员后使用',
                    'membership_required': True
                }, status=status.HTTP_403_FORBIDDEN)

        # 保存OCR识别内容到content字段
        plan_doc.content = ocr_content

        # 如果有文件内容，保存文件
        if file_content:
            try:
                # 解码base64文件内容
                file_data = base64.b64decode(file_content)
                plan_doc.file_path.save(file_name, ContentFile(file_data), save=False)
            except Exception as e:
                print(f"文件保存失败: {e}")

        # 保存额外信息到extracted_data
        plan_doc.extracted_data = {
            'task_id': task_id,
            'result_dir': result_dir,
            'content_length': len(ocr_content),
            'saved_at': str(json.dumps({"timestamp": "now"}))
        }

        # 设置初始状态
        plan_doc.status = 'processing'
        plan_doc.processing_stage = 'pending'

        # 保存到数据库
        plan_doc.save()

        # 使用Celery启动异步任务流水线（处理基本信息、年度表、概要）
        process_document_pipeline.apply_async(args=[plan_doc.id], countdown=1)
        logger.info(f"✅ 文档 {plan_doc.id} 已保存，Celery任务已调度")

        return Response({
            'status': 'success',
            'message': '保存成功',
            'document_id': plan_doc.id,
            'data': {
                'id': plan_doc.id,
                'file_name': plan_doc.file_name,
                'status': plan_doc.status,
                'created_at': plan_doc.created_at.isoformat(),
                'content_length': len(ocr_content)
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'保存失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_documents(request):
    """
    获取用户未完成的文档列表（OCR中或AI分析中）
    同时返回最近完成的任务（最多5个）
    """
    try:
        # 从认证的用户获取 user_id
        user_id = request.user.id
        logger.info(f"🔍 查询未完成任务 - user: {request.user.username}, user_id: {user_id}")

        # 查询未完成的文档（状态为pending或processing）
        pending_docs = PlanDocument.objects.filter(
            user_id=user_id,
            status__in=['pending', 'processing']
        ).exclude(
            processing_stage='all_completed'
        ).order_by('-created_at')[:10]

        # 查询最近完成的文档（最多5个）
        completed_docs = PlanDocument.objects.filter(
            user_id=user_id,
            status='completed',
            processing_stage='all_completed'
        ).order_by('-updated_at')[:5]

        data = []
        for doc in pending_docs:
            data.append({
                'id': doc.id,
                'file_name': doc.file_name,
                'status': doc.status,
                'processing_stage': doc.processing_stage,
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat(),
                'has_content': bool(doc.content),
                'has_basic_info': bool(doc.extracted_data),
                'has_table': bool(doc.table),
                'has_summary': bool(doc.summary)
            })

        for doc in completed_docs:
            data.append({
                'id': doc.id,
                'file_name': doc.file_name,
                'status': doc.status,
                'processing_stage': doc.processing_stage,
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat(),
                'has_content': bool(doc.content),
                'has_basic_info': bool(doc.extracted_data),
                'has_table': bool(doc.table),
                'has_summary': bool(doc.summary)
            })

        logger.info(f"✅ 找到 {len(pending_docs)} 个未完成任务, {len(completed_docs)} 个已完成任务")

        return Response({
            'status': 'success',
            'count': len(data),
            'data': data
        })

    except Exception as e:
        logger.error(f"❌ 查询未完成任务失败: {e}")
        return Response({
            'status': 'error',
            'message': f'查询失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_saved_documents(request):
    """
    获取已保存的文档列表（仅返回当前用户的文档）
    """
    try:
        # 从认证的用户获取 user_id（安全的方式）
        if not request.user or not request.user.is_authenticated:
            logger.warning(f"⚠️ 未登录用户尝试获取文档列表")
            return Response({
                'status': 'error',
                'message': '请先登录',
                'data': []
            }, status=status.HTTP_401_UNAUTHORIZED)

        user_id = request.user.id
        logger.info(f"📊 获取文档列表 - user: {request.user.username}, user_id: {user_id}")

        # 只返回当前登录用户的文档
        documents = PlanDocument.objects.filter(user_id=user_id).order_by('-created_at')[:50]
        logger.info(f"📊 找到 {documents.count()} 个文档")

        data = []
        for doc in documents:
            # 统计年度价值表记录数
            table_count = len(doc.table.get('years', [])) if doc.table else 0

            # 解析table1和table2 JSON字符串为对象
            table1_data = None
            if doc.table1:
                try:
                    table1_data = json.loads(doc.table1)
                except (json.JSONDecodeError, TypeError):
                    table1_data = None

            table2_data = None
            if doc.table2:
                try:
                    table2_data = json.loads(doc.table2)
                except (json.JSONDecodeError, TypeError):
                    table2_data = None

            data.append({
                'id': doc.id,
                'file_name': doc.file_name,
                'file_size': doc.file_size,
                'status': doc.status,

                # 受保人信息
                'insured_name': doc.insured_name,
                'insured_age': doc.insured_age,
                'insured_gender': doc.insured_gender,

                # 保险产品信息
                'insurance_product': doc.insurance_product,
                'insurance_company': doc.insurance_company,

                # 保费信息
                'sum_assured': str(doc.sum_assured) if doc.sum_assured else None,
                'annual_premium': str(doc.annual_premium) if doc.annual_premium else None,
                'payment_years': doc.payment_years,
                'total_premium': str(doc.total_premium) if doc.total_premium else None,
                'insurance_period': doc.insurance_period,

                # 年度价值表数据
                'table': doc.table if doc.table else {},
                'table_record_count': table_count,

                # 基本计划退保价值表（table1）- 返回对象而非字符串
                'table1': table1_data,

                # 无忧选退保价值表（table2）- 返回对象而非字符串
                'table2': table2_data,

                # 计划书概要（简要版，只返回summary字段）
                'summary': doc.summary if doc.summary else {},

                # 内容统计
                'content_length': len(doc.content) if doc.content else 0,

                # 时间信息
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat()
            })

        return Response({
            'status': 'success',
            'count': len(data),
            'data': data
        })

    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'获取失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_document_detail(request, document_id):
    """
    获取单个文档详情
    """
    try:
        doc = PlanDocument.objects.get(id=document_id)

        # 统计年度价值表记录数
        table_count = len(doc.table.get('years', [])) if doc.table else 0

        # 解析table1和table2 JSON字符串为对象
        table1_data = None
        if doc.table1:
            try:
                table1_data = json.loads(doc.table1)
            except (json.JSONDecodeError, TypeError):
                table1_data = None

        table2_data = None
        if doc.table2:
            try:
                table2_data = json.loads(doc.table2)
            except (json.JSONDecodeError, TypeError):
                table2_data = None

        return Response({
            'status': 'success',
            'data': {
                'id': doc.id,
                'file_name': doc.file_name,
                'file_size': doc.file_size,
                'status': doc.status,
                'processing_stage': doc.processing_stage,
                'error_message': doc.error_message if hasattr(doc, 'error_message') else None,
                'content': doc.content,

                # 受保人信息
                'insured_name': doc.insured_name,
                'insured_age': doc.insured_age,
                'insured_gender': doc.insured_gender,

                # 保险产品信息
                'insurance_company': doc.insurance_company,
                'insurance_product': doc.insurance_product,

                # 保费信息
                'sum_assured': str(doc.sum_assured) if doc.sum_assured else None,
                'annual_premium': str(doc.annual_premium) if doc.annual_premium else None,
                'payment_years': doc.payment_years,
                'total_premium': str(doc.total_premium) if doc.total_premium else None,
                'insurance_period': doc.insurance_period,

                # 年度价值表数据
                'table': doc.table if doc.table else {},
                'table_record_count': table_count,

                # 基本计划退保价值表（table1）- 返回对象而非字符串
                'table1': table1_data,

                # 无忧选退保价值表（table2）- 返回对象而非字符串
                'table2': table2_data,

                # 计划书概要
                'summary': doc.summary if doc.summary else {},

                # 计划书Table源代码内容
                'tablecontent': doc.tablecontent if doc.tablecontent else '',

                # 计划书Table概要
                'tablesummary': doc.tablesummary if doc.tablesummary else '',

                # 其他数据
                'extracted_data': doc.extracted_data,
                'content_length': len(doc.content) if doc.content else 0,

                # 时间信息
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat()
            }
        })

    except PlanDocument.DoesNotExist:
        return Response({
            'status': 'error',
            'message': '文档不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'获取失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def analyze_document_table(request, document_id):
    """
    手动触发分析文档的年度价值表
    使用DeepSeek从content字段提取年度价值表数据并保存到table字段
    """
    try:
        # 获取文档
        logger.info("="*80)
        logger.info(f"📊 开始分析文档 ID: {document_id}")
        doc = PlanDocument.objects.get(id=document_id)

        # 检查是否有内容
        if not doc.content:
            logger.warning(f"⚠️  文档 {document_id} 内容为空")
            return Response({
                'status': 'error',
                'message': '文档内容为空，无法分析'
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"📄 文档名称: {doc.file_name}")
        logger.info(f"📝 内容长度: {len(doc.content)} 字符")

        # ============== 第一步：提取基本信息 ==============
        logger.info("="*80)
        logger.info("📋 步骤1：提取基本信息（客户姓名、保额、保费等）")
        logger.info("="*80)

        basic_result = extract_plan_data_from_text(doc.content)

        if basic_result and basic_result.get('success'):
            basic_data = basic_result.get('data', {})

            # 更新基本信息到数据库（字段名已对齐）
            doc.insured_name = basic_data.get('insured_name', '')

            # 年龄转换为整数
            try:
                age = basic_data.get('insured_age')
                doc.insured_age = int(age) if age else None
            except (ValueError, TypeError):
                doc.insured_age = None
                logger.warning(f"⚠️  年龄转换失败: {basic_data.get('insured_age')}")

            doc.insured_gender = basic_data.get('insured_gender', '')
            doc.insurance_product = basic_data.get('insurance_product', '')
            doc.insurance_company = basic_data.get('insurance_company', '')

            # 保额转换为长整型
            try:
                amount = basic_data.get('sum_assured')
                doc.sum_assured = int(float(amount)) if amount else None
            except (ValueError, TypeError):
                doc.sum_assured = None
                logger.warning(f"⚠️  保额转换失败: {basic_data.get('sum_assured')}")

            # 年缴保费转换为长整型
            try:
                premium = basic_data.get('annual_premium')
                doc.annual_premium = int(float(premium)) if premium else None
            except (ValueError, TypeError):
                doc.annual_premium = None
                logger.warning(f"⚠️  保费转换失败: {basic_data.get('annual_premium')}")

            # 缴费年数转换为整数（从"20年"提取数字）
            try:
                payment_years = basic_data.get('payment_years')
                if payment_years:
                    # 提取数字部分
                    import re
                    numbers = re.findall(r'\d+', str(payment_years))
                    doc.payment_years = int(numbers[0]) if numbers else None
                else:
                    doc.payment_years = None
            except (ValueError, TypeError, IndexError):
                doc.payment_years = None
                logger.warning(f"⚠️  缴费年数转换失败: {basic_data.get('payment_years')}")

            doc.insurance_period = basic_data.get('insurance_period', '')
            doc.extracted_data = basic_data

            logger.info(f"✅ 基本信息提取成功")
            logger.info(f"   - 受保人姓名: {doc.insured_name}")
            logger.info(f"   - 年龄: {doc.insured_age}")
            logger.info(f"   - 性别: {doc.insured_gender}")
            logger.info(f"   - 保险产品: {doc.insurance_product}")
            logger.info(f"   - 保险公司: {doc.insurance_company}")
            logger.info(f"   - 保额: {doc.sum_assured}")
            logger.info(f"   - 年缴保费: {doc.annual_premium}")
            logger.info(f"   - 缴费年数: {doc.payment_years}")
            logger.info(f"   - 保险期限: {doc.insurance_period}")
        else:
            logger.warning(f"⚠️  基本信息提取失败或返回空数据")
            logger.warning(f"   错误: {basic_result.get('error') if basic_result else '未知错误'}")

        # ============== 第二步：提取年度价值表 ==============
        logger.info("="*80)
        logger.info("📊 步骤2：提取年度价值表数据")
        logger.info("="*80)

        table_data = analyze_insurance_table(doc.content)

        if table_data:
            # 更新数据库中的table字段
            doc.table = table_data
            doc.save()

            record_count = len(table_data.get('years', []))
            logger.info(f"✅ 年度价值表分析成功！提取到 {record_count} 条记录")
            logger.info(f"💾 所有数据已保存到数据库")
            logger.info("="*80)

            return Response({
                'status': 'success',
                'message': '分析完成',
                'data': {
                    'basic_info': basic_data if basic_result and basic_result.get('success') else None,
                    'table': table_data,
                    'record_count': record_count
                }
            })
        else:
            logger.error(f"❌ 年度价值表分析失败 - DeepSeek返回空数据")
            logger.error("="*80)

            # 即使年度价值表失败，也保存基本信息
            if basic_result and basic_result.get('success'):
                doc.save()
                logger.info("💾 基本信息已保存，但年度价值表提取失败")

            return Response({
                'status': 'error',
                'message': 'DeepSeek分析失败，未能提取年度价值表数据',
                'data': {
                    'basic_info': basic_data if basic_result and basic_result.get('success') else None
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except PlanDocument.DoesNotExist:
        logger.error(f"❌ 文档 {document_id} 不存在")
        return Response({
            'status': 'error',
            'message': '文档不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"❌ 分析文档 {document_id} 时发生异常:")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        logger.error("="*80)
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'status': 'error',
            'message': f'分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def analyze_basic_info(request, document_id):
    """
    只分析基本信息（不分析年度价值表）
    使用DeepSeek从content字段提取基本信息并保存到数据库
    """
    try:
        # 获取文档
        logger.info("="*80)
        logger.info(f"📋 开始分析文档基本信息 ID: {document_id}")
        doc = PlanDocument.objects.get(id=document_id)

        # 检查是否有内容
        if not doc.content:
            logger.warning(f"⚠️  文档 {document_id} 内容为空")
            return Response({
                'status': 'error',
                'message': '文档内容为空，无法分析'
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"📄 文档名称: {doc.file_name}")
        logger.info(f"📝 内容长度: {len(doc.content)} 字符")

        # 提取基本信息
        basic_result = extract_plan_data_from_text(doc.content)

        if basic_result and basic_result.get('success'):
            basic_data = basic_result.get('data', {})

            # 更新基本信息到数据库（字段名已对齐）
            doc.insured_name = basic_data.get('insured_name', '')

            # 年龄转换为整数
            try:
                age = basic_data.get('insured_age')
                doc.insured_age = int(age) if age else None
            except (ValueError, TypeError):
                doc.insured_age = None
                logger.warning(f"⚠️  年龄转换失败: {basic_data.get('insured_age')}")

            doc.insured_gender = basic_data.get('insured_gender', '')
            doc.insurance_product = basic_data.get('insurance_product', '')
            doc.insurance_company = basic_data.get('insurance_company', '')

            # 保额转换为长整型
            try:
                amount = basic_data.get('sum_assured')
                doc.sum_assured = int(float(amount)) if amount else None
            except (ValueError, TypeError):
                doc.sum_assured = None
                logger.warning(f"⚠️  保额转换失败: {basic_data.get('sum_assured')}")

            # 年缴保费转换为长整型
            try:
                premium = basic_data.get('annual_premium')
                doc.annual_premium = int(float(premium)) if premium else None
            except (ValueError, TypeError):
                doc.annual_premium = None
                logger.warning(f"⚠️  保费转换失败: {basic_data.get('annual_premium')}")

            # 缴费年数转换为整数（从"20年"提取数字）
            try:
                payment_years = basic_data.get('payment_years')
                if payment_years:
                    # 提取数字部分
                    import re
                    numbers = re.findall(r'\d+', str(payment_years))
                    doc.payment_years = int(numbers[0]) if numbers else None
                else:
                    doc.payment_years = None
            except (ValueError, TypeError, IndexError):
                doc.payment_years = None
                logger.warning(f"⚠️  缴费年数转换失败: {basic_data.get('payment_years')}")

            doc.insurance_period = basic_data.get('insurance_period', '')
            doc.extracted_data = basic_data

            # 保存到数据库
            doc.save()

            logger.info(f"✅ 基本信息提取并保存成功")
            logger.info(f"   - 受保人姓名: {doc.insured_name}")
            logger.info(f"   - 年龄: {doc.insured_age}")
            logger.info(f"   - 性别: {doc.insured_gender}")
            logger.info(f"   - 保险产品: {doc.insurance_product}")
            logger.info(f"   - 保险公司: {doc.insurance_company}")
            logger.info(f"   - 保额: {doc.sum_assured}")
            logger.info(f"   - 年缴保费: {doc.annual_premium}")
            logger.info(f"   - 缴费年数: {doc.payment_years}")
            logger.info(f"   - 保险期限: {doc.insurance_period}")
            logger.info("="*80)

            return Response({
                'status': 'success',
                'message': '基本信息分析完成',
                'data': {
                    'basic_info': basic_data
                }
            })
        else:
            logger.error(f"❌ 基本信息提取失败")
            logger.error(f"   错误: {basic_result.get('error') if basic_result else '未知错误'}")
            logger.error("="*80)
            return Response({
                'status': 'error',
                'message': 'DeepSeek分析失败，未能提取基本信息'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except PlanDocument.DoesNotExist:
        logger.error(f"❌ 文档 {document_id} 不存在")
        return Response({
            'status': 'error',
            'message': '文档不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"❌ 分析文档 {document_id} 时发生异常:")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        logger.error("="*80)
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'status': 'error',
            'message': f'分析失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_documents(request):
    """
    批量删除文档
    请求体: {"document_ids": [1, 2, 3]}
    """
    try:
        document_ids = request.data.get('document_ids', [])

        if not document_ids:
            return Response({
                'status': 'error',
                'message': '请选择要删除的文档'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 使用原始SQL删除，避免Django ORM的级联检查
        from django.db import connection

        with connection.cursor() as cursor:
            # 构建SQL语句
            ids_placeholder = ', '.join(['%s'] * len(document_ids))
            sql = f"DELETE FROM plan_documents WHERE id IN ({ids_placeholder})"

            # 执行删除
            cursor.execute(sql, document_ids)
            deleted_count = cursor.rowcount

        logger.info(f"✅ 批量删除文档成功: {deleted_count} 条记录")

        return Response({
            'status': 'success',
            'message': f'成功删除 {deleted_count} 条记录',
            'deleted_count': deleted_count
        })

    except Exception as e:
        logger.error(f"❌ 删除文档时发生错误: {e}")
        return Response({
            'status': 'error',
            'message': f'删除失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsMemberActive])
def chat_with_document(request, document_id):
    """
    与计划书文档进行多轮对话（支持流式输出）

    请求体：
    {
        "message": "用户的问题",
        "history": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ],
        "stream": true  // 可选，是否使用流式输出
    }
    """
    try:
        # 获取文档
        try:
            document = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            return Response({
                'status': 'error',
                'message': '文档不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 获取请求参数
        user_message = request.data.get('message', '').strip()
        history = request.data.get('history', [])
        use_stream = request.data.get('stream', False)

        if not user_message:
            return Response({
                'status': 'error',
                'message': '消息不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取DeepSeek API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            return Response({
                'status': 'error',
                'message': 'DeepSeek API密钥未配置'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 初始化DeepSeek客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # 构建系统提示词，包含完整文档内容
        system_prompt = f"""你是一个专业的保险计划书助手。你正在帮助用户理解以下保险计划书的内容。

计划书基本信息：
- 受保人：{document.insured_name or '未提取'}
- 年龄：{document.insured_age or '未提取'}
- 性别：{document.insured_gender or '未提取'}
- 保险公司：{document.insurance_company or '未提取'}
- 保险产品：{document.insurance_product or '未提取'}
- 保额：{document.sum_assured or '未提取'}
- 年缴保费：{document.annual_premium or '未提取'}
- 缴费期：{document.payment_years or '未提取'}
- 保障期：{document.insurance_period or '未提取'}

计划书完整OCR识别内容：
{document.content if document.content else '无OCR内容'}

重要提示：
- 年龄和保单年度是不同的概念。例如：客户3岁投保，第1保单年度对应4岁，那么80岁对应的是第77保单年度（80-3=77）
- 当用户询问"80岁"时，需要根据投保年龄换算成对应的保单年度
- 当用户询问"第80年度"时，这是指保单年度，不是年龄

请根据以上完整的计划书内容回答用户的问题。如果用户询问的信息在文档中没有，请明确告知。回答要专业、准确、简洁。你可以引用文档中的具体内容来支持你的回答。"""

        # 构建对话历史
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # 添加历史对话（排除系统消息和欢迎消息）
        # 只保留最近的10轮对话（20条消息：10条用户+10条助手）
        MAX_HISTORY_MESSAGES = 20
        filtered_history = []

        for msg in history:
            if msg.get('role') in ['user', 'assistant']:
                # 跳过欢迎消息
                if msg.get('role') == 'assistant' and '我是计划书助手' in msg.get('content', ''):
                    continue
                filtered_history.append({
                    "role": msg['role'],
                    "content": msg['content']
                })

        # 只取最近的消息
        recent_history = filtered_history[-MAX_HISTORY_MESSAGES:] if len(filtered_history) > MAX_HISTORY_MESSAGES else filtered_history
        messages.extend(recent_history)

        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })

        logger.info(f"💬 历史消息数: {len(recent_history)}, 总消息数: {len(messages)}")

        logger.info(f"💬 计划书助手 - 文档ID: {document_id}, 消息: {user_message[:50]}..., 流式: {use_stream}")

        # 如果使用流式输出
        if use_stream:
            from django.http import StreamingHttpResponse

            def generate_stream():
                try:
                    stream = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=messages,
                        temperature=0.3,
                        max_tokens=1000,
                        stream=True
                    )

                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            yield f"data: {json.dumps({'content': content})}\n\n"

                    yield "data: [DONE]\n\n"

                except Exception as e:
                    logger.error(f"❌ 流式输出错误: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            response = StreamingHttpResponse(generate_stream(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response

        # 非流式输出（保留原有逻辑）
        else:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )

            # 获取AI回复
            ai_reply = response.choices[0].message.content.strip()

            logger.info(f"✅ AI回复: {ai_reply[:100]}...")

            return Response({
                'status': 'success',
                'reply': ai_reply
            })

    except Exception as e:
        logger.error(f"❌ 聊天处理失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'status': 'error',
            'message': f'处理失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_processing_status(request, document_id):
    """
    获取文档处理状态
    """
    try:
        doc = PlanDocument.objects.get(id=document_id)

        # 计算完成百分比
        stage_progress = {
            'ocr_pending': 5,
            'ocr_processing': 10,
            'ocr_completed': 15,
            'extracting_tablecontent': 20,
            'tablecontent_completed': 25,
            'pending': 30,
            'extracting_basic_info': 35,
            'basic_info_completed': 45,
            'extracting_tablesummary': 55,
            'tablesummary_completed': 60,
            'extracting_table': 65,
            'table_completed': 75,
            'extracting_wellness_table': 80,
            'wellness_table_completed': 85,
            'extracting_summary': 90,
            'all_completed': 100,
            'error': 0
        }

        progress_percentage = stage_progress.get(doc.processing_stage, 0)

        return Response({
            'status': 'success',
            'data': {
                'processing_stage': doc.processing_stage,
                'progress_percentage': progress_percentage,
                'last_processed_at': doc.last_processed_at.isoformat() if doc.last_processed_at else None,
                'status': doc.status,
                'error_message': doc.error_message if doc.error_message else None
            }
        })

    except PlanDocument.DoesNotExist:
        return Response({
            'status': 'error',
            'message': '文档不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'获取状态失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def extract_summary(request, document_id):
    """
    提取计划书概要
    使用DeepSeek从content字段提取计划书概要并保存到summary字段
    """
    try:
        # 获取文档
        logger.info("="*80)
        logger.info(f"📝 开始提取计划书概要 - 文档ID: {document_id}")
        doc = PlanDocument.objects.get(id=document_id)

        # 检查是否有内容
        if not doc.content:
            logger.warning(f"⚠️  文档 {document_id} 内容为空")
            return Response({
                'status': 'error',
                'message': '文档内容为空，无法提取概要'
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"📄 文档名称: {doc.file_name}")
        logger.info(f"📝 内容长度: {len(doc.content)} 字符")

        # 提取概要
        summary_data = extract_plan_summary(doc.content)

        if summary_data:
            # 更新数据库中的summary字段
            doc.summary = summary_data
            doc.save()

            logger.info(f"✅ 计划书概要提取成功！")
            logger.info(f"   - 概述: {summary_data.get('summary', '')[:50]}...")
            logger.info(f"   - 关键点数: {len(summary_data.get('key_points', []))}")
            logger.info(f"   - 重要日期数: {len(summary_data.get('important_dates', []))}")
            logger.info(f"💾 概要已保存到数据库")
            logger.info("="*80)

            return Response({
                'status': 'success',
                'message': '概要提取完成',
                'data': summary_data
            })
        else:
            logger.error(f"❌ 计划书概要提取失败 - DeepSeek返回空数据")
            logger.error("="*80)

            return Response({
                'status': 'error',
                'message': 'DeepSeek分析失败，未能提取计划书概要'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except PlanDocument.DoesNotExist:
        logger.error(f"❌ 文档 {document_id} 不存在")
        return Response({
            'status': 'error',
            'message': '文档不存在'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"❌ 提取概要时发生异常:")
        logger.error(f"错误类型: {type(e).__name__}")
        logger.error(f"错误信息: {str(e)}")
        logger.error("="*80)
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'status': 'error',
            'message': f'提取失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsMemberActive])
def create_pending_document(request):
    """
    创建待处理的文档记录（在OCR开始前）
    返回document_id供OCR服务使用作为task_id

    请求体：
    {
        "file_name": "文件名.pdf",
        "user_id": 用户ID
    }
    """
    try:
        file_name = request.data.get('file_name', 'unknown.pdf')
        user_id = request.data.get('user_id')

        logger.info("="*80)
        logger.info(f"📝 创建待处理文档: {file_name}")

        if not user_id:
            return Response({
                'status': 'error',
                'message': '缺少user_id参数'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证用户
        from django.contrib.auth.models import User
        try:
            user_obj = User.objects.get(id=user_id)
            logger.info(f"👤 用户: {user_obj.username} (ID: {user_id})")
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': '用户不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 验证会员状态
        from .models import Membership
        try:
            membership = Membership.objects.get(user=user_obj)
            if not membership.is_valid():
                logger.error(f"❌ 会员已过期")
                return Response({
                    'status': 'error',
                    'error': '您的会员已过期，请续费后继续使用',
                    'membership_expired': True,
                    'expired_at': membership.end_date.isoformat()
                }, status=status.HTTP_403_FORBIDDEN)
            logger.info(f"✅ 会员验证通过: {membership.get_plan_type_display()}")
        except Membership.DoesNotExist:
            logger.error(f"❌ 用户无会员资格")
            return Response({
                'status': 'error',
                'error': '您还不是会员，请购买会员后使用',
                'membership_required': True
            }, status=status.HTTP_403_FORBIDDEN)

        # 创建待处理文档
        plan_doc = PlanDocument()
        plan_doc.file_name = file_name
        plan_doc.user = user_obj
        plan_doc.status = 'pending'
        plan_doc.processing_stage = 'ocr_pending'
        plan_doc.save()

        logger.info(f"✅ 待处理文档已创建，ID: {plan_doc.id}")
        logger.info("="*80)

        return Response({
            'status': 'success',
            'document_id': plan_doc.id,
            'message': '文档记录已创建'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"❌ 创建待处理文档失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'status': 'error',
            'message': f'创建失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def ocr_webhook(request):
    """
    OCR服务完成回调接口（简化版）
    当远程OCR服务完成处理后，会调用此接口通知本地服务器

    请求体（简化）：
    {
        "task_id": "文档ID（document_id）",
        "result_dir": "结果目录路径"
    }
    """
    try:
        logger.info("="*80)
        logger.info("🔔 收到OCR Webhook回调")

        # 获取请求数据（简化）
        task_id = request.data.get('task_id', '')
        result_dir = request.data.get('result_dir', '')

        logger.info(f"📋 任务ID/文档ID: {task_id}")
        logger.info(f"📁 结果目录: {result_dir}")

        if not task_id:
            logger.error("❌ 缺少task_id参数")
            return Response({
                'status': 'error',
                'message': '缺少task_id参数'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not result_dir:
            logger.error("❌ 缺少result_dir参数")
            return Response({
                'status': 'error',
                'message': '缺少result_dir参数'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 用task_id直接查找文档（task_id就是document_id）
        try:
            document_id = int(task_id)
            plan_doc = PlanDocument.objects.get(id=document_id)
            logger.info(f"✅ 找到文档: {plan_doc.file_name} (用户: {plan_doc.user.username if plan_doc.user else '未知'})")
        except (ValueError, PlanDocument.DoesNotExist):
            logger.error(f"❌ 文档不存在: {task_id}")
            return Response({
                'status': 'error',
                'message': f'文档不存在: {task_id}'
            }, status=status.HTTP_404_NOT_FOUND)

        # 从远程OCR服务获取结果文件内容
        logger.info(f"🔄 开始获取OCR结果...")
        ocr_content = fetch_ocr_result(result_dir)

        if not ocr_content:
            logger.error("❌ 获取OCR结果失败")
            plan_doc.status = 'failed'
            plan_doc.error_message = '获取OCR结果失败'
            plan_doc.save()
            return Response({
                'status': 'error',
                'message': '获取OCR结果失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(f"✅ OCR内容获取成功，长度: {len(ocr_content)} 字符")

        # 预检查1：验证OCR内容长度
        if len(ocr_content) < 1000:
            # OCR内容过短，删除文档记录
            logger.error(f"❌ OCR内容过短（长度: {len(ocr_content)}），文件可能不是保险计划书")
            document_id = plan_doc.id
            file_name = plan_doc.file_name

            # 删除文档记录
            plan_doc.delete()

            logger.info(f"🗑️  已删除文档记录 ID: {document_id}, 文件名: {file_name}")
            logger.info("⛔ 任务链未启动：OCR内容过短")
            logger.info("="*80)

            return Response({
                'status': 'error',
                'message': '文档内容过短，上传的文件可能不是保险计划书'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 预检查2：验证是否包含表格元素
        import re
        table_regex = re.compile(r'<table[^>]*>([\s\S]*?)</table>', re.IGNORECASE)
        matches = table_regex.findall(ocr_content)

        if not matches:
            # 未检测到表格，删除文档记录
            logger.error("❌ OCR内容中未检测到表格元素，文件可能不是保险计划书")
            document_id = plan_doc.id
            file_name = plan_doc.file_name

            # 删除文档记录
            plan_doc.delete()

            logger.info(f"🗑️  已删除文档记录 ID: {document_id}, 文件名: {file_name}")
            logger.info("⛔ 任务链未启动：文件不包含表格元素")
            logger.info("="*80)

            return Response({
                'status': 'error',
                'message': '未检测到表格元素，上传的文件可能不是保险计划书'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 提取表格内容并检查长度
        tables = []
        for match_obj in table_regex.finditer(ocr_content):
            tables.append(match_obj.group(0))
        tablecontent = '\n\n'.join(tables)

        if not tablecontent or len(tablecontent.strip()) < 50:
            # 表格内容为空或过短，删除文档记录
            logger.error(f"❌ 表格内容为空或过短（长度: {len(tablecontent)}），文件可能不是保险计划书")
            document_id = plan_doc.id
            file_name = plan_doc.file_name

            # 删除文档记录
            plan_doc.delete()

            logger.info(f"🗑️  已删除文档记录 ID: {document_id}, 文件名: {file_name}")
            logger.info("⛔ 任务链未启动：表格内容为空或过短")
            logger.info("="*80)

            return Response({
                'status': 'error',
                'message': '提取的表格内容为空或过短，上传的文件可能不是保险计划书'
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"✅ 预检查通过：检测到 {len(tables)} 个表格，总长度 {len(tablecontent)} 字符")

        # 更新文档内容
        plan_doc.content = ocr_content
        plan_doc.file_size = len(ocr_content.encode('utf-8'))
        plan_doc.status = 'processing'
        plan_doc.processing_stage = 'pending'

        # 保存OCR结果信息
        if not plan_doc.extracted_data:
            plan_doc.extracted_data = {}
        plan_doc.extracted_data.update({
            'result_dir': result_dir,
            'webhook_received_at': timezone.now().isoformat(),
            'ocr_completed_at': timezone.now().isoformat()
        })

        plan_doc.save()

        logger.info(f"✅ 文档已更新，ID: {plan_doc.id}")

        # 使用Celery启动异步AI分析任务
        from .tasks import process_document_pipeline
        process_document_pipeline.apply_async(args=[plan_doc.id], countdown=1)

        logger.info(f"🚀 已启动Celery AI分析任务")
        logger.info("="*80)

        return Response({
            'status': 'success',
            'message': 'Webhook处理成功',
            'document_id': plan_doc.id
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"❌ Webhook处理失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'status': 'error',
            'message': f'Webhook处理失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def fetch_ocr_result(result_dir):
    """
    从远程OCR服务获取结果文件内容

    Args:
        result_dir: 结果目录路径

    Returns:
        str: OCR识别的文本内容，失败返回None
    """
    try:
        import requests

        # 构建OCR结果文件获取URL
        # 假设远程OCR服务提供了获取文件内容的API
        api_base_url = 'https://yu.xingke888.com'

        # 获取目录下的文件列表
        folder_url = f'{api_base_url}/api/folder?path={result_dir}'
        logger.info(f"🔍 获取文件列表: {folder_url}")

        folder_response = requests.get(folder_url, timeout=30)
        folder_data = folder_response.json()

        if folder_data.get('status') != 'success':
            logger.error(f"❌ 获取文件列表失败: {folder_data}")
            return None

        # 查找.mmd文件（排除*det.mmd）
        children = folder_data.get('children', [])
        mmd_file = None

        for file in children:
            if file.get('type') == 'file' and file.get('name', '').endswith('.mmd'):
                if not file.get('name', '').endswith('det.mmd'):
                    mmd_file = file
                    break

        if not mmd_file:
            logger.error("❌ 未找到OCR结果文件(.mmd)")
            return None

        # 获取文件内容
        file_path = mmd_file.get('path')
        content_url = f'{api_base_url}/api/file/content?path={file_path}'
        logger.info(f"📥 下载OCR内容: {content_url}")

        content_response = requests.get(content_url, timeout=60)
        content_data = content_response.json()

        # 兼容两种响应格式
        if content_data.get('status') == 'success':
            content = content_data.get('content', '')
        elif 'content' in content_data:
            content = content_data.get('content', '')
        else:
            logger.error(f"❌ 内容格式错误: {content_data}")
            return None

        logger.info(f"✅ OCR内容获取成功，长度: {len(content)}")
        return content

    except Exception as e:
        logger.error(f"❌ 获取OCR结果异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


@api_view(['POST'])
def retry_failed_document(request, document_id):
    """
    手动重试失败的文档处理任务

    Args:
        document_id: 文档ID

    可选参数:
        retry_stage: 指定重试的阶段 ('all', 'basic_info', 'table', 'summary')
    """
    try:
        retry_stage = request.data.get('retry_stage', 'all')

        # 获取文档
        try:
            doc = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            return Response({
                'status': 'error',
                'message': f'文档 {document_id} 不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        logger.info("=" * 80)
        logger.info(f"🔄 手动重试文档 {document_id} - 阶段: {retry_stage}")
        logger.info(f"   当前状态: {doc.status}")
        logger.info(f"   处理阶段: {doc.processing_stage}")

        # 检查文档内容
        if not doc.content:
            return Response({
                'status': 'error',
                'message': '文档内容为空，无法重试'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 重置错误信息
        doc.error_message = ''
        doc.save()

        # 根据retry_stage决定执行哪些任务
        if retry_stage == 'all':
            # 重新执行完整流水线
            doc.processing_stage = 'pending'
            doc.status = 'processing'
            doc.save()
            from .tasks import extract_basic_info_task
            extract_basic_info_task.apply_async(args=[document_id], countdown=1)
            logger.info("✅ 已启动完整流水线重试")

        elif retry_stage == 'basic_info':
            # 只重试基本信息提取
            doc.processing_stage = 'pending'
            doc.save()
            from .tasks import extract_basic_info_task
            extract_basic_info_task.apply_async(args=[document_id], countdown=1)
            logger.info("✅ 已启动基本信息提取重试")

        elif retry_stage == 'table':
            # 只重试年度价值表提取
            from .tasks import extract_table_task
            extract_table_task.apply_async(args=[document_id], countdown=1)
            logger.info("✅ 已启动年度价值表提取重试")

        elif retry_stage == 'summary':
            # 只重试计划书概要提取
            from .tasks import extract_summary_task
            extract_summary_task.apply_async(args=[document_id], countdown=1)
            logger.info("✅ 已启动计划书概要提取重试")

        else:
            return Response({
                'status': 'error',
                'message': f'不支持的重试阶段: {retry_stage}'
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info("=" * 80)

        return Response({
            'status': 'success',
            'message': f'已启动重试任务 (阶段: {retry_stage})',
            'document_id': document_id,
            'retry_stage': retry_stage
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"❌ 重试任务失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'status': 'error',
            'message': f'重试失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsMemberActive])
def upload_pdf_async(request):
    """
    异步上传PDF文件进行OCR识别

    流程：
    1. 接收PDF文件上传
    2. 创建PlanDocument记录（状态：ocr_pending）
    3. 启动Celery异步OCR任务
    4. 立即返回document_id
    5. 前端轮询状态查看进度

    请求参数：
    - file: PDF文件（multipart/form-data）
    - user_id: 用户ID（可选）

    返回：
    {
        "status": "success",
        "document_id": 123,
        "message": "文件已上传，正在后台处理OCR"
    }
    """
    try:
        # 获取上传的文件
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({
                'status': 'error',
                'message': '未上传文件'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证文件类型
        if not uploaded_file.name.lower().endswith('.pdf'):
            return Response({
                'status': 'error',
                'message': '仅支持PDF文件'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取用户ID
        user_id = request.data.get('user_id', None)
        user_obj = None

        if user_id:
            from django.contrib.auth.models import User
            try:
                user_obj = User.objects.get(id=user_id)
            except User.DoesNotExist:
                pass

        # 验证会员状态
        if user_obj:
            from .models import Membership
            try:
                membership = Membership.objects.get(user=user_obj)
                if not membership.is_valid():
                    return Response({
                        'status': 'error',
                        'error': '您的会员已过期，请续费后继续使用',
                        'membership_expired': True,
                        'expired_at': membership.end_date.isoformat()
                    }, status=status.HTTP_403_FORBIDDEN)
                logger.info(f"✅ 会员验证通过: {user_obj.username} ({membership.get_plan_type_display()})")
            except Membership.DoesNotExist:
                return Response({
                    'status': 'error',
                    'error': '您还不是会员，请购买会员后使用',
                    'membership_required': True
                }, status=status.HTTP_403_FORBIDDEN)

        # 创建PlanDocument记录
        plan_doc = PlanDocument()
        plan_doc.file_name = uploaded_file.name
        plan_doc.file_size = uploaded_file.size
        plan_doc.user = user_obj
        plan_doc.status = 'processing'
        plan_doc.processing_stage = 'ocr_pending'

        # 保存文件到 media 目录
        plan_doc.file_path.save(uploaded_file.name, uploaded_file, save=False)

        # 保存记录到数据库
        plan_doc.save()

        logger.info(f"📤 文件已上传: {uploaded_file.name} (ID: {plan_doc.id})")
        logger.info(f"   文件大小: {uploaded_file.size} bytes")
        logger.info(f"   保存路径: {plan_doc.file_path.path}")

        # 启动Celery异步OCR任务（从第一个任务开始：OCR识别）
        from .tasks import ocr_document_task
        ocr_document_task.apply_async(args=[plan_doc.id], countdown=1)
        logger.info(f"✅ OCR任务已调度，文档ID: {plan_doc.id}")

        return Response({
            'status': 'success',
            'message': '文件已上传，正在后台处理OCR',
            'document_id': plan_doc.id,
            'data': {
                'id': plan_doc.id,
                'file_name': plan_doc.file_name,
                'file_size': plan_doc.file_size,
                'status': plan_doc.status,
                'processing_stage': plan_doc.processing_stage,
                'created_at': plan_doc.created_at.isoformat()
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"❌ 文件上传失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'status': 'error',
            'message': f'文件上传失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
