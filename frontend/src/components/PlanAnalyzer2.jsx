import { useState } from 'react';
import { Upload, Trash2, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useAppNavigate } from '../hooks/useAppNavigate';
import * as pdfjsLib from 'pdfjs-dist';

// 配置 PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist/${pdfjsLib.version}/build/pdf.worker.min.mjs`;

function PlanAnalyzer2() {
  const onNavigate = useAppNavigate();
  const { user } = useAuth();
  const [uploadedFile, setUploadedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [documentId, setDocumentId] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  // 7个步骤的状态
  const [steps, setSteps] = useState({
    ocr: { status: 'pending', message: '', loading: false },
    tablecontent: { status: 'pending', message: '', loading: false },
    basicInfo: { status: 'pending', message: '', loading: false },
    tableSummary: { status: 'pending', message: '', loading: false },
    surrenderTable: { status: 'pending', message: '', loading: false },
    wellnessTable: { status: 'pending', message: '', loading: false },
    summary: { status: 'pending', message: '', loading: false }
  });

  // 快速检测PDF是否包含表格元素
  const detectTableInPDF = async (file) => {
    try {
      console.log('🔍 开始检测PDF表格...');
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;

      const pagesToCheck = Math.min(pdf.numPages, 6);

      for (let pageNum = 1; pageNum <= pagesToCheck; pageNum++) {
        const page = await pdf.getPage(pageNum);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map(item => item.str).join(' ');

        const hasTableMarkers = /<table|<tr|<td/i.test(pageText);
        const hasTableKeywords = /年度|保单年度|退保金|现金价值|保险金额|累计|表格/i.test(pageText);

        const digitCount = (pageText.match(/\d/g) || []).length;
        const textLength = pageText.length;
        const digitRatio = textLength > 0 ? digitCount / textLength : 0;

        if (hasTableMarkers || (hasTableKeywords && digitRatio > 0.15)) {
          console.log(`✅ 在第${pageNum}页检测到表格元素`);
          return true;
        }
      }

      return false;
    } catch (error) {
      console.error('PDF检测出错:', error);
      return true;
    }
  };

  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        alert('请上传PDF文件');
        return;
      }

      file.createdAt = new Date().toISOString();

      setIsUploading(true);
      const hasTable = await detectTableInPDF(file);

      if (!hasTable) {
        alert('检测到上传的PDF文件不是计划书。请上传计划书文件。');
        setIsUploading(false);
        return;
      }

      setUploadedFile(file);
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      setIsUploading(false);

      // 重置所有步骤状态
      setSteps({
        ocr: { status: 'pending', message: '', loading: false },
        tablecontent: { status: 'pending', message: '', loading: false },
        basicInfo: { status: 'pending', message: '', loading: false },
        tableSummary: { status: 'pending', message: '', loading: false },
        surrenderTable: { status: 'pending', message: '', loading: false },
        wellnessTable: { status: 'pending', message: '', loading: false },
        summary: { status: 'pending', message: '', loading: false }
      });
      setDocumentId(null);
    }
  };

  const handleDelete = () => {
    setUploadedFile(null);
    setPreviewUrl('');
    setDocumentId(null);
    setSteps({
      ocr: { status: 'pending', message: '', loading: false },
      tablecontent: { status: 'pending', message: '', loading: false },
      basicInfo: { status: 'pending', message: '', loading: false },
      tableSummary: { status: 'pending', message: '', loading: false },
      surrenderTable: { status: 'pending', message: '', loading: false },
      wellnessTable: { status: 'pending', message: '', loading: false },
      summary: { status: 'pending', message: '', loading: false }
    });
  };

  const updateStep = (stepName, updates) => {
    setSteps(prev => ({
      ...prev,
      [stepName]: { ...prev[stepName], ...updates }
    }));
  };

  // 步骤1: OCR识别并上传
  const handleStep1OCR = async () => {
    if (!uploadedFile) {
      alert('请先上传文件');
      return;
    }

    updateStep('ocr', { loading: true, message: '正在上传和OCR识别...' });

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      if (user?.id) {
        formData.append('user_id', user.id);
      }

      const response = await fetch('/api/ocr/upload-async/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.status === 'success') {
        const docId = data.document_id;
        setDocumentId(docId);

        // 轮询OCR状态
        const pollInterval = setInterval(async () => {
          try {
            const statusRes = await fetch(`/api/ocr/documents/${docId}/status/`);
            const statusData = await statusRes.json();

            if (statusData.status === 'success') {
              const { processing_stage } = statusData.data;

              if (processing_stage === 'ocr_completed' || processing_stage.includes('extracting')) {
                clearInterval(pollInterval);
                updateStep('ocr', {
                  loading: false,
                  status: 'success',
                  message: `OCR识别成功！文档ID: ${docId}`
                });
              } else if (processing_stage === 'error') {
                clearInterval(pollInterval);
                updateStep('ocr', {
                  loading: false,
                  status: 'error',
                  message: 'OCR识别失败'
                });
              } else {
                updateStep('ocr', { message: `OCR处理中: ${processing_stage}` });
              }
            }
          } catch (err) {
            console.error('轮询出错:', err);
          }
        }, 2000);

        // 60秒超时
        setTimeout(() => {
          clearInterval(pollInterval);
          if (steps.ocr.loading) {
            updateStep('ocr', {
              loading: false,
              status: 'error',
              message: 'OCR处理超时'
            });
          }
        }, 60000);

      } else {
        throw new Error(data.message || '上传失败');
      }
    } catch (error) {
      updateStep('ocr', {
        loading: false,
        status: 'error',
        message: `上传失败: ${error.message}`
      });
    }
  };

  // 通用轮询函数
  const pollStepStatus = (stepKey, completedStagePrefix, stepLabel) => {
    if (!documentId) {
      alert('请先完成OCR识别');
      return;
    }

    updateStep(stepKey, { loading: true, message: `正在${stepLabel}...` });

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/ocr/documents/${documentId}/status/`);
        const data = await response.json();

        if (data.status === 'success') {
          const { processing_stage } = data.data;

          if (processing_stage.includes(completedStagePrefix) || processing_stage === 'all_completed') {
            clearInterval(pollInterval);
            updateStep(stepKey, {
              loading: false,
              status: 'success',
              message: `${stepLabel}完成`
            });
          } else if (processing_stage === 'error') {
            clearInterval(pollInterval);
            updateStep(stepKey, {
              loading: false,
              status: 'error',
              message: `${stepLabel}失败`
            });
          }
        }
      } catch (err) {
        console.error('轮询出错:', err);
      }
    }, 2000);

    setTimeout(() => clearInterval(pollInterval), 60000);
  };

  const handleStep2TableContent = () => pollStepStatus('tablecontent', 'tablecontent_completed', '提取表格源代码');
  const handleStep3BasicInfo = () => pollStepStatus('basicInfo', 'basic_info_completed', '提取基本信息');
  const handleStep4TableSummary = () => pollStepStatus('tableSummary', 'tablesummary_completed', '分析表格结构');
  const handleStep5SurrenderTable = () => pollStepStatus('surrenderTable', 'table_completed', '提取退保价值表');
  const handleStep6WellnessTable = () => pollStepStatus('wellnessTable', 'wellness_table_completed', '提取无忧选表');
  const handleStep7Summary = () => pollStepStatus('summary', 'all_completed', '提取计划书概要');

  const getStatusIcon = (status, loading) => {
    if (loading) return <Loader2 className="w-5 h-5 animate-spin text-blue-600" />;
    if (status === 'success') return <CheckCircle className="w-5 h-5 text-green-600" />;
    if (status === 'error') return <AlertCircle className="w-5 h-5 text-red-600" />;
    return <div className="w-5 h-5 border-2 border-gray-300 rounded-full" />;
  };

  const stepButtons = [
    { key: 'ocr', label: '1. OCR识别', handler: handleStep1OCR },
    { key: 'tablecontent', label: '2. 提取表格源代码', handler: handleStep2TableContent },
    { key: 'basicInfo', label: '3. 提取基本信息', handler: handleStep3BasicInfo },
    { key: 'tableSummary', label: '4. 分析表格结构', handler: handleStep4TableSummary },
    { key: 'surrenderTable', label: '5. 提取退保价值表', handler: handleStep5SurrenderTable },
    { key: 'wellnessTable', label: '6. 提取无忧选表', handler: handleStep6WellnessTable },
    { key: 'summary', label: '7. 提取计划书概要', handler: handleStep7Summary }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 via-blue-50 to-slate-100">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 md:px-8 py-3 md:py-4">
          <div className="mb-3">
            <button
              onClick={() => onNavigate && onNavigate('plan-management')}
              className="px-3 md:px-4 py-1.5 md:py-2 bg-white text-blue-600 hover:bg-blue-50 rounded-lg font-medium transition-all text-sm md:text-base whitespace-nowrap shadow-sm border border-gray-200"
            >
              ← 返回计划书列表
            </button>
          </div>

          <div className="text-center">
            <h1 className="text-2xl md:text-3xl lg:text-4xl text-gray-800 font-bold tracking-wide">
              计划书分步骤分析工具
            </h1>
            <p className="mt-1 md:mt-2 text-gray-600 text-xs md:text-sm">手动控制每个分析步骤</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 md:px-8 py-4 md:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
          {/* Left Panel - File Upload */}
          <div className="space-y-3 md:space-y-4">
            <div className="flex gap-2">
              <button
                onClick={() => document.getElementById('file-input-2')?.click()}
                disabled={isUploading}
                className="flex-1 px-3 md:px-4 py-2.5 md:py-3 bg-gradient-to-r from-primary-50 to-blue-50 border-2 border-dashed border-primary-300 hover:border-primary-500 rounded-lg transition-all hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm md:text-base"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="h-4 w-4 md:h-5 md:w-5 animate-spin" />
                    <span>上传中...</span>
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 md:h-5 md:w-5" />
                    <span>上传PDF文件</span>
                  </>
                )}
              </button>
              <input
                id="file-input-2"
                type="file"
                accept="application/pdf,.pdf"
                className="hidden"
                onChange={handleFileSelect}
                disabled={isUploading}
              />
              <button
                onClick={handleDelete}
                disabled={!uploadedFile}
                className="px-3 md:px-4 py-2.5 md:py-3 bg-white hover:bg-red-50 border-2 border-gray-300 hover:border-red-300 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Trash2 className="h-4 w-4 md:h-5 md:w-5" />
              </button>
            </div>

            {/* File Preview */}
            <div className="bg-white rounded-xl border-2 border-primary-200 shadow-lg p-3 md:p-6 h-[120px] md:h-[500px] overflow-auto">
              {previewUrl ? (
                <div className="w-full h-full">
                  {uploadedFile?.type === 'application/pdf' ? (
                    <>
                      <iframe
                        src={previewUrl}
                        className="hidden md:block w-full h-full rounded-lg border border-gray-300"
                        title="PDF Preview"
                      />
                      <div className="md:hidden flex items-center justify-start h-full text-left gap-3 px-2">
                        <FileText className="h-10 w-10 text-primary-500 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-semibold text-gray-700 mb-0.5">PDF 已上传</p>
                          <p className="text-xs text-gray-500 truncate">{uploadedFile?.name}</p>
                        </div>
                      </div>
                    </>
                  ) : null}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <Upload className="h-8 w-8 md:h-16 md:w-16 mb-1 md:mb-4 opacity-30" />
                  <p className="text-xs md:text-base">请上传文件以预览</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Step-by-Step Controls */}
          <div className="space-y-3 md:space-y-4">
            <div className="bg-white rounded-xl border-2 border-primary-200 shadow-lg p-4 md:p-6">
              <h2 className="text-lg md:text-xl font-bold text-gray-800 mb-4">分析步骤</h2>

              {documentId && (
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>文档ID:</strong> {documentId}
                  </p>
                </div>
              )}

              <div className="space-y-3">
                {stepButtons.map(({ key, label, handler }) => (
                  <div key={key} className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(steps[key].status, steps[key].loading)}
                        <span className="font-medium text-gray-800">{label}</span>
                      </div>
                      <button
                        onClick={handler}
                        disabled={steps[key].loading || (key === 'ocr' && !uploadedFile)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm"
                      >
                        {steps[key].loading ? '执行中...' : '执行'}
                      </button>
                    </div>
                    {steps[key].message && (
                      <p className={`text-xs mt-2 ${
                        steps[key].status === 'error' ? 'text-red-600' :
                        steps[key].status === 'success' ? 'text-green-600' :
                        'text-gray-600'
                      }`}>
                        {steps[key].message}
                      </p>
                    )}
                  </div>
                ))}
              </div>

              {/* 查看结果按钮 */}
              {documentId && steps.ocr.status === 'success' && (
                <div className="mt-6">
                  <button
                    onClick={() => onNavigate && onNavigate('plan-management')}
                    className="w-full px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all font-semibold"
                  >
                    查看文档详情
                  </button>
                </div>
              )}
            </div>

            {/* 说明 */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <h3 className="font-semibold text-amber-900 mb-2 text-sm">💡 使用说明</h3>
              <ul className="text-xs text-amber-800 space-y-1">
                <li>• 必须先执行步骤1（OCR识别）</li>
                <li>• 其他步骤由系统自动触发，点击按钮查看进度</li>
                <li>• 每个步骤都是异步执行，可以随时查看状态</li>
                <li>• 所有步骤完成后可查看文档详情</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default PlanAnalyzer2;
