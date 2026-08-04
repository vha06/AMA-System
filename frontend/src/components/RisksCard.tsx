'use client';

import React from 'react';
import { AlertOctagon, ShieldAlert, AlertTriangle } from 'lucide-react';

interface RisksCardProps {
  risks?: string[];
  isStreaming?: boolean;
}

export const RisksCard: React.FC<RisksCardProps> = ({ risks = [], isStreaming = false }) => {
  return (
    <div className="relative group bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/90 hover:border-orange-300 dark:hover:border-orange-500/30 rounded-2xl p-6 backdrop-blur-xl shadow-md transition-all space-y-4">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <div className="p-2.5 bg-orange-50 dark:bg-orange-500/20 rounded-xl border border-orange-200 dark:border-orange-500/30 text-orange-600 dark:text-orange-400">
          <AlertOctagon className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 flex items-center space-x-2">
            <span>Rủi Ro & Thách Thức Kinh Doanh</span>
            {isStreaming && (
              <span className="w-2 h-2 rounded-full bg-orange-500 dark:bg-orange-400 animate-pulse"></span>
            )}
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400">Các yếu tố rủi ro chính cần kiểm soát</p>
        </div>
      </div>

      {/* Risks List */}
      {risks.length > 0 ? (
        <div className="space-y-2.5">
          {risks.map((risk, index) => (
            <div
              key={index}
              className="flex items-start space-x-3 p-3.5 rounded-xl bg-white dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800/80 hover:border-orange-300 dark:hover:border-orange-500/20 transition-colors shadow-xs"
            >
              <div className="pt-0.5 text-orange-600 dark:text-orange-400">
                <AlertTriangle className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <p className="text-xs sm:text-sm text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
                  {risk}
                </p>
              </div>
              <span className="px-2 py-0.5 text-[10px] font-semibold uppercase rounded-md bg-orange-50 dark:bg-orange-500/10 text-orange-600 dark:text-orange-400 border border-orange-200 dark:border-orange-500/20 shrink-0">
                Cần lưu ý #{index + 1}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-slate-100/60 dark:bg-slate-950/40 border border-slate-200 dark:border-slate-800/50 rounded-xl p-6 flex flex-col items-center justify-center text-center space-y-2 text-slate-400 dark:text-slate-500">
          <ShieldAlert className="w-8 h-8 animate-pulse text-orange-500/40" />
          <p className="text-xs">Đang đánh giá ma trận rủi ro thị trường...</p>
        </div>
      )}
    </div>
  );
};
