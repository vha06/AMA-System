'use client';

import React, { useState } from 'react';
import { Bot, Copy, Check, Terminal, Sparkles } from 'lucide-react';

interface AiPromptsCardProps {
  prompts?: string[];
  isStreaming?: boolean;
}

export const AiPromptsCard: React.FC<AiPromptsCardProps> = ({
  prompts = [],
  isStreaming = false,
}) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleCopyPrompt = (promptText: string, index: number) => {
    navigator.clipboard.writeText(promptText);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="relative group bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/90 hover:border-indigo-300 dark:hover:border-indigo-500/30 rounded-2xl p-6 backdrop-blur-xl shadow-md transition-all space-y-4">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <div className="p-2.5 bg-indigo-50 dark:bg-indigo-500/20 rounded-xl border border-indigo-200 dark:border-indigo-500/30 text-indigo-600 dark:text-indigo-400">
          <Bot className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
            <span>Câu Lệnh AI Đề Xuất (Prompts)</span>
            {isStreaming && (
              <span className="w-2 h-2 rounded-full bg-indigo-600 dark:bg-indigo-400 animate-pulse"></span>
            )}
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">Sử dụng trực tiếp cho ChatGPT, Claude hoặc Gemini</p>
        </div>
      </div>

      {/* Prompts List */}
      {prompts.length > 0 ? (
        <div className="space-y-3">
          {prompts.map((promptText, index) => (
            <div
              key={index}
              className="group/prompt relative bg-white dark:bg-slate-950/80 border border-slate-200 dark:border-slate-800/80 hover:border-indigo-300 dark:hover:border-indigo-500/40 rounded-xl p-4 transition-all shadow-xs"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start space-x-2.5 flex-1 min-w-0">
                  <Terminal className="w-4 h-4 text-indigo-600 dark:text-indigo-400 mt-0.5 shrink-0" />
                  <p className="text-xs sm:text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-mono select-all">
                    {promptText}
                  </p>
                </div>

                <button
                  onClick={() => handleCopyPrompt(promptText, index)}
                  className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 text-xs font-medium transition-colors shrink-0 cursor-pointer"
                  title="Sao chép prompt này"
                >
                  {copiedIndex === index ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                      <span className="text-emerald-600 dark:text-emerald-400">Đã chép!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Sao chép</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-slate-100/60 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/50 rounded-xl p-6 flex flex-col items-center justify-center text-center space-y-2 text-slate-400 dark:text-slate-500">
          <Sparkles className="w-8 h-8 animate-pulse text-indigo-500/40" />
          <p className="text-xs">Đang sinh bộ câu lệnh AI chuyên sâu...</p>
        </div>
      )}
    </div>
  );
};
