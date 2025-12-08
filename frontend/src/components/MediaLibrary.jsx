import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  PhotoIcon,
  HeartIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  ArrowUpTrayIcon,
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';
import { API_BASE_URL } from '../config';

function MediaLibrary() {
  const navigate = useNavigate();

  const [mediaList, setMediaList] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [selectedType, setSelectedType] = useState(''); // '' | 'ip_image' | 'content_image'
  const [showFavoriteOnly, setShowFavoriteOnly] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [previewImage, setPreviewImage] = useState(null);

  // 上传相关状态
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadPreview, setUploadPreview] = useState(null);
  const [uploadType, setUploadType] = useState('content_image');
  const [uploadPrompt, setUploadPrompt] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  // 检测是否在小程序环境
  const [isInMiniProgram, setIsInMiniProgram] = useState(false);

  useEffect(() => {
    const checkMiniProgram = () => {
      const hasMiniProgram = typeof window !== 'undefined' &&
                            typeof window.wx !== 'undefined' &&
                            typeof window.wx.miniProgram !== 'undefined';
      setIsInMiniProgram(hasMiniProgram);
    };
    checkMiniProgram();
  }, []);

  // 获取素材库列表
  useEffect(() => {
    fetchMediaLibrary();
    fetchStats();
  }, [currentPage, selectedType, showFavoriteOnly]);

  const fetchMediaLibrary = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('access_token');
      const params = new URLSearchParams({
        page: currentPage,
        page_size: 12
      });

      if (selectedType) {
        params.append('media_type', selectedType);
      }

      if (showFavoriteOnly) {
        params.append('is_favorite', 'true');
      }

      const response = await fetch(`${API_BASE_URL}/api/media-library/?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.status === 'success') {
        setMediaList(data.data.items);
        setTotalPages(data.data.total_pages);
      }
    } catch (error) {
      console.error('获取素材库失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/media-library/stats/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.status === 'success') {
        setStats(data.data);
      }
    } catch (error) {
      console.error('获取统计信息失败:', error);
    }
  };

  const toggleFavorite = async (mediaId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/media-library/${mediaId}/favorite/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.status === 'success') {
        // 更新列表中的收藏状态
        setMediaList(prev => prev.map(item =>
          item.id === mediaId ? { ...item, is_favorite: data.is_favorite } : item
        ));
        // 刷新统计
        fetchStats();
      }
    } catch (error) {
      console.error('切换收藏失败:', error);
    }
  };

  const deleteMedia = async (mediaId) => {
    if (!confirm('确定要删除这个素材吗？')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/media-library/${mediaId}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.status === 'success') {
        // 从列表中移除
        setMediaList(prev => prev.filter(item => item.id !== mediaId));
        // 刷新统计
        fetchStats();
      }
    } catch (error) {
      console.error('删除素材失败:', error);
    }
  };

  const batchDelete = async () => {
    if (selectedItems.size === 0) {
      alert('请先选择要删除的素材');
      return;
    }

    if (!confirm(`确定要删除选中的 ${selectedItems.size} 个素材吗？`)) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/media-library/batch-delete/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          media_ids: Array.from(selectedItems)
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        // 清空选择
        setSelectedItems(new Set());
        // 刷新列表
        fetchMediaLibrary();
        fetchStats();
        alert(data.message);
      }
    } catch (error) {
      console.error('批量删除失败:', error);
      alert('删除失败，请重试');
    }
  };

  const toggleSelectItem = (itemId) => {
    setSelectedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  const selectAll = () => {
    if (selectedItems.size === mediaList.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(mediaList.map(item => item.id)));
    }
  };

  const downloadImage = (url, id) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = `media-${id}-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 处理文件选择
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件');
      return;
    }

    // 验证文件大小
    if (file.size > 10 * 1024 * 1024) {
      alert('图片大小不能超过10MB');
      return;
    }

    setUploadFile(file);

    // 创建预览
    const reader = new FileReader();
    reader.onload = (e) => {
      setUploadPreview(e.target.result);
    };
    reader.readAsDataURL(file);
  };

  // 上传图片
  const handleUpload = async () => {
    if (!uploadFile) {
      alert('请选择图片文件');
      return;
    }

    try {
      setIsUploading(true);

      const formData = new FormData();
      formData.append('image', uploadFile);
      formData.append('media_type', uploadType);
      formData.append('prompt', uploadPrompt);

      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/media-library/upload/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();
      if (data.status === 'success') {
        alert('上传成功！');
        // 关闭模态框
        setShowUploadModal(false);
        // 重置表单
        setUploadFile(null);
        setUploadPreview(null);
        setUploadPrompt('');
        setUploadType('content_image');
        // 刷新列表
        fetchMediaLibrary();
        fetchStats();
      } else {
        alert(data.message || '上传失败');
      }
    } catch (error) {
      console.error('上传失败:', error);
      alert('上传失败，请重试');
    } finally {
      setIsUploading(false);
    }
  };

  // 关闭上传模态框
  const closeUploadModal = () => {
    setShowUploadModal(false);
    setUploadFile(null);
    setUploadPreview(null);
    setUploadPrompt('');
    setUploadType('content_image');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-7xl mx-auto px-3 md:px-4 sm:px-6 lg:px-8 py-3 md:py-6">
        {/* Header */}
        <div className="mb-4 md:mb-6">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center text-gray-600 hover:text-gray-900 transition-colors mb-3 md:mb-4"
          >
            <ArrowLeftIcon className="w-4 h-4 md:w-5 md:h-5 mr-1 md:mr-2" />
            <span className="text-sm md:text-base">返回</span>
          </button>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl md:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                我的素材库
              </h1>
              <p className="text-xs md:text-base text-gray-600 mt-1 md:mt-2">管理您生成的所有图片素材</p>
            </div>
          </div>
        </div>

        {/* 统计卡片 */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-4 mb-4 md:mb-6">
            <div className="bg-white rounded-lg md:rounded-xl p-2 md:p-4 shadow-md">
              <div className="text-gray-600 text-xs md:text-sm mb-1">总素材</div>
              <div className="text-lg md:text-2xl font-bold text-blue-600">{stats.total_count}</div>
            </div>
            <div className="bg-white rounded-lg md:rounded-xl p-2 md:p-4 shadow-md">
              <div className="text-gray-600 text-xs md:text-sm mb-1">IP形象</div>
              <div className="text-lg md:text-2xl font-bold text-purple-600">{stats.ip_image_count}</div>
            </div>
            <div className="bg-white rounded-lg md:rounded-xl p-2 md:p-4 shadow-md">
              <div className="text-gray-600 text-xs md:text-sm mb-1">文案配图</div>
              <div className="text-lg md:text-2xl font-bold text-indigo-600">{stats.content_image_count}</div>
            </div>
            <div className="bg-white rounded-lg md:rounded-xl p-2 md:p-4 shadow-md">
              <div className="text-gray-600 text-xs md:text-sm mb-1">存储空间</div>
              <div className="text-lg md:text-2xl font-bold text-green-600">{stats.total_size_mb} MB</div>
            </div>
          </div>
        )}

        {/* 筛选栏 */}
        <div className="bg-white rounded-lg md:rounded-xl shadow-md p-2 md:p-4 mb-4 md:mb-6">
          <div className="flex flex-col md:flex-row md:flex-wrap items-stretch md:items-center gap-2 md:gap-4">
            {/* 类型筛选 */}
            <div className="flex items-center gap-1 md:gap-2 flex-1 md:flex-initial">
              <button
                onClick={() => setSelectedType('')}
                className={`flex-1 md:flex-initial px-2 md:px-4 py-1.5 md:py-2 text-xs md:text-sm rounded-lg transition-all ${
                  selectedType === ''
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                全部
              </button>
              <button
                onClick={() => setSelectedType('ip_image')}
                className={`flex-1 md:flex-initial px-2 md:px-4 py-1.5 md:py-2 text-xs md:text-sm rounded-lg transition-all ${
                  selectedType === 'ip_image'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                IP形象
              </button>
              <button
                onClick={() => setSelectedType('content_image')}
                className={`flex-1 md:flex-initial px-2 md:px-4 py-1.5 md:py-2 text-xs md:text-sm rounded-lg transition-all ${
                  selectedType === 'content_image'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                文案配图
              </button>
            </div>

            {/* 第二行：收藏、上传、操作按钮 */}
            <div className="flex items-center gap-2 flex-wrap">
              {/* 收藏筛选 */}
              <button
                onClick={() => setShowFavoriteOnly(!showFavoriteOnly)}
                className={`px-2 md:px-4 py-1.5 md:py-2 text-xs md:text-sm rounded-lg transition-all flex items-center gap-1 md:gap-2 ${
                  showFavoriteOnly
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <HeartIcon className="w-4 h-4 md:w-5 md:h-5" />
                <span className="hidden md:inline">仅收藏</span>
              </button>

              {/* 上传按钮 */}
              <button
                onClick={() => setShowUploadModal(true)}
                className="px-2 md:px-4 py-1.5 md:py-2 text-xs md:text-sm bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all flex items-center gap-1 md:gap-2 shadow-md hover:shadow-lg"
              >
                <ArrowUpTrayIcon className="w-4 h-4 md:w-5 md:h-5" />
                <span>上传</span>
              </button>

              {/* 批量操作 */}
              {selectedItems.size > 0 ? (
                <>
                  <span className="text-xs md:text-sm text-gray-600">已选 {selectedItems.size}</span>
                  <button
                    onClick={batchDelete}
                    className="px-2 md:px-4 py-1.5 md:py-2 text-xs md:text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all flex items-center gap-1 md:gap-2"
                  >
                    <TrashIcon className="w-4 h-4 md:w-5 md:h-5" />
                    <span>删除</span>
                  </button>
                </>
              ) : null}

              {/* 全选按钮 */}
              <button
                onClick={selectAll}
                className="px-2 md:px-4 py-1.5 md:py-2 text-xs md:text-sm bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-all ml-auto"
              >
                {selectedItems.size === mediaList.length && mediaList.length > 0 ? '取消' : '全选'}
              </button>
            </div>
          </div>
        </div>

        {/* 素材网格 */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : mediaList.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 md:gap-4">
            {mediaList.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-lg md:rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-all relative group"
              >
                {/* 选择框 */}
                <div className="absolute top-1 left-1 md:top-2 md:left-2 z-10">
                  <input
                    type="checkbox"
                    checked={selectedItems.has(item.id)}
                    onChange={() => toggleSelectItem(item.id)}
                    className="w-4 h-4 md:w-5 md:h-5 rounded cursor-pointer"
                  />
                </div>

                {/* 类型标签 */}
                <div className="absolute top-1 right-1 md:top-2 md:right-2 z-10">
                  <span className={`px-1.5 py-0.5 md:px-2 md:py-1 text-[10px] md:text-xs rounded-full text-white ${
                    item.media_type === 'ip_image' ? 'bg-purple-600' : 'bg-indigo-600'
                  }`}>
                    {item.media_type_display}
                  </span>
                </div>

                {/* 图片 */}
                <div
                  className="aspect-square cursor-pointer"
                  onClick={() => setPreviewImage(item)}
                >
                  <img
                    src={item.url}
                    alt={item.prompt}
                    className="w-full h-full object-cover"
                  />
                </div>

                {/* 信息栏 */}
                <div className="p-2 md:p-3">
                  <p className="text-xs md:text-sm text-gray-600 line-clamp-2 mb-1 md:mb-2">
                    {item.prompt || '无描述'}
                  </p>

                  <div className="flex items-center justify-between">
                    <span className="text-[10px] md:text-xs text-gray-500">{item.created_at}</span>

                    <div className="flex items-center gap-1 md:gap-2">
                      {/* 收藏按钮 */}
                      <button
                        onClick={() => toggleFavorite(item.id)}
                        className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                      >
                        {item.is_favorite ? (
                          <HeartSolidIcon className="w-4 h-4 md:w-5 md:h-5 text-red-600" />
                        ) : (
                          <HeartIcon className="w-4 h-4 md:w-5 md:h-5 text-gray-400" />
                        )}
                      </button>

                      {/* 删除按钮 */}
                      <button
                        onClick={() => deleteMedia(item.id)}
                        className="p-1 hover:bg-gray-100 rounded-full transition-colors"
                      >
                        <TrashIcon className="w-4 h-4 md:w-5 md:h-5 text-gray-400 hover:text-red-600" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg md:rounded-xl shadow-md p-8 md:p-12 text-center">
            <PhotoIcon className="w-12 h-12 md:w-16 md:h-16 mx-auto text-gray-300 mb-3 md:mb-4" />
            <p className="text-sm md:text-base text-gray-500">暂无素材</p>
          </div>
        )}

        {/* 分页 */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-2 mt-4 md:mt-6">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1.5 md:px-4 md:py-2 text-xs md:text-sm bg-white rounded-lg shadow-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
            >
              上一页
            </button>

            <span className="px-2 md:px-4 py-1.5 md:py-2 text-xs md:text-sm text-gray-600">
              {currentPage} / {totalPages}
            </span>

            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-3 py-1.5 md:px-4 md:py-2 text-xs md:text-sm bg-white rounded-lg shadow-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
            >
              下一页
            </button>
          </div>
        )}

        {/* 图片预览模态框 */}
        {previewImage && (
          <div
            className="fixed inset-0 bg-black bg-opacity-80 flex items-center justify-center z-50 p-4"
            onClick={() => setPreviewImage(null)}
          >
            <div className="relative max-w-4xl max-h-[90vh] w-full">
              {/* 关闭按钮 */}
              <button
                onClick={() => setPreviewImage(null)}
                className="absolute -top-12 right-0 text-white hover:text-gray-300 transition-colors"
              >
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              {/* 图片 */}
              <div
                className="bg-white rounded-2xl overflow-hidden"
                onClick={(e) => e.stopPropagation()}
              >
                <img
                  src={previewImage.url}
                  alt={previewImage.prompt}
                  className="w-full h-auto max-h-[70vh] object-contain"
                />

                {/* 信息栏 */}
                <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-2 py-1 text-xs rounded-full text-white ${
                          previewImage.media_type === 'ip_image' ? 'bg-purple-600' : 'bg-indigo-600'
                        }`}>
                          {previewImage.media_type_display}
                        </span>
                        <span className="text-xs text-gray-500">{previewImage.created_at}</span>
                      </div>
                      <p className="text-sm text-gray-700">{previewImage.prompt || '无描述'}</p>
                    </div>

                    <div className="flex items-center gap-2 ml-4">
                      {/* 收藏 */}
                      <button
                        onClick={() => {
                          toggleFavorite(previewImage.id);
                          setPreviewImage(prev => ({ ...prev, is_favorite: !prev.is_favorite }));
                        }}
                        className="p-2 hover:bg-white rounded-lg transition-colors"
                      >
                        {previewImage.is_favorite ? (
                          <HeartSolidIcon className="w-6 h-6 text-red-600" />
                        ) : (
                          <HeartIcon className="w-6 h-6 text-gray-400" />
                        )}
                      </button>

                      {/* 下载 */}
                      {!isInMiniProgram && (
                        <button
                          onClick={() => downloadImage(previewImage.url, previewImage.id)}
                          className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all"
                        >
                          下载
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 上传模态框 */}
        {showUploadModal && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={closeUploadModal}
          >
            <div
              className="bg-white rounded-2xl max-w-lg w-full p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900">上传图片</h3>
                <button
                  onClick={closeUploadModal}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* 上传区域 */}
              {!uploadPreview ? (
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-blue-400 transition-colors">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="upload-input"
                  />
                  <label htmlFor="upload-input" className="cursor-pointer">
                    <ArrowUpTrayIcon className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600 mb-2">点击或拖拽上传图片</p>
                    <p className="text-sm text-gray-400">支持 JPG、PNG、WEBP、GIF，最大10MB</p>
                  </label>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* 图片预览 */}
                  <div className="relative">
                    <img
                      src={uploadPreview}
                      alt="预览"
                      className="w-full h-64 object-contain rounded-xl bg-gray-100"
                    />
                    <button
                      onClick={() => {
                        setUploadFile(null);
                        setUploadPreview(null);
                      }}
                      className="absolute top-2 right-2 p-2 bg-red-600 text-white rounded-full hover:bg-red-700 transition-colors"
                    >
                      <TrashIcon className="w-5 h-5" />
                    </button>
                  </div>

                  {/* 类型选择 */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      素材类型
                    </label>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setUploadType('content_image')}
                        className={`flex-1 px-4 py-2 rounded-lg transition-all ${
                          uploadType === 'content_image'
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        文案配图
                      </button>
                      <button
                        onClick={() => setUploadType('ip_image')}
                        className={`flex-1 px-4 py-2 rounded-lg transition-all ${
                          uploadType === 'ip_image'
                            ? 'bg-purple-600 text-white'
                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        }`}
                      >
                        IP形象
                      </button>
                    </div>
                  </div>

                  {/* 描述输入 */}
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      描述/标题（可选）
                    </label>
                    <textarea
                      value={uploadPrompt}
                      onChange={(e) => setUploadPrompt(e.target.value)}
                      placeholder="为这张图片添加描述..."
                      className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                      rows="3"
                      maxLength="500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      {uploadPrompt.length}/500 字符
                    </p>
                  </div>

                  {/* 上传按钮 */}
                  <div className="flex gap-2">
                    <button
                      onClick={closeUploadModal}
                      className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 transition-colors font-semibold"
                    >
                      取消
                    </button>
                    <button
                      onClick={handleUpload}
                      disabled={isUploading}
                      className="flex-1 px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {isUploading ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                          <span>上传中...</span>
                        </>
                      ) : (
                        <>
                          <ArrowUpTrayIcon className="w-5 h-5" />
                          <span>确认上传</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default MediaLibrary;
