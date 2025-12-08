# 远程OCR服务修改指南

## 📋 目标

让远程OCR服务（https://yu.xingke888.com）支持：
1. 接收客户端传来的 `task_id` 和 `webhook_url`
2. OCR完成后自动回调webhook

---

## 🔍 需要修改的内容

### **第1步：找到处理 `/api/start` 的代码**

通常在主文件（如 `app.py`, `main.py`, `server.py` 等）中。

**查找方法：**
```bash
cd /root/deepseek/DeepSeek-OCR-Web  # 或者OCR服务的目录
grep -r "api/start" *.py
grep -r "@app.route.*start" *.py
```

---

### **第2步：修改 `/api/start` 接口**

**原来的代码可能是：**
```python
@app.route('/api/start', methods=['POST'])
def start_ocr():
    data = request.json
    file_path = data.get('file_path')
    prompt = data.get('prompt', '')

    # 生成task_id
    task_id = generate_unique_id()

    # 启动OCR处理
    start_processing(task_id, file_path, prompt)

    return jsonify({
        'status': 'running',
        'task_id': task_id
    })
```

**修改为（添加task_id和webhook_url支持）：**
```python
# 全局字典存储webhook信息（可以改用Redis更好）
task_webhooks = {}

@app.route('/api/start', methods=['POST'])
def start_ocr():
    data = request.json
    file_path = data.get('file_path')
    prompt = data.get('prompt', '')
    task_id = data.get('task_id')  # ✅ 新增：接收客户端的task_id
    webhook_url = data.get('webhook_url')  # ✅ 新增：接收webhook URL

    # 如果客户端没有提供task_id，自动生成一个
    if not task_id:
        task_id = generate_unique_id()

    # ✅ 新增：保存webhook信息
    if webhook_url:
        task_webhooks[task_id] = webhook_url
        print(f"📌 保存webhook: task_id={task_id}, url={webhook_url}")

    # 启动OCR处理
    start_processing(task_id, file_path, prompt)

    return jsonify({
        'status': 'running',
        'task_id': task_id
    })
```

---

### **第3步：修改OCR完成回调**

找到OCR处理完成的代码位置（通常在异步任务完成的回调函数中）。

**查找方法：**
```bash
grep -r "finished\|completed\|done" *.py
grep -r "result_dir\|output" *.py
```

**添加webhook调用：**
```python
def on_ocr_complete(task_id, result_dir, success=True):
    """OCR完成后的回调函数"""

    # 原有的逻辑...
    print(f"✅ OCR完成: task_id={task_id}, result_dir={result_dir}")

    # ✅ 新增：检查并调用webhook
    webhook_url = task_webhooks.get(task_id)
    if webhook_url:
        call_webhook_async(webhook_url, task_id, result_dir)
        # 调用后可以删除，避免内存泄漏
        del task_webhooks[task_id]
    else:
        print(f"⚠️  任务 {task_id} 没有配置webhook")


def call_webhook_async(webhook_url, task_id, result_dir):
    """异步调用webhook（避免阻塞主线程）"""
    import threading
    import requests

    def call_webhook():
        try:
            webhook_data = {
                'task_id': task_id,
                'result_dir': result_dir
            }

            print(f"🔔 调用webhook: {webhook_url}")
            print(f"   数据: {webhook_data}")

            response = requests.post(
                webhook_url,
                json=webhook_data,
                timeout=30
            )

            if response.status_code == 200:
                print(f"✅ Webhook调用成功: {task_id}")
            else:
                print(f"❌ Webhook调用失败: {response.status_code}")
                print(f"   响应: {response.text}")

        except Exception as e:
            print(f"❌ Webhook异常: {e}")
            import traceback
            traceback.print_exc()

    # 在新线程中调用，不阻塞主流程
    thread = threading.Thread(target=call_webhook)
    thread.daemon = True
    thread.start()
```

---

## 📝 完整示例

假设OCR服务使用Flask，完整修改示例：

```python
from flask import Flask, request, jsonify
import requests
import threading

app = Flask(__name__)

# 存储webhook信息
task_webhooks = {}

@app.route('/api/start', methods=['POST'])
def start_ocr():
    """接收OCR任务"""
    data = request.json
    file_path = data.get('file_path')
    prompt = data.get('prompt', '')
    task_id = data.get('task_id')  # ← 接收task_id
    webhook_url = data.get('webhook_url')  # ← 接收webhook_url

    if not task_id:
        task_id = generate_unique_id()

    # 保存webhook
    if webhook_url:
        task_webhooks[task_id] = webhook_url

    # 启动OCR（异步）
    start_ocr_processing(task_id, file_path, prompt)

    return jsonify({
        'status': 'running',
        'task_id': task_id
    })


def on_ocr_finished(task_id, result_dir):
    """OCR完成回调"""
    print(f"✅ OCR完成: {task_id}")

    # 调用webhook
    webhook_url = task_webhooks.pop(task_id, None)
    if webhook_url:
        threading.Thread(
            target=lambda: call_webhook(webhook_url, task_id, result_dir),
            daemon=True
        ).start()


def call_webhook(url, task_id, result_dir):
    """调用webhook"""
    try:
        response = requests.post(url, json={
            'task_id': task_id,
            'result_dir': result_dir
        }, timeout=30)
        print(f"Webhook: {response.status_code}")
    except Exception as e:
        print(f"Webhook失败: {e}")
```

---

## 🧪 测试webhook

修改完成后，在远程OCR服务器上测试：

```python
# test_webhook_call.py
import requests

# 模拟OCR完成，调用本地webhook
webhook_url = "https://hongkong.xingke888.com/api/ocr/webhook/"

response = requests.post(webhook_url, json={
    'task_id': '61',  # 使用一个测试文档ID
    'result_dir': '/root/deepseek/DeepSeek-OCR-Web/workspace/results/...'
})

print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")
```

---

## ✅ 验证清单

修改完成后，检查以下几点：

- [ ] `/api/start` 接口能接收 `task_id` 参数
- [ ] `/api/start` 接口能接收 `webhook_url` 参数
- [ ] `task_id` 和 `webhook_url` 被正确存储
- [ ] OCR完成时能找到对应的webhook_url
- [ ] webhook调用使用了异步方式（不阻塞主线程）
- [ ] webhook调用携带了 `task_id` 和 `result_dir`
- [ ] 调用后从存储中删除webhook信息（防止内存泄漏）

---

## 🚀 上线后的工作流程

```
用户点击"开始分析"
  ↓
前端创建本地文档 → 获得document_id
  ↓
前端提交OCR任务(task_id=document_id, webhook_url=...)
  ↓
远程OCR接收并保存webhook信息
  ↓
OCR处理中...（用户可关闭浏览器）
  ↓
OCR完成 → 自动调用webhook
  ↓
本地服务器接收webhook → 下载OCR结果 → 触发AI分析
  ↓
用户重新打开页面 → 查看完成的结果
```

---

## 📞 需要帮助？

如果在修改过程中遇到问题，请提供：
1. 远程OCR服务的代码结构（目录列表）
2. 主要的Python文件内容
3. 报错信息

我可以提供更具体的修改方案。
