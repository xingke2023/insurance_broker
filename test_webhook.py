#!/usr/bin/env python3
"""
测试OCR Webhook接口
模拟远程OCR服务完成后回调本地webhook
"""

import requests
import json

# 配置
WEBHOOK_URL = "http://localhost:8017/api/ocr/webhook/"
# 或使用公网地址测试
# WEBHOOK_URL = "https://hongkong.xingke888.com/api/ocr/webhook/"

def test_webhook_with_existing_result():
    """
    测试webhook：使用已存在的OCR结果
    """
    print("="*80)
    print("🧪 测试OCR Webhook接口")
    print("="*80)

    # 构造webhook回调数据
    # 这些数据通常由远程OCR服务在完成后发送
    # 使用真实的任务c6b94e26的数据进行测试
    webhook_data = {
        "task_id": "c6b94e26",  # 真实的任务ID
        "status": "finished",
        "result_dir": "/root/deepseek/DeepSeek-OCR-Web/workspace/results/ocr_task_c6b94e26_20251115_065003_7ef11bba",  # 真实的结果目录
        "file_name": "宏摯傳承保障計劃 5.pdf",  # 真实的文件名
        "user_id": 15,  # 测试用户ID
        # "signature": "test_signature"  # 可选：安全签名
    }

    print("📤 发送Webhook回调请求...")
    print(f"URL: {WEBHOOK_URL}")
    print(f"数据: {json.dumps(webhook_data, indent=2, ensure_ascii=False)}")
    print()

    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_data,
            timeout=60
        )

        print(f"📥 响应状态码: {response.status_code}")
        print(f"📥 响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        print()

        if response.status_code == 201:
            result = response.json()
            if result.get('status') == 'success':
                document_id = result.get('document_id')
                print(f"✅ Webhook处理成功！")
                print(f"📄 新文档ID: {document_id}")
                print(f"🚀 Celery AI分析任务已启动")
                print()
                print("💡 提示：")
                print(f"   - 可以在计划书列表中查看ID {document_id}的文档")
                print(f"   - Celery会自动分析基本信息、年度表和概要")
                print(f"   - 预计1-2分钟后完成所有分析")
                return document_id
            else:
                print(f"❌ Webhook处理失败: {result.get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ 请求失败: {e}")
        import traceback
        traceback.print_exc()

    print("="*80)
    return None


def check_document_status(document_id):
    """
    检查文档处理状态
    """
    import time

    print(f"\n🔍 检查文档 ID {document_id} 的处理状态...")
    print("="*80)

    status_url = f"http://localhost:8017/api/ocr/documents/{document_id}/status/"

    for i in range(30):  # 最多检查30次（约1分钟）
        try:
            response = requests.get(status_url)
            if response.status_code == 200:
                data = response.json()
                stage = data['data']['processing_stage']
                progress = data['data']['progress_percentage']
                status = data['data']['status']

                print(f"[{i+1}/30] 状态: {status} | 阶段: {stage} | 进度: {progress}%")

                if stage == 'all_completed':
                    print("\n✅ 所有分析已完成！")
                    print("="*80)
                    return True

                if stage == 'error':
                    print(f"\n❌ 处理出错: {data['data'].get('error_message')}")
                    print("="*80)
                    return False

            time.sleep(2)  # 每2秒检查一次

        except Exception as e:
            print(f"检查失败: {e}")
            time.sleep(2)

    print("\n⏱️  超时：30次检查后仍未完成")
    print("="*80)
    return False


if __name__ == '__main__':
    import time

    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║          OCR Webhook 接口测试                                ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    # 测试webhook
    document_id = test_webhook_with_existing_result()

    if document_id:
        print("\n等待3秒后开始检查处理状态...\n")
        time.sleep(3)

        # 检查处理状态
        check_document_status(document_id)

        print("\n")
        print("🎉 测试完成！")
        print(f"   可以访问以下URL查看详情：")
        print(f"   http://localhost:8017/api/ocr/documents/{document_id}/")
        print()
