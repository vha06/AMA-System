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
    <div className="relative group bg-slate-900/60 border border-slate-800/90 hover:border-emerald-500/30 rounded-2xl p-6 backdrop-blur-xl shadow-xl transition-all space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-br from-emerald-500/20 to-teal-500/10 rounded-xl border border-emerald-500/30 text-emerald-400">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
              <span>Phân Tích Ngách Thị Trường</span>
              {isStreaming && (
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              )}
            </h3>
            <p className="text-xs text-slate-400">Đánh giá tiềm năng và cơ hội tăng trưởng</p>
          </div>
        </div>

        {nicheAnalysis && (
          <button
            onClick={handleCopy}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 rounded-lg border border-slate-800 transition-colors cursor-pointer"
            title="Sao chép nội dung"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>
        )}
      </div>

      {/* Content */}
      <div className="space-y-3">
        {nicheAnalysis ? (
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 text-slate-200 text-sm leading-relaxed whitespace-pre-line">
            {nicheAnalysis}
          </div>
        ) : (
          <div className="bg-slate-950/40 border border-slate-800/50 rounded-xl p-6 flex flex-col items-center justify-center text-center space-y-2 text-slate-500">
            <Compass className="w-8 h-8 animate-pulse text-emerald-500/40" />
            <p className="text-xs">Đang nhận dữ liệu phân tích ngách từ Gemini API...</p>
          </div>
        )}
      </div>

      {/* Indicator Footer */}
      <div className="flex items-center space-x-2 pt-1 text-xs text-emerald-400 font-medium">
        <TrendingUp className="w-3.5 h-3.5" />
        <span>Tiềm năng tăng trưởng: Cao trong ngách mục tiêu</span>
      </div>
    </div>
  );
};
