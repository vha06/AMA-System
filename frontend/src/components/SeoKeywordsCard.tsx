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
    <div className="relative group bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/90 hover:border-orange-300 dark:hover:border-orange-500/30 rounded-2xl p-6 backdrop-blur-xl shadow-md transition-all space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-orange-50 dark:bg-orange-500/20 rounded-xl border border-orange-200 dark:border-orange-500/30 text-orange-600 dark:text-orange-400">
            <Search className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
              <span>Từ Khóa SEO & Quảng Cáo Tiềm Năng</span>
              {isStreaming && (
                <span className="w-2 h-2 rounded-full bg-orange-500 dark:bg-orange-400 animate-pulse"></span>
              )}
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">Từ khóa độ tìm kiếm tốt cho nội dung & chạy ads</p>
          </div>
        </div>

        {keywords.length > 0 && (
          <button
            onClick={handleCopyAll}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold text-orange-600 dark:text-orange-300 hover:text-orange-700 dark:hover:text-white bg-orange-50 dark:bg-orange-500/10 hover:bg-orange-100 dark:hover:bg-orange-500/20 border border-orange-200 dark:border-orange-500/30 rounded-lg transition-colors cursor-pointer"
          >
            {copiedAll ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
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
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-white dark:bg-slate-950/80 hover:bg-orange-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 hover:border-orange-300 dark:hover:border-orange-500/40 text-slate-800 dark:text-slate-200 hover:text-orange-600 dark:hover:text-orange-300 text-xs font-medium transition-all cursor-pointer group/tag shadow-xs"
              title="Bấm để sao chép từ khóa"
            >
              <Hash className="w-3.5 h-3.5 text-orange-500 dark:text-orange-400 group-hover/tag:text-orange-600" />
              <span>{kw}</span>
              {copiedIndex === index ? (
                <Check className="w-3 h-3 text-emerald-600 dark:text-emerald-400 ml-1" />
              ) : (
                <Copy className="w-3 h-3 opacity-0 group-hover/tag:opacity-100 text-slate-400 transition-opacity ml-1" />
              )}
            </button>
          ))}
        </div>
      ) : (
        <div className="bg-slate-100/60 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/50 rounded-xl p-6 flex flex-col items-center justify-center text-center space-y-2 text-slate-400 dark:text-slate-500">
          <Sparkles className="w-8 h-8 animate-pulse text-orange-500/40" />
          <p className="text-xs">Đang đề xuất bộ từ khóa SEO chất lượng cao...</p>
        </div>
      )}
    </div>
  );
};
