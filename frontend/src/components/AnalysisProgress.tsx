'use client';

import React from 'react';
import { CheckCircle2, Loader2, Circle, Bot, Database, Sparkles } from 'lucide-react';
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
      title: 'Router Agent',
      desc: 'Phân loại ý định & kiểm tra Cache',
      icon: Bot,
    },
    {
      id: 2,
      title: 'GraphRAG & Scraper',
      desc: 'Truy xuất tri thức & dữ liệu mạng',
      icon: Database,
    },
    {
      id: 3,
      title: 'Insight Agent',
      desc: 'Sinh báo cáo chiến lược (Gemini 3.1 Pro)',
      icon: Sparkles,
    },
  ];

  return (
    <div className="w-full max-w-4xl mx-auto bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 sm:p-6 backdrop-blur-xl shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
          <span>Tiến trình phân tích hệ thống</span>
        </h3>
        <span className="text-xs text-slate-400 font-mono">
          {status === 'routing' && 'Đang kiểm tra ý định...'}
          {status === 'analyzing' && 'Đang truyền dữ liệu (Streaming)...'}
          {status === 'completed' && 'Đã hoàn thành!'}
          {status === 'error' && 'Đã xảy ra lỗi'}
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
                  ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-400'
                  : isCurrent
                  ? 'bg-slate-800/60 border-emerald-500/50 text-slate-100 ring-1 ring-emerald-500/30'
                  : 'bg-slate-950/40 border-slate-800/50 text-slate-500'
              }`}
            >
              <div className="pt-0.5">
                {isDone ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                ) : isCurrent ? (
                  <Loader2 className="w-5 h-5 text-emerald-400 animate-spin" />
                ) : (
                  <Circle className="w-5 h-5 text-slate-600" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-1.5 font-medium text-xs sm:text-sm">
                  <Icon className="w-4 h-4 text-emerald-400" />
                  <span className="truncate">{step.title}</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5 truncate">{step.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
