import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  PlusIcon,
  PlayIcon,
  DocumentTextIcon,
  TrashIcon,
  ClockIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { API_BASE_URL } from '../config';

function VideoProjectList() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [videoModalOpen, setVideoModalOpen] = useState(false);
  const [currentVideoUrl, setCurrentVideoUrl] = useState(null);

  // 加载项目列表
  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${API_BASE_URL}/api/video/projects/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.status === 'success') {
        setProjects(data.data);
      }
    } catch (error) {
      console.error('加载项目列表失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 删除项目
  const deleteProject = async (projectId) => {
    if (!confirm('确定要删除这个视频项目吗？')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${API_BASE_URL}/api/video/projects/${projectId}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.status === 'success') {
        loadProjects(); // 重新加载列表
      } else {
        alert(data.message || '删除失败');
      }
    } catch (error) {
      console.error('删除项目失败:', error);
      alert('删除失败');
    }
  };

  // 格式化日期
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // 打开视频播放器
  const openVideoPlayer = (videoUrl) => {
    setCurrentVideoUrl(videoUrl);
    setVideoModalOpen(true);
  };

  // 关闭视频播放器
  const closeVideoPlayer = () => {
    setVideoModalOpen(false);
    setCurrentVideoUrl(null);
  };

  // 状态徽章颜色
  const getStatusBadge = (status) => {
    const statusColors = {
      draft: 'bg-gray-100 text-gray-700',
      processing: 'bg-yellow-100 text-yellow-700',
      completed: 'bg-green-100 text-green-700',
      failed: 'bg-red-100 text-red-700',
    };
    return statusColors[status] || 'bg-gray-100 text-gray-700';
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
                视频项目
              </h1>
              <p className="text-xs md:text-base text-gray-600 mt-1 md:mt-2">
                管理你的视频创作项目
              </p>
            </div>

            <button
              onClick={() => navigate('/video-generator')}
              className="px-4 md:px-6 py-2 md:py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg md:rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all flex items-center gap-2 text-sm md:text-base font-semibold shadow-md hover:shadow-lg"
            >
              <PlusIcon className="w-4 h-4 md:w-5 md:h-5" />
              <span>新建视频</span>
            </button>
          </div>
        </div>

        {/* 加载状态 */}
        {isLoading && (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        {/* 项目列表 */}
        {!isLoading && projects.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                className="bg-white rounded-lg md:rounded-xl shadow-md hover:shadow-lg transition-all p-4 md:p-6"
              >
                {/* 项目标题和状态 */}
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-base md:text-lg font-semibold text-gray-900 flex-1 mr-2">
                    {project.title}
                  </h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(project.status)}`}>
                    {project.status_display}
                  </span>
                </div>

                {/* 项目信息 */}
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-xs md:text-sm text-gray-600">
                    <DocumentTextIcon className="w-4 h-4 mr-2" />
                    <span>{project.scene_count} 个场景</span>
                  </div>
                  <div className="flex items-center text-xs md:text-sm text-gray-600">
                    <ClockIcon className="w-4 h-4 mr-2" />
                    <span>{formatDate(project.updated_at)}</span>
                  </div>
                </div>

                {/* 操作按钮 */}
                <div className="flex gap-2">
                  {project.video_url ? (
                    <>
                      <button
                        onClick={() => openVideoPlayer(project.video_url)}
                        className="flex-1 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all flex items-center justify-center gap-2 text-xs md:text-sm font-semibold"
                      >
                        <PlayIcon className="w-4 h-4" />
                        <span>播放</span>
                      </button>
                      <button
                        onClick={() => navigate(`/video-generator?project=${project.id}`)}
                        className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all flex items-center justify-center text-xs md:text-sm"
                      >
                        <DocumentTextIcon className="w-4 h-4" />
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => navigate(`/video-generator?project=${project.id}`)}
                      className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all flex items-center justify-center gap-2 text-xs md:text-sm font-semibold"
                    >
                      <PlayIcon className="w-4 h-4" />
                      <span>编辑</span>
                    </button>
                  )}
                  <button
                    onClick={() => deleteProject(project.id)}
                    className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all flex items-center justify-center text-xs md:text-sm"
                  >
                    <TrashIcon className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 空状态 */}
        {!isLoading && projects.length === 0 && (
          <div className="bg-white rounded-lg md:rounded-xl shadow-md p-8 md:p-12 text-center">
            <DocumentTextIcon className="w-12 h-12 md:w-16 md:h-16 mx-auto text-gray-300 mb-3 md:mb-4" />
            <h3 className="text-base md:text-lg font-semibold text-gray-900 mb-2">
              还没有视频项目
            </h3>
            <p className="text-xs md:text-sm text-gray-600 mb-4">
              点击上方"新建视频"按钮创建你的第一个视频项目
            </p>
            <button
              onClick={() => navigate('/video-generator')}
              className="px-4 md:px-6 py-2 md:py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg md:rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all inline-flex items-center gap-2 text-sm md:text-base font-semibold"
            >
              <PlusIcon className="w-4 h-4 md:w-5 md:h-5" />
              <span>新建视频</span>
            </button>
          </div>
        )}
      </div>

      {/* 视频播放模态框 */}
      {videoModalOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={closeVideoPlayer}
        >
          <div
            className="relative bg-white rounded-xl shadow-2xl max-w-4xl w-full"
            onClick={(e) => e.stopPropagation()}
          >
            {/* 关闭按钮 */}
            <button
              onClick={closeVideoPlayer}
              className="absolute -top-10 right-0 text-white hover:text-gray-300 transition-colors"
            >
              <XMarkIcon className="w-8 h-8" />
            </button>

            {/* 视频播放器 */}
            <div className="p-4">
              <video
                src={currentVideoUrl}
                controls
                autoPlay
                className="w-full rounded-lg"
                style={{ maxHeight: '70vh' }}
              >
                您的浏览器不支持视频播放。
              </video>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default VideoProjectList;
