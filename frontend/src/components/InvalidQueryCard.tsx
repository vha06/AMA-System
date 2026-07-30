'use client';

import React from 'react';
import { AlertTriangle, HelpCircle, ArrowUpRight } from 'lucide-react';
import { RouterDecision } from '../types/market';

interface InvalidQueryCardProps {
  decision: RouterDecision;
  onTryQuery: (suggested: string) => void;
}

export const InvalidQueryCard: React.FC<InvalidQueryCardProps> = ({ decision, onTryQuery }) => {
  return (
    <div className="w-full max-w-4xl mx-auto bg-amber-950/20 border border-amber-500/30 rounded-2xl p-6 backdrop-blur-xl shadow-xl space-y-4 text-slate-200">
      <div className="flex items-start space-x-3">
        <div className="p-2 bg-amber-500/10 rounded-xl border border-amber-500/20 text-amber-400">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <h3 className="text-base font-bold text-amber-300">
              Truy vấn không thuộc phạm vi phân tích thị trường
            </h3>
            <span className="px-2 py-0.5 text-[10px] font-semibold uppercase rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/30">
              Router Agent Flag
            </span>
          </div>
          <p className="text-sm text-slate-300 mt-1 leading-relaxed">
            {decision.reasoning ||
              'Router Agent nhận thấy truy vấn của bạn quá chung chung hoặc không chứa từ khóa kinh doanh/thị trường.'}
          </p>
        </div>
      </div>

      {decision.suggested_action && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
            <HelpCircle className="w-4 h-4 text-emerald-400" />
            <span>Gợi ý hành động từ hệ thống:</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">{decision.suggested_action}</p>

          {decision.topic && (
            <div className="pt-2">
              <button
                onClick={() => onTryQuery(decision.topic)}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-semibold transition-colors cursor-pointer"
              >
                <span>Thử lại với gợi ý: &quot;{decision.topic}&quot;</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
