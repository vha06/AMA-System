'use client';

import React, { useState } from 'react';
import { Search, Sparkles, X, ArrowRight, Lightbulb } from 'lucide-react';

interface SearchInputProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

const PRESET_QUERIES = [
  'Thị trường mỹ phẩm thuần chay Việt Nam',
  'Nước ép trái cây tươi đóng chai ngách văn phòng',
  'Khóa học lập trình AI cho sinh viên ngành CNTT',
  'Dịch vụ thiết kế website AI cho doanh nghiệp nhỏ',
];

export const SearchInput: React.FC<SearchInputProps> = ({ onSearch, isLoading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSearch(query.trim());
    }
  };

  const handleSelectPreset = (preset: string) => {
    setQuery(preset);
    if (!isLoading) {
      onSearch(preset);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      <form onSubmit={handleSubmit} className="relative group">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-indigo-600 to-purple-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-300"></div>
        <div className="relative flex items-center bg-white/90 dark:bg-slate-950/90 backdrop-blur-xl border border-slate-200 dark:border-slate-800 rounded-2xl p-2 shadow-xl transition-colors">
          <div className="pl-4 pr-2 text-slate-400">
            <Search className="w-5 h-5 group-focus-within:text-indigo-600 dark:group-focus-within:text-indigo-400 transition-colors" />
          </div>

          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Nhập chủ đề hoặc thị trường muốn phân tích (ví dụ: Nước ép đóng chai, Khóa học AI...)"
            disabled={isLoading}
            className="w-full bg-transparent text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 text-sm sm:text-base px-2 py-2 focus:outline-none disabled:opacity-50 font-medium"
          />

          {query && !isLoading && (
            <button
              type="button"
              onClick={() => setQuery('')}
              className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 mr-2"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-semibold text-sm transition-all shadow-md shadow-indigo-500/20 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
          >
            <span>{isLoading ? 'Đang phân tích...' : 'Phân tích'}</span>
            {isLoading ? (
              <Sparkles className="w-4 h-4 animate-spin" />
            ) : (
              <ArrowRight className="w-4 h-4" />
            )}
          </button>
        </div>
      </form>

      {/* Preset Suggestions */}
      <div className="flex flex-wrap items-center gap-2 pt-1">
        <div className="flex items-center space-x-1 text-xs text-slate-500 dark:text-slate-400 font-medium mr-1">
          <Lightbulb className="w-3.5 h-3.5 text-amber-500" />
          <span>Gợi ý:</span>
        </div>
        {PRESET_QUERIES.map((preset, index) => (
          <button
            key={index}
            onClick={() => handleSelectPreset(preset)}
            disabled={isLoading}
            className="text-xs px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-900/80 hover:bg-slate-200 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors cursor-pointer text-left shadow-xs"
          >
            {preset}
          </button>
        ))}
      </div>
    </div>
  );
};
