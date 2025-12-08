# CosyVoice 使用说明

## 概述

系统已成功迁移到阿里云CosyVoice-v3-plus语音合成服务。

## 标准语音合成

### 可用语音

**中文女声:**
- longxiaochun (龙小春)
- longshuling (龙舒灵)
- longxiaohui (龙晓晖)
- longjingqi (龙靖琪)
- longwan (龙婉)
- longjieer (龙杰儿)
- longxiaomei (龙小妹)
- longmeier (龙美儿)

**中文男声:**
- longjun (龙钧)
- longmingze (龙明泽)
- longtianye (龙天野)
- longxiaoche (龙小澈)
- longhaotian (龙浩天)
- longjingxuan (龙景轩)

**英文:**
- stella (女声)
- andy (男声)

**多语种:**
- betty (女声)
- william (男声)

### API调用示例

```bash
curl -X POST http://localhost:8017/api/tts/synthesize/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，世界",
    "voice": "longxiaochun",
    "rate": "0%",
    "pitch": "0%"
  }'
```

## 个人语音克隆

### 重要说明

创建个人语音需要提供**公网可访问的音频URL**（必须是http://或https://开头）。

### 方法1: 直接提供公网URL

如果您的音频文件已经托管在公网服务器上：

```bash
curl -X POST http://localhost:8017/api/personal-voice/create/ \
  -F "voice_name=我的声音" \
  -F "voice_talent_name=张三" \
  -F "company_name=我的公司" \
  -F "audio_url=https://your-server.com/path/to/audio.wav"
```

### 方法2: 上传文件（推荐）

系统会自动将上传的文件转换为公网可访问的URL：

```bash
curl -X POST http://localhost:8017/api/personal-voice/create/ \
  -F "voice_name=我的声音" \
  -F "voice_talent_name=张三" \
  -F "company_name=我的公司" \
  -F "voice_sample=@/path/to/your/audio.wav"
```

**音频要求:**
- 格式: WAV, MP3, 或其他常见格式
- 时长: 建议10-60秒
- 采样率: 系统会自动转换为16kHz
- 声道: 系统会自动转换为单声道

### 配置服务器域名

在 `.env` 文件中配置服务器域名（默认使用 `https://hongkong.xingke888.com`）：

```bash
SERVER_DOMAIN=https://your-domain.com
```

## 故障排查

### 问题: "音频URL格式错误"

**原因:** 音频URL不是http://或https://开头

**解决方案:**
1. 确保上传的文件可以通过Web服务器访问
2. 检查 `SERVER_DOMAIN` 环境变量配置是否正确
3. 确认Nginx/Web服务器配置允许访问 `/media/personal_voices/` 目录

### 问题: "创建音色失败: InvalidURL"

**原因:** 阿里云无法访问提供的URL

**解决方案:**
1. 确认URL可以从公网访问（不能是localhost或内网IP）
2. 确认服务器防火墙允许外部访问
3. 测试URL: `curl -I https://your-domain.com/media/personal_voices/xxx/voice_sample.wav`

### 问题: "Engine return error code: 418"

**原因:**
1. API Key可能没有开通cosyvoice-v3-plus服务
2. 账户余额不足或配额用完
3. 语音名称不支持

**解决方案:**
1. 登录阿里云DashScope控制台检查服务状态
2. 确认账户有足够余额和配额
3. 联系阿里云技术支持开通服务

## 示例: 使用Nginx配置静态文件访问

确保Nginx配置中包含media文件访问：

```nginx
location /media/ {
    alias /var/www/harry-insurance2/media/;
    expires 30d;
    access_log off;
}
```

重启Nginx:
```bash
sudo systemctl reload nginx
```

## 测试音频URL可访问性

```bash
# 替换为您的实际URL
curl -I https://hongkong.xingke888.com/media/personal_voices/pv-xxx/voice_sample.wav
```

应该返回 `200 OK` 状态码。
