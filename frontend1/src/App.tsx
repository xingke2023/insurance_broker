import { useState } from 'react';
import { FileUploader } from './components/FileUploader';
import { PromptInput } from './components/PromptInput';
import { FileExplorer } from './components/FileExplorer';
import { FilePreview } from './components/FilePreview';
import { ContentCreator } from './components/ContentCreator';
import { TextToSpeech } from './components/TextToSpeech';
import { Button } from './components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from './components/ui/dialog';
import { Gift, ChevronDown, ChevronUp, FileText, Sparkles, Volume2 } from 'lucide-react';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner@2.0.3';
import qrCode from 'figma:asset/dea850b023f7f1cbbc3378bbd2cedd67c865d9f2.png';
import API_CONFIG from './config/api';

interface FileNode {
  name: string;
  type: 'folder' | 'file';
  fileType?: 'markdown' | 'image' | 'pdf';
  content?: string;
}

const API_BASE_URL = API_CONFIG.BASE_URL;

type PageType = 'document-analysis' | 'content-creator' | 'text-to-speech';

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageType>('document-analysis');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadedFilePath, setUploadedFilePath] = useState<string>('');
  const [prompt, setPrompt] = useState('<image>\n<|grounding|>Convert the document to markdown.');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [taskId, setTaskId] = useState<string>('');
  const [resultDir, setResultDir] = useState<string>('');
  const [parseCompleted, setParseCompleted] = useState(false);
  const [selectedPreviewFile, setSelectedPreviewFile] = useState<any>(null);
  const [isQrDialogOpen, setIsQrDialogOpen] = useState(false);
  const [isPreviewExpanded, setIsPreviewExpanded] = useState(false);
  const [isExplorerCollapsed, setIsExplorerCollapsed] = useState(false);

  const handleFileChange = async (file: File | null) => {
    setUploadedFile(file);
    // Reset states when file is deleted
    if (!file) {
      setParseCompleted(false);
      setSelectedPreviewFile(null);
      setIsProcessing(false);
      setIsUploading(false);
      setUploadedFilePath('');
      setTaskId('');
      setResultDir('');
    } else {
      // Upload file to backend
      setIsUploading(true);
      toast.info('正在上传中...', {
        description: `上传文件: ${file.name}`,
        style: {
          background: 'linear-gradient(to right, #3b82f6, #2563eb)',
          color: 'white',
          border: '1px solid #2563eb',
        },
      });

      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/upload`, {
          method: 'POST',
          body: formData,
        });

        const data = await response.json();
        if (data.status === 'success') {
          setUploadedFilePath(data.file_path);
          setIsUploading(false);
          toast.success('文件上传成功', {
            description: `已上传 ${file.name}`,
            style: {
              background: 'linear-gradient(to right, #10b981, #059669)',
              color: 'white',
              border: '1px solid #059669',
            },
          });
        } else {
          setIsUploading(false);
          setUploadedFile(null);
          toast.error('文件上传失败', {
            style: {
              background: 'linear-gradient(to right, #ef4444, #dc2626)',
              color: 'white',
              border: '1px solid #dc2626',
            },
          });
        }
      } catch (error) {
        console.error('Upload error:', error);
        setIsUploading(false);
        setUploadedFile(null);
        toast.error('文件上传失败', {
          description: '无法连接到后端服务',
          style: {
            background: 'linear-gradient(to right, #ef4444, #dc2626)',
            color: 'white',
            border: '1px solid #dc2626',
          },
        });
      }
    }
  };

  const handleStartParsing = async () => {
    if (!uploadedFilePath) {
      toast.error('请先上传文件', {
        style: {
          background: 'linear-gradient(to right, #ef4444, #dc2626)',
          color: 'white',
          border: '1px solid #dc2626',
        },
      });
      return;
    }

    setIsProcessing(true);
    setParseCompleted(false);
    setResultDir('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_path: uploadedFilePath,
          prompt: prompt,
        }),
      });

      const data = await response.json();
      if (data.status === 'running' && data.task_id) {
        setTaskId(data.task_id);
        
        let isTaskFinished = false;
        
        // Poll for completion from backend
        const pollInterval = setInterval(async () => {
          try {
            const progressRes = await fetch(`${API_BASE_URL}/api/progress/${data.task_id}`);
            const progressData = await progressRes.json();
            
            if (progressData.status === 'success' && progressData.state === 'finished') {
              isTaskFinished = true;
              clearInterval(pollInterval);
              setIsProcessing(false);
              
              // Fetch result
              const resultRes = await fetch(`${API_BASE_URL}/api/result/${data.task_id}`);
              const resultData = await resultRes.json();
              
              if (resultData.status === 'success' && resultData.state === 'finished') {
                setResultDir(resultData.result_dir);
                setParseCompleted(true);
                toast.success('解析完成！', {
                  description: '已经顺利完成解析',
                  style: {
                    background: 'linear-gradient(to right, #10b981, #059669)',
                    color: 'white',
                    border: '1px solid #059669',
                  },
                });
              }
            }
          } catch (error) {
            console.error('Progress poll error:', error);
          }
        }, 2000); // Poll every 2 seconds
      } else {
        toast.error('启动解析任务失败', {
          style: {
            background: 'linear-gradient(to right, #ef4444, #dc2626)',
            color: 'white',
            border: '1px solid #dc2626',
          },
        });
        setIsProcessing(false);
      }
    } catch (error) {
      console.error('Parse error:', error);
      toast.error('解析失败', {
        description: '无法连接到后端服务',
        style: {
          background: 'linear-gradient(to right, #ef4444, #dc2626)',
          color: 'white',
          border: '1px solid #dc2626',
        },
      });
      setIsProcessing(false);
    }
  };

  const handleGetSourceCode = () => {
    setIsQrDialogOpen(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-cyan-50">
      <Toaster position="top-right" />

      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 shadow-2xl sticky top-0 z-10 border-b-4 border-purple-400/30">
        <div className="container mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex flex-col items-start gap-2">
              <h1 className="text-4xl text-white font-black tracking-wider drop-shadow-2xl">
                香港保險人保單分析系統
              </h1>
              <span className="text-sm text-white/90 font-medium tracking-wide">Powered by 寰宇數據</span>
            </div>

            {/* 导航菜单 */}
            <div className="flex items-center gap-4">
              <div className="flex gap-2 bg-white/10 backdrop-blur-sm rounded-lg p-1">
                <Button
                  onClick={() => setCurrentPage('document-analysis')}
                  className={`${
                    currentPage === 'document-analysis'
                      ? 'bg-white text-blue-600 shadow-lg'
                      : 'bg-transparent text-white hover:bg-white/20'
                  } transition-all font-semibold`}
                >
                  <FileText className="mr-2 h-4 w-4" />
                  保单分析
                </Button>
                <Button
                  onClick={() => setCurrentPage('content-creator')}
                  className={`${
                    currentPage === 'content-creator'
                      ? 'bg-white text-blue-600 shadow-lg'
                      : 'bg-transparent text-white hover:bg-white/20'
                  } transition-all font-semibold`}
                >
                  <Sparkles className="mr-2 h-4 w-4" />
                  文案制作
                </Button>
                <Button
                  onClick={() => setCurrentPage('text-to-speech')}
                  className={`${
                    currentPage === 'text-to-speech'
                      ? 'bg-white text-blue-600 shadow-lg'
                      : 'bg-transparent text-white hover:bg-white/20'
                  } transition-all font-semibold`}
                >
                  <Volume2 className="mr-2 h-4 w-4" />
                  语音合成
                </Button>
              </div>

              <Button
                onClick={handleGetSourceCode}
                className="bg-white text-blue-600 hover:bg-blue-50 shadow-xl transition-all hover:shadow-2xl hover:scale-105 font-bold cursor-pointer border-2 border-white/30"
              >
                <Gift className="mr-2 h-5 w-5" />
                领取源码
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="py-6">
        {currentPage === 'document-analysis' ? (
          <div className="container mx-auto px-8">
            <div className="grid grid-cols-2 gap-6 h-[calc(100vh-200px)]">
              {/* Left Panel - File Upload */}
              <div className="flex flex-col min-h-0">
                <FileUploader onFileChange={handleFileChange} />
              </div>

              {/* Right Panel - Results */}
              <div className="flex flex-col gap-4 min-h-0">
                {/* Prompt Input and Parse Button Row */}
                <div
                  className={`flex-shrink-0 transition-all duration-300 overflow-hidden ${
                    isPreviewExpanded ? 'h-0 opacity-0' : 'opacity-100'
                  }`}
                >
                  <PromptInput
                    prompt={prompt}
                    onPromptChange={setPrompt}
                    onParse={handleStartParsing}
                    isProcessing={isProcessing}
                    hasFile={!!uploadedFile && !!uploadedFilePath}
                    isUploading={isUploading}
                    isCompact={isPreviewExpanded}
                  />
                </div>

                {/* File Explorer - Collapsible */}
                <div
                  className={`flex-shrink-0 transition-all duration-300 overflow-hidden ${
                    isPreviewExpanded ? 'h-0 opacity-0' : ''
                  }`}
                >
                  <div className="bg-gradient-to-br from-emerald-50/70 via-teal-50/60 to-cyan-50/70 backdrop-blur-sm rounded-xl border border-emerald-200 shadow-xl overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-emerald-100 to-teal-100 px-4 py-3 border-b border-emerald-200 flex items-center justify-between cursor-pointer hover:from-emerald-200 hover:to-teal-200 transition-colors"
                      onClick={() => setIsExplorerCollapsed(!isExplorerCollapsed)}
                    >
                      <h3 className="text-sm text-gray-700 font-semibold">文件浏览器</h3>
                      {isExplorerCollapsed ? <ChevronDown className="h-4 w-4" /> : <ChevronUp className="h-4 w-4" />}
                    </div>
                    <div
                      className={`transition-all duration-300 ${
                        isExplorerCollapsed ? 'h-0' : 'h-[200px]'
                      }`}
                    >
                      <FileExplorer
                        onFileSelect={setSelectedPreviewFile}
                        selectedFile={selectedPreviewFile}
                        parseCompleted={parseCompleted}
                        resultDir={resultDir}
                      />
                    </div>
                  </div>
                </div>

                {/* File Preview */}
                <div className="flex-1 min-h-0">
                  <FilePreview
                    file={selectedPreviewFile}
                    isExpanded={isPreviewExpanded}
                    onToggleExpand={() => setIsPreviewExpanded(!isPreviewExpanded)}
                  />
                </div>
              </div>
            </div>
          </div>
        ) : currentPage === 'content-creator' ? (
          <ContentCreator />
        ) : (
          <TextToSpeech />
        )}
      </main>

      {/* QR Code Dialog */}
      <Dialog open={isQrDialogOpen} onOpenChange={setIsQrDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-center text-xl font-semibold bg-gradient-to-r from-teal-600 to-cyan-600 bg-clip-text text-transparent">
              扫码免费领取项目源码
            </DialogTitle>
          </DialogHeader>
          <div className="flex flex-col items-center gap-4 py-6">
            <div className="bg-white p-4 rounded-xl shadow-md">
              <img src={qrCode} alt="QR Code" className="w-64 h-64" />
            </div>
            <p className="text-sm text-gray-500 text-center">
              使用微信扫描二维码即可获取完整项目源码
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}