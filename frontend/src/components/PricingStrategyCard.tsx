'use client';

import React from 'react';
import { DollarSign, Tag, Info, ShieldCheck } from 'lucide-react';
import { PricingStrategy } from '../types/market';

interface PricingStrategyCardProps {
  pricing?: PricingStrategy;
  isStreaming?: boolean;
}

export const PricingStrategyCard: React.FC<PricingStrategyCardProps> = ({
  pricing,
  isStreaming = false,
}) => {
  return (
    <div className="relative group bg-slate-900/60 border border-slate-800/90 hover:border-cyan-500/30 rounded-2xl p-6 backdrop-blur-xl shadow-xl transition-all space-y-4">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <div className="p-2.5 bg-gradient-to-br from-cyan-500/20 to-blue-500/10 rounded-xl border border-cyan-500/30 text-cyan-400">
          <DollarSign className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-slate-100 flex items-center space-x-2">
            <span>Chiến Lược Định Giá</span>
            {isStreaming && (
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
            )}
          </h3>
          <p className="text-xs text-slate-400">Mức giá đề xuất và luận điểm kinh doanh</p>
        </div>
      </div>

      {/* Suggested Price Highlight */}
      {pricing?.suggested_price ? (
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 border border-cyan-500/30 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="flex items-center space-x-2">
              <Tag className="w-4 h-4 text-cyan-400" />
              <span className="text-xs text-slate-400 font-medium">Khoảng giá tối ưu:</span>
            </div>
            <div className="px-3.5 py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-bold text-base sm:text-lg tracking-wide">
              {pricing.suggested_price}
            </div>
          </div>

          {/* Rationale */}
          {pricing.rationale && (
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 space-y-2">
              <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
                <Info className="w-4 h-4 text-cyan-400" />
                <span>Cơ sở & Cơ chế định giá:</span>
              </div>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                {pricing.rationale}
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-slate-950/40 border border-slate-800/50 rounded-xl p-6 flex flex-col items-center justify-center text-center space-y-2 text-slate-500">
          <DollarSign className="w-8 h-8 animate-pulse text-cyan-500/40" />
          <p className="text-xs">Đang tính toán chiến lược định giá tối ưu...</p>
        </div>
      )}

      {/* Pricing Tagline */}
      <div className="flex items-center space-x-2 pt-1 text-xs text-cyan-400 font-medium">
        <ShieldCheck className="w-3.5 h-3.5" />
        <span>Tối ưu điểm hòa vốn & tỷ lệ chuyển đổi ban đầu</span>
      </div>
    </div>
  );
};
