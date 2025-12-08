import { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Input } from './ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Card } from './ui/card';
import { Slider } from './ui/slider';
import { Volume2, Download, Loader2, Play, Pause, Upload, Trash2, Plus, User } from 'lucide-react';
import { toast } from 'sonner';
import API_CONFIG from '../config/api';

const API_BASE_URL = API_CONFIG.BASE_URL;

interface Voice {
  id: string;
  name: string;
  language: string;
  gender: string;
}

interface VoiceGroup {
  label: string;
  language: string;
  voices: Voice[];
}

interface PersonalVoice {
  id: string;
  name: string;
  voice_talent_name: string;
  company_name: string;
  voice_id: string;
  status: string;
  created_at: string;
}

export function TextToSpeech() {
  // 标准语音状态
  const [text, setText] = useState('');
  const [voices, setVoices] = useState<Voice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState('longxiaochun');
  const [rate, setRate] = useState(0);
  const [pitch, setPitch] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioElement, setAudioElement] = useState<HTMLAudioElement | null>(null);

  // 个人语音状态
  const [personalVoices, setPersonalVoices] = useState<PersonalVoice[]>([]);
  const [selectedPersonalVoice, setSelectedPersonalVoice] = useState<string>('');
  const [personalText, setPersonalText] = useState('');
  const [personalRate, setPersonalRate] = useState(0);
  const [personalPitch, setPersonalPitch] = useState(0);
  const [isPersonalLoading, setIsPersonalLoading] = useState(false);
  const [personalAudioUrl, setPersonalAudioUrl] = useState<string | null>(null);
  const [isPersonalPlaying, setIsPersonalPlaying] = useState(false);
  const [personalAudioElement, setPersonalAudioElement] = useState<HTMLAudioElement | null>(null);

  // 创建个人语音状态
  const [isCreating, setIsCreating] = useState(false);
  const [voiceName, setVoiceName] = useState('');
  const [voiceTalentName, setVoiceTalentName] = useState('');
  const [companyName, setCompanyName] = useState('寰宇數據');
  const [consentFile, setConsentFile] = useState<File | null>(null);
  const [voiceSampleFile, setVoiceSampleFile] = useState<File | null>(null);

  // 获取可用语音列表
  useEffect(() => {
    const fetchVoices = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/tts/voices/`);
        const data = await response.json();
        if (data.status === 'success') {
          setVoices(data.voices);
        }
      } catch (error) {
        console.error('Failed to fetch voices:', error);
        toast.error('获取语音列表失败');
      }
    };
    fetchVoices();
  }, []);

  // 获取个人语音列表
  useEffect(() => {
    fetchPersonalVoices();
  }, []);

  const fetchPersonalVoices = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/personal-voice/`);
      const data = await response.json();
      if (data.status === 'success') {
        setPersonalVoices(data.voices);
        if (data.voices.length > 0 && !selectedPersonalVoice) {
          setSelectedPersonalVoice(data.voices[0].voice_id);
        }
      }
    } catch (error) {
      console.error('Failed to fetch personal voices:', error);
    }
  };

  // 按语言分组语音
  const groupedVoices: VoiceGroup[] = [
    {
      label: '中文（普通话）',
      language: 'zh-CN',
      voices: voices.filter((v) => v.language === 'zh-CN'),
    },
    {
      label: '粤语',
      language: 'zh-HK',
      voices: voices.filter((v) => v.language === 'zh-HK'),
    },
    {
      label: '台湾话',
      language: 'zh-TW',
      voices: voices.filter((v) => v.language === 'zh-TW'),
    },
    {
      label: '英语（美国）',
      language: 'en-US',
      voices: voices.filter((v) => v.language === 'en-US'),
    },
    {
      label: '英语（英国）',
      language: 'en-GB',
      voices: voices.filter((v) => v.language === 'en-GB'),
    },
  ].filter((group) => group.voices.length > 0);

  // 标准语音合成
  const handleSynthesize = async () => {
    if (!text.trim()) {
      toast.error('请输入要转换的文本');
      return;
    }

    if (text.length > 5000) {
      toast.error('文本长度不能超过5000个字符');
      return;
    }

    setIsLoading(true);
    setAudioUrl(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/tts/synthesize/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          voice: selectedVoice,
          rate: `${rate}%`,
          pitch: `${pitch}%`,
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        setAudioUrl(`${API_BASE_URL}${data.audio_url}`);
        toast.success('语音合成成功！');
      } else {
        toast.error(data.message || '语音合成失败');
      }
    } catch (error) {
      console.error('Synthesis error:', error);
      toast.error('语音合成失败，请检查网络连接');
    } finally {
      setIsLoading(false);
    }
  };

  // 个人语音合成
  const handlePersonalSynthesize = async () => {
    if (!personalText.trim()) {
      toast.error('请输入要转换的文本');
      return;
    }

    if (!selectedPersonalVoice) {
      toast.error('请选择个人语音');
      return;
    }

    setIsPersonalLoading(true);
    setPersonalAudioUrl(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/personal-voice/synthesize/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: personalText,
          voice_id: selectedPersonalVoice,
          rate: `${personalRate}%`,
          pitch: `${personalPitch}%`,
        }),
      });

      const data = await response.json();

      if (data.status === 'success') {
        setPersonalAudioUrl(`${API_BASE_URL}${data.audio_url}`);
        toast.success('个人语音合成成功！');
      } else {
        toast.error(data.message || '个人语音合成失败');
      }
    } catch (error) {
      console.error('Personal synthesis error:', error);
      toast.error('个人语音合成失败');
    } finally {
      setIsPersonalLoading(false);
    }
  };

  // 创建个人语音
  const handleCreatePersonalVoice = async () => {
    if (!voiceName || !voiceTalentName || !consentFile || !voiceSampleFile) {
      toast.error('请填写所有必填项并上传音频文件');
      return;
    }

    setIsCreating(true);

    try {
      const formData = new FormData();
      formData.append('voice_name', voiceName);
      formData.append('voice_talent_name', voiceTalentName);
      formData.append('company_name', companyName);
      formData.append('consent_audio', consentFile);
      formData.append('voice_sample', voiceSampleFile);

      const response = await fetch(`${API_BASE_URL}/api/personal-voice/create/`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.status === 'success') {
        toast.success('个人语音创建成功！');
        // 重置表单
        setVoiceName('');
        setVoiceTalentName('');
        setCompanyName('寰宇數據');
        setConsentFile(null);
        setVoiceSampleFile(null);
        // 刷新列表
        fetchPersonalVoices();
      } else {
        toast.error(data.message || '创建个人语音失败');
      }
    } catch (error) {
      console.error('Create personal voice error:', error);
      toast.error('创建个人语音失败');
    } finally {
      setIsCreating(false);
    }
  };

  // 删除个人语音
  const handleDeletePersonalVoice = async (voiceId: string) => {
    if (!confirm('确定要删除这个个人语音吗？此操作不可撤销。')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/personal-voice/${voiceId}/delete/`, {
        method: 'DELETE',
      });

      const data = await response.json();

      if (data.status === 'success') {
        toast.success('个人语音已删除');
        fetchPersonalVoices();
      } else {
        toast.error(data.message || '删除失败');
      }
    } catch (error) {
      console.error('Delete error:', error);
      toast.error('删除失败');
    }
  };

  // 播放/暂停控制
  const handlePlayPause = (isPersonal: boolean) => {
    const url = isPersonal ? personalAudioUrl : audioUrl;
    const audio = isPersonal ? personalAudioElement : audioElement;
    const setAudio = isPersonal ? setPersonalAudioElement : setAudioElement;
    const playing = isPersonal ? isPersonalPlaying : isPlaying;
    const setPlaying = isPersonal ? setIsPersonalPlaying : setIsPlaying;

    if (!url) return;

    if (!audio) {
      const newAudio = new Audio(url);
      newAudio.addEventListener('ended', () => setPlaying(false));
      newAudio.addEventListener('error', () => {
        toast.error('音频播放失败');
        setPlaying(false);
      });
      setAudio(newAudio);
      newAudio.play();
      setPlaying(true);
    } else {
      if (playing) {
        audio.pause();
        setPlaying(false);
      } else {
        audio.play();
        setPlaying(true);
      }
    }
  };

  const handleDownload = (url: string | null) => {
    if (!url) return;

    const link = document.createElement('a');
    link.href = url;
    link.download = `tts_${Date.now()}.mp3`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('开始下载音频文件');
  };

  // 清理音频元素
  useEffect(() => {
    return () => {
      if (audioElement) {
        audioElement.pause();
        audioElement.remove();
      }
      if (personalAudioElement) {
        personalAudioElement.pause();
        personalAudioElement.remove();
      }
    };
  }, [audioElement, personalAudioElement]);

  return (
    <div className="container mx-auto px-8 py-6">
      <div className="max-w-5xl mx-auto">
        <Card className="bg-gradient-to-br from-white via-blue-50/30 to-purple-50/30 p-8 shadow-2xl border-2 border-blue-200/50">
          {/* 标题 */}
          <div className="mb-8">
            <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
              AI语音合成
            </h2>
            <p className="text-gray-600">使用Azure认知服务将文本转换为自然流畅的语音</p>
          </div>

          <Tabs defaultValue="standard" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="standard" className="text-base">
                <Volume2 className="mr-2 h-4 w-4" />
                标准语音
              </TabsTrigger>
              <TabsTrigger value="personal" className="text-base">
                <User className="mr-2 h-4 w-4" />
                个人语音
              </TabsTrigger>
            </TabsList>

            {/* 标准语音标签页 */}
            <TabsContent value="standard" className="space-y-6">
              {/* 文本输入 */}
              <div>
                <Label className="text-base font-semibold text-gray-700 mb-2 block">
                  输入文本内容
                </Label>
                <Textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="在此输入要转换为语音的文本内容..."
                  className="min-h-[200px] text-base resize-none border-2 border-blue-200 focus:border-blue-400 transition-colors"
                  maxLength={5000}
                />
                <div className="flex justify-between items-center mt-2">
                  <span className="text-sm text-gray-500">
                    {text.length} / 5000 字符
                  </span>
                </div>
              </div>

              {/* 语音选择 */}
              <div>
                <Label className="text-base font-semibold text-gray-700 mb-2 block">
                  选择语音
                </Label>
                <Select value={selectedVoice} onValueChange={setSelectedVoice}>
                  <SelectTrigger className="w-full border-2 border-blue-200">
                    <SelectValue placeholder="选择语音" />
                  </SelectTrigger>
                  <SelectContent className="max-h-[400px]">
                    {groupedVoices.map((group) => (
                      <div key={group.language}>
                        <div className="px-2 py-1.5 text-sm font-semibold text-gray-500 bg-gray-100">
                          {group.label}
                        </div>
                        {group.voices.map((voice) => (
                          <SelectItem key={voice.id} value={voice.id}>
                            {voice.name}
                          </SelectItem>
                        ))}
                      </div>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* 语速和音调 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <Label className="text-base font-semibold text-gray-700">
                      语速
                    </Label>
                    <span className="text-sm text-gray-600 font-medium">
                      {rate > 0 ? `+${rate}%` : `${rate}%`}
                    </span>
                  </div>
                  <Slider
                    value={[rate]}
                    onValueChange={(value) => setRate(value[0])}
                    min={-50}
                    max={50}
                    step={10}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>慢速</span>
                    <span>正常</span>
                    <span>快速</span>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between items-center mb-2">
                    <Label className="text-base font-semibold text-gray-700">
                      音调
                    </Label>
                    <span className="text-sm text-gray-600 font-medium">
                      {pitch > 0 ? `+${pitch}%` : `${pitch}%`}
                    </span>
                  </div>
                  <Slider
                    value={[pitch]}
                    onValueChange={(value) => setPitch(value[0])}
                    min={-50}
                    max={50}
                    step={10}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>低沉</span>
                    <span>正常</span>
                    <span>高亢</span>
                  </div>
                </div>
              </div>

              {/* 生成按钮 */}
              <Button
                onClick={handleSynthesize}
                disabled={isLoading || !text.trim()}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-6 text-lg font-semibold shadow-lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    合成中...
                  </>
                ) : (
                  <>
                    <Volume2 className="mr-2 h-5 w-5" />
                    生成语音
                  </>
                )}
              </Button>

              {/* 音频播放 */}
              {audioUrl && (
                <div className="p-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border-2 border-green-200">
                  <h3 className="text-lg font-semibold text-gray-700 mb-4">
                    语音已生成
                  </h3>
                  <div className="flex gap-3">
                    <Button
                      onClick={() => handlePlayPause(false)}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white"
                    >
                      {isPlaying ? (
                        <>
                          <Pause className="mr-2 h-4 w-4" />
                          暂停播放
                        </>
                      ) : (
                        <>
                          <Play className="mr-2 h-4 w-4" />
                          播放语音
                        </>
                      )}
                    </Button>
                    <Button
                      onClick={() => handleDownload(audioUrl)}
                      variant="outline"
                      className="flex-1 border-2 border-blue-600 text-blue-600 hover:bg-blue-50"
                    >
                      <Download className="mr-2 h-4 w-4" />
                      下载音频
                    </Button>
                  </div>
                </div>
              )}
            </TabsContent>

            {/* 个人语音标签页 */}
            <TabsContent value="personal" className="space-y-6">
              {/* 创建个人语音 */}
              <Card className="p-6 bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200">
                <h3 className="text-xl font-bold text-gray-700 mb-4 flex items-center">
                  <Plus className="mr-2 h-5 w-5" />
                  创建个人语音
                </h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>语音名称 *</Label>
                      <Input
                        value={voiceName}
                        onChange={(e) => setVoiceName(e.target.value)}
                        placeholder="例如：我的语音"
                      />
                    </div>
                    <div>
                      <Label>配音员姓名 *</Label>
                      <Input
                        value={voiceTalentName}
                        onChange={(e) => setVoiceTalentName(e.target.value)}
                        placeholder="例如：张三"
                      />
                    </div>
                  </div>

                  <div>
                    <Label>公司名称</Label>
                    <Input
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="寰宇數據"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label>同意声明音频 *</Label>
                      <Input
                        type="file"
                        accept="audio/wav,audio/mp3"
                        onChange={(e) => setConsentFile(e.target.files?.[0] || null)}
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        需朗读：我 [配音员姓名] 知道我的录音将被 [公司名称] 用于创建和使用我的语音合成版本。
                      </p>
                    </div>
                    <div>
                      <Label>语音样本音频 * (5-90秒)</Label>
                      <Input
                        type="file"
                        accept="audio/wav,audio/mp3"
                        onChange={(e) => setVoiceSampleFile(e.target.files?.[0] || null)}
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        清晰朗读任意文本，用于训练个人语音模型
                      </p>
                    </div>
                  </div>

                  <Button
                    onClick={handleCreatePersonalVoice}
                    disabled={isCreating}
                    className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                  >
                    {isCreating ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        创建中...
                      </>
                    ) : (
                      <>
                        <Plus className="mr-2 h-4 w-4" />
                        创建个人语音
                      </>
                    )}
                  </Button>
                </div>
              </Card>

              {/* 个人语音列表 */}
              {personalVoices.length > 0 && (
                <>
                  <div>
                    <Label className="text-base font-semibold text-gray-700 mb-2 block">
                      我的个人语音
                    </Label>
                    <div className="space-y-2">
                      {personalVoices.map((voice) => (
                        <div
                          key={voice.id}
                          className="flex items-center justify-between p-4 bg-white rounded-lg border-2 border-gray-200 hover:border-purple-300 transition-colors"
                        >
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-700">{voice.name}</h4>
                            <p className="text-sm text-gray-500">
                              配音员: {voice.voice_talent_name} | 公司: {voice.company_name}
                            </p>
                          </div>
                          <Button
                            onClick={() => handleDeletePersonalVoice(voice.id)}
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 使用个人语音合成 */}
                  <div>
                    <Label className="text-base font-semibold text-gray-700 mb-2 block">
                      选择个人语音
                    </Label>
                    <Select value={selectedPersonalVoice} onValueChange={setSelectedPersonalVoice}>
                      <SelectTrigger className="w-full border-2 border-purple-200">
                        <SelectValue placeholder="选择个人语音" />
                      </SelectTrigger>
                      <SelectContent>
                        {personalVoices.map((voice) => (
                          <SelectItem key={voice.voice_id} value={voice.voice_id}>
                            {voice.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label className="text-base font-semibold text-gray-700 mb-2 block">
                      输入文本内容
                    </Label>
                    <Textarea
                      value={personalText}
                      onChange={(e) => setPersonalText(e.target.value)}
                      placeholder="在此输入要转换为语音的文本内容..."
                      className="min-h-[150px] text-base resize-none border-2 border-purple-200 focus:border-purple-400 transition-colors"
                      maxLength={5000}
                    />
                  </div>

                  {/* 语速和音调 */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <Label className="text-base font-semibold text-gray-700">
                          语速
                        </Label>
                        <span className="text-sm text-gray-600 font-medium">
                          {personalRate > 0 ? `+${personalRate}%` : `${personalRate}%`}
                        </span>
                      </div>
                      <Slider
                        value={[personalRate]}
                        onValueChange={(value) => setPersonalRate(value[0])}
                        min={-50}
                        max={50}
                        step={10}
                        className="w-full"
                      />
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <Label className="text-base font-semibold text-gray-700">
                          音调
                        </Label>
                        <span className="text-sm text-gray-600 font-medium">
                          {personalPitch > 0 ? `+${personalPitch}%` : `${personalPitch}%`}
                        </span>
                      </div>
                      <Slider
                        value={[personalPitch]}
                        onValueChange={(value) => setPersonalPitch(value[0])}
                        min={-50}
                        max={50}
                        step={10}
                        className="w-full"
                      />
                    </div>
                  </div>

                  <Button
                    onClick={handlePersonalSynthesize}
                    disabled={isPersonalLoading || !personalText.trim() || !selectedPersonalVoice}
                    className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white py-6 text-lg font-semibold shadow-lg"
                  >
                    {isPersonalLoading ? (
                      <>
                        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                        合成中...
                      </>
                    ) : (
                      <>
                        <Volume2 className="mr-2 h-5 w-5" />
                        生成个人语音
                      </>
                    )}
                  </Button>

                  {/* 个人语音播放 */}
                  {personalAudioUrl && (
                    <div className="p-6 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border-2 border-purple-200">
                      <h3 className="text-lg font-semibold text-gray-700 mb-4">
                        个人语音已生成
                      </h3>
                      <div className="flex gap-3">
                        <Button
                          onClick={() => handlePlayPause(true)}
                          className="flex-1 bg-purple-600 hover:bg-purple-700 text-white"
                        >
                          {isPersonalPlaying ? (
                            <>
                              <Pause className="mr-2 h-4 w-4" />
                              暂停播放
                            </>
                          ) : (
                            <>
                              <Play className="mr-2 h-4 w-4" />
                              播放语音
                            </>
                          )}
                        </Button>
                        <Button
                          onClick={() => handleDownload(personalAudioUrl)}
                          variant="outline"
                          className="flex-1 border-2 border-purple-600 text-purple-600 hover:bg-purple-50"
                        >
                          <Download className="mr-2 h-4 w-4" />
                          下载音频
                        </Button>
                      </div>
                    </div>
                  )}
                </>
              )}

              {personalVoices.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <User className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                  <p>还没有个人语音，请先创建一个</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </Card>

        {/* 使用说明 */}
        <div className="mt-8 p-6 bg-blue-50/50 rounded-lg border border-blue-200">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">使用说明</h3>
          <div className="space-y-3">
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">标准语音</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="mr-2 text-blue-600">•</span>
                  <span>支持20+种中文语音和多种英语语音</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-blue-600">•</span>
                  <span>可调节语速和音调</span>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">个人语音</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start">
                  <span className="mr-2 text-purple-600">•</span>
                  <span>上传5-90秒的清晰语音样本创建个性化语音</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-purple-600">•</span>
                  <span>需要录制同意声明音频</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-purple-600">•</span>
                  <span>创建后可用于任意文本的语音合成</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
