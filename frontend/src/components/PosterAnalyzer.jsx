import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useAppNavigate } from '../hooks/useAppNavigate';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import { ArrowLeftIcon, SparklesIcon, ArrowsPointingOutIcon, XMarkIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { handleMembershipError } from '../utils/membershipHelper';

function PosterAnalyzer() {
  const { user } = useAuth();
  const onNavigate = useAppNavigate();

  // 状态管理
  const [selectedPosterFile, setSelectedPosterFile] = useState(null);
  const [posterPreviewUrl, setPosterPreviewUrl] = useState(null);
  const [posterAnalyzing, setPosterAnalyzing] = useState(false);
  const [posterAnalysisResult, setPosterAnalysisResult] = useState(null);
  const [analysisTemplates, setAnalysisTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [showFullscreen, setShowFullscreen] = useState(false);
  const [showTemplateDropdown, setShowTemplateDropdown] = useState(false);

  // 加载分析模板
  useEffect(() => {
    const loadAnalysisTemplates = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        const response = await axios.get(`${API_BASE_URL}/api/poster/templates`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.data.success) {
          setAnalysisTemplates(response.data.templates);
        }
      } catch (error) {
        console.error('加载分析模板失败:', error);
      }
    };

    loadAnalysisTemplates();
  }, []);

  // 处理点击外部关闭下拉菜单
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showTemplateDropdown && !event.target.closest('.template-dropdown')) {
        setShowTemplateDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showTemplateDropdown]);

  // 处理海报文件选择
  const handlePosterFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // 验证文件类型
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        alert('不支持的文件类型，请上传图片文件 (jpg, png, webp, gif)');
        return;
      }

      // 验证文件大小（10MB）
      const maxSize = 10 * 1024 * 1024;
      if (file.size > maxSize) {
        alert('图片文件过大，请上传小于10MB的图片');
        return;
      }

      setSelectedPosterFile(file);
      setPosterPreviewUrl(URL.createObjectURL(file));
      setPosterAnalysisResult(null);
    }
  };

  // 分析海报
  const handleAnalyzePoster = async () => {
    if (!selectedPosterFile) {
      alert('请先选择海报图片');
      return;
    }

    try {
      setPosterAnalyzing(true);

      const token = localStorage.getItem('access_token');
      if (!token) {
        alert('请先登录');
        return;
      }

      const formData = new FormData();
      formData.append('image', selectedPosterFile);

      // 如果选择了模板，添加自定义提示词
      if (selectedTemplate) {
        formData.append('custom_prompt', selectedTemplate.prompt);
      }

      const response = await axios.post(
        `${API_BASE_URL}/api/poster/analyze`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      if (response.data.success) {
        setPosterAnalysisResult(response.data.analysis);
      } else {
        alert(response.data.error || '分析失败');
      }
    } catch (error) {
      console.error('海报分析失败:', error);

      // 检查是否为会员权限错误
      if (!handleMembershipError(error, onNavigate)) {
        // 如果不是会员权限错误，显示普通错误消息
        alert(error.response?.data?.error || '分析失败，请重试');
      }
    } finally {
      setPosterAnalyzing(false);
    }
  };

  // 重新分析
  const handleResetAnalysis = () => {
    setPosterAnalysisResult(null);
    setSelectedPosterFile(null);
    setPosterPreviewUrl(null);
    setSelectedTemplate(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-orange-50 to-red-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 头部导航 */}
        <div className="mb-8">
          <button
            onClick={() => onNavigate('dashboard')}
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors mb-4"
          >
            <ArrowLeftIcon className="w-5 h-5" />
            <span>返回首页</span>
          </button>

          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-yellow-600 to-orange-600 flex items-center justify-center shadow-lg">
              <SparklesIcon className="w-9 h-9 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">海报分析工具</h1>
              <p className="text-gray-600 mt-1">使用AI智能分析海报设计和营销效果</p>
            </div>
          </div>
        </div>

        {/* 主内容区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左侧：上传和预览区域 */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">上传海报图片</h2>

              <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 hover:border-yellow-500 transition-colors bg-gray-50">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handlePosterFileChange}
                  className="hidden"
                  id="poster-upload"
                />
                <label
                  htmlFor="poster-upload"
                  className="cursor-pointer flex flex-col items-center justify-center"
                >
                  {posterPreviewUrl ? (
                    <div className="w-full">
                      <img
                        src={posterPreviewUrl}
                        alt="海报预览"
                        className="w-full h-auto rounded-xl shadow-md max-h-[500px] object-contain"
                      />
                      <p className="text-sm text-gray-600 text-center mt-4 font-medium">
                        点击更换图片
                      </p>
                    </div>
                  ) : (
                    <>
                      <svg className="w-20 h-20 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                      <p className="text-lg text-gray-700 font-medium mb-2">点击上传海报图片</p>
                      <p className="text-sm text-gray-500">支持 JPG, PNG, WebP, GIF (最大10MB)</p>
                    </>
                  )}
                </label>
              </div>
            </div>

            {/* 分析模板选择 - 下拉选择 */}
            <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">选择分析模板</h2>
              <p className="text-sm text-gray-600 mb-4">选择一个分析模板，或不选择使用默认全面分析</p>

              <div className="relative template-dropdown">
                {/* 下拉选择按钮 */}
                <button
                  type="button"
                  onClick={() => setShowTemplateDropdown(!showTemplateDropdown)}
                  className={`w-full px-4 py-3 border-2 rounded-xl text-left flex items-center justify-between transition-all ${
                    showTemplateDropdown
                      ? 'border-yellow-500 bg-yellow-50 shadow-md'
                      : 'border-gray-300 bg-white hover:border-yellow-400 hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    {selectedTemplate ? (
                      <>
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-yellow-500 to-orange-500 text-white flex items-center justify-center flex-shrink-0 shadow-md">
                          <span className="text-sm font-bold">{selectedTemplate.id}</span>
                        </div>
                        <div>
                          <div className="font-semibold text-gray-900">{selectedTemplate.name}</div>
                          <div className="text-xs text-gray-600 line-clamp-1">{selectedTemplate.description}</div>
                        </div>
                      </>
                    ) : (
                      <>
                        <div className="w-8 h-8 rounded-lg bg-gray-100 text-gray-400 flex items-center justify-center flex-shrink-0">
                          <SparklesIcon className="w-5 h-5" />
                        </div>
                        <div className="text-gray-500">选择分析模板（可选）</div>
                      </>
                    )}
                  </div>
                  <ChevronDownIcon className={`w-5 h-5 text-gray-400 transition-transform ${showTemplateDropdown ? 'rotate-180' : ''}`} />
                </button>

                {/* 下拉菜单 */}
                {showTemplateDropdown && (
                  <div className="absolute z-10 w-full mt-2 bg-white border-2 border-yellow-400 rounded-xl shadow-2xl max-h-[500px] overflow-y-auto">
                    {/* 清除选择选项 */}
                    {selectedTemplate && (
                      <button
                        type="button"
                        onClick={() => {
                          setSelectedTemplate(null);
                          setShowTemplateDropdown(false);
                        }}
                        className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-200 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-gray-100 text-gray-400 flex items-center justify-center flex-shrink-0">
                            <XMarkIcon className="w-5 h-5" />
                          </div>
                          <div>
                            <div className="font-medium text-gray-700">不选择模板</div>
                            <div className="text-xs text-gray-500">使用默认全面分析</div>
                          </div>
                        </div>
                      </button>
                    )}

                    {/* 模板选项列表 */}
                    {analysisTemplates.map((template, index) => (
                      <button
                        key={template.id}
                        type="button"
                        onClick={() => {
                          setSelectedTemplate(template);
                          setShowTemplateDropdown(false);
                        }}
                        className={`w-full px-4 py-3 text-left transition-all ${
                          selectedTemplate?.id === template.id
                            ? 'bg-gradient-to-r from-yellow-50 to-orange-50'
                            : 'hover:bg-yellow-50/50'
                        } ${index !== analysisTemplates.length - 1 ? 'border-b border-gray-200' : ''}`}
                      >
                        <div className="flex items-start gap-3">
                          {/* 编号徽章 */}
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 transition-all ${
                            selectedTemplate?.id === template.id
                              ? 'bg-gradient-to-br from-yellow-500 to-orange-500 text-white shadow-md'
                              : 'bg-gray-100 text-gray-600'
                          }`}>
                            <span className="text-sm font-bold">{template.id}</span>
                          </div>

                          {/* 模板信息 */}
                          <div className="flex-1">
                            <div className={`font-semibold mb-1 ${
                              selectedTemplate?.id === template.id ? 'text-yellow-900' : 'text-gray-900'
                            }`}>
                              {template.name}
                            </div>
                            <div className={`text-xs ${
                              selectedTemplate?.id === template.id ? 'text-gray-700' : 'text-gray-600'
                            }`}>
                              {template.description}
                            </div>
                          </div>

                          {/* 选中指示器 */}
                          {selectedTemplate?.id === template.id && (
                            <div className="flex-shrink-0">
                              <svg className="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                            </div>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* 分析按钮 */}
            <button
              type="button"
              onClick={handleAnalyzePoster}
              disabled={!selectedPosterFile || posterAnalyzing}
              className="w-full px-6 py-4 bg-gradient-to-r from-yellow-600 to-orange-600 text-white rounded-xl hover:from-yellow-700 hover:to-orange-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-lg shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
            >
              {posterAnalyzing ? (
                <>
                  <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-white"></div>
                  <span>AI分析中...</span>
                </>
              ) : (
                <>
                  <SparklesIcon className="w-6 h-6" />
                  <span>开始AI分析</span>
                </>
              )}
            </button>
          </div>

          {/* 右侧：分析结果区域 */}
          <div className="space-y-6">
            <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200 min-h-[600px]">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">分析结果</h2>
                {posterAnalysisResult && (
                  <button
                    type="button"
                    onClick={() => setShowFullscreen(true)}
                    className="p-2 text-gray-600 hover:text-yellow-600 hover:bg-yellow-50 rounded-lg transition-all"
                    title="全屏显示"
                  >
                    <ArrowsPointingOutIcon className="w-5 h-5" />
                  </button>
                )}
              </div>

              <div className="border border-gray-200 rounded-xl p-6 bg-gray-50 min-h-[500px] max-h-[700px] overflow-y-auto">
                {posterAnalysisResult ? (
                  <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-800 prose-strong:text-gray-900 prose-ul:text-gray-800 prose-ol:text-gray-800 prose-table:text-sm">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {posterAnalysisResult}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-gray-400 py-20">
                    <svg className="w-24 h-24 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <p className="text-lg font-medium">分析结果将在此显示</p>
                    <p className="text-sm mt-2">上传海报图片并点击"开始AI分析"按钮</p>
                  </div>
                )}
              </div>

              {/* 操作按钮 */}
              {posterAnalysisResult && (
                <div className="flex gap-4 mt-6">
                  <button
                    type="button"
                    onClick={() => {
                      navigator.clipboard.writeText(posterAnalysisResult);
                      alert('分析结果已复制到剪贴板');
                    }}
                    className="flex-1 px-4 py-3 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 hover:border-gray-400 transition-all font-medium"
                  >
                    📋 复制结果
                  </button>
                  <button
                    type="button"
                    onClick={handleResetAnalysis}
                    className="flex-1 px-4 py-3 bg-gradient-to-r from-yellow-600 to-orange-600 text-white rounded-xl hover:from-yellow-700 hover:to-orange-700 transition-all font-medium shadow-md hover:shadow-lg"
                  >
                    🔄 重新分析
                  </button>
                </div>
              )}
            </div>

            {/* 使用提示 */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                使用提示
              </h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 font-bold">•</span>
                  <span>支持多种图片格式：JPG、PNG、WebP、GIF</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 font-bold">•</span>
                  <span>图片文件大小不超过10MB</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 font-bold">•</span>
                  <span>选择分析模板可获得更针对性的分析结果</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 font-bold">•</span>
                  <span>分析结果可直接复制使用</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* 全屏模态框 */}
      {showFullscreen && posterAnalysisResult && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl h-[90vh] flex flex-col">
            {/* 全屏模态框头部 */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">分析结果</h2>
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => {
                    navigator.clipboard.writeText(posterAnalysisResult);
                    alert('分析结果已复制到剪贴板');
                  }}
                  className="px-4 py-2 border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-all font-medium"
                >
                  📋 复制结果
                </button>
                <button
                  type="button"
                  onClick={() => setShowFullscreen(false)}
                  className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                  title="关闭全屏"
                >
                  <XMarkIcon className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* 全屏模态框内容 */}
            <div className="flex-1 overflow-y-auto p-8">
              <div className="prose prose-base max-w-none prose-headings:text-gray-900 prose-p:text-gray-800 prose-strong:text-gray-900 prose-ul:text-gray-800 prose-ol:text-gray-800 prose-li:text-gray-800 prose-table:text-sm prose-headings:font-bold prose-h1:text-3xl prose-h2:text-2xl prose-h3:text-xl">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {posterAnalysisResult}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PosterAnalyzer;
