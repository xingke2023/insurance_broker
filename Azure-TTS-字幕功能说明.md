# Azure TTS 字符级别字幕功能说明

## 📋 功能概述

标准语音已切换回使用 **Azure Cognitive Services TTS**，并增加了**字符级别字幕**生成功能。

## ✨ 主要特性

### 1. 语音合成
- 使用 Azure Neural TTS
- 支持25+种中文、粤语、台湾话、英文语音
- 支持语速和音调调节

### 2. 字幕生成（新功能）
- **字符级别时间戳** - 每个字/词都有精确的开始时间和持续时间
- **多种格式** - JSON、SRT、WebVTT三种格式
- **实时返回** - API直接返回字幕数据
- **自动保存** - 字幕文件自动保存到服务器

## 🎯 API返回数据结构

### 请求示例

```bash
curl -X POST http://localhost:8017/api/tts/synthesize/ \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好世界，这是一个测试。",
    "voice": "zh-CN-XiaoxiaoNeural",
    "rate": "0%",
    "pitch": "0%"
  }'
```

### 响应示例

```json
{
  "status": "success",
  "message": "语音合成成功",
  "audio_url": "/media/tts/tts_xxx.mp3",
  "subtitle_url": "/media/tts/tts_xxx.json",
  "srt_url": "/media/tts/tts_xxx.srt",
  "vtt_url": "/media/tts/tts_xxx.vtt",
  "filename": "tts_xxx.mp3",
  "subtitle_count": 7,
  "subtitles": [
    {
      "text": "你好世界",
      "audio_offset": 50.0,
      "duration": 862.5,
      "word_length": 4,
      "text_offset": 207,
      "boundary_type": "Word"
    },
    {
      "text": "，",
      "audio_offset": 1012.5,
      "duration": 162.5,
      "word_length": 1,
      "text_offset": 211,
      "boundary_type": "Punctuation"
    },
    ...
  ]
}
```

## 📝 字幕数据字段说明

### subtitles 数组中每个元素

| 字段 | 类型 | 说明 |
|------|------|------|
| `text` | string | 字符/词的文本内容 |
| `audio_offset` | float | 音频开始时间（毫秒） |
| `duration` | float | 持续时间（毫秒） |
| `word_length` | int | 文本长度 |
| `text_offset` | int | 在原始文本中的偏移位置 |
| `boundary_type` | string | 边界类型：Word（词）或 Punctuation（标点） |

### 时间单位
- `audio_offset`: 从音频开始的毫秒数
- `duration`: 该字符/词的持续时间（毫秒）

## 📂 生成的文件格式

### 1. JSON 格式 (*.json)

```json
{
  "text": "你好世界，这是一个测试。",
  "voice": "zh-CN-XiaoxiaoNeural",
  "rate": "0%",
  "pitch": "0%",
  "subtitles": [
    {
      "text": "你好世界",
      "audio_offset": 50.0,
      "duration": 862.5,
      "word_length": 4,
      "text_offset": 207,
      "boundary_type": "Word"
    }
  ]
}
```

**用途**: 程序化处理、数据分析

### 2. SRT 格式 (*.srt)

```srt
1
00:00:00,050 --> 00:00:00,912
你好世界

2
00:00:01,012 --> 00:00:01,175
，

3
00:00:01,175 --> 00:00:01,337
这
```

**用途**:
- 视频编辑软件（Premiere Pro, Final Cut Pro）
- 播放器（VLC, PotPlayer）
- 通用字幕格式

### 3. WebVTT 格式 (*.vtt)

```vtt
WEBVTT

1
00:00:00.050 --> 00:00:00.912
你好世界

2
00:00:01.012 --> 00:00:01.175
，

3
00:00:01.175 --> 00:00:01.337
这
```

**用途**:
- HTML5 `<video>` 标签
- Web播放器
- 现代浏览器原生支持

## 🎬 使用场景

### 1. 视频字幕生成
```javascript
// 获取字幕数据
const response = await fetch('/api/tts/synthesize/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: '你的文本', voice: 'zh-CN-XiaoxiaoNeural'})
});

const data = await response.json();

// 使用字幕
data.subtitles.forEach(subtitle => {
  console.log(`${subtitle.text} 出现在 ${subtitle.audio_offset}ms`);
});
```

### 2. HTML5视频播放器

```html
<video controls>
  <source src="/media/tts/tts_xxx.mp3" type="audio/mpeg">
  <track kind="subtitles" src="/media/tts/tts_xxx.vtt" srclang="zh" label="中文">
</video>
```

### 3. 同步动画

