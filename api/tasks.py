"""
Celery异步任务定义
处理保险文档OCR结果的七个核心任务（按执行顺序）：
0. OCR识别 (ocr_document_task) - 新增
1. 提取表格源代码 (extract_tablecontent_task)
2. 提取基本信息 (extract_basic_info_task)
3. 提取表格概要 (extract_tablesummary_task)
4. 提取年度价值表 (extract_table_task)
5. 提取无忧选退保价值表 (extract_wellness_table_task)
6. 提取计划书概要 (extract_summary_task)
"""
import logging
import time
import re
import json
import os
import requests
from celery import shared_task
from django.utils import timezone
from openai import OpenAI
from .models import PlanDocument
from .deepseek_service import extract_plan_data_from_text, analyze_insurance_table, extract_plan_summary, extract_table_summary

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def ocr_document_task(self, document_id):
    """
    步骤0：OCR识别文档
    调用PaddleLayout API识别PDF文档，提取markdown格式文本

    Args:
        document_id: PlanDocument的ID

    Returns:
        dict: {'success': bool, 'error': str (if failed)}
    """
    try:
        logger.info("=" * 80)
        logger.info(f"📄 Celery任务开始 - 步骤0/7: OCR识别文档 - 文档ID: {document_id}")
        logger.info(f"   重试次数: {self.request.retries}/{self.max_retries}")

        # 加载文档
        try:
            doc = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            error_msg = f"文档 {document_id} 不存在"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

        # 更新状态
        doc.processing_stage = 'ocr_processing'
        doc.last_processed_at = timezone.now()
        doc.save(update_fields=['processing_stage', 'last_processed_at'])

        # 检查文件是否存在
        if not doc.file_path or not os.path.exists(doc.file_path.path):
            error_msg = "PDF文件不存在"
            logger.error(f"❌ {error_msg}: {doc.file_path}")
            doc.processing_stage = 'error'
            doc.error_message = error_msg
            doc.status = 'failed'
            doc.save()
            return {'success': False, 'error': error_msg}

        # 调用PaddleLayout API
        logger.info(f"📤 开始调用PaddleLayout OCR: {doc.file_path.path}")

        try:
            with open(doc.file_path.path, 'rb') as pdf_file:
                files = {
                    'file': (doc.file_name, pdf_file, 'application/pdf')
                }
                data = {
                    'format': 'markdown'
                }
                headers = {
                    'X-API-Key': '0dbe66d87befa7a9d5d7c1bdbc631a9b7dc5ce88be9a20e41c26790060802647'
                }

                response = requests.post(
                    'http://localhost:5003/api/paddle-layout/pdf',
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=300  # 5分钟超时
                )

            if response.status_code == 200:
                ocr_content = response.text
                logger.info(f"✅ OCR识别成功，内容长度: {len(ocr_content)}")

                if not ocr_content or not ocr_content.strip():
                    raise Exception("OCR返回内容为空")

                # 保存OCR内容到数据库
                doc.content = ocr_content
                doc.processing_stage = 'ocr_completed'
                doc.last_processed_at = timezone.now()
                doc.save(update_fields=['content', 'processing_stage', 'last_processed_at'])

                logger.info("✅ 步骤0完成: OCR识别成功")

                # 自动触发下一个任务：提取表格源代码
                extract_tablecontent_task.apply_async(args=[document_id], countdown=2)

                return {'success': True}

            else:
                error_msg = f"PaddleLayout API错误: {response.status_code} - {response.text[:200]}"
                raise Exception(error_msg)

        except requests.exceptions.Timeout:
            error_msg = "OCR请求超时（5分钟）"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            error_msg = f"OCR请求失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)

    except Exception as e:
        error_msg = f"OCR识别失败: {str(e)}"
        logger.error(error_msg)

        # 重试机制
        if self.request.retries < self.max_retries:
            logger.warning(f"⏳ 将在60秒后重试 ({self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=Exception(error_msg))

        # 达到最大重试次数后，标记失败
        logger.error(f"❌ 已达最大重试次数，OCR识别失败")
        doc.processing_stage = 'error'
        doc.error_message = f"OCR识别失败（已重试{self.max_retries}次）: {error_msg}"
        doc.status = 'failed'
        doc.save()

        return {'success': False, 'error': error_msg}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def extract_basic_info_task(self, document_id):
    """
    步骤2：提取基本信息
    从OCR文本中提取受保人、保险产品、保额、保费等核心信息

    Args:
        document_id: PlanDocument的ID

    Returns:
        dict: {'success': bool, 'error': str (if failed)}
    """
    try:
        logger.info("=" * 80)
        logger.info(f"📋 Celery任务开始 - 步骤2/6: 提取基本信息 - 文档ID: {document_id}")
        logger.info(f"   重试次数: {self.request.retries}/{self.max_retries}")

        # 加载文档
        try:
            doc = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            error_msg = f"文档 {document_id} 不存在"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

        # 检查OCR是否成功（前置条件）
        if doc.status == 'failed' or doc.processing_stage == 'error':
            error_msg = f"OCR识别失败，跳过后续任务: {doc.error_message}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}

        # 更新状态
        doc.processing_stage = 'extracting_basic_info'
        doc.last_processed_at = timezone.now()
        doc.save(update_fields=['processing_stage', 'last_processed_at'])

        if not doc.content:
            error_msg = "文档内容为空"
            logger.error(f"❌ {error_msg}")
            # 采用降级策略：至少保留OCR内容
            doc.processing_stage = 'basic_info_completed'
            doc.error_message = f"基本信息提取失败: {error_msg}，但OCR内容已保存"
            doc.status = 'completed'  # 降级为部分完成
            doc.save()
            # 继续执行后续任务
            logger.info("⚠️ 降级策略：跳过基本信息提取，继续后续步骤")
            extract_table_task.apply_async(args=[document_id], countdown=2)
            return {'success': False, 'error': error_msg, 'degraded': True}

        # 调用DeepSeek提取基本信息
        basic_result = extract_plan_data_from_text(doc.content)

        if not basic_result or not basic_result.get('success'):
            error_msg = f"基本信息提取失败: {basic_result.get('error') if basic_result else '未知错误'}"
            logger.error(error_msg)
            # 重试机制
            if self.request.retries < self.max_retries:
                logger.warning(f"⏳ 将在60秒后重试 ({self.request.retries + 1}/{self.max_retries})")
                raise self.retry(exc=Exception(error_msg))

            # 达到最大重试次数后，采用降级策略
            logger.error(f"❌ 已达最大重试次数，启用降级策略")
            doc.processing_stage = 'basic_info_completed'
            doc.error_message = f"基本信息提取失败（已重试{self.max_retries}次），但OCR内容已保存"
            doc.status = 'completed'  # 降级为部分完成
            doc.save()
            # 继续执行后续任务
            logger.info("⚠️ 降级策略：跳过基本信息提取，继续后续步骤")
            extract_table_task.apply_async(args=[document_id], countdown=2)
            return {'success': False, 'error': error_msg, 'degraded': True}

        basic_data = basic_result.get('data', {})

        # 更新数据库字段
        doc.insured_name = basic_data.get('insured_name', '')

        # 年龄转换
        try:
            age = basic_data.get('insured_age')
            doc.insured_age = int(age) if age else None
        except (ValueError, TypeError):
            doc.insured_age = None

        doc.insured_gender = basic_data.get('insured_gender', '')
        doc.insurance_product = basic_data.get('insurance_product', '')
        doc.insurance_company = basic_data.get('insurance_company', '')

        # 保额转换
        try:
            amount = basic_data.get('sum_assured')
            doc.sum_assured = int(float(amount)) if amount else None
        except (ValueError, TypeError):
            doc.sum_assured = None

        # 年缴保费转换
        try:
            premium = basic_data.get('annual_premium')
            doc.annual_premium = int(float(premium)) if premium else None
        except (ValueError, TypeError):
            doc.annual_premium = None

        # 缴费年数转换
        try:
            payment_years = basic_data.get('payment_years')
            if payment_years:
                numbers = re.findall(r'\d+', str(payment_years))
                doc.payment_years = int(numbers[0]) if numbers else None
            else:
                doc.payment_years = None
        except (ValueError, TypeError, IndexError):
            doc.payment_years = None

        doc.insurance_period = basic_data.get('insurance_period', '')
        doc.extracted_data = basic_data

        # 更新阶段为完成
        doc.processing_stage = 'basic_info_completed'
        doc.last_processed_at = timezone.now()
        doc.save()

        logger.info("✅ 步骤2完成: 基本信息提取成功")
        logger.info(f"   - 受保人: {doc.insured_name}")
        logger.info(f"   - 保险产品: {doc.insurance_product}")

        # 自动触发下一个任务：提取表格概要
        extract_tablesummary_task.apply_async(args=[document_id], countdown=2)

        return {'success': True}

    except Exception as e:
        error_msg = f"提取基本信息时发生异常: {str(e)}"
        logger.error(error_msg)
        import traceback
        logger.error(traceback.format_exc())

        # 重试机制
        if self.request.retries < self.max_retries:
            logger.warning(f"⏳ 发生异常，将在60秒后重试 ({self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e)

        # 达到最大重试次数后，采用降级策略
        logger.error(f"❌ 异常处理：已达最大重试次数，启用降级策略")
        try:
            doc = PlanDocument.objects.get(id=document_id)
            doc.processing_stage = 'basic_info_completed'
            doc.error_message = f"基本信息提取异常（已重试{self.max_retries}次）: {error_msg}，但OCR内容已保存"
            doc.status = 'completed'  # 降级为部分完成
            doc.save()
            # 继续执行后续任务
            logger.info("⚠️ 降级策略：跳过基本信息提取，继续后续步骤")
            extract_table_task.apply_async(args=[document_id], countdown=2)
        except Exception as save_error:
            logger.error(f"保存降级状态时出错: {save_error}")

        return {'success': False, 'error': error_msg, 'degraded': True}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def extract_table_task(self, document_id):
    """
    步骤4：提取退保价值表 (table1字段)
    调用 content_editor_views.process_surrender_value_table 核心函数

    Args:
        document_id: PlanDocument的ID

    Returns:
        dict: {'success': bool, 'error': str (if failed)}
    """
    from api.content_editor_views import process_surrender_value_table

    try:
        logger.info("=" * 80)
        logger.info(f"📊 Celery任务开始 - 步骤4/6: 提取退保价值表 - 文档ID: {document_id}")

        # 更新状态为正在提取
        try:
            doc = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            error_msg = f"文档 {document_id} 不存在"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

        # 检查OCR是否成功（前置条件）
        if doc.status == 'failed' or doc.processing_stage == 'error':
            error_msg = f"OCR识别失败，跳过后续任务: {doc.error_message}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}

        try:
            doc.processing_stage = 'extracting_table'
            doc.last_processed_at = timezone.now()
            doc.save(update_fields=['processing_stage', 'last_processed_at'])
        except Exception as e:
            error_msg = f"更新状态失败: {str(e)}"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

        # 调用核心函数处理
        result = process_surrender_value_table(document_id)

        # 更新状态为已完成
        doc.processing_stage = 'table_completed'
        doc.last_processed_at = timezone.now()
        doc.save(update_fields=['processing_stage', 'last_processed_at'])

        if result['success']:
            logger.info(f"✅ 步骤4完成: 退保价值表提取成功")
        else:
            logger.warning(f"⚠️ 步骤4完成: {result.get('message', result.get('error', '未找到退保价值表'))}")

        # 自动触发下一个任务：提取无忧选退保价值表
        extract_wellness_table_task.apply_async(args=[document_id], countdown=2)

        return result

    except Exception as e:
        logger.error(f"❌ 提取退保价值表时发生异常: {e}")
        import traceback
        logger.error(traceback.format_exc())

        # 即使失败也继续下一个任务
        try:
            doc = PlanDocument.objects.get(id=document_id)
            doc.table1 = ''
            doc.processing_stage = 'table_completed'
            doc.save()
            extract_wellness_table_task.apply_async(args=[document_id], countdown=2)
        except:
            pass

        # 达到最大重试次数后继续
        if self.request.retries >= self.max_retries:
            return {'success': False, 'error': str(e)}

        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def extract_wellness_table_task(self, document_id):
    """
    步骤5：提取无忧选退保价值表 (table2字段)
    调用 content_editor_views.process_wellness_table 核心函数

    Args:
        document_id: PlanDocument的ID

    Returns:
        dict: {'success': bool, 'error': str (if failed)}
    """
    from api.content_editor_views import process_wellness_table

    try:
        logger.info("=" * 80)
        logger.info(f"💰 Celery任务开始 - 步骤5/6: 提取无忧选退保价值表 - 文档ID: {document_id}")

        # 更新状态为正在提取
        try:
            doc = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            error_msg = f"文档 {document_id} 不存在"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

        # 检查OCR是否成功（前置条件）
        if doc.status == 'failed' or doc.processing_stage == 'error':
            error_msg = f"OCR识别失败，跳过后续任务: {doc.error_message}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}

        doc.processing_stage = 'extracting_wellness_table'
        doc.last_processed_at = timezone.now()
        doc.save(update_fields=['processing_stage', 'last_processed_at'])

        # 调用核心函数处理
        result = process_wellness_table(document_id)

        # 更新状态为已完成
        doc.processing_stage = 'wellness_table_completed'
        doc.last_processed_at = timezone.now()
        doc.save(update_fields=['processing_stage', 'last_processed_at'])

        if result['success']:
            logger.info(f"✅ 步骤5完成: 无忧选退保价值表提取成功")
        else:
            logger.warning(f"⚠️ 步骤5完成: {result.get('message', result.get('error', '未找到无忧选退保价值表'))}")

        # 自动触发下一个任务：提取计划书概要
        extract_summary_task.apply_async(args=[document_id], countdown=2)

        return result

    except Exception as e:
        logger.error(f"❌ 提取无忧选退保价值表时发生异常: {e}")
        import traceback
        logger.error(traceback.format_exc())

        # 即使失败也继续下一个任务
        try:
            doc = PlanDocument.objects.get(id=document_id)
            doc.table2 = ''
            doc.processing_stage = 'wellness_table_completed'
            doc.save()
            extract_summary_task.apply_async(args=[document_id], countdown=2)
        except:
            pass

        # 达到最大重试次数后继续
        if self.request.retries >= self.max_retries:
            return {'success': False, 'error': str(e)}

        raise self.retry(exc=e)

@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def extract_summary_task(self, document_id):
    """
    步骤6：提取计划书概要（使用年度价值表数据）
    从OCR文本中提取计划书的整体概要、关键点、重要日期等信息

    Args:
        document_id: PlanDocument的ID

    Returns:
        dict: {'success': bool, 'error': str (if failed)}
    """
    try:
        logger.info("=" * 80)
        logger.info(f"📝 Celery任务开始 - 步骤6/6: 提取计划书概要 - 文档ID: {document_id}")

        # 加载文档
        try:
            doc = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            error_msg = f"文档 {document_id} 不存在"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

        # 检查OCR是否成功（前置条件）
        if doc.status == 'failed' or doc.processing_stage == 'error':
            error_msg = f"OCR识别失败，跳过后续任务: {doc.error_message}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}

        # 更新状态
        doc.processing_stage = 'extracting_summary'
        doc.last_processed_at = timezone.now()
        doc.save(update_fields=['processing_stage', 'last_processed_at'])

        if not doc.content:
            error_msg = "文档内容为空"
            logger.warning(error_msg)
            # 概要失败也不是致命错误
            doc.processing_stage = 'all_completed'
            doc.status = 'completed'
            doc.save()
            return {'success': False, 'error': error_msg}

        # 解析table1数据用于计算里程碑
        table1_data = None
        if doc.table1:
            try:
                import json
                table1_data = json.loads(doc.table1) if isinstance(doc.table1, str) else doc.table1
            except (json.JSONDecodeError, TypeError):
                logger.warning("⚠️ table1数据解析失败，将不包含里程碑信息")
                table1_data = None

        # 解析table2数据用于收入规划
        table2_data = None
        if doc.table2:
            try:
                import json
                table2_data = json.loads(doc.table2) if isinstance(doc.table2, str) else doc.table2
            except (json.JSONDecodeError, TypeError):
                logger.warning("⚠️ table2数据解析失败，将不包含收入规划")
                table2_data = None

        # 调用DeepSeek提取概要（返回Markdown文本，传入table1和table2数据）
        summary_data = extract_plan_summary(
            doc.content,
            table1_data,
            doc.annual_premium,
            doc.payment_years,
            table2_data,
            doc.insured_age
        )

        # 检查是否成功提取（空字符串表示失败）
        if not summary_data or len(summary_data.strip()) == 0:
            error_msg = "计划书概要提取失败"
            logger.warning(f"{error_msg}（但基本信息和年度表已保存）")
            # 概要失败也不是致命错误，保存空字符串
            doc.summary = ''
            doc.processing_stage = 'all_completed'
            doc.status = 'completed'
            doc.save()
            return {'success': False, 'error': error_msg}

        # 更新数据库 - 直接保存Markdown文本
        doc.summary = summary_data
        doc.processing_stage = 'all_completed'
        doc.status = 'completed'
        doc.last_processed_at = timezone.now()
        doc.save()

        logger.info(f"📝 Summary已保存到数据库，长度: {len(summary_data)} 字符")
        logger.info("✅ 步骤6完成: 计划书概要提取成功")
        logger.info(f"   - 概要长度: {len(summary_data)} 字符")
        logger.info(f"   - 概要预览: {summary_data[:100]}...")
        logger.info("=" * 80)
        logger.info(f"🎉 文档 {document_id} 所有6个任务处理完成！")
        logger.info("=" * 80)

        return {'success': True}

    except Exception as e:
        error_msg = f"提取计划书概要时发生异常: {str(e)}"
        logger.warning(f"{error_msg}（但基本信息和年度表已保存）")
        import traceback
        logger.error(traceback.format_exc())

        # 概要失败也不是致命错误
        try:
            doc = PlanDocument.objects.get(id=document_id)
            doc.processing_stage = 'all_completed'
            doc.status = 'completed'
            doc.save()
        except:
            pass

        return {'success': False, 'error': error_msg}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def extract_tablecontent_task(self, document_id):
    """
    步骤1：提取表格源代码
    从OCR文本中提取所有<table>标签的源代码并保存

    Args:
        document_id: PlanDocument的ID

    Returns:
        dict: {'success': bool, 'error': str (if failed)}
    """
    try:
        logger.info("=" * 80)
        logger.info(f"📊 Celery任务开始 - 步骤1/6: 提取表格源代码 - 文档ID: {document_id}")

        # 加载文档
        try:
            doc = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            error_msg = f"文档 {document_id} 不存在"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

        # 检查OCR是否成功（前置条件）
        if doc.status == 'failed' or doc.processing_stage == 'error':
            error_msg = f"OCR识别失败，跳过后续任务: {doc.error_message}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}

        if not doc.content:
            error_msg = "OCR内容为空，无法继续处理"
            logger.error(f"❌ {error_msg}")
            doc.processing_stage = 'error'
            doc.status = 'failed'
            doc.error_message = error_msg
            doc.save()
            return {'success': False, 'error': error_msg}

        # 使用正则表达式提取所有<table>标签
        import re
        table_regex = re.compile(r'<table[^>]*>([\s\S]*?)</table>', re.IGNORECASE)
        matches = table_regex.findall(doc.content)

        if matches:
            # 提取完整的<table>...</table>
            tables = []
            for match_obj in table_regex.finditer(doc.content):
                tables.append(match_obj.group(0))

            # 合并所有表格，使用双换行分隔
            tablecontent = '\n\n'.join(tables)
            doc.tablecontent = tablecontent

            logger.info(f"✅ 提取到 {len(tables)} 个表格")
            logger.info(f"   - 总长度: {len(tablecontent)} 字符")

            doc.save(update_fields=['tablecontent'])

            logger.info("✅ 步骤1完成: 表格源代码提取成功")
            logger.info("=" * 80)

            # 自动触发下一个任务：提取基本信息
            extract_basic_info_task.apply_async(args=[document_id], countdown=2)

            return {'success': True}
        else:
            # 理论上不应该到这里，因为webhook已经预检查过了
            # 但保留作为二次保护
            error_msg = "未检测到表格元素（任务链二次检查）"
            logger.warning(f"⚠️ {error_msg}")
            doc.tablecontent = ''
            doc.save(update_fields=['tablecontent'])
            # 继续后续任务，因为可能是边缘情况
            extract_basic_info_task.apply_async(args=[document_id], countdown=2)
            return {'success': True}

    except Exception as e:
        error_msg = f"提取表格源代码时发生异常: {str(e)}"
        logger.error(f"❌ {error_msg}")
        import traceback
        logger.error(traceback.format_exc())

        try:
            doc = PlanDocument.objects.get(id=document_id)
            doc.tablecontent = ''
            doc.processing_stage = 'error'
            doc.status = 'failed'
            doc.error_message = error_msg
            doc.save()
        except Exception as save_error:
            logger.error(f"保存错误状态失败: {save_error}")

        logger.info("⛔ 任务链已终止：表格提取异常")
        return {'success': False, 'error': error_msg, 'terminate': True}


@shared_task(bind=True, max_retries=2, default_retry_delay=60)
def extract_tablesummary_task(self, document_id):
    """
    步骤3：提取表格概要
    使用DeepSeek API分析OCR内容中的表格结构
    提取表格名称、行数、字段信息

    Args:
        document_id: PlanDocument的ID

    Returns:
        dict: {'success': bool, 'error': str (if failed)}
    """
    try:
        logger.info("=" * 80)
        logger.info(f"📋 Celery任务开始 - 步骤3/6: 提取表格概要 - 文档ID: {document_id}")

        # 加载文档
        try:
            doc = PlanDocument.objects.get(id=document_id)
        except PlanDocument.DoesNotExist:
            error_msg = f"文档 {document_id} 不存在"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

        # 检查OCR是否成功（前置条件）
        if doc.status == 'failed' or doc.processing_stage == 'error':
            error_msg = f"OCR识别失败，跳过后续任务: {doc.error_message}"
            logger.error(f"❌ {error_msg}")
            return {'success': False, 'error': error_msg}

        if not doc.content:
            error_msg = "文档内容为空"
            logger.warning(error_msg)
            # 概要失败也不是致命错误
            doc.tablesummary = ''
            doc.save(update_fields=['tablesummary'])
            # 继续下一个任务
            extract_table_task.apply_async(args=[document_id], countdown=2)
            return {'success': False, 'error': error_msg}

        # 获取DeepSeek API密钥
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            error_msg = 'DEEPSEEK_API_KEY环境变量未设置'
            logger.error(f'❌ {error_msg}')
            # 概要失败也不是致命错误
            doc.tablesummary = ''
            doc.save(update_fields=['tablesummary'])
            # 继续下一个任务
            extract_table_task.apply_async(args=[document_id], countdown=2)
            return {'success': False, 'error': error_msg}

        # 初始化DeepSeek客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # 构建提示词（与content_editor_views.py中完全一致）
        prompt = f"""以保单年度终结为坐标，分析以下保险计划书中的所有表格。

要求：
1. 识别所有以"保单年度终结"为坐标的表格
2. 有些表格可能跨度好几个页面，但只算一张表，请完整识别
3. 对每个表格提取：表详细名称、行数、基本字段

只输出结果，不要有任何解释说明。

输出格式示例：
1.
表名：詳細說明 - 退保價值 (只根據基本計劃計算)
行数：100行
基本字段：保单年度终结,缴付保费总额,退保价值(保证金额(保证现金价值),非保證金額(续期红利),总额),累積已支付非保證入息+總退保價值

2.
表名：身故賠償
行数：50行
基本字段：保单年度终结,身故赔偿(保证金额,非保证金额,总额)

计划书内容：
{doc.content[:120000]}

请直接返回分析结果，不要包含markdown代码块标记。"""

        logger.info("⏳ 开始调用 DeepSeek API 分析表格结构")
        logger.info(f"   OCR内容长度: {len(doc.content)} 字符")
        logger.info(f"   使用内容长度: {min(len(doc.content), 120000)} 字符")

        # 调用DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的保险文档分析助手，擅长识别和分析表格结构。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )

        # 提取结果
        content = response.choices[0].message.content.strip()
        logger.info(f"📦 DeepSeek API返回，长度: {len(content)} 字符")

        # 清理可能的代码块标记
        if content.startswith('```'):
            lines = content.split('\n')
            # 移除第一行（```）和最后一行（```）
            if len(lines) > 2 and lines[-1].strip() == '```':
                content = '\n'.join(lines[1:-1])
            elif len(lines) > 1:
                content = '\n'.join(lines[1:])

        # 最终检查
        if not content or len(content.strip()) == 0:
            error_msg = "表格概要提取失败，返回内容为空"
            logger.warning(f"{error_msg}（但其他数据已保存）")
            # 概要失败也不是致命错误，保存空字符串
            doc.tablesummary = ''
            doc.save(update_fields=['tablesummary'])
            # 继续下一个任务
            extract_table_task.apply_async(args=[document_id], countdown=2)
            return {'success': False, 'error': error_msg}

        # 更新数据库 - 直接保存文本
        doc.tablesummary = content
        doc.last_processed_at = timezone.now()
        doc.save(update_fields=['tablesummary', 'last_processed_at'])

        logger.info(f"📋 表格概要已保存到数据库，长度: {len(content)} 字符")

        # 更新会员使用统计
        if doc.user:
            from .models import Membership
            try:
                membership = Membership.objects.get(user=doc.user)
                membership.documents_created += 1
                membership.save()
                logger.info(f"📊 会员已创建计划书数: {membership.documents_created}")
            except Membership.DoesNotExist:
                pass

        logger.info("✅ 步骤3完成: 表格概要提取成功")
        logger.info(f"   - 概要长度: {len(content)} 字符")
        logger.info(f"   - 概要预览: {content[:200]}...")

        # 自动触发下一个任务：提取年度价值表
        extract_table_task.apply_async(args=[document_id], countdown=2)

        return {'success': True}

    except Exception as e:
        error_msg = f"提取表格概要时发生异常: {str(e)}"
        logger.warning(f"{error_msg}（但其他数据已保存）")
        import traceback
        logger.error(traceback.format_exc())

        # 概要失败也不是致命错误
        try:
            doc = PlanDocument.objects.get(id=document_id)
            doc.tablesummary = ''
            doc.save(update_fields=['tablesummary'])
            # 继续下一个任务
            extract_table_task.apply_async(args=[document_id], countdown=2)
        except:
            pass

        return {'success': False, 'error': error_msg}


@shared_task
def process_document_pipeline(document_id):
    """
    完整的文档处理流水线入口
    按顺序触发六个任务：表格源代码 -> 基本信息 -> 表格概要 -> 年度价值表 -> 无忧选退保价值表 -> 计划书概要

    Args:
        document_id: PlanDocument的ID
    """
    logger.info(f"🚀 启动文档处理流水线（6个任务）- 文档ID: {document_id}")

    # 触发第一个任务：提取表格源代码，后续任务会自动链式触发
    extract_tablecontent_task.apply_async(args=[document_id])

    return {'status': 'pipeline_started', 'document_id': document_id}
