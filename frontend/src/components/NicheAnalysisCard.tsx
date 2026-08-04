'use client';

import React, { useState } from 'react';
import { Target, Copy, Check, TrendingUp, Compass } from 'lucide-react';

interface NicheAnalysisCardProps {
  nicheAnalysis?: string;
  isStreaming?: boolean;
}

export const NicheAnalysisCard: React.FC<NicheAnalysisCardProps> = ({
  nicheAnalysis,
  isStreaming = false,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (nicheAnalysis) {
      navigator.clipboard.writeText(nicheAnalysis);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="relative group bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/90 hover:border-indigo-300 dark:hover:border-indigo-500/30 rounded-2xl p-6 backdrop-blur-xl shadow-md transition-all space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-indigo-50 dark:bg-indigo-500/20 rounded-xl border border-indigo-200 dark:border-indigo-500/30 text-indigo-600 dark:text-indigo-400">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
              <span>Phân Tích Ngách Thị Trường</span>
              {isStreaming && (
                <span className="w-2 h-2 rounded-full bg-indigo-600 dark:bg-indigo-400 animate-pulse"></span>
              )}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">Đánh giá tiềm năng và cơ hội tăng trưởng</p>
          </div>
        </div>

        {nicheAnalysis && (
          <button
            onClick={handleCopy}
            className="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-200/60 dark:hover:bg-slate-800/80 rounded-lg border border-slate-200 dark:border-slate-800 transition-colors cursor-pointer"
            title="Sao chép nội dung"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-600 dark:text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>
        )}
      </div>

      {/* Content */}
      <div className="space-y-3">
        {nicheAnalysis ? (
          <div className="bg-white dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/80 rounded-xl p-4 text-slate-800 dark:text-slate-200 text-sm leading-relaxed whitespace-pre-line shadow-xs">
            {nicheAnalysis}
          </div>
        ) : (
          <div className="bg-slate-100/60 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/50 rounded-xl p-6 flex flex-col items-center justify-center text-center space-y-2 text-slate-400 dark:text-slate-500">
            <Compass className="w-8 h-8 animate-pulse text-indigo-500/40" />
            <p className="text-xs">Đang nhận dữ liệu phân tích ngách từ Gemini API...</p>
          </div>
        )}
      </div>

      {/* Indicator Footer */}
      <div className="flex items-center space-x-2 pt-1 text-xs text-indigo-600 dark:text-indigo-400 font-medium">
        <TrendingUp className="w-3.5 h-3.5" />
        <span>Tiềm năng tăng trưởng: Cao trong ngách mục tiêu</span>
      </div>
    </div>
  );
};
