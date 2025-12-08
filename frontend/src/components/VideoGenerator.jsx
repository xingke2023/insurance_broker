import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  ArrowLeftIcon,
  SparklesIcon,
  PhotoIcon,
  PlusIcon,
  TrashIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import { API_BASE_URL } from '../config';

function VideoGenerator() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // 当前项目ID（用于更新草稿）
  const [currentProjectId, setCurrentProjectId] = useState(null);

  // 字幕输入
  const [subtitles, setSubtitles] = useState('');

  // 自定义场景数量
  const [customSceneCount, setCustomSceneCount] = useState('');

  // 语音选择
  const [voice, setVoice] = useState('zh-CN-YunxiNeural');

  // 生成的提示词列表（场景列表）
  const [prompts, setPrompts] = useState([]);

  // 生成状态
  const [isGeneratingPrompts, setIsGeneratingPrompts] = useState(false);
  const [generatingImageIndex, setGeneratingImageIndex] = useState(null);
  const [isCreatingVideo, setIsCreatingVideo] = useState(false);

  // 拖拽状态
  const [draggedIndex, setDraggedIndex] = useState(null);

  // 字幕分配相关
  const [subtitleLines, setSubtitleLines] = useState([]);

  // 素材库模态框
  const [showMediaLibrary, setShowMediaLibrary] = useState(false);
  const [selectingForIndex, setSelectingForIndex] = useState(null);
  const [mediaList, setMediaList] = useState([]);
  const [isLoadingMedia, setIsLoadingMedia] = useState(false);

  // 图片预览放大
  const [previewImage, setPreviewImage] = useState(null);

  // 草稿相关
  const [hasDraft, setHasDraft] = useState(false);

  // 页面加载时检查URL参数，加载项目
  useEffect(() => {
    const projectId = searchParams.get('project');
    if (projectId) {
      loadProject(projectId);
    } else {
      // 检查localStorage草稿
      const draft = localStorage.getItem('video_draft');
      if (draft) {
        setHasDraft(true);
      }
    }
  }, [searchParams]);

  // 加载项目数据
  const loadProject = async (projectId) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/api/video/projects/${projectId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const result = await response.json();
      if (result.status === 'success') {
        const project = result.data;
        setCurrentProjectId(project.id);
        setSubtitles(project.subtitles || '');
        setCustomSceneCount('');
        setVoice(project.voice || 'zh-CN-YunxiNeural');
        setPrompts(project.scenes_data || []);
        // 清除localStorage草稿提示
        setHasDraft(false);
      } else {
        alert('加载项目失败');
      }
    } catch (error) {
      console.error('加载项目失败:', error);
      alert('加载项目失败');
    }
  };

  // 加载草稿
  const loadDraft = () => {
    const draftStr = localStorage.getItem('video_draft');
    if (!draftStr) {
      alert('没有找到草稿');
      return;
    }

    try {
      const draft = JSON.parse(draftStr);
      setSubtitles(draft.subtitles || '');
      setCustomSceneCount(draft.customSceneCount || '');
      setPrompts(draft.prompts || []);
      setHasDraft(false);
      alert('草稿已加载！');
    } catch (error) {
      console.error('加载草稿失败:', error);
      alert('加载草稿失败');
    }
  };

  // 删除草稿
  const deleteDraft = () => {
    if (confirm('确定要删除草稿吗？')) {
      localStorage.removeItem('video_draft');
      setHasDraft(false);
      alert('草稿已删除');
    }
  };

  // 保存草稿到数据库
  const saveDraft = async () => {
    try {
      const token = localStorage.getItem('access_token');

      const projectData = {
        title: '未命名视频',
        subtitles,
        scenes_data: prompts,
        duration: 3.0,
        voice: voice,
        status: 'draft'
      };

      let response;
      if (currentProjectId) {
        // 更新现有草稿
        response = await fetch(`${API_BASE_URL}/api/video/projects/${currentProjectId}/update/`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(projectData)
        });
      } else {
        // 创建新草稿
        response = await fetch(`${API_BASE_URL}/api/video/projects/create/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(projectData)
        });
      }

      const result = await response.json();
      if (result.status === 'success') {
        if (!currentProjectId) {
          setCurrentProjectId(result.data.id);
          // 更新URL参数
          navigate(`/video-generator?project=${result.data.id}`, { replace: true });
        }
        alert('草稿已保存！');
      } else {
        alert('保存失败: ' + (result.message || '未知错误'));
      }
    } catch (error) {
      console.error('保存草稿失败:', error);
      alert('保存失败');
    }
  };

  // 创建视频
  const createVideo = async () => {
    // 检查是否所有场景都有图片
    const scenesWithoutImage = prompts.filter(p => !p.image);
    if (scenesWithoutImage.length > 0) {
      alert(`请为所有场景添加图片后再制作视频！\n还有 ${scenesWithoutImage.length} 个场景没有图片。`);
      return;
    }

    try {
      setIsCreatingVideo(true);

      // 获取认证token
      const token = localStorage.getItem('access_token');

      // 1. 先调用视频生成API获取taskid
      const requestData = {
        images: prompts.map(prompt => ({
          image_url: prompt.image,
          text: (prompt.assignedSubtitles || []).join('，')
        })),
        duration: 3.0,
        voice: voice
      };

      console.log('发送视频创建请求:', requestData);

      const response = await fetch(`${API_BASE_URL}/api/video/create/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });

      const result = await response.json();

      // 2. 检查API返回结果
      if (!response.ok) {
        console.error('视频创建失败:', result);
        alert(`视频创建失败: ${result.message || '未知错误'}`);
        return;
      }

      console.log('视频创建成功:', result);

      // 3. 必须等待返回task_id才保存到数据库
      if (!result.task_id) {
        alert('视频服务未返回任务ID，无法保存记录');
        return;
      }

      // 4. 保存项目到数据库
      const projectData = {
        title: subtitles.split('\n')[0].slice(0, 50) || '未命名视频',
        subtitles,
        scene_count: prompts.length,
        scenes_data: prompts,
        duration: 3.0,
        voice: voice,
        status: 'processing',
        taskid: result.task_id
      };

      let projectId = currentProjectId;
      let projectResponse;

      if (currentProjectId) {
        // 更新现有项目
        projectResponse = await fetch(`${API_BASE_URL}/api/video/projects/${currentProjectId}/update/`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(projectData)
        });
      } else {
        // 创建新项目
        projectResponse = await fetch(`${API_BASE_URL}/api/video/projects/create/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(projectData)
        });
      }

      const projectResult = await projectResponse.json();

      if (projectResult.status === 'success') {
        projectId = projectResult.data.id;
        if (!currentProjectId) {
          setCurrentProjectId(projectId);
        }

        alert(`视频生成任务已提交！任务ID: ${result.task_id}`);

        // 跳转到项目列表
        navigate('/video-projects');
      } else {
        alert(`保存项目失败: ${projectResult.message || '未知错误'}`);
      }

    } catch (error) {
      console.error('创建视频时出错:', error);
      alert(`创建视频失败: ${error.message}`);
    } finally {
      setIsCreatingVideo(false);
    }
  };

  // 使用DeepSeek生成提示词
  const generatePrompts = async () => {
    if (!subtitles.trim()) {
      alert('请输入字幕内容');
      return;
    }

    try {
      setIsGeneratingPrompts(true);
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${API_BASE_URL}/api/video/generate-prompts/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          subtitles: subtitles
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        // 将生成的提示词转换为列表格式
        setPrompts(data.prompts.map((prompt, index) => ({
          id: Date.now() + index,
          text: prompt,
          image: null,
          isGenerating: false,
          assignedSubtitles: []
        })));
      } else {
        alert(data.message || '生成提示词失败');
      }
    } catch (error) {
      console.error('生成提示词失败:', error);
      alert('生成失败，请重试');
    } finally {
      setIsGeneratingPrompts(false);
    }
  };

  // 根据提示词生成图片
  const generateImage = async (index) => {
    const prompt = prompts[index];
    if (!prompt.text.trim()) {
      alert('提示词不能为空');
      return;
    }

    try {
      setGeneratingImageIndex(index);

      // 更新状态
      setPrompts(prev => prev.map((p, i) =>
        i === index ? { ...p, isGenerating: true } : p
      ));

      const token = localStorage.getItem('access_token');
      const formData = new FormData();
      formData.append('content', prompt.text);
      formData.append('image_index', 1);

      const response = await fetch(`${API_BASE_URL}/api/ip-image/generate-v2`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const data = await response.json();

      if (data.status === 'success') {
        // 更新图片
        setPrompts(prev => prev.map((p, i) =>
          i === index ? { ...p, image: data.image_url, isGenerating: false } : p
        ));
      } else {
        alert(data.message || '生成图片失败');
        setPrompts(prev => prev.map((p, i) =>
          i === index ? { ...p, isGenerating: false } : p
        ));
      }
    } catch (error) {
      console.error('生成图片失败:', error);
      alert('生成失败，请重试');
      setPrompts(prev => prev.map((p, i) =>
        i === index ? { ...p, isGenerating: false } : p
      ));
    } finally {
      setGeneratingImageIndex(null);
    }
  };

  // 打开素材库选择
  const openMediaLibrary = async (index) => {
    setSelectingForIndex(index);
    setShowMediaLibrary(true);

    // 加载素材库
    try {
      setIsLoadingMedia(true);
      const token = localStorage.getItem('access_token');

      const response = await fetch(`${API_BASE_URL}/api/media-library/?page=1&page_size=50`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      if (data.status === 'success') {
        setMediaList(data.data.items);
      }
    } catch (error) {
      console.error('加载素材库失败:', error);
    } finally {
      setIsLoadingMedia(false);
    }
  };

  // 从素材库选择图片
  const selectFromLibrary = (imageUrl) => {
    if (selectingForIndex !== null) {
      setPrompts(prev => prev.map((p, i) =>
        i === selectingForIndex ? { ...p, image: imageUrl } : p
      ));
    }
    setShowMediaLibrary(false);
    setSelectingForIndex(null);
  };

  // 删除提示词
  const deletePrompt = (index) => {
    setPrompts(prev => prev.filter((_, i) => i !== index));
  };

  // 编辑提示词
  const updatePromptText = (index, newText) => {
    setPrompts(prev => prev.map((p, i) =>
      i === index ? { ...p, text: newText } : p
    ));
  };

  // 添加空白提示词
  const addEmptyPrompt = () => {
    setPrompts(prev => [...prev, {
      id: Date.now(),
      text: '',
      image: null,
      isGenerating: false,
      assignedSubtitles: []
    }]);
  };

  // 拖拽开始
  const handleDragStart = (index) => {
    setDraggedIndex(index);
  };

  // 拖拽经过
  const handleDragOver = (e, index) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === index) return;

    // 重新排列数组
    const newPrompts = [...prompts];
    const draggedItem = newPrompts[draggedIndex];
    newPrompts.splice(draggedIndex, 1);
    newPrompts.splice(index, 0, draggedItem);

    setPrompts(newPrompts);
    setDraggedIndex(index);
  };

  // 拖拽结束
  const handleDragEnd = () => {
    setDraggedIndex(null);
  };

  // 解析字幕为句子数组（按逗号、句号、分号、换行等分割）
  const parseSubtitles = () => {
    // 将所有文本合并
    const fullText = subtitles.trim();

    if (!fullText) {
      return [];
    }

    // 按所有常见分隔符分割：逗号、句号、感叹号、问号、分号、顿号、换行、破折号等
    // 分割但保留有意义的短语
    const sentences = fullText.split(/[，。！？；、\n—]+/);

    // 过滤空句子并去除首尾空格
    const cleanedSentences = sentences
      .map(s => s.trim())
      .filter(s => s.length > 0);

    setSubtitleLines(cleanedSentences);
    return cleanedSentences;
  };

  // 一键分配字幕到各个场景
  const autoAssignSubtitles = () => {
    const lines = parseSubtitles();

    console.log('解析的字幕行数:', lines.length);
    console.log('字幕内容:', lines);

    if (lines.length === 0) {
      alert('请先输入字幕');
      return;
    }

    const newPrompts = [];

    // 检查是否有自定义场景数量
    const targetSceneCount = customSceneCount ? parseInt(customSceneCount) : null;

    if (targetSceneCount && targetSceneCount > 0) {
      // 用户指定了场景数量，平均分配
      if (targetSceneCount > lines.length) {
        alert(`场景数量(${targetSceneCount})不能超过字幕句数(${lines.length})`);
        return;
      }

      const linesPerScene = Math.floor(lines.length / targetSceneCount);
      const remainder = lines.length % targetSceneCount;

      let currentIndex = 0;
      for (let i = 0; i < targetSceneCount; i++) {
        // 前remainder个场景多分配1句
        const groupSize = linesPerScene + (i < remainder ? 1 : 0);
        const groupLines = lines.slice(currentIndex, currentIndex + groupSize);

        console.log(`场景 ${i + 1}: groupSize=${groupSize}, 字幕:`, groupLines);

        newPrompts.push({
          id: Date.now() + currentIndex + i,
          text: groupLines.join('，'),
          image: null,
          isGenerating: false,
          assignedSubtitles: groupLines
        });

        currentIndex += groupSize;
      }
    } else {
      // 自动智能分组：每组2-4句话
      let currentIndex = 0;

      while (currentIndex < lines.length) {
        const remainingLines = lines.length - currentIndex;
        let groupSize;

        if (remainingLines <= 2) {
          groupSize = remainingLines;
        } else if (remainingLines === 3) {
          groupSize = 3;
        } else if (remainingLines === 4) {
          groupSize = 4;
        } else if (remainingLines === 5) {
          groupSize = currentIndex === 0 ? 2 : 3;
        } else if (remainingLines === 6) {
          groupSize = 3;
        } else if (remainingLines === 7) {
          groupSize = currentIndex === 0 ? 3 : 4;
        } else {
          const idealGroups = Math.ceil(remainingLines / 3);
          groupSize = Math.ceil(remainingLines / idealGroups);
          groupSize = Math.max(2, Math.min(4, groupSize));
        }

        const groupLines = lines.slice(currentIndex, currentIndex + groupSize);

        console.log(`场景 ${newPrompts.length + 1}: groupSize=${groupSize}, 字幕:`, groupLines);

        newPrompts.push({
          id: Date.now() + currentIndex + newPrompts.length,
          text: groupLines.join('，'),
          image: null,
          isGenerating: false,
          assignedSubtitles: groupLines
        });

        currentIndex += groupSize;
      }
    }

    console.log('总共创建场景数:', newPrompts.length);
    setPrompts(newPrompts);
  };

  // 更新场景的字幕分配
  const updateAssignedSubtitles = (index, subtitles) => {
    setPrompts(prev => prev.map((p, i) =>
      i === index ? { ...p, assignedSubtitles: subtitles.split('\n').filter(s => s.trim()) } : p
    ));
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

          <div>
            <h1 className="text-xl md:text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              视频场景生成
            </h1>
            <p className="text-xs md:text-base text-gray-600 mt-1 md:mt-2">
              输入字幕，AI将为您生成场景图提示词和配图
            </p>
          </div>
        </div>

        {/* 草稿提示 */}
        {hasDraft && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg md:rounded-xl p-3 md:p-4 mb-4 md:mb-6 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 flex-1">
              <svg className="w-5 h-5 text-blue-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-xs md:text-sm text-blue-900">
                检测到未完成的草稿，是否加载？
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={loadDraft}
                className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all text-xs md:text-sm font-semibold whitespace-nowrap"
              >
                加载草稿
              </button>
              <button
                onClick={deleteDraft}
                className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-all text-xs md:text-sm whitespace-nowrap"
              >
                删除
              </button>
            </div>
          </div>
        )}

        {/* 字幕输入区域 */}
        <div className="bg-white rounded-lg md:rounded-xl shadow-md p-4 md:p-6 mb-4 md:mb-6">
          <label className="block text-sm md:text-base font-semibold text-gray-700 mb-3">
            视频字幕
          </label>
          <textarea
            value={subtitles}
            onChange={(e) => setSubtitles(e.target.value)}
            placeholder="请输入视频字幕内容，每行一句...&#10;例如：&#10;春天到了，万物复苏&#10;花园里开满了鲜花&#10;阳光洒在草地上"
            className="w-full px-3 md:px-4 py-2 md:py-3 border border-gray-300 rounded-lg md:rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-sm md:text-base"
            rows="8"
          />
          <div className="mt-4 space-y-3">
            {/* 场景数量设置 */}
            <div className="flex items-center gap-3">
              <label className="text-xs md:text-sm text-gray-700 font-medium whitespace-nowrap">
                场景数量：
              </label>
              <input
                type="number"
                value={customSceneCount}
                onChange={(e) => setCustomSceneCount(e.target.value)}
                placeholder="留空自动分配"
                min="1"
                className="flex-1 max-w-xs px-3 py-1.5 md:py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-xs md:text-sm"
              />
              <span className="text-xs text-gray-500">（可选）</span>
            </div>

            {/* 语音选择 */}
            <div className="flex items-center gap-3">
              <label className="text-xs md:text-sm text-gray-700 font-medium whitespace-nowrap">
                配音语音：
              </label>
              <select
                value={voice}
                onChange={(e) => setVoice(e.target.value)}
                className="flex-1 max-w-xs px-3 py-1.5 md:py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-xs md:text-sm"
              >
                <optgroup label="男声">
                  <option value="zh-CN-YunxiNeural">云希 - 年轻活力</option>
                  <option value="zh-CN-YunjianNeural">云健 - 成熟稳重</option>
                  <option value="zh-CN-YunyangNeural">云扬 - 新闻播报</option>
                  <option value="zh-CN-YunzeNeural">云泽 - 专业沉稳</option>
                  <option value="zh-CN-YunfengNeural">云枫 - 温和亲切</option>
                  <option value="zh-CN-YunhaoNeural">云皓 - 阳光开朗</option>
                </optgroup>
                <optgroup label="女声">
                  <option value="zh-CN-XiaoxiaoNeural">晓晓 - 温柔甜美</option>
                  <option value="zh-CN-XiaoyiNeural">晓伊 - 亲切自然</option>
                  <option value="zh-CN-XiaoxuanNeural">晓萱 - 温柔大方</option>
                  <option value="zh-CN-XiaoyanNeural">晓颜 - 新闻播报</option>
                  <option value="zh-CN-XiaomengNeural">晓梦 - 清新活泼</option>
                  <option value="zh-CN-XiaomoNeural">晓墨 - 知性优雅</option>
                  <option value="zh-CN-XiaohanNeural">晓涵 - 温婉柔和</option>
                  <option value="zh-CN-XiaoruiNeural">晓睿 - 温柔亲和</option>
                </optgroup>
              </select>
            </div>

            {/* 按钮行 */}
            <div className="flex items-center justify-between">
              <p className="text-xs md:text-sm text-gray-500">
                {subtitles.length} 字符
              </p>
              <div className="flex gap-2 md:gap-3">
                <button
                  onClick={autoAssignSubtitles}
                  disabled={!subtitles.trim()}
                  className="px-3 md:px-4 py-2 md:py-3 bg-green-600 text-white rounded-lg md:rounded-xl hover:bg-green-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-xs md:text-sm font-semibold shadow-md hover:shadow-lg"
                >
                  <ArrowPathIcon className="w-4 h-4 md:w-5 md:h-5" />
                  <span>字幕分配到场景</span>
                </button>
                <button
                  onClick={generatePrompts}
                  disabled={isGeneratingPrompts || !subtitles.trim()}
                  className="px-4 md:px-6 py-2 md:py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg md:rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-xs md:text-sm font-semibold shadow-md hover:shadow-lg"
                >
                  {isGeneratingPrompts ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 md:h-5 md:w-5 border-b-2 border-white"></div>
                      <span>生成中...</span>
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="w-4 h-4 md:w-5 md:h-5" />
                      <span>生成场景提示词</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* 提示词列表 */}
        {prompts.length > 0 && (
          <div>
            <div className="flex items-center justify-between gap-2 mb-3 md:mb-4">
              <h2 className="text-base md:text-lg font-semibold text-gray-900">
                场景列表 ({prompts.length})
              </h2>
              <div className="flex items-center gap-2">
                <button
                  onClick={saveDraft}
                  className="px-3 md:px-4 py-1.5 md:py-2 bg-gray-600 text-white rounded-lg md:rounded-xl hover:bg-gray-700 transition-all flex items-center gap-1 md:gap-2 text-xs md:text-sm font-semibold shadow-md hover:shadow-lg whitespace-nowrap"
                >
                  <svg className="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                  </svg>
                  <span>保存草稿</span>
                </button>
                <button
                  onClick={createVideo}
                  disabled={prompts.some(p => !p.image) || isCreatingVideo}
                  className="px-3 md:px-6 py-1.5 md:py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg md:rounded-xl hover:from-purple-700 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 md:gap-2 text-xs md:text-base font-semibold shadow-md hover:shadow-lg whitespace-nowrap"
                >
                  {isCreatingVideo ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 md:h-5 md:w-5 border-b-2 border-white"></div>
                      <span>制作中...</span>
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="w-4 h-4 md:w-5 md:h-5" />
                      <span>开始制作视频</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* 场景网格 - 手机端纵向，桌面端横向 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4">
              {prompts.map((prompt, index) => (
                <div
                  key={prompt.id}
                  draggable
                  onDragStart={() => handleDragStart(index)}
                  onDragOver={(e) => handleDragOver(e, index)}
                  onDragEnd={handleDragEnd}
                  className={`bg-white rounded-lg md:rounded-xl shadow-md p-3 md:p-4 cursor-move transition-all ${
                    draggedIndex === index ? 'opacity-50 scale-95' : 'opacity-100 scale-100'
                  }`}
                >
                <div className="flex items-start gap-3 md:gap-4">
                  {/* 序号和拖拽提示 */}
                  <div className="flex-shrink-0">
                    <div className="w-6 h-6 md:w-8 md:h-8 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full flex items-center justify-center font-bold text-xs md:text-sm mb-1">
                      {index + 1}
                    </div>
                    <div className="text-[10px] md:text-xs text-gray-400 text-center">
                      拖拽
                    </div>
                  </div>

                  {/* 内容区域 */}
                  <div className="flex-1 space-y-3">
                    {/* 场景描述和图片 */}
                    <div className="flex flex-col gap-3">
                      {/* 手机端：横向排列，桌面端：纵向排列 */}
                      <div className="flex flex-row md:flex-col gap-3">
                        {/* 场景描述 */}
                        <div className="flex-1">
                          <label className="block text-xs md:text-sm font-semibold text-gray-700 mb-2">
                            场景描述
                          </label>
                          <textarea
                            value={prompt.text}
                            onChange={(e) => updatePromptText(index, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-xs md:text-sm"
                            rows="3"
                          />
                        </div>

                        {/* 图片预览 - 手机端在右侧，桌面端在下方 */}
                        <div className="w-32 md:w-full flex-shrink-0">
                          <label className="block text-xs md:text-sm font-semibold text-gray-700 mb-2">
                            图片预览
                          </label>
                          {prompt.image ? (
                            <img
                              src={prompt.image}
                              alt={`场景 ${index + 1}`}
                              onClick={() => setPreviewImage(prompt.image)}
                              className="w-full h-24 md:h-40 object-cover rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
                            />
                          ) : (
                            <div className="w-full h-24 md:h-40 bg-gray-100 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300">
                              <PhotoIcon className="w-8 h-8 md:w-12 md:h-12 text-gray-400" />
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* 操作按钮 - 移到场景描述和图片下方 */}
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => generateImage(index)}
                        disabled={prompt.isGenerating || !prompt.text.trim()}
                        className="flex-1 md:flex-initial px-3 md:px-4 py-1.5 md:py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-1 md:gap-2 text-xs md:text-sm font-semibold"
                      >
                        {prompt.isGenerating ? (
                          <>
                            <div className="animate-spin rounded-full h-3 w-3 md:h-4 md:w-4 border-b-2 border-white"></div>
                            <span>生成中...</span>
                          </>
                        ) : (
                          <>
                            <SparklesIcon className="w-4 h-4" />
                            <span>生成图片</span>
                          </>
                        )}
                      </button>

                      <button
                        onClick={() => openMediaLibrary(index)}
                        className="flex-1 md:flex-initial px-3 md:px-4 py-1.5 md:py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-all flex items-center justify-center gap-1 md:gap-2 text-xs md:text-sm font-semibold"
                      >
                        <PhotoIcon className="w-4 h-4" />
                        <span>从素材库选择</span>
                      </button>

                      <button
                        onClick={() => deletePrompt(index)}
                        className="px-3 md:px-4 py-1.5 md:py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all flex items-center gap-1 md:gap-2 text-xs md:text-sm"
                      >
                        <TrashIcon className="w-4 h-4" />
                        <span className="hidden md:inline">删除</span>
                      </button>
                    </div>

                    {/* 分配的字幕 - 在按钮下方 */}
                    <div>
                      <label className="block text-xs md:text-sm font-semibold text-gray-700 mb-2">
                        分配的字幕
                      </label>
                      <textarea
                        value={(prompt.assignedSubtitles || []).join('\n')}
                        onChange={(e) => updateAssignedSubtitles(index, e.target.value)}
                        placeholder="手动输入或使用一键分配功能..."
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-xs md:text-sm"
                        rows="2"
                      />
                      {prompt.assignedSubtitles && prompt.assignedSubtitles.length > 0 && (
                        <p className="text-xs text-gray-500 mt-1">
                          已分配 {prompt.assignedSubtitles.length} 行字幕
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              ))}
            </div>

            {/* 添加场景按钮 */}
            <div className="flex justify-center pt-2 mt-4">
              <button
                onClick={addEmptyPrompt}
                className="px-4 md:px-6 py-2 md:py-3 bg-green-600 text-white rounded-lg md:rounded-xl hover:bg-green-700 transition-all flex items-center gap-2 text-sm md:text-base font-semibold shadow-md hover:shadow-lg"
              >
                <PlusIcon className="w-5 h-5" />
                <span>添加场景</span>
              </button>
            </div>
          </div>
        )}

        {/* 空状态 */}
        {prompts.length === 0 && !isGeneratingPrompts && (
          <div className="bg-white rounded-lg md:rounded-xl shadow-md p-8 md:p-12 text-center">
            <SparklesIcon className="w-12 h-12 md:w-16 md:h-16 mx-auto text-gray-300 mb-3 md:mb-4" />
            <p className="text-sm md:text-base text-gray-500">输入字幕后，点击按钮生成场景提示词</p>
          </div>
        )}

        {/* 图片预览放大模态框 */}
        {previewImage && (
          <div
            className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4"
            onClick={() => setPreviewImage(null)}
          >
            <div className="relative max-w-7xl max-h-[90vh] w-full h-full flex items-center justify-center">
              <img
                src={previewImage}
                alt="预览"
                className="max-w-full max-h-full object-contain rounded-lg"
                onClick={(e) => e.stopPropagation()}
              />
              <button
                onClick={() => setPreviewImage(null)}
                className="absolute top-4 right-4 w-10 h-10 bg-white bg-opacity-20 hover:bg-opacity-30 text-white rounded-full flex items-center justify-center text-2xl font-bold transition-all"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* 素材库选择模态框 */}
        {showMediaLibrary && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowMediaLibrary(false)}
          >
            <div
              className="bg-white rounded-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col"
              onClick={(e) => e.stopPropagation()}
            >
              {/* 标题 */}
              <div className="p-4 md:p-6 border-b">
                <h3 className="text-lg md:text-xl font-bold text-gray-900">从素材库选择图片</h3>
              </div>

              {/* 图片网格 */}
              <div className="flex-1 overflow-y-auto p-4 md:p-6">
                {isLoadingMedia ? (
                  <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                  </div>
                ) : mediaList.length > 0 ? (
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 md:gap-4">
                    {mediaList.map((media) => (
                      <div
                        key={media.id}
                        onClick={() => selectFromLibrary(media.url)}
                        className="aspect-square cursor-pointer rounded-lg overflow-hidden hover:ring-4 hover:ring-blue-500 transition-all"
                      >
                        <img
                          src={media.url}
                          alt={media.prompt}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <PhotoIcon className="w-16 h-16 mx-auto text-gray-300 mb-4" />
                    <p className="text-gray-500">素材库暂无图片</p>
                  </div>
                )}
              </div>

              {/* 关闭按钮 */}
              <div className="p-4 md:p-6 border-t">
                <button
                  onClick={() => setShowMediaLibrary(false)}
                  className="w-full px-4 py-2 md:py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-semibold"
                >
                  关闭
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default VideoGenerator;
