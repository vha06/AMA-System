'use client';

import React from 'react';
import { Loader2, CheckCircle2, Cpu } from 'lucide-react';

interface ServerWakeupNoticeProps {
  state: 'waking' | 'ready';
}

export const ServerWakeupNotice: React.FC<ServerWakeupNoticeProps> = ({ state }) => {
  if (state === 'waking') {
    return (
      <div className="w-full max-w-4xl mx-auto bg-amber-50/90 dark:bg-amber-950/30 border border-amber-300 dark:border-amber-500/40 rounded-2xl p-4 sm:p-5 text-amber-900 dark:text-amber-100 flex items-start space-x-3 shadow-md animate-in fade-in slide-in-from-top-2 duration-300">
        <div className="p-2 rounded-xl bg-amber-100 dark:bg-amber-900/50 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5">
          <Loader2 className="w-5 h-5 animate-spin" />
        </div>
        <div className="space-y-1 flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-bold text-amber-950 dark:text-amber-200 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              <span>Đang kết nối & khởi động máy chủ AI...</span>
            </h4>
            <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-amber-200/60 dark:bg-amber-900/60 text-amber-800 dark:text-amber-300 font-medium">
              Render Hibernation
            </span>
          </div>
          <p className="text-xs sm:text-sm text-amber-800 dark:text-amber-300 font-medium leading-relaxed">
            Đang khởi động hệ thống AI, sẽ mất khoảng 1 đến 2 phút, bạn vui lòng chờ nhé!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-300 dark:border-emerald-500/40 rounded-2xl p-4 sm:p-5 text-emerald-900 dark:text-emerald-100 flex items-start space-x-3 shadow-md animate-in fade-in slide-in-from-top-2 duration-300">
      <div className="p-2 rounded-xl bg-emerald-100 dark:bg-emerald-900/50 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5">
        <CheckCircle2 className="w-5 h-5" />
      </div>
      <div className="space-y-1 flex-1 min-w-0">
        <h4 className="text-sm font-bold text-emerald-950 dark:text-emerald-200 flex items-center gap-2">
          <span>Kết nối máy chủ thành công</span>
        </h4>
        <p className="text-xs sm:text-sm text-emerald-800 dark:text-emerald-300 font-medium leading-relaxed">
          Đã khởi động thành công hệ thống AI! Đang tiến hành phân tích dữ liệu...
        </p>
      </div>
    </div>
  );
};
