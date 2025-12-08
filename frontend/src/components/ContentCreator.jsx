import { useState } from 'react';
import { useAppNavigate } from '../hooks/useAppNavigate';
import { API_BASE_URL } from '../config';
import axios from 'axios';
import {
  ArrowLeftIcon,
  VideoCameraIcon,
  SparklesIcon,
  DocumentTextIcon,
  ClipboardDocumentIcon
} from '@heroicons/react/24/outline';

function ContentCreator() {
  const onNavigate = useAppNavigate();
  const [videoUrl, setVideoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [subtitle, setSubtitle] = useState('');
  const [error, setError] = useState('');

  // 提取视频字幕
  const handleExtractSubtitle = async () => {
    if (!videoUrl.trim()) {
      setError('请输入 YouTube 视频链接');
      return;
    }

    // 简单验证是否为 YouTube 链接
    if (!videoUrl.includes('youtube.com') && !videoUrl.includes('youtu.be')) {
      setError('请输入有效的 YouTube 视频链接');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setSubtitle('');

      // 调用后端 API
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `${API_BASE_URL}/api/content/extract-subtitle`,
        { video_url: videoUrl },
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.data.code === 200) {
        setSubtitle(response.data.data.subtitle);
      } else {
        setError(response.data.message || '提取字幕失败');
      }
    } catch (err) {
      console.error('提取字幕错误:', err);
      setError(err.response?.data?.message || '提取字幕失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 复制字幕内容
  const handleCopySubtitle = () => {
    navigator.clipboard.writeText(subtitle);
    alert('字幕内容已复制到剪贴板');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => onNavigate('dashboard')}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-4"
          >
            <ArrowLeftIcon className="w-5 h-5 mr-2" />
            <span className="text-sm font-medium">返回控制台</span>
          </button>

          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg">
              <SparklesIcon className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">文案制作</h1>
              <p className="text-sm text-gray-500 mt-0.5">AI 视频字幕提取工具</p>
            </div>
          </div>
        </div>

        {/* Main Content Card */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
          {/* Input Section */}
          <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white">
            <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <VideoCameraIcon className="w-5 h-5 mr-2 text-gray-600" />
              YouTube 视频链接
            </label>
            <div className="flex space-x-3">
              <input
                type="text"
                value={videoUrl}
                onChange={(e) => {
                  setVideoUrl(e.target.value);
                  setError('');
                }}
                placeholder="请输入 YouTube 视频链接，例如: https://www.youtube.com/watch?v=xxxxx 或 Shorts 链接"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-sm"
                disabled={loading}
              />
              <button
                onClick={handleExtractSubtitle}
                disabled={loading || !videoUrl.trim()}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium text-sm shadow-md hover:shadow-lg flex items-center space-x-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    <span>提取中...</span>
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-5 h-5" />
                    <span>提取字幕</span>
                  </>
                )}
              </button>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-2">
                <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Info Box */}
            <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <div className="text-sm text-blue-700">
                  <p className="font-medium">使用说明</p>
                  <ul className="mt-1 space-y-0.5 list-disc list-inside">
                    <li>支持 YouTube 视频链接（包括 Shorts 和短链接）</li>
                    <li>AI 会自动提取视频字幕内容</li>
                    <li>提取的字幕可用于文案创作</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Subtitle Display Section */}
          {subtitle && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-semibold text-gray-700 flex items-center">
                  <DocumentTextIcon className="w-5 h-5 mr-2 text-gray-600" />
                  提取的字幕内容
                </label>
                <button
                  onClick={handleCopySubtitle}
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium flex items-center space-x-2"
                >
                  <ClipboardDocumentIcon className="w-4 h-4" />
                  <span>复制</span>
                </button>
              </div>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono leading-relaxed">
                  {subtitle}
                </pre>
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && !subtitle && (
            <div className="p-12 text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
              <p className="mt-4 text-gray-600 text-sm font-medium">正在使用 AI 提取字幕...</p>
              <p className="mt-1 text-gray-500 text-xs">这可能需要一些时间，请耐心等待</p>
            </div>
          )}

          {/* Empty State */}
          {!loading && !subtitle && !error && (
            <div className="p-12 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full mb-4">
                <VideoCameraIcon className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">开始提取视频字幕</h3>
              <p className="text-sm text-gray-500">输入 YouTube 视频链接，让 AI 帮你提取字幕内容</p>
            </div>
          )}
        </div>

        {/* Feature Cards */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <SparklesIcon className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-gray-900">AI 智能提取</h4>
                <p className="text-xs text-gray-500 mt-0.5">使用 Gemini AI 技术</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <VideoCameraIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-gray-900">支持 YouTube</h4>
                <p className="text-xs text-gray-500 mt-0.5">各种视频链接格式</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <DocumentTextIcon className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-gray-900">快速复制</h4>
                <p className="text-xs text-gray-500 mt-0.5">一键复制字幕内容</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ContentCreator;
