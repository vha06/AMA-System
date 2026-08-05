'use client';

import React from 'react';
import { Bot, Sparkles, ArrowRight, Lightbulb } from 'lucide-react';
import { RouterDecision } from '../types/market';

interface ChatbotResponseCardProps {
  decision: RouterDecision;
  onTryQuery: (query: string) => void;
}

export const ChatbotResponseCard: React.FC<ChatbotResponseCardProps> = ({
  decision,
  onTryQuery,
}) => {
  const sampleSuggestions = [
    'Phân tích ngách mỹ phẩm thuần chay',
    'Thị trường đồ ăn vặt đóng gói',
    'Chiến lược giá ngành thời trang trẻ em',
  ];

  return (
    <div className="w-full max-w-4xl mx-auto bg-white/80 dark:bg-slate-900/80 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-6 shadow-lg backdrop-blur-xl transition-all space-y-5 animate-in fade-in slide-in-from-bottom-3 duration-300">
      {/* Header & Bot Identity */}
      <div className="flex items-start space-x-4">
        <div className="relative shrink-0">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
            <Bot className="w-6 h-6" />
          </div>
          <span className="absolute -bottom-1 -right-1 flex h-3.5 w-3.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500 border-2 border-white dark:border-slate-900"></span>
          </span>
        </div>

        <div className="flex-1 space-y-1.5 pt-0.5">
          <div className="flex items-center space-x-2">
            <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center gap-1.5">
              <span>Trợ Lý Phân Tích AMA</span>
              <Sparkles className="w-4 h-4 text-amber-500 dark:text-amber-400 fill-amber-400/20" />
            </h3>
            <span className="px-2.5 py-0.5 text-[11px] font-medium rounded-full bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-500/20">
              Trợ Lý Trực Tuyến
            </span>
          </div>

          {/* Conversational Message Bubble */}
          <div className="bg-slate-100/80 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/50 rounded-2xl rounded-tl-sm p-4 text-sm text-slate-700 dark:text-slate-200 leading-relaxed shadow-xs">
            {decision.reasoning || (
              <p>
                Xin chào! Mình là trợ lý phân tích thị trường. Hiện tại mình chuyên hỗ trợ phân tích ngách sản phẩm, lập chiến lược giá và tối ưu từ khóa kinh doanh.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Suggested Action & Quick Reply Queries */}
      <div className="pt-2 border-t border-slate-100 dark:border-slate-800/80 space-y-3">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-500 dark:text-slate-400">
          <Lightbulb className="w-4 h-4 text-amber-500 shrink-0" />
          <span>Bạn có muốn thử phân tích một chủ đề gợi ý dưới đây không?</span>
        </div>

        <div className="flex flex-wrap gap-2">
          {/* Action suggested by decision topic if exists */}
          {decision.topic && (
            <button
              onClick={() => onTryQuery(decision.topic)}
              className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-medium transition-all shadow-sm hover:shadow-indigo-500/20 active:scale-[0.98] cursor-pointer"
            >
              <span>{decision.topic}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}

          {/* General market research suggestions */}
          {sampleSuggestions.map((sug, idx) => (
            <button
              key={idx}
              onClick={() => onTryQuery(sug)}
              className="inline-flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-slate-100 hover:bg-indigo-50 dark:bg-slate-800/80 dark:hover:bg-indigo-950/40 text-slate-700 hover:text-indigo-600 dark:text-slate-300 dark:hover:text-indigo-400 border border-slate-200 dark:border-slate-700/60 hover:border-indigo-300 dark:hover:border-indigo-500/30 text-xs font-medium transition-all cursor-pointer"
            >
              <span>{sug}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
