import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  PhotoIcon,
  SparklesIcon,
  DocumentTextIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline';
import { generateContentImage, getSavedIPImage, getUsageStats } from '../services/geminiApi';

function ContentImageGenerator() {
  const navigate = useNavigate();

  const [content, setContent] = useState('');
  const [imageCount, setImageCount] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImages, setGeneratedImages] = useState([]);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState({ current: 0, total: 0 });
  const [aspectRatio, setAspectRatio] = useState('9:16');

  // IP形象相关
  const [ipImage, setIpImage] = useState(null);
  const [includeIpImage, setIncludeIpImage] = useState(true);
  const [isLoadingIpImage, setIsLoadingIpImage] = useState(true);

  // 图片预览
  const [previewImage, setPreviewImage] = useState(null);

  // 检测是否在小程序环境中
  const [isInMiniProgram, setIsInMiniProgram] = useState(false);

  // 使用统计
  const [usageStats, setUsageStats] = useState(null);
  const [isLoadingStats, setIsLoadingStats] = useState(true);

  // 支持的纵横比
  const aspectRatios = [
    { value: '1:1', label: '正方形 (1:1)' },
    { value: '16:9', label: '横屏 (16:9)' },
    { value: '9:16', label: '竖屏 (9:16)' },
    { value: '4:3', label: '标准 (4:3)' },
    { value: '3:4', label: '竖版 (3:4)' },
  ];

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

  // 键盘事件监听 - ESC关闭预览
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && previewImage) {
        setPreviewImage(null);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [previewImage]);

  // 检测小程序环境
  useEffect(() => {
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

    checkMiniProgram();
  }, []);

  // 获取用户的IP形象
  useEffect(() => {
    const fetchIpImage = async () => {
      try {
        setIsLoadingIpImage(true);
        const data = await getSavedIPImage();
        if (data.status === 'success' && data.has_saved) {
          setIpImage(data.data);
        }
      } catch (error) {
        console.error('获取IP形象失败:', error);
      } finally {
        setIsLoadingIpImage(false);
      }
    };

    fetchIpImage();
  }, []);

  // 获取使用统计
  useEffect(() => {
    const fetchUsageStats = async () => {
      try {
        setIsLoadingStats(true);
        const data = await getUsageStats('content_image');
        console.log('📊 [ContentImageGenerator] 使用统计数据:', data);
        if (data.status === 'success') {
          setUsageStats(data.data);
        } else {
          console.error('❌ [ContentImageGenerator] API返回错误:', data);
          // 设置默认值以确保UI能够显示
          setUsageStats({
            quota: { available: 0, total_purchased: 0 },
            total_count: 0
          });
        }
      } catch (error) {
        console.error('❌ [ContentImageGenerator] 获取使用统计失败:', error);
        // 设置默认值以确保UI能够显示
        setUsageStats({
          quota: { available: 0, total_purchased: 0 },
          total_count: 0
        });
      } finally {
        setIsLoadingStats(false);
      }
    };

    fetchUsageStats();
  }, []);

  // 处理生成配图
  const handleGenerate = async () => {
    if (!content.trim()) {
      setError('请输入文案内容');
      return;
    }

    try {
      setIsGenerating(true);
      setError('');
      setGeneratedImages([]);
      setProgress({ current: 0, total: imageCount });

      // 逐张生成图片
      const images = [];
      for (let i = 0; i < imageCount; i++) {
        setProgress({ current: i + 1, total: imageCount });

        // 准备API调用参数
        const options = {};
        if (includeIpImage && ipImage) {
          options.includeIpImage = true;
          options.ipImageUrl = ipImage.generated_image_url;
        }

        const data = await generateContentImage(content, i + 1, options, aspectRatio);

        if (data.status === 'success' && data.image_url) {
          images.push({
            id: i + 1,
            url: data.image_url
          });
          setGeneratedImages([...images]); // 实时更新显示
        } else {
          console.error(`生成第 ${i + 1} 张图片失败:`, data.message);
        }
      }

      if (images.length === 0) {
        setError('生成失败，请重试');
      } else {
        // 刷新使用统计
        const statsData = await getUsageStats('content_image');
        if (statsData.status === 'success') {
          setUsageStats(statsData.data);
        }
      }
    } catch (error) {
      console.error('生成错误:', error);
      setError('生成失败，请重试');
    } finally {
      setIsGenerating(false);
      setProgress({ current: 0, total: 0 });
    }
  };

  // 重置表单
  const handleReset = () => {
    setContent('');
    setGeneratedImages([]);
    setError('');
    setImageCount(1);
  };

  // 下载单张图片
  const handleDownload = (imageUrl, index) => {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = `content-image-${index}-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 下载全部图片
  const handleDownloadAll = () => {
    generatedImages.forEach((image, index) => {
      setTimeout(() => {
        handleDownload(image.url, index + 1);
      }, index * 500); // 每张图片间隔500ms下载
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
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
                文案配图制作
              </h1>
              <p className="text-gray-600 mt-2">输入您的文案内容，AI将为您生成精美的配图</p>
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Input */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-xl p-6 sticky top-6">
              <div className="space-y-6">
                {/* IP Image Option */}
                {!isLoadingIpImage && ipImage && (
                  <div className="border border-purple-200 bg-purple-50 rounded-xl p-4">
                    <div className="flex items-start space-x-3 mb-3">
                      <img
                        src={ipImage.generated_image_url}
                        alt="个人IP形象"
                        className="w-16 h-16 rounded-lg object-cover shadow-md"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-gray-900">个人IP形象</p>
                        <p className="text-xs text-gray-600 line-clamp-2 mt-1">{ipImage.prompt || '您的专属IP形象'}</p>
                      </div>
                    </div>
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={includeIpImage}
                        onChange={(e) => setIncludeIpImage(e.target.checked)}
                        disabled={isGenerating}
                        className="w-5 h-5 text-purple-600 border-gray-300 rounded focus:ring-purple-500 focus:ring-2"
                      />
                      <span className="ml-3 text-sm font-medium text-gray-900">
                        将个人IP形象加入到配图中
                      </span>
                    </label>
                    <p className="text-xs text-gray-500 mt-2 ml-8">
                      勾选后，您的IP形象会作为配图中的主人翁出现，融入场景但不喧宾夺主
                    </p>
                  </div>
                )}

                {isLoadingIpImage && (
                  <div className="border border-gray-200 rounded-xl p-4 text-center">
                    <div className="inline-block animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-gray-400"></div>
                    <p className="text-xs text-gray-500 mt-2">加载IP形象中...</p>
                  </div>
                )}

                {!isLoadingIpImage && !ipImage && (
                  <div className="border border-gray-200 bg-gray-50 rounded-xl p-4">
                    <div className="flex items-center space-x-2 text-gray-600">
                      <UserCircleIcon className="w-5 h-5" />
                      <span className="text-sm">暂无个人IP形象</span>
                    </div>
                    <button
                      onClick={() => navigate('/ip-image-generator')}
                      className="mt-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      去创建 →
                    </button>
                  </div>
                )}

                {/* Content Input */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-3">
                    <DocumentTextIcon className="w-5 h-5 inline mr-2" />
                    文案内容
                  </label>
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    placeholder="请输入您的文案内容...&#10;例如：&#10;- 春天的花园，阳光明媚&#10;- 现代办公室，团队合作&#10;- 美食料理，色香味俱全"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                    rows="10"
                    maxLength="1000"
                  />
                  <p className="text-xs text-gray-500 mt-2">
                    {content.length}/1000 字符
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
                        disabled={isGenerating}
                        className={`px-4 py-2 rounded-lg border-2 font-medium transition-all ${
                          aspectRatio === ratio.value
                            ? 'border-blue-600 bg-blue-50 text-blue-700'
                            : 'border-gray-300 bg-white text-gray-700 hover:border-blue-400'
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        {ratio.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Image Count */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-3">
                    生成数量
                  </label>
                  <select
                    value={imageCount}
                    onChange={(e) => setImageCount(parseInt(e.target.value))}
                    disabled={isGenerating}
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={1}>1 张</option>
                    <option value={2} disabled>2 张 (会员可用)</option>
                    <option value={3} disabled>3 张 (会员可用)</option>
                    <option value={4} disabled>4 张 (会员可用)</option>
                    <option value={5} disabled>5 张 (会员可用)</option>
                  </select>
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
                  disabled={!content.trim() || isGenerating}
                  className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 font-semibold shadow-lg hover:shadow-xl"
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>生成中 ({progress.current}/{progress.total})</span>
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="w-6 h-6" />
                      <span>生成配图</span>
                    </>
                  )}
                </button>

                {/* Reset Button */}
                {generatedImages.length > 0 && !isGenerating && (
                  <button
                    onClick={handleReset}
                    className="w-full py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-medium"
                  >
                    重新制作
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">
                  生成结果 {generatedImages.length > 0 && `(${generatedImages.length})`}
                </h3>
                {generatedImages.length > 0 && !isInMiniProgram && (
                  <button
                    onClick={handleDownloadAll}
                    className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors font-medium"
                  >
                    下载全部
                  </button>
                )}
                {generatedImages.length > 0 && isInMiniProgram && (
                  <p className="text-sm text-gray-600">长按图片保存</p>
                )}
              </div>

              {generatedImages.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {generatedImages.map((image) => (
                    <div key={image.id} className="relative group">
                      <div
                        className="relative overflow-hidden rounded-xl border-2 border-gray-200 hover:border-blue-400 transition-all cursor-pointer"
                        onClick={() => setPreviewImage(image)}
                      >
                        <img
                          src={image.url}
                          alt={`配图 ${image.id}`}
                          className="w-full h-auto object-cover"
                        />
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all flex items-center justify-center gap-3">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setPreviewImage(image);
                            }}
                            className="opacity-0 group-hover:opacity-100 transition-opacity px-4 py-2 bg-white text-gray-900 rounded-lg font-medium shadow-lg flex items-center gap-2"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                            </svg>
                            查看
                          </button>
                          {!isInMiniProgram && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDownload(image.url, image.id);
                              }}
                              className="opacity-0 group-hover:opacity-100 transition-opacity px-4 py-2 bg-green-600 text-white rounded-lg font-medium shadow-lg flex items-center gap-2"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                              </svg>
                              下载
                            </button>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mt-2 text-center">配图 {image.id}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="h-[500px] border-2 border-dashed border-gray-300 rounded-xl flex items-center justify-center">
                  <div className="text-center">
                    <PhotoIcon className="w-20 h-20 mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-400">生成的配图将在这里显示</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Tips Section */}
        <div className="mt-6 bg-white rounded-xl shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">使用提示</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div className="flex items-start space-x-2">
              <span className="text-blue-600 font-bold">•</span>
              <p>描述越详细，生成效果越精准</p>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-blue-600 font-bold">•</span>
              <p>可以指定画面风格、色调、氛围等</p>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-blue-600 font-bold">•</span>
              <p>支持生成1-5张不同风格的配图</p>
            </div>
          </div>
        </div>

        {/* 图片预览模态框 */}
        {previewImage && (
          <div
            className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4"
            onClick={() => setPreviewImage(null)}
          >
            <div className="relative max-w-6xl max-h-[95vh] w-full">
              {/* 关闭按钮 */}
              <button
                onClick={() => setPreviewImage(null)}
                className="absolute -top-12 right-0 text-white hover:text-gray-300 transition-colors flex items-center gap-2"
              >
                <span className="text-sm">ESC 或点击任意位置关闭</span>
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              {/* 图片容器 */}
              <div
                className="bg-white rounded-2xl overflow-hidden shadow-2xl"
                onClick={(e) => e.stopPropagation()}
              >
                <img
                  src={previewImage.url}
                  alt={`配图 ${previewImage.id} 大图`}
                  className="w-full h-auto object-contain max-h-[75vh]"
                />

                {/* 底部操作栏 */}
                <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-gray-900 mb-1">配图 {previewImage.id}</p>
                      {previewImage.prompt && (
                        <p className="text-xs text-gray-600">{previewImage.prompt}</p>
                      )}
                    </div>
                    {!isInMiniProgram && (
                      <button
                        onClick={() => handleDownload(previewImage.url, previewImage.id)}
                        className="ml-4 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-medium shadow-md hover:shadow-lg flex items-center gap-2"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        下载图片
                      </button>
                    )}
                    {isInMiniProgram && (
                      <p className="ml-4 text-sm text-gray-600">长按图片保存</p>
                    )}
                  </div>
                </div>
              </div>

              {/* 键盘提示 */}
              <div className="mt-4 text-center">
                <p className="text-white text-sm opacity-75">按 ESC 键或点击背景可关闭预览</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ContentImageGenerator;
