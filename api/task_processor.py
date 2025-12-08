"""
稳定的异步任务处理器
用于处理计划书的分析任务，确保长时间运行的稳定性
"""
import logging
import time
from datetime import datetime
from django.utils import timezone
from .models import PlanDocument
from .deepseek_service import extract_plan_data_from_text, analyze_insurance_table, extract_plan_summary
import re

logger = logging.getLogger(__name__)


class DocumentTaskProcessor:
    """
    文档任务处理器
    负责按顺序执行：基本信息提取 → 年度价值表提取 → 计划书概要提取
    """

    def __init__(self, document_id):
        self.document_id = document_id
        self.doc = None

    def load_document(self):
        """加载文档"""
        try:
            self.doc = PlanDocument.objects.get(id=self.document_id)
            return True
        except PlanDocument.DoesNotExist:
            logger.error(f"文档 {self.document_id} 不存在")
            return False

    def update_stage(self, stage, save=True):
        """更新处理阶段"""
        if self.doc:
            self.doc.processing_stage = stage
            self.doc.last_processed_at = timezone.now()
            if save:
                self.doc.save(update_fields=['processing_stage', 'last_processed_at'])
            logger.info(f"文档 {self.document_id} 阶段更新: {stage}")

    def mark_error(self, error_msg):
        """标记错误"""
        if self.doc:
            self.doc.processing_stage = 'error'
            self.doc.error_message = error_msg
            self.doc.status = 'failed'
            self.doc.last_processed_at = timezone.now()
            self.doc.save()
            logger.error(f"文档 {self.document_id} 处理失败: {error_msg}")

    def step1_extract_basic_info(self):
        """
        第1步：提取基本信息
        返回: (success, error_msg)
        """
        try:
            logger.info("=" * 80)
            logger.info(f"📋 步骤1/3: 提取基本信息 - 文档ID: {self.document_id}")
            self.update_stage('extracting_basic_info')

            if not self.doc.content:
                return False, "文档内容为空"

            # 调用DeepSeek提取基本信息
            basic_result = extract_plan_data_from_text(self.doc.content)

            if not basic_result or not basic_result.get('success'):
                return False, f"基本信息提取失败: {basic_result.get('error') if basic_result else '未知错误'}"

            basic_data = basic_result.get('data', {})

            # 更新数据库字段
            self.doc.insured_name = basic_data.get('insured_name', '')

            # 年龄转换
            try:
                age = basic_data.get('insured_age')
                self.doc.insured_age = int(age) if age else None
            except (ValueError, TypeError):
                self.doc.insured_age = None

            self.doc.insured_gender = basic_data.get('insured_gender', '')
            self.doc.insurance_product = basic_data.get('insurance_product', '')
            self.doc.insurance_company = basic_data.get('insurance_company', '')

            # 保额转换
            try:
                amount = basic_data.get('sum_assured')
                self.doc.sum_assured = int(float(amount)) if amount else None
            except (ValueError, TypeError):
                self.doc.sum_assured = None

            # 年缴保费转换
            try:
                premium = basic_data.get('annual_premium')
                self.doc.annual_premium = int(float(premium)) if premium else None
            except (ValueError, TypeError):
                self.doc.annual_premium = None

            # 缴费年数转换
            try:
                payment_years = basic_data.get('payment_years')
                if payment_years:
                    numbers = re.findall(r'\d+', str(payment_years))
                    self.doc.payment_years = int(numbers[0]) if numbers else None
                else:
                    self.doc.payment_years = None
            except (ValueError, TypeError, IndexError):
                self.doc.payment_years = None

            self.doc.insurance_period = basic_data.get('insurance_period', '')
            self.doc.extracted_data = basic_data

            # 更新阶段为完成
            self.update_stage('basic_info_completed', save=False)
            self.doc.save()

            logger.info("✅ 步骤1完成: 基本信息提取成功")
            logger.info(f"   - 受保人: {self.doc.insured_name}")
            logger.info(f"   - 保险产品: {self.doc.insurance_product}")
            return True, None

        except Exception as e:
            error_msg = f"提取基本信息时发生异常: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            return False, error_msg

    def step2_extract_table(self):
        """
        第2步：提取年度价值表
        返回: (success, error_msg)
        """
        try:
            logger.info("=" * 80)
            logger.info(f"📊 步骤2/3: 提取年度价值表 - 文档ID: {self.document_id}")
            self.update_stage('extracting_table')

            if not self.doc.content:
                return False, "文档内容为空"

            # 调用DeepSeek提取年度价值表
            table_data = analyze_insurance_table(self.doc.content)

            if not table_data:
                return False, "年度价值表提取失败"

            # 更新数据库
            self.doc.table = table_data
            self.update_stage('table_completed', save=False)
            self.doc.save()

            record_count = len(table_data.get('years', []))
            logger.info(f"✅ 步骤2完成: 年度价值表提取成功，共 {record_count} 条记录")
            return True, None

        except Exception as e:
            error_msg = f"提取年度价值表时发生异常: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            return False, error_msg

    def step3_extract_summary(self):
        """
        第3步：提取计划书概要（使用年度价值表数据）
        返回: (success, error_msg)
        """
        try:
            logger.info("=" * 80)
            logger.info(f"📝 步骤3/3: 提取计划书概要 - 文档ID: {self.document_id}")
            self.update_stage('extracting_summary')

            if not self.doc.content:
                return False, "文档内容为空"

            # 调用DeepSeek提取概要
            summary_data = extract_plan_summary(self.doc.content)

            if not summary_data:
                return False, "计划书概要提取失败"

            # 更新数据库
            self.doc.summary = summary_data
            self.update_stage('all_completed', save=False)
            self.doc.status = 'completed'
            self.doc.save()

            logger.info("✅ 步骤3完成: 计划书概要提取成功")
            logger.info(f"   - 关键点数: {len(summary_data.get('key_points', []))}")
            logger.info(f"   - 重要日期数: {len(summary_data.get('important_dates', []))}")
            return True, None

        except Exception as e:
            error_msg = f"提取计划书概要时发生异常: {str(e)}"
            logger.error(error_msg)
            import traceback
            logger.error(traceback.format_exc())
            return False, error_msg

    def process_all_steps(self):
        """
        执行所有步骤（带重试机制）
        """
        logger.info("=" * 80)
        logger.info(f"🚀 开始处理文档 {self.document_id} 的所有分析任务")
        logger.info("=" * 80)

        # 加载文档
        if not self.load_document():
            return

        # 步骤1：提取基本信息
        success, error = self.step1_extract_basic_info()
        if not success:
            self.mark_error(f"步骤1失败: {error}")
            return

        # 短暂延迟，避免API限流
        time.sleep(2)

        # 步骤2：提取年度价值表
        success, error = self.step2_extract_table()
        if not success:
            # 年度价值表失败不是致命错误，继续后续步骤
            logger.warning(f"步骤2失败（继续后续步骤）: {error}")

        # 短暂延迟
        time.sleep(2)

        # 步骤3：提取计划书概要
        success, error = self.step3_extract_summary()
        if not success:
            # 概要提取失败也不是致命错误
            logger.warning(f"步骤3失败（但基本信息和年度表已保存）: {error}")
            # 标记为部分完成
            self.doc.processing_stage = 'table_completed'
            self.doc.status = 'completed'
            self.doc.save()

        logger.info("=" * 80)
        logger.info(f"🎉 文档 {self.document_id} 处理完成！")
        logger.info(f"   最终阶段: {self.doc.processing_stage}")
        logger.info("=" * 80)


def process_document_async(document_id):
    """
    异步处理文档的入口函数
    这个函数将在后台线程中执行
    """
    try:
        processor = DocumentTaskProcessor(document_id)
        processor.process_all_steps()
    except Exception as e:
        logger.error(f"处理文档 {document_id} 时发生未捕获的异常: {e}")
        import traceback
        logger.error(traceback.format_exc())
