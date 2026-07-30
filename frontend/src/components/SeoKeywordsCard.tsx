'use client';

import React, { useState } from 'react';
import { Search, Copy, Check, Hash, Sparkles } from 'lucide-react';

interface SeoKeywordsCardProps {
  keywords?: string[];
  isStreaming?: boolean;
}

export const SeoKeywordsCard: React.FC<SeoKeywordsCardProps> = ({
  keywords = [],
  isStreaming = false,
}) => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [copiedAll, setCopiedAll] = useState(false);

  const handleCopyOne = (keyword: string, index: number) => {
    navigator.clipboard.writeText(keyword);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 1500);
  };

  const handleCopyAll = () => {
    if (keywords.length > 0) {
      navigator.clipboard.writeText(keywords.join(', '));
      setCopiedAll(true);
      setTimeout(() => setCopiedAll(false), 2000);
    }
  };

  return (
    <div className="relative group bg-slate-900/60 border border-slate-800/90 hover:border-violet-500/30 rounded-2xl p-6 backdrop-blur-xl shadow-xl transition-all space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-br from-violet-500/20 to-purple-500/10 rounded-xl border border-violet-500/30 text-violet-400">
            <Search className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
              <span>Từ Khóa SEO & Quảng Cáo Tiềm Năng</span>
              {isStreaming && (
                <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse"></span>
              )}
            </h3>
            <p className="text-xs text-slate-400">Từ khóa độ tìm kiếm tốt cho nội dung & chạy ads</p>
          </div>
        </div>

        {keywords.length > 0 && (
          <button
            onClick={handleCopyAll}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-violet-300 hover:text-white bg-violet-500/10 hover:bg-violet-500/20 border border-violet-500/30 rounded-lg transition-colors cursor-pointer"
          >
            {copiedAll ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span>Đã sao chép tất cả</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Sao chép danh sách</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Keywords Tag Cloud */}
      {keywords.length > 0 ? (
        <div className="flex flex-wrap gap-2 pt-1">
          {keywords.map((kw, index) => (
            <button
              key={index}
              onClick={() => handleCopyOne(kw, index)}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-950/80 hover:bg-slate-800 border border-slate-800 hover:border-violet-500/40 text-slate-200 hover:text-violet-300 text-xs font-medium transition-all cursor-pointer group/tag shadow-sm"
              title="Bấm để sao chép từ khóa"
            >
              <Hash className="w-3.5 h-3.5 text-violet-400 group-hover/tag:text-violet-300" />
              <span>{kw}</span>
              {copiedIndex === index ? (
                <Check className="w-3 h-3 text-emerald-400 ml-1" />
              ) : (
                <Copy className="w-3 h-3 opacity-0 group-hover/tag:opacity-100 text-slate-400 transition-opacity ml-1" />
              )}
            </button>
          ))}
        </div>
      ) : (
        <div className="bg-slate-950/40 border border-slate-800/50 rounded-xl p-6 flex flex-col items-center justify-center text-center space-y-2 text-slate-500">
          <Sparkles className="w-8 h-8 animate-pulse text-violet-500/40" />
          <p className="text-xs">Đang đề xuất bộ từ khóa SEO chất lượng cao...</p>
        </div>
      )}
    </div>
  );
};
