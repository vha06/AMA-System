'use client';

import React, { useState } from 'react';
import { Header } from '../components/Header';
import { SearchInput } from '../components/SearchInput';
import { AnalysisProgress } from '../components/AnalysisProgress';
import { InvalidQueryCard } from '../components/InvalidQueryCard';
import { NicheAnalysisCard } from '../components/NicheAnalysisCard';
import { PricingStrategyCard } from '../components/PricingStrategyCard';
import { RisksCard } from '../components/RisksCard';
import { SeoKeywordsCard } from '../components/SeoKeywordsCard';
import { AiPromptsCard } from '../components/AiPromptsCard';
import { ReportToolbar } from '../components/ReportToolbar';

import { analyzeRouterQuery, streamInsightReport } from '../lib/api';
import { parsePartialInsightReport } from '../lib/json-stream-parser';
import { RouterDecision, InsightReport, AnalysisStatus } from '../types/market';
import { Sparkles, AlertCircle, BarChart3 } from 'lucide-react';

export default function Home() {
  const [status, setStatus] = useState<AnalysisStatus>('idle');
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [activeTopic, setActiveTopic] = useState<string>('');
  const [routerDecision, setRouterDecision] = useState<RouterDecision | null>(null);
  const [report, setReport] = useState<Partial<InsightReport>>({});
  const [errorMessage, setErrorMessage] = useState<string>('');

  const handleSearch = async (query: string) => {
    setActiveTopic(query);
    setErrorMessage('');
    setRouterDecision(null);
    setReport({});
    setStatus('routing');
    setCurrentStep(1);

    try {
      // Step 1: Analyze query via Router Agent
      const decision = await analyzeRouterQuery(query);
      setRouterDecision(decision);

      if (decision.intent === 'INVALID') {
        setStatus('completed');
        return;
      }

      // Step 2: Proceed to Scraper & GraphRAG phase
      setCurrentStep(2);
      await new Promise((resolve) => setTimeout(resolve, 600));

      // Step 3: Stream Insight Report
      setCurrentStep(3);
      setStatus('analyzing');

      const targetTopic = decision.topic || query;
      await streamInsightReport(targetTopic, '', (accumulatedText) => {
        const partial = parsePartialInsightReport(accumulatedText);
        setReport(partial);
      });

      setStatus('completed');
    } catch (err: unknown) {
      console.error('Error during market analysis execution:', err);
      const message = err instanceof Error ? err.message : 'Đã có lỗi xảy ra khi gọi hệ thống backend.';
      setErrorMessage(message);
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 bg-grid-pattern relative selection:bg-emerald-500 selection:text-slate-950">
      {/* Glow Effects */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-b from-emerald-500/10 via-teal-500/5 to-transparent blur-3xl pointer-events-none -z-10" />

      {/* Header */}
      <Header />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
        {/* Hero Banner */}
        <section className="text-center space-y-4 pt-4 pb-2">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Multi-Agent Strategy Engine powered by Gemini 3.1 Pro</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight max-w-3xl mx-auto leading-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-100 via-slate-200 to-emerald-300">
            Phân Tích Thị Trường & Sinh Chiến Lược Kinh Doanh Tự Động
          </h2>

          <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
            Nhập ngành hàng hoặc chủ đề sản phẩm để nhận báo cáo phân tích ngách, chiến lược giá, rủi ro và câu lệnh AI chuyên sâu trong thời gian thực.
          </p>
        </section>

        {/* Search Input Box */}
        <section>
          <SearchInput onSearch={handleSearch} isLoading={status === 'routing' || status === 'analyzing'} />
        </section>

        {/* Progress Stepper */}
        <section>
          <AnalysisProgress status={status} currentStep={currentStep} />
        </section>

        {/* Error State display */}
        {status === 'error' && (
          <div className="w-full max-w-4xl mx-auto bg-rose-950/20 border border-rose-500/30 rounded-2xl p-6 text-slate-200 flex items-start space-x-3 shadow-xl">
            <AlertCircle className="w-6 h-6 text-rose-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <h4 className="text-sm font-bold text-rose-300">Lỗi kết nối hoặc xử lý dữ liệu</h4>
              <p className="text-xs text-slate-300">{errorMessage}</p>
              <p className="text-[11px] text-slate-400 pt-1">
                Hãy đảm bảo backend FastAPI đang khởi chạy tại <code className="text-emerald-400">http://localhost:8000</code>.
              </p>
            </div>
          </div>
        )}

        {/* Router Invalid Decision */}
        {routerDecision && routerDecision.intent === 'INVALID' && (
          <section className="animate-in fade-in slide-in-from-bottom-4 duration-300">
            <InvalidQueryCard decision={routerDecision} onTryQuery={handleSearch} />
          </section>
        )}

        {/* Generative UI Section */}
        {status !== 'idle' && routerDecision?.intent !== 'INVALID' && (
          <section className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-5 h-5 text-emerald-400" />
                <h3 className="text-lg font-bold text-slate-100">
                  Báo Cáo Phân Tích Chiến Lược: <span className="text-emerald-400">{activeTopic}</span>
                </h3>
              </div>
              {status === 'analyzing' && (
                <div className="flex items-center space-x-2 text-xs text-emerald-400 font-mono animate-pulse">
                  <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                  <span>Streaming Generative UI...</span>
                </div>
              )}
            </div>

            {/* Export Toolbar */}
            {(report.niche_analysis || report.pricing?.suggested_price) && (
              <ReportToolbar report={report} topic={activeTopic} />
            )}

            {/* Generative Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Card 1: Niche Analysis */}
              <div className="md:col-span-2">
                <NicheAnalysisCard nicheAnalysis={report.niche_analysis} isStreaming={status === 'analyzing'} />
              </div>

              {/* Card 2: Pricing Strategy */}
              <PricingStrategyCard pricing={report.pricing} isStreaming={status === 'analyzing'} />

              {/* Card 3: Risks & Challenges */}
              <RisksCard risks={report.risks} isStreaming={status === 'analyzing'} />

              {/* Card 4: SEO Keywords Cloud */}
              <div className="md:col-span-2">
                <SeoKeywordsCard keywords={report.seo_keywords} isStreaming={status === 'analyzing'} />
              </div>

              {/* Card 5: AI Prompts */}
              <div className="md:col-span-2">
                <AiPromptsCard prompts={report.ai_prompts} isStreaming={status === 'analyzing'} />
              </div>
            </div>
          </section>
        )}

        {/* Empty State / Initial Landing Guide */}
        {status === 'idle' && (
          <section className="max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
            <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 space-y-2 hover:border-slate-700 transition-colors">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold text-sm">
                01
              </div>
              <h4 className="text-sm font-semibold text-slate-200">Định tuyến & Lọc truy vấn</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Router Agent sử dụng Gemini API phân tích và lọc truy vấn hợp lệ trước khi thực thi.
              </p>
            </div>

            <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 space-y-2 hover:border-slate-700 transition-colors">
              <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400 font-bold text-sm">
                02
              </div>
              <h4 className="text-sm font-semibold text-slate-200">Truy xuất GraphRAG</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Kết hợp vector database ChromaDB và đồ thị thực thể NetworkX để tổng hợp tri thức.
              </p>
            </div>

            <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 space-y-2 hover:border-slate-700 transition-colors">
              <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold text-sm">
                03
              </div>
              <h4 className="text-sm font-semibold text-slate-200">Generative UI Streaming</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Nội dung chiến lược được stream trực tiếp dạng JSON và cập nhật giao diện thời gian thực.
              </p>
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-800/80 bg-slate-950/80 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <p>© 2026 AMA-System. Automated Market Analysis & Strategy Engine.</p>
          <div className="flex items-center space-x-4">
            <span className="hover:text-slate-400 cursor-pointer">Next.js 16 App Router</span>
            <span>•</span>
            <span className="hover:text-slate-400 cursor-pointer">FastAPI + CrewAI</span>
            <span>•</span>
            <span className="hover:text-slate-400 cursor-pointer">Gemini 3.1 Pro</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
