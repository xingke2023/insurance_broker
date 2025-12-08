import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Loader2, Youtube, Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import API_CONFIG from '../config/api';

const API_BASE_URL = API_CONFIG.BASE_URL;

export function ContentCreator() {
  const [videoUrl, setVideoUrl] = useState('');
  const [subtitle, setSubtitle] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleExtractSubtitle = async () => {
    if (!videoUrl.trim()) {
      toast.error('请输入视频链接', {
        style: {
          background: 'linear-gradient(to right, #ef4444, #dc2626)',
          color: 'white',
          border: '1px solid #dc2626',
        },
      });
      return;
    }

    setIsLoading(true);
    setSubtitle('');

    try {
      // 获取 token (从 localStorage)
      const token = localStorage.getItem('auth_token');

      if (!token) {
        toast.error('请先登录', {
          style: {
            background: 'linear-gradient(to right, #ef4444, #dc2626)',
            color: 'white',
            border: '1px solid #dc2626',
          },
        });
        setIsLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/content/extract-subtitle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${token}`,
        },
        body: JSON.stringify({
          video_url: videoUrl,
        }),
      });

      const data = await response.json();

      if (data.code === 200) {
        setSubtitle(data.data.subtitle);
        toast.success('字幕提取成功！', {
          description: '已成功提取视频字幕',
          style: {
            background: 'linear-gradient(to right, #10b981, #059669)',
            color: 'white',
            border: '1px solid #059669',
          },
        });
      } else {
        toast.error('字幕提取失败', {
          description: data.message || '未知错误',
          style: {
            background: 'linear-gradient(to right, #ef4444, #dc2626)',
            color: 'white',
            border: '1px solid #dc2626',
          },
        });
      }
    } catch (error) {
      console.error('Extract subtitle error:', error);
      toast.error('字幕提取失败', {
        description: '无法连接到服务器',
        style: {
          background: 'linear-gradient(to right, #ef4444, #dc2626)',
          color: 'white',
          border: '1px solid #dc2626',
        },
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopySubtitle = () => {
    if (subtitle) {
      navigator.clipboard.writeText(subtitle);
      toast.success('已复制到剪贴板', {
        style: {
          background: 'linear-gradient(to right, #10b981, #059669)',
          color: 'white',
          border: '1px solid #059669',
        },
      });
    }
  };

  return (
    <div className="container mx-auto px-8 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2 flex items-center gap-3">
          <Sparkles className="h-10 w-10 text-purple-600" />
          文案制作
        </h1>
        <p className="text-gray-600">使用 AI 从 YouTube 视频中提取和优化字幕内容</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 输入区域 */}
        <Card className="shadow-xl border-2 border-blue-100">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-700">
              <Youtube className="h-5 w-5" />
              视频链接
            </CardTitle>
            <CardDescription>
              输入 YouTube 视频链接以提取字幕
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Input
                type="text"
                placeholder="例如: https://www.youtube.com/watch?v=..."
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                className="text-base"
                disabled={isLoading}
              />
              <p className="text-xs text-gray-500">
                支持格式: youtube.com/watch?v=xxx, youtu.be/xxx
              </p>
            </div>

            <Button
              onClick={handleExtractSubtitle}
              disabled={isLoading || !videoUrl.trim()}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-6 text-base"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  正在提取字幕...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-5 w-5" />
                  提取字幕
                </>
              )}
            </Button>

            {isLoading && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-700 flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  正在使用 Gemini AI 处理视频字幕，请稍候...
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 结果区域 */}
        <Card className="shadow-xl border-2 border-purple-100">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="text-purple-700">提取结果</span>
              {subtitle && (
                <Button
                  onClick={handleCopySubtitle}
                  variant="outline"
                  size="sm"
                  className="text-xs"
                >
                  复制文本
                </Button>
              )}
            </CardTitle>
            <CardDescription>
              提取并优化后的字幕内容
            </CardDescription>
          </CardHeader>
          <CardContent>
            {subtitle ? (
              <Textarea
                value={subtitle}
                readOnly
                className="min-h-[400px] font-mono text-sm resize-none"
                placeholder="字幕内容将显示在这里..."
              />
            ) : (
              <div className="min-h-[400px] flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg">
                <div className="text-center text-gray-400">
                  <Youtube className="h-16 w-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium">暂无内容</p>
                  <p className="text-sm mt-1">输入视频链接并点击提取按钮</p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* 说明区域 */}
      <Card className="mt-6 bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-200">
        <CardHeader>
          <CardTitle className="text-lg text-blue-800">功能说明</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-gray-700">
          <p>1. 输入 YouTube 视频链接，系统会自动提取视频字幕</p>
          <p>2. 优先提取中文字幕，如果没有则提取英文或其他可用字幕</p>
          <p>3. 使用 Gemini AI 自动优化字幕格式，删除重复内容并合理分段</p>
          <p>4. 提取完成后，可以复制字幕内容用于创作文案</p>
        </CardContent>
      </Card>
    </div>
  );
}
