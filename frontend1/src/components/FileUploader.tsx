import { useState } from 'react';
import { Button } from './ui/button';
import { ScrollArea } from './ui/scroll-area';
import { Upload, Trash2 } from 'lucide-react';

interface FileUploaderProps {
  onFileChange: (file: File | null) => void;
}

export function FileUploader({ onFileChange }: FileUploaderProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      onFileChange(file);
      
      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  };

  const handleDelete = () => {
    setSelectedFile(null);
    setPreviewUrl('');
    onFileChange(null);
  };

  return (
    <div className="flex flex-col gap-4 h-full min-h-0">
      <div className="flex gap-2 flex-shrink-0">
        <Button
          variant="outline"
          className="flex-1 h-12 bg-gradient-to-r from-blue-50 to-purple-50 backdrop-blur-sm border-2 border-dashed border-blue-300 hover:border-purple-400 hover:from-blue-100 hover:to-purple-100 transition-all hover:shadow-lg cursor-pointer"
          onClick={() => document.getElementById('file-input')?.click()}
        >
          <Upload className="mr-2 h-5 w-5" />
          上传文件（PDF / PNG / JPG）
        </Button>
        <input
          id="file-input"
          type="file"
          accept=".pdf,.png,.jpg,.jpeg"
          className="hidden"
          onChange={handleFileSelect}
        />
        <Button
          variant="outline"
          size="icon"
          className="h-12 w-12 bg-white/50 backdrop-blur-sm hover:bg-red-50 hover:border-red-300 transition-all hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          onClick={handleDelete}
          disabled={!selectedFile}
        >
          <Trash2 className="h-5 w-5" />
        </Button>
      </div>

      <div className="flex-1 min-h-0 bg-gradient-to-br from-white/80 via-blue-50/50 to-purple-50/50 backdrop-blur-sm rounded-xl border border-blue-200 shadow-xl overflow-hidden">
        <ScrollArea className="h-full w-full">
          <div className="p-6">
            {previewUrl ? (
              <div className="flex items-center justify-center">
                {selectedFile?.type === 'application/pdf' ? (
                  <div className="w-full">
                    <iframe
                      src={previewUrl}
                      className="w-full h-[calc(100vh-300px)] min-h-[600px] rounded-lg border border-gray-300 shadow-md bg-white"
                      title="PDF Preview"
                    />
                    <p className="text-xs text-gray-500 text-center mt-2">
                      💡 提示：可以在 PDF 查看器中滚动、缩放和导航
                    </p>
                  </div>
                ) : (
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="max-w-full h-auto rounded-lg shadow-md"
                  />
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center min-h-[400px]">
                <div className="text-center text-gray-400">
                  <Upload className="h-16 w-16 mx-auto mb-4 opacity-30" />
                  <p>请上传文件以预览</p>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}