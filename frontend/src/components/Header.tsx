'use client';

import React from 'react';
import { BrainCircuit, Activity } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

interface HeaderProps {
  apiStatus?: 'online' | 'offline' | 'checking';
}

export const Header: React.FC<HeaderProps> = () => {
  return (
    <header className="w-full border-b border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-950/60 backdrop-blur-xl sticky top-0 z-50 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo & System Name */}
        <div className="flex items-center space-x-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 shadow-md shadow-indigo-500/20">
            <BrainCircuit className="w-5 h-5 text-white" />
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-slate-800 dark:text-slate-100">
                AMA Market Intelligence
              </h1>
              <span className="px-2.5 py-0.5 text-[10px] font-semibold tracking-wide uppercase rounded-full bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800">
                Enterprise Edition
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
              Hệ thống Phân tích Thị trường & Chiến lược Kinh doanh Tự động
            </p>
          </div>
        </div>

        {/* Right Info & Links */}
        <div className="flex items-center space-x-3 sm:space-x-4">
          {/* Status Badge */}
          <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-300">
            <Activity className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400 animate-pulse" />
            <span className="hidden md:inline">Dữ liệu thị trường:</span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400">Sẵn sàng</span>
          </div>

          <ThemeToggle />

        </div>
      </div>
    </header>
  );
};

