import { Textarea } from './ui/textarea';
import { Button } from './ui/button';
import { Sparkles, Loader2 } from 'lucide-react';
import { ScrollArea } from './ui/scroll-area';

interface PromptInputProps {
  prompt: string;
  onPromptChange: (value: string) => void;
  onParse: () => void;
  isProcessing: boolean;
  isUploading?: boolean;
  hasFile: boolean;
  isCompact?: boolean;
}

export function PromptInput({
  prompt,
  onPromptChange,
  onParse,
  isProcessing,
  isUploading = false,
  hasFile,
  isCompact = false,
}: PromptInputProps) {
  return (
    <div className="bg-gradient-to-br from-cyan-50/70 via-white/60 to-blue-50/70 backdrop-blur-sm rounded-xl border border-cyan-200 shadow-xl p-4">
      <label className="block text-sm text-gray-600 mb-2">提示词输入</label>
      <div className="flex gap-3 items-start">
        <div className="flex-1">
          <Textarea
            value={prompt}
            onChange={(e) => onPromptChange(e.target.value)}
            className="w-full bg-white/80 border-gray-200 focus:border-teal-400 focus:ring-teal-400 resize-none h-[70px]"
            placeholder="输入您的提示词..."
          />
        </div>
        {!isCompact && (
          <Button
            onClick={onParse}
            disabled={!hasFile || isProcessing || isUploading}
            className="h-[70px] w-[160px] bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 hover:from-indigo-600 hover:via-purple-600 hover:to-pink-600 text-white shadow-lg disabled:opacity-50 disabled:from-gray-300 disabled:to-gray-400 transition-all hover:shadow-xl hover:scale-[1.02] cursor-pointer disabled:cursor-not-allowed flex-shrink-0"
          >
            {isProcessing ? (
              <div className="flex flex-col items-center gap-2">
                <Loader2 className="h-6 w-6 animate-spin" />
                <span className="text-sm">解析中...</span>
              </div>
            ) : isUploading ? (
              <div className="flex flex-col items-center gap-2">
                <Loader2 className="h-6 w-6 animate-spin" />
                <span className="text-sm">上传中...</span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <Sparkles className="h-6 w-6" />
                <span className="text-base font-bold">开始解析</span>
              </div>
            )}
          </Button>
        )}
      </div>
    </div>
  );
}