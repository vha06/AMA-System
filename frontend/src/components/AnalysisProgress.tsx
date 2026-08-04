'use client';

import React from 'react';
import { CheckCircle2, Loader2, Circle, Search, TrendingUp, BarChart3 } from 'lucide-react';
import { AnalysisStatus } from '../types/market';

interface AnalysisProgressProps {
  status: AnalysisStatus;
  currentStep: number; // 1, 2, or 3
}

export const AnalysisProgress: React.FC<AnalysisProgressProps> = ({ status, currentStep }) => {
  if (status === 'idle') return null;

  const steps = [
    {
      id: 1,
      title: 'Xác thực & Định tuyến',
      desc: 'Đánh giá từ khóa & phạm vi kinh doanh',
      icon: Search,
    },
    {
      id: 2,
      title: 'Thu thập Dữ liệu Thị trường',
      desc: 'Tổng hợp thông tin xu hướng & đối thủ',
      icon: TrendingUp,
    },
    {
      id: 3,
      title: 'Xây dựng Báo cáo Chiến lược',
      desc: 'Trích xuất ngách, giá tối ưu & rủi ro',
      icon: BarChart3,
    },
  ];

  return (
    <div className="w-full max-w-4xl mx-auto bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800/80 rounded-2xl p-4 sm:p-6 backdrop-blur-xl shadow-md space-y-4 transition-colors">
      <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
        <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200 flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-indigo-600 dark:bg-indigo-400 animate-ping"></span>
          <span>Tiến trình tổng hợp báo cáo</span>
        </h3>
        <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
          {status === 'routing' && 'Đang kiểm tra từ khóa...'}
          {status === 'analyzing' && 'Đang xây dựng báo cáo chiến lược...'}
          {status === 'completed' && 'Đã hoàn tất báo cáo!'}
          {status === 'error' && 'Xảy ra gián đoạn xử lý'}
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {steps.map((step) => {
          const isDone = currentStep > step.id || status === 'completed';
          const isCurrent = currentStep === step.id && status !== 'completed' && status !== 'error';
          const Icon = step.icon;

          return (
            <div
              key={step.id}
              className={`flex items-start space-x-3 p-3 rounded-xl border transition-all ${
                isDone
                  ? 'bg-emerald-50 dark:bg-emerald-950/20 border-emerald-300 dark:border-emerald-500/30 text-emerald-700 dark:text-emerald-400'
                  : isCurrent
                  ? 'bg-indigo-50 dark:bg-slate-800/60 border-indigo-400 dark:border-indigo-500/50 text-indigo-950 dark:text-slate-100 ring-1 ring-indigo-500/30'
                  : 'bg-slate-100/60 dark:bg-slate-950/40 border-slate-200 dark:border-slate-800/50 text-slate-400 dark:text-slate-500'
              }`}
            >
              <div className="pt-0.5">
                {isDone ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                ) : isCurrent ? (
                  <Loader2 className="w-5 h-5 text-indigo-600 dark:text-indigo-400 animate-spin" />
                ) : (
                  <Circle className="w-5 h-5 text-slate-400 dark:text-slate-600" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-1.5 font-medium text-xs sm:text-sm">
                  <Icon className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                  <span className="truncate">{step.title}</span>
                </div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 truncate">{step.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
