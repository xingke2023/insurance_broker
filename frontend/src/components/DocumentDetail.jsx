import React, { useState, useEffect, useRef } from 'react';
import { ArrowLeft, User, Building2, Calendar, DollarSign, FileText, Loader2, AlertCircle, MessageSquare, Send, X, ChevronDown, ChevronUp } from 'lucide-react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authFetch } from '../utils/authFetch';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';

function DocumentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Collapse states
  const [isBasicInfoOpen, setIsBasicInfoOpen] = useState(true);
  const [isSummaryOpen, setIsSummaryOpen] = useState(true);
  const [isTableOpen, setIsTableOpen] = useState(true);
  const [isContentOpen, setIsContentOpen] = useState(false); // 默认折叠内容区域

  // Chat states
  const [showChatModal, setShowChatModal] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatMessagesEndRef = useRef(null);

  useEffect(() => {
    fetchDocumentDetail();
  }, [id]);

  const fetchDocumentDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('📡 正在获取文档详情，ID:', id);
      const response = await authFetch(`/api/ocr/documents/${id}/`);

      if (!response.ok) {
        console.error('❌ HTTP错误:', response.status, response.statusText);
        setError(`HTTP错误 ${response.status}: ${response.statusText}`);
        setLoading(false);
        return;
      }

      const data = await response.json();
      console.log('📦 API返回数据:', data);

      if (data.status === 'success') {
        console.log('✅ 文档数据加载成功');
        setDocument(data.data);
      } else {
        console.error('❌ API返回错误:', data.message);
        setError(data.message || '获取文档详情失败');
      }
    } catch (error) {
      console.error('❌ 获取文档详情失败:', error);
      setError('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (!num) return '-';
    return Number(num).toLocaleString('zh-CN');
  };

  const formatCurrency = (num) => {
    if (!num) return '-';
    return `¥${formatNumber(num)}`;
  };

  // Chat functions
  const handleOpenChat = () => {
    setShowChatModal(true);
    if (chatMessages.length === 0) {
      setChatMessages([{
        role: 'assistant',
        content: '您好！我是计划书助手，可以帮您解答关于这份保险计划书的问题。请问有什么可以帮您的吗？',
        timestamp: new Date()
      }]);
    }
  };

  const handleCloseChat = () => {
    setShowChatModal(false);
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim() || chatLoading) return;

    const userMessage = {
      role: 'user',
      content: chatInput.trim(),
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setChatLoading(true);

    const tempAssistantMessage = {
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true
    };
    setChatMessages(prev => [...prev, tempAssistantMessage]);

    try {
      const response = await authFetch(`/api/ocr/documents/${id}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          history: chatMessages.map(msg => ({
            role: msg.role,
            content: msg.content
          })),
          stream: true
        }),
      });

      if (!response.ok) {
        throw new Error('请求失败');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              break;
            }
            try {
              const json = JSON.parse(data);
              if (json.content) {
                accumulatedContent += json.content;
                setChatMessages(prev => {
                  const newMessages = [...prev];
                  newMessages[newMessages.length - 1] = {
                    ...newMessages[newMessages.length - 1],
                    content: accumulatedContent
                  };
                  return newMessages;
                });
              }
            } catch (e) {
              console.error('解析流式数据失败:', e);
            }
          }
        }
      }

      setChatMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          ...newMessages[newMessages.length - 1],
          isStreaming: false
        };
        return newMessages;
      });

    } catch (error) {
      console.error('发送消息失败:', error);
      setChatMessages(prev => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          role: 'assistant',
          content: '抱歉，连接失败，请稍后重试。',
          timestamp: new Date(),
          isStreaming: false
        };
        return newMessages;
      });
    } finally {
      setChatLoading(false);
    }
  };

  useEffect(() => {
    if (chatMessagesEndRef.current) {
      chatMessagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-800 text-center mb-2">加载失败</h2>
          <p className="text-gray-600 text-center mb-4">{error}</p>
          <button
            onClick={() => navigate('/plan-management')}
            className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition"
          >
            返回列表
          </button>
        </div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md">
          <AlertCircle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-gray-800 text-center mb-2">文档未找到</h2>
          <p className="text-gray-600 text-center mb-4">未能加载文档数据</p>
          <button
            onClick={() => navigate('/plan-management')}
            className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition"
          >
            返回列表
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航栏 */}
      <div className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 py-3 sm:py-4">
          {/* 移动端：垂直布局 */}
          <div className="flex flex-col gap-3 sm:hidden">
            <div className="flex items-center justify-between">
              <button
                onClick={() => navigate('/plan-management')}
                className="flex items-center space-x-1 text-gray-600 hover:text-gray-800"
              >
                <ArrowLeft className="w-4 h-4" />
                <span className="text-sm">返回</span>
              </button>
              <button
                onClick={handleOpenChat}
                disabled={document.processing_stage !== 'all_completed'}
                className={`flex items-center space-x-1.5 px-3 py-1 rounded-lg shadow transition-all ${
                  document.processing_stage !== 'all_completed'
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white hover:shadow-lg'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                <span className="text-sm">计划书助手</span>
              </button>
            </div>
            <h1 className="text-base font-bold text-gray-800 line-clamp-2 break-words">{document.file_name}</h1>
          </div>

          {/* 桌面端：水平布局 */}
          <div className="hidden sm:flex items-center justify-between">
            <div className="flex items-center space-x-4 min-w-0 flex-1">
              <button
                onClick={() => navigate('/plan-management')}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 flex-shrink-0"
              >
                <ArrowLeft className="w-5 h-5" />
                <span>返回列表</span>
              </button>
              <div className="h-6 w-px bg-gray-300 flex-shrink-0"></div>
              <h1 className="text-xl font-bold text-gray-800 truncate">{document.file_name}</h1>
            </div>
            <button
              onClick={handleOpenChat}
              disabled={document.processing_stage !== 'all_completed'}
              className={`flex items-center space-x-2 px-4 py-1.5 rounded-lg shadow transition-all flex-shrink-0 ${
                document.processing_stage !== 'all_completed'
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white hover:shadow-lg'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>计划书助手</span>
            </button>
          </div>
        </div>
      </div>

      {/* 主内容区域 */}
      <div className="max-w-7xl mx-auto px-2 sm:px-4 py-2 sm:py-4 space-y-2 sm:space-y-4">

        {/* 错误状态提示 */}
        {document && document.processing_stage === 'error' && (
          <div className="w-full bg-gradient-to-r from-red-50 to-rose-50 border-2 border-red-300 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-red-900 mb-1">文档处理失败</h3>
                <p className="text-xs text-red-800 mb-2">
                  {document.error_message || '上传的文件可能不是保险计划书，请检查文件内容后重新上传。'}
                </p>
              </div>
              <button
                onClick={() => navigate('/plan-management')}
                className="px-3 py-1.5 bg-red-600 text-white text-xs rounded-lg hover:bg-red-700 transition-colors flex-shrink-0"
              >
                返回列表
              </button>
            </div>
          </div>
        )}

        {/* 处理状态提示 */}
        {document && document.processing_stage !== 'all_completed' && document.processing_stage !== 'error' && (
          <div className="w-full bg-gradient-to-r from-amber-50 to-orange-50 border-2 border-amber-300 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Loader2 className="w-5 h-5 text-amber-600 animate-spin flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-amber-900 mb-1">文档正在处理中</h3>
                <p className="text-xs text-amber-800 mb-2">
                  该计划书正在后台分析中，部分信息可能尚未提取完成。您可以稍后刷新页面查看完整结果。
                </p>
                <div className="flex items-center gap-2 text-xs text-amber-700">
                  <span className="font-medium">当前阶段:</span>
                  <span className="px-2 py-0.5 bg-amber-100 rounded">
                    {document.processing_stage === 'ocr_pending' && 'OCR识别待处理'}
                    {document.processing_stage === 'pending' && '等待分析'}
                    {document.processing_stage === 'extracting_basic_info' && '正在提取基本信息'}
                    {document.processing_stage === 'basic_info_completed' && '基本信息已完成'}
                    {document.processing_stage === 'extracting_tablesummary' && '正在分析表格结构'}
                    {document.processing_stage === 'tablesummary_completed' && '表格结构已完成'}
                    {document.processing_stage === 'extracting_table' && '正在提取退保价值表'}
                    {document.processing_stage === 'table_completed' && '退保价值表已完成'}
                    {document.processing_stage === 'extracting_wellness_table' && '正在提取无忧选表'}
                    {document.processing_stage === 'wellness_table_completed' && '无忧选表已完成'}
                    {document.processing_stage === 'extracting_summary' && '正在提取计划书概要'}
                    {!document.processing_stage && '处理中'}
                  </span>
                </div>
              </div>
              <button
                onClick={fetchDocumentDetail}
                className="px-3 py-1.5 bg-amber-600 text-white text-xs rounded-lg hover:bg-amber-700 transition-colors flex-shrink-0"
              >
                刷新
              </button>
            </div>
          </div>
        )}

        {/* 1. 基本信息卡片 */}
        <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200 p-2 sm:p-4">
          <div
            className="flex items-center justify-between cursor-pointer hover:bg-gray-50 -mx-2 sm:-mx-4 px-2 sm:px-4 py-1 rounded"
            onClick={() => setIsBasicInfoOpen(!isBasicInfoOpen)}
          >
            <div className="flex items-center space-x-1.5">
              <User className="w-4 h-4 text-blue-500" />
              <h2 className="text-sm sm:text-base font-semibold text-gray-800">基本信息</h2>
            </div>
            {isBasicInfoOpen ? (
              <ChevronUp className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            )}
          </div>

          {/* 紧凑的横向布局 */}
          {isBasicInfoOpen && (
            <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs sm:text-sm mt-2">
            {/* 如果没有任何基本信息，显示处理中提示 */}
            {!document.insured_name && !document.insured_age && !document.insured_gender &&
             !document.insurance_company && !document.insurance_product &&
             !document.sum_assured && !document.annual_premium && (
              <div className="w-full text-center py-4 text-gray-500">
                <Loader2 className="w-5 h-5 animate-spin mx-auto mb-2" />
                <p className="text-xs">基本信息提取中...</p>
              </div>
            )}

            {/* 受保人 */}
            {document.insured_name && (
              <div className="flex items-center gap-1">
                <span className="text-gray-500">姓名:</span>
                <span className="font-medium text-gray-800">{document.insured_name}</span>
              </div>
            )}
            {document.insured_age && (
              <div className="flex items-center gap-1">
                <span className="text-gray-500">年龄:</span>
                <span className="font-medium text-gray-800">{document.insured_age}岁</span>
              </div>
            )}
            {document.insured_gender && (
              <div className="flex items-center gap-1">
                <span className="text-gray-500">性别:</span>
                <span className="font-medium text-gray-800">{document.insured_gender}</span>
              </div>
            )}

            {/* 分隔符 */}
            {(document.insured_name || document.insured_age || document.insured_gender) && (document.insurance_company || document.insurance_product) && (
              <div className="hidden sm:block w-px h-4 bg-gray-300"></div>
            )}

            {/* 保险产品 */}
            {document.insurance_company && (
              <div className="flex items-center gap-1">
                <span className="text-gray-500">公司:</span>
                <span className="font-medium text-gray-800">{document.insurance_company}</span>
              </div>
            )}
            {document.insurance_product && (
              <div className="flex items-center gap-1">
                <span className="text-gray-500">产品:</span>
                <span className="font-medium text-gray-800 max-w-[200px] truncate" title={document.insurance_product}>{document.insurance_product}</span>
              </div>
            )}

            {/* 分隔符 */}
            {(document.insurance_company || document.insurance_product) && (document.sum_assured || document.annual_premium) && (
              <div className="hidden sm:block w-px h-4 bg-gray-300"></div>
            )}

            {/* 保费信息 */}
            {document.sum_assured && (
              <div className="flex items-center gap-1">
                <span className="text-gray-500">保额:</span>
                <span className="font-medium text-gray-800">{formatCurrency(document.sum_assured)}</span>
              </div>
            )}
            {document.annual_premium && (
              <div className="flex items-center gap-1">
                <span className="text-gray-500">年缴:</span>
                <span className="font-medium text-gray-800">{formatCurrency(document.annual_premium)}</span>
              </div>
            )}
            {document.payment_years && (
              <div className="flex items-center gap-1">
                <span className="text-gray-500">缴费:</span>
                <span className="font-medium text-gray-800">{document.payment_years}年</span>
              </div>
            )}
            {document.total_premium && (
              <div className="flex items-center gap-1">
                <span className="text-gray-500">总保费:</span>
                <span className="font-medium text-gray-800">{formatCurrency(document.total_premium)}</span>
              </div>
            )}
            {document.insurance_period && (
              <div className="flex items-center gap-1">
                <span className="text-gray-500">期限:</span>
                <span className="font-medium text-gray-800">{document.insurance_period}</span>
              </div>
            )}
          </div>
          )}
        </div>

        {/* 2. 计划书概要卡片 */}
        {((document.summary && typeof document.summary === 'string' && document.summary.trim().length > 0) || document.processing_stage !== 'all_completed') && (
          <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200 p-2 sm:p-4">
            <div
              className="flex items-center justify-between cursor-pointer hover:bg-gray-50 -mx-2 sm:-mx-4 px-2 sm:px-4 py-1 rounded"
              onClick={() => setIsSummaryOpen(!isSummaryOpen)}
            >
              <div className="flex items-center space-x-1.5">
                <FileText className="w-4 h-4 text-green-500" />
                <h2 className="text-sm sm:text-base font-semibold text-gray-800">计划书概要</h2>
              </div>
              {isSummaryOpen ? (
                <ChevronUp className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              )}
            </div>

            {isSummaryOpen && (
              document.summary && typeof document.summary === 'string' && document.summary.trim().length > 0 ? (
                <div className="mt-3 prose prose-sm max-w-none">
                  <ReactMarkdown
                    rehypePlugins={[rehypeRaw]}
                    className="text-xs sm:text-sm text-gray-600 leading-relaxed"
                    components={{
                      h1: ({node, ...props}) => <h1 className="text-base sm:text-lg font-bold text-gray-900 mt-4 mb-3" {...props} />,
                      h2: ({node, ...props}) => <h2 className="text-sm sm:text-base font-semibold text-gray-800 mt-4 mb-2" {...props} />,
                      h3: ({node, ...props}) => <h3 className="text-xs sm:text-sm font-medium text-gray-700 mt-3 mb-1" {...props} />,
                      p: ({node, ...props}) => <p className="text-xs sm:text-sm text-gray-600 mb-2 leading-relaxed" {...props} />,
                      ul: ({node, ...props}) => <ul className="list-disc list-inside space-y-1 mb-2" {...props} />,
                      ol: ({node, ...props}) => <ol className="list-decimal list-inside space-y-1 mb-2" {...props} />,
                      li: ({node, ...props}) => <li className="text-xs sm:text-sm text-gray-600" {...props} />,
                      strong: ({node, ...props}) => <strong className="font-semibold text-gray-800" {...props} />,
                      table: ({node, ...props}) => (
                        <div className="overflow-x-auto my-4">
                          <table className="min-w-full border-collapse border border-gray-300" {...props} />
                        </div>
                      ),
                      thead: ({node, ...props}) => <thead className="bg-gray-100" {...props} />,
                      tbody: ({node, ...props}) => <tbody {...props} />,
                      tr: ({node, ...props}) => <tr className="border-b border-gray-300" {...props} />,
                      th: ({node, ...props}) => <th className="border border-gray-300 px-2 sm:px-4 py-1 sm:py-2 text-left text-xs sm:text-sm font-semibold text-gray-700" {...props} />,
                      td: ({node, ...props}) => <td className="border border-gray-300 px-2 sm:px-4 py-1 sm:py-2 text-xs sm:text-sm text-gray-600" {...props} />,
                    }}
                  >
                    {document.summary}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="mt-3 text-center py-6 text-gray-500">
                  <Loader2 className="w-5 h-5 animate-spin mx-auto mb-2" />
                  <p className="text-xs">计划书概要提取中...</p>
                </div>
              )
            )}
          </div>
        )}

        {/* 3. 保单按年度现金价值卡片 */}
        {((document.table1 && document.table1.years && document.table1.years.length > 0) || document.processing_stage !== 'all_completed') && (
          <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200 p-2 sm:p-4">
            <div
              className="flex items-center justify-between cursor-pointer hover:bg-gray-50 -mx-2 sm:-mx-4 px-2 sm:px-4 py-1 rounded"
              onClick={() => setIsTableOpen(!isTableOpen)}
            >
              <div className="flex items-center space-x-1.5">
                <DollarSign className="w-4 h-4 text-purple-500" />
                <h2 className="text-sm sm:text-base font-semibold text-gray-800">保单按年度现金价值</h2>
                {document.table1?.years?.length > 0 && (
                  <span className="text-xs text-gray-500">({document.table1.years.length} 条)</span>
                )}
              </div>
              {isTableOpen ? (
                <ChevronUp className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              )}
            </div>

            {/* 表格 */}
            {isTableOpen && (
              document.table1 && document.table1.years && document.table1.years.length > 0 ? (
                <div className="overflow-x-auto -mx-2 sm:mx-0 mt-2">
                <table className="w-full text-xs border-collapse">
                  <thead>
                    <tr className="bg-gray-50 border-b-2 border-gray-200">
                      <th className="px-1.5 sm:px-3 py-1.5 sm:py-2 text-left font-medium text-gray-700 border-r border-gray-200 whitespace-nowrap" colSpan="2">
                        <div className="flex items-center gap-1">
                          <span>保单年度</span>
                          <span className="text-gray-400">/</span>
                          <span>年龄</span>
                        </div>
                      </th>
                      <th className="px-1.5 sm:px-3 py-1.5 sm:py-2 text-right font-medium text-gray-700 border-r border-gray-200 whitespace-nowrap">保证金额</th>
                      <th className="px-1.5 sm:px-3 py-1.5 sm:py-2 text-right font-medium text-gray-700 border-r border-gray-200 whitespace-nowrap">总额</th>
                      <th className="px-1.5 sm:px-3 py-1.5 sm:py-2 text-right font-medium text-gray-700 border-r border-gray-200 whitespace-nowrap">年化单利%</th>
                      <th className="px-1.5 sm:px-3 py-1.5 sm:py-2 text-right font-medium text-gray-700 whitespace-nowrap">IRR%</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white">
                    {document.table1.years.map((row, index) => {
                    console.log('🔍 渲染行数据:', row);
                    const age = document.insured_age ? parseInt(document.insured_age) + parseInt(row.policy_year) : null;

                    // 计算年化单利和IRR
                    const annualPremium = document?.annual_premium ? parseInt(document.annual_premium) : 0;
                    const paymentYears = document?.payment_years ? parseInt(document.payment_years) : 0;
                    const actualInvestment = annualPremium * Math.min(row.policy_year, paymentYears);
                    const returnValue = row.total || 0;

                    // 年化单利
                    const simpleReturn = actualInvestment > 0 && returnValue > 0 && row.policy_year > 0
                      ? ((returnValue - actualInvestment) / actualInvestment / row.policy_year * 100)
                      : 0;

                    // IRR (内部收益率)
                    const irr = actualInvestment > 0 && returnValue > 0 && row.policy_year > 0
                      ? (Math.pow(returnValue / actualInvestment, 1 / row.policy_year) - 1) * 100
                      : 0;

                    return (
                      <tr key={index} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                        <td className="px-1.5 sm:px-3 py-1.5 sm:py-2 text-gray-800 border-r border-gray-100" colSpan="2">
                          <div className="flex items-center gap-1">
                            <span>{row.policy_year || '-'}</span>
                            <span className="text-gray-400 text-xs">/</span>
                            <span>{age ? `${age}岁` : '-'}</span>
                          </div>
                        </td>
                        <td className="px-1.5 sm:px-3 py-1.5 sm:py-2 text-right text-gray-800 border-r border-gray-100">{formatNumber(row.guaranteed)}</td>
                        <td className="px-1.5 sm:px-3 py-1.5 sm:py-2 text-right font-medium text-gray-900 border-r border-gray-100">{formatNumber(row.total)}</td>
                        <td className="px-1.5 sm:px-3 py-1.5 sm:py-2 text-right font-semibold text-purple-600 border-r border-gray-100">
                          {!isNaN(simpleReturn) && simpleReturn !== 0 ? simpleReturn.toFixed(2) : '-'}
                        </td>
                        <td className="px-1.5 sm:px-3 py-1.5 sm:py-2 text-right font-semibold text-green-600">
                          {!isNaN(irr) && irr !== 0 ? irr.toFixed(2) : '-'}
                        </td>
                      </tr>
                    );
                    })}
                  </tbody>
                </table>
              </div>
              ) : (
                <div className="mt-2 text-center py-6 text-gray-500">
                  <Loader2 className="w-5 h-5 animate-spin mx-auto mb-2" />
                  <p className="text-xs">退保价值表提取中...</p>
                </div>
              )
            )}
          </div>
        )}


        {/* 4. 计划书内容卡片 */}
        <div className="w-full bg-white rounded-lg shadow-sm border border-gray-200 p-2 sm:p-4">
          <div
            className="flex items-center justify-between cursor-pointer hover:bg-gray-50 -mx-2 sm:-mx-4 px-2 sm:px-4 py-1 rounded"
            onClick={() => setIsContentOpen(!isContentOpen)}
          >
            <div className="flex items-center space-x-1.5">
              <FileText className="w-4 h-4 text-orange-500" />
              <h2 className="text-sm sm:text-base font-semibold text-gray-800">计划书内容</h2>
              {document.content && (
                <span className="text-xs text-gray-500">({document.content_length?.toLocaleString() || 0} 字符)</span>
              )}
            </div>
            {isContentOpen ? (
              <ChevronUp className="w-4 h-4 text-gray-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-400" />
            )}
          </div>

          {isContentOpen && (
            document.content ? (
              <div className="bg-gray-50 rounded-lg p-2 sm:p-3 max-h-60 sm:max-h-80 overflow-y-auto mt-2 sm:mt-3">
                <pre className="text-xs text-gray-700 whitespace-pre-wrap font-mono leading-snug">
                  {document.content}
                </pre>
              </div>
            ) : (
              <div className="mt-2 text-center py-6 text-gray-500">
                <Loader2 className="w-5 h-5 animate-spin mx-auto mb-2" />
                <p className="text-xs">OCR内容解析中...</p>
              </div>
            )
          )}
        </div>

        {/* 5. 底部按钮 - 进入内容编辑器 */}
        <div className="w-full">
          <button
            onClick={() => navigate(`/document/${id}/content-editor`)}
            className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-3 px-6 rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 flex items-center justify-center space-x-2 font-medium"
          >
            <FileText className="w-5 h-5" />
            <span>进入计划书内容编辑器</span>
          </button>
        </div>

      </div>

      {/* 聊天助手对话框 */}
      {showChatModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl h-[calc(100vh-2rem)] sm:h-[600px] flex flex-col">
            {/* 对话框头部 */}
            <div className="flex items-center justify-between p-3 sm:p-4 border-b bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-t-2xl">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 sm:w-5 sm:h-5" />
                <h3 className="text-base sm:text-lg font-semibold">计划书助手</h3>
              </div>
              <button
                onClick={handleCloseChat}
                className="p-1 hover:bg-white/20 rounded-lg transition-colors"
              >
                <X className="w-4 h-4 sm:w-5 sm:h-5" />
              </button>
            </div>

            {/* 消息列表 */}
            <div className="flex-1 overflow-y-auto p-2 sm:p-4 space-y-2 sm:space-y-4 bg-gray-50">
              {chatMessages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] sm:max-w-[80%] rounded-lg p-2 sm:p-3 ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-800 shadow'
                    }`}
                  >
                    {msg.role === 'user' ? (
                      <p className="text-xs sm:text-sm whitespace-pre-wrap break-words">{msg.content}</p>
                    ) : (
                      <div className="text-xs sm:text-sm prose prose-sm max-w-none prose-headings:text-gray-800 prose-p:text-gray-800 prose-strong:text-gray-900 prose-ul:text-gray-800 prose-ol:text-gray-800 prose-li:text-gray-800">
                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-white text-gray-800 shadow rounded-lg p-2 sm:p-3">
                    <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={chatMessagesEndRef} />
            </div>

            {/* 输入框 */}
            <div className="p-2 sm:p-4 border-t bg-white rounded-b-2xl">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  placeholder="输入您的问题..."
                  className="flex-1 px-3 sm:px-4 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={chatLoading}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={chatLoading || !chatInput.trim()}
                  className="px-3 sm:px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 sm:gap-2"
                >
                  <Send className="w-4 h-4" />
                  <span className="hidden sm:inline">发送</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DocumentDetail;
