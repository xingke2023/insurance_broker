import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  PhotoIcon,
  CameraIcon,
  SparklesIcon,
  BookmarkIcon,
} from '@heroicons/react/24/outline';
import { generateIPImage, getSavedIPImage, saveIPImage, getUsageStats } from '../services/geminiApi';

function IPImageGenerator() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const [uploadedImage, setUploadedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [error, setError] = useState('');
  const [savedImage, setSavedImage] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [usageStats, setUsageStats] = useState(null);
  const [isLoadingStats, setIsLoadingStats] = useState(true);
  const [aspectRatio, setAspectRatio] = useState('1:1');

  // 检测是否在小程序环境中
  const [isInMiniProgram, setIsInMiniProgram] = useState(false);

  // 支持的纵横比
  const aspectRatios = [
    { value: '1:1', label: '正方形 (1:1)' },
    { value: '16:9', label: '横屏 (16:9)' },
    { value: '9:16', label: '竖屏 (9:16)' },
    { value: '4:3', label: '标准 (4:3)' },
    { value: '3:4', label: '竖版 (3:4)' },
  ];

  // 页面加载时获取已保存的IP形象和使用统计
  useEffect(() => {
    fetchSavedImage();
    fetchUsageStats();
    checkMiniProgram();
  }, []);

  // 检测小程序环境
  const checkMiniProgram = () => {
    const hasMiniProgram = typeof window !== 'undefined' &&
                          typeof window.wx !== 'undefined' &&
                          typeof window.wx.miniProgram !== 'undefined';
    const hasWxEnvironment = typeof window !== 'undefined' &&
                            window.__wxjs_environment === 'miniprogram';
    const userAgent = navigator.userAgent || '';
    const hasWxUserAgent = userAgent.toLowerCase().indexOf('miniprogram') > -1;

    setIsInMiniProgram(hasMiniProgram || hasWxEnvironment || hasWxUserAgent);
  };

  // 获取已保存的IP形象
  const fetchSavedImage = async () => {
    try {
      setIsLoading(true);
      const data = await getSavedIPImage();
      if (data.status === 'success' && data.has_saved) {
        setSavedImage(data.data);
        // 如果有保存的图片，显示在生成结果区域
        setGeneratedImage(data.data.generated_image_url);
        setPrompt(data.data.prompt || '');
      }
    } catch (error) {
      console.error('获取保存的IP形象失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 获取使用统计
  const fetchUsageStats = async () => {
    try {
      setIsLoadingStats(true);
      const data = await getUsageStats('ip_image');
      console.log('📊 [IPImageGenerator] 使用统计数据:', data);
      if (data.status === 'success') {
        setUsageStats(data.data);
      } else {
        console.error('❌ [IPImageGenerator] API返回错误:', data);
        // 设置默认值以确保UI能够显示
        setUsageStats({
          quota: { available: 0, total_purchased: 0 },
          total_count: 0
        });
      }
    } catch (error) {
      console.error('❌ [IPImageGenerator] 获取使用统计失败:', error);
      // 设置默认值以确保UI能够显示
      setUsageStats({
        quota: { available: 0, total_purchased: 0 },
        total_count: 0
      });
    } finally {
      setIsLoadingStats(false);
    }
  };

  // 检测是否为移动设备
  const isMobile = () => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  };

  // 处理购买次数按钮点击
  const handlePurchaseClick = () => {
    if (isInMiniProgram && typeof window !== 'undefined' && window.wx && window.wx.miniProgram) {
      // 在小程序环境中，跳转到小程序支付页面
      window.wx.miniProgram.navigateTo({
        url: '/pages/payment/payment'
      });
    } else {
      // 在浏览器环境中，跳转到 Web 支付页面
      navigate('/payment');
    }
  };

  // 处理文件选择
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      setError('请上传图片文件');
      return;
    }

    // 验证文件大小 (限制10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('图片大小不能超过10MB');
      return;
    }

    setError('');
    setUploadedImage(file);

    // 创建预览
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewUrl(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  // 处理生成IP形象
  const handleGenerate = async () => {
    if (!uploadedImage) {
      setError('请先上传照片');
      return;
    }

    if (!prompt.trim()) {
      setError('请输入提示语');
      return;
    }

    try {
      setIsGenerating(true);
      setError('');

      const data = await generateIPImage(uploadedImage, prompt, aspectRatio);

      if (data.status === 'success' && data.image_url) {
        setGeneratedImage(data.image_url);
        // 刷新使用统计
        fetchUsageStats();
      } else {
        setError(data.message || '生成失败，请重试');
      }
    } catch (error) {
      console.error('生成错误:', error);
      setError('生成失败，请重试');
    } finally {
      setIsGenerating(false);
    }
  };

  // 重置表单
  const handleReset = () => {
    setUploadedImage(null);
    setPreviewUrl(null);
    setPrompt('');
    setGeneratedImage(null);
    setError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  // 下载生成的图片
  const handleDownload = () => {
    if (!generatedImage) return;

    const link = document.createElement('a');
    link.href = generatedImage;
    link.download = `ip-image-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 保存IP形象到数据库
  const handleSave = async () => {
    if (!generatedImage) {
      setError('没有可保存的图片');
      return;
    }

    try {
      setIsSaving(true);
      setError('');

      const data = await saveIPImage(generatedImage, prompt);
      if (data.status === 'success') {
        setSavedImage(data.data);
        alert('IP形象保存成功！');
      } else {
        setError(data.message || '保存失败');
      }
    } catch (error) {
      console.error('保存错误:', error);
      setError('保存失败，请重试');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-4"
          >
            <ArrowLeftIcon className="w-5 h-5 mr-2" />
            返回
          </button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                打造个人IP形象
              </h1>
              <p className="text-gray-600 mt-2">上传您的照片，输入创意提示语，AI将为您生成专属IP形象</p>
            </div>

            {/* 统计和购买按钮 - 右对齐，无box */}
            {!isLoadingStats && usageStats && (
              <div className="hidden md:flex items-center gap-2">
                {/* 可用次数 */}
                <div className="flex items-center gap-1.5 px-3 py-1 bg-gradient-to-r from-green-50 to-emerald-50 rounded-md border border-green-200">
                  <span className="text-xs text-gray-600">可用</span>
                  <span className="text-lg font-bold text-green-600">{usageStats.quota.available}次</span>
                </div>

                {/* 购买按钮 */}
                <button
                  onClick={handlePurchaseClick}
                  className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-4 py-1 rounded-md shadow-sm hover:shadow-md hover:from-orange-600 hover:to-red-600 transition-all flex items-center gap-1.5"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm font-semibold">购买</span>
                </button>
              </div>
            )}
          </div>

          {/* 移动端统计和购买按钮 - 右对齐，无box */}
          {!isLoadingStats && usageStats && (
            <div className="md:hidden mt-4 flex items-center justify-end gap-2">
              {/* 可用 */}
              <div className="flex items-center gap-1.5 px-2 py-1 bg-gradient-to-r from-green-50 to-emerald-50 rounded-md border border-green-200">
                <span className="text-xs text-gray-600">可用</span>
                <span className="text-base font-bold text-green-600">{usageStats.quota.available}次</span>
              </div>

              {/* 购买按钮 */}
              <button
                onClick={handlePurchaseClick}
                className="bg-gradient-to-r from-orange-500 to-red-500 text-white px-3 py-1 rounded-md shadow-sm active:scale-95 transition-all flex items-center gap-1"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="text-xs font-semibold">购买</span>
              </button>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
            {/* Left Column - Upload & Input */}
            <div className="space-y-6">
              {/* Upload Section */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  上传照片
                </label>

                {/* Preview or Upload Area */}
                {previewUrl ? (
                  <div className="relative">
                    <img
                      src={previewUrl}
                      alt="预览"
                      className="w-full h-64 object-cover rounded-xl border-2 border-gray-200"
                    />
                    <button
                      onClick={handleReset}
                      className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition-colors shadow-lg"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ) : (
                  <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-500 transition-colors">
                    <PhotoIcon className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600 mb-4">点击按钮上传或拍照</p>
                    <div className="flex flex-col sm:flex-row gap-3 justify-center">
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="flex items-center justify-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-md"
                      >
                        <PhotoIcon className="w-5 h-5 mr-2" />
                        选择照片
                      </button>
                      {isMobile() && (
                        <button
                          onClick={() => cameraInputRef.current?.click()}
                          className="flex items-center justify-center px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors shadow-md"
                        >
                          <CameraIcon className="w-5 h-5 mr-2" />
                          拍照
                        </button>
                      )}
                    </div>
                  </div>
                )}

                {/* Hidden file inputs */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <input
                  ref={cameraInputRef}
                  type="file"
                  accept="image/*"
                  capture="environment"
                  onChange={handleFileChange}
                  className="hidden"
                />
              </div>

              {/* Prompt Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  创意提示语
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="例如：专业的商务风格、可爱的卡通形象、科技感的未来风格..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  rows="5"
                  maxLength="500"
                />
                <p className="text-xs text-gray-500 mt-2">
                  {prompt.length}/500 字符
                </p>
              </div>

              {/* Aspect Ratio Selection */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  图片比例
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {aspectRatios.map((ratio) => (
                    <button
                      key={ratio.value}
                      type="button"
                      onClick={() => setAspectRatio(ratio.value)}
                      className={`px-4 py-2 rounded-lg border-2 font-medium transition-all ${
                        aspectRatio === ratio.value
                          ? 'border-blue-600 bg-blue-50 text-blue-700'
                          : 'border-gray-300 bg-white text-gray-700 hover:border-blue-400'
                      }`}
                    >
                      {ratio.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={!uploadedImage || !prompt.trim() || isGenerating}
                className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 font-semibold shadow-lg hover:shadow-xl"
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>生成中...</span>
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-6 h-6" />
                    <span>生成IP形象</span>
                  </>
                )}
              </button>
            </div>

            {/* Right Column - Result */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                生成结果
              </label>

              {isLoading ? (
                <div className="h-full min-h-[400px] border-2 border-dashed border-gray-300 rounded-xl flex items-center justify-center">
                  <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-600 mb-4"></div>
                    <p className="text-gray-400">加载中...</p>
                  </div>
                </div>
              ) : generatedImage ? (
                <div className="space-y-4">
                  <div className="relative">
                    <img
                      src={generatedImage}
                      alt="生成的IP形象"
                      className="w-full h-auto rounded-xl shadow-lg border-2 border-purple-200"
                    />
                    {savedImage && generatedImage === savedImage.generated_image_url && (
                      <div className="absolute top-4 right-4 bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-medium shadow-lg flex items-center">
                        <BookmarkIcon className="w-4 h-4 mr-1" />
                        已保存
                      </div>
                    )}
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <button
                      onClick={handleDownload}
                      className="py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium shadow-md"
                    >
                      下载
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={isSaving}
                      className="py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                    >
                      {isSaving ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          保存中
                        </>
                      ) : (
                        <>
                          <BookmarkIcon className="w-5 h-5 mr-1" />
                          保存
                        </>
                      )}
                    </button>
                    <button
                      onClick={handleReset}
                      className="py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium shadow-md"
                    >
                      重新生成
                    </button>
                  </div>
                </div>
              ) : (
                <div className="h-full min-h-[400px] border-2 border-dashed border-gray-300 rounded-xl flex items-center justify-center">
                  <div className="text-center">
                    <SparklesIcon className="w-20 h-20 mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-400">生成的IP形象将在这里显示</p>
                    {savedImage && (
                      <p className="text-sm text-blue-600 mt-2">上次保存于 {new Date(savedImage.updated_at).toLocaleString('zh-CN')}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Tips Section */}
        <div className="mt-6 bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">使用提示</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
            <div className="flex items-start space-x-2">
              <span className="text-blue-600 font-bold">•</span>
              <p>上传清晰的正面照片效果最佳</p>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-blue-600 font-bold">•</span>
              <p>提示语越详细，生成效果越精准</p>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-blue-600 font-bold">•</span>
              <p>支持JPG、PNG等常见图片格式</p>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-blue-600 font-bold">•</span>
              <p>图片大小不超过10MB</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default IPImageGenerator;
