#!/bin/bash
# 测试个人语音创建功能

echo "======================================"
echo "个人语音创建测试"
echo "======================================"

# 使用阿里云官方示例音频
AUDIO_URL="https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/cosyvoice/cosyvoice-zeroshot-sample.wav"

echo ""
echo "步骤1: 测试音频URL可访问性"
echo "URL: $AUDIO_URL"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$AUDIO_URL")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ 音频URL可访问 (HTTP $HTTP_CODE)"
else
    echo "❌ 音频URL无法访问 (HTTP $HTTP_CODE)"
    exit 1
fi

echo ""
echo "步骤2: 创建个人语音"
echo "正在提交请求..."

RESPONSE=$(curl -s -X POST http://localhost:8017/api/personal-voice/create/ \
  -F "voice_name=测试语音$(date +%s)" \
  -F "voice_talent_name=测试用户" \
  -F "company_name=测试公司" \
  -F "audio_url=$AUDIO_URL")

echo ""
echo "响应结果:"
echo "$RESPONSE" | python3 -m json.tool

# 检查是否成功
STATUS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'error'))")

if [ "$STATUS" = "success" ]; then
    echo ""
    echo "✅ 个人语音创建成功！"

    # 提取voice_id
    VOICE_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('voice', {}).get('voice_id', ''))")

    if [ -n "$VOICE_ID" ]; then
        echo ""
        echo "步骤3: 使用创建的语音合成测试"
        echo "Voice ID: $VOICE_ID"

        SYNTH_RESPONSE=$(curl -s -X POST http://localhost:8017/api/personal-voice/synthesize/ \
          -H "Content-Type: application/json" \
          -d "{\"text\":\"你好，这是使用复刻语音的测试\",\"voice_id\":\"$VOICE_ID\"}")

        echo "合成结果:"
        echo "$SYNTH_RESPONSE" | python3 -m json.tool

        SYNTH_STATUS=$(echo "$SYNTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'error'))")

        if [ "$SYNTH_STATUS" = "success" ]; then
            echo ""
            echo "✅ 语音合成成功！"
            AUDIO_URL=$(echo "$SYNTH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('audio_url', ''))")
            echo "音频URL: http://localhost:8017$AUDIO_URL"
        else
            echo ""
            echo "❌ 语音合成失败"
        fi
    fi
else
    echo ""
    echo "❌ 个人语音创建失败"
    MESSAGE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', 'Unknown error'))")
    echo "错误信息: $MESSAGE"
fi

echo ""
echo "======================================"
echo "测试完成"
echo "======================================"