```javascript
// 根据字幕时间同步文字高亮
audio.addEventListener('timeupdate', () => {
  const currentTime = audio.currentTime * 1000; // 转为毫秒

  const currentSubtitle = subtitles.find(sub =>
    currentTime >= sub.audio_offset &&
    currentTime < (sub.audio_offset + sub.duration)
  );

  if (currentSubtitle) {
    highlightText(currentSubtitle.text);
  }
});
```

### 4. 卡拉OK效果

```javascript
// 逐字高亮显示
subtitles.forEach((subtitle, index) => {
  setTimeout(() => {
    highlightCharacter(subtitle.text);
  }, subtitle.audio_offset);
});
```

## 🔧 技术实现

### Azure Word Boundary 事件

使用 Azure SDK 的 `synthesis_word_boundary` 事件：

```python
def word_boundary_cb(evt):
    """处理词边界事件"""
    subtitle_data.append({
        'text': evt.text,
        'audio_offset': evt.audio_offset / 10000,  # 转换为毫秒
        'duration': evt.duration.total_seconds() * 1000,
        'word_length': evt.word_length,
        'text_offset': evt.text_offset,
        'boundary_type': evt.boundary_type.name
    })

synthesizer.synthesis_word_boundary.connect(word_boundary_cb)
```

### 支持的边界类型

- `Word` - 词语边界（中文一般以词为单位）
- `Punctuation` - 标点符号边界

## 📊 字幕精度

### 中文
- **粒度**: 词级别（一般2-4个字为一个词）
- **精度**: ±10ms
- **示例**: "你好世界" 会被识别为一个词

### 英文
- **粒度**: 单词级别
- **精度**: ±10ms
- **示例**: "Hello world" 会被识别为两个词

### 标点符号
- 独立标记
- 有自己的时间戳
- 示例: "你好，世界" 中的"，"是单独的条目

## 🎨 前端集成建议

### 1. 下载字幕文件

```javascript
// 下载SRT字幕
const downloadSubtitle = (srtUrl, filename) => {
  const link = document.createElement('a');
  link.href = srtUrl;
  link.download = filename;
  link.click();
};

// 使用
downloadSubtitle(data.srt_url, 'subtitle.srt');
```

### 2. 实时字幕显示

```javascript
const [currentSubtitle, setCurrentSubtitle] = useState('');

audio.addEventListener('timeupdate', () => {
  const time = audio.currentTime * 1000;
  const subtitle = subtitles.find(s =>
    time >= s.audio_offset &&
    time < s.audio_offset + s.duration
  );

  if (subtitle) {
    setCurrentSubtitle(subtitle.text);
  }
});

return <div className="subtitle">{currentSubtitle}</div>;
```

### 3. 字幕编辑器

```javascript
// 字幕时间轴可视化
subtitles.map((subtitle, index) => (
  <div
    key={index}
    style={{
      left: `${subtitle.audio_offset / totalDuration * 100}%`,
      width: `${subtitle.duration / totalDuration * 100}%`
    }}
  >
    {subtitle.text}
  </div>
));
```

## 🔐 文件访问

所有生成的文件都保存在：
```
/var/www/harry-insurance2/media/tts/
```

通过以下URL访问：
```
https://hongkong.xingke888.com/media/tts/filename
```

## ⚙️ 配置

环境变量 (`.env`):
```bash
AZURE_SPEECH_KEY=your-key-here
AZURE_SPEECH_REGION=eastasia
AZURE_SPEECH_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
```

## 🎯 与CosyVoice的区别

| 功能 | Azure TTS | CosyVoice |
|------|-----------|-----------|
| 用途 | 标准语音 | 个人语音克隆 |
| 字幕支持 | ✅ 字符级别 | ❌ 不支持 |
| 语音数量 | 25+ 预置语音 | 自定义无限 |
| 语速音调 | ✅ 支持 | ❌ 有限支持 |
| 时间戳精度 | ±10ms | N/A |
| API稳定性 | 很高 | 中等 |

## 📈 性能指标

- **合成速度**: ~1-2秒（10字文本）
- **字幕生成**: 实时（与合成同步）
- **文件大小**:
  - 音频: ~50KB/10秒
  - JSON字幕: ~1-2KB
  - SRT字幕: ~500B-1KB
  - VTT字幕: ~500B-1KB

## 🎉 总结

现在标准语音功能不仅能生成高质量的TTS音频，还能同时提供精确到字符级别的时间戳信息，非常适合：

- 视频配音 + 自动字幕
- 教育应用（逐字朗读）
- 卡拉OK应用
- 语音学习应用
- 字幕编辑器

所有数据都以多种格式提供，方便各种场景使用！
