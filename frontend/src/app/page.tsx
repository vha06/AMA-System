'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { Sidebar, SessionLogItem } from '../components/Sidebar';
import { AuthModal } from '../components/AuthModal';
import { SearchInput } from '../components/SearchInput';
import { AnalysisProgress } from '../components/AnalysisProgress';
import { InvalidQueryCard } from '../components/InvalidQueryCard';
import { NicheAnalysisCard } from '../components/NicheAnalysisCard';
import { PricingStrategyCard } from '../components/PricingStrategyCard';
import { RisksCard } from '../components/RisksCard';
import { SeoKeywordsCard } from '../components/SeoKeywordsCard';
import { AiPromptsCard } from '../components/AiPromptsCard';
import { ReportToolbar } from '../components/ReportToolbar';
import { ServerWakeupNotice } from '../components/ServerWakeupNotice';

import { analyzeRouterQuery, streamInsightReport, checkBackendHealth } from '../lib/api';
import { parsePartialInsightReport } from '../lib/json-stream-parser';
import { createClient } from '../lib/supabase/client';
import { RouterDecision, InsightReport, AnalysisStatus } from '../types/market';
import { Sparkles, AlertCircle, BarChart3 } from 'lucide-react';

export default function Home() {
  const [status, setStatus] = useState<AnalysisStatus>('idle');
  const [currentStep, setCurrentStep] = useState<number>(0);
  const [activeTopic, setActiveTopic] = useState<string>('');
  const [routerDecision, setRouterDecision] = useState<RouterDecision | null>(null);
  const [report, setReport] = useState<Partial<InsightReport>>({});
  const [errorMessage, setErrorMessage] = useState<string>('');

  // Backend Health & Render Hibernation States
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);
  const [wakeupNoticeState, setWakeupNoticeState] = useState<'waking' | 'ready' | null>(null);

  // Auth & Session States
  const [user, setUser] = useState<any | null>(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState<number>(0);

  const supabase = createClient();

  useEffect(() => {
    // Proactive background ping on mount to wake up Render backend
    checkBackendHealth(3500).then((healthy) => {
      setIsBackendHealthy(healthy);
    });

    // Check active session
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user);
    });

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      setUser(session?.user ?? null);
      if (event === 'SIGNED_OUT' || !session?.user) {
        handleNewSession();
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleNewSession = () => {
    setCurrentSessionId(null);
    setActiveTopic('');
    setRouterDecision(null);
    setReport({});
    setStatus('idle');
    setErrorMessage('');
  };

  const handleSelectSession = (sessionItem: SessionLogItem) => {
    setCurrentSessionId(sessionItem.id);
    setActiveTopic(sessionItem.prompt);
    setRouterDecision({
      intent: 'VALID',
      topic: sessionItem.prompt,
      reasoning: 'Truy xuất từ lịch sử Supabase',
      suggested_action: 'PROCEED'
    });

    if (sessionItem.results) {
      if (sessionItem.results.raw_result && typeof sessionItem.results.raw_result === 'string') {
        const parsed = parsePartialInsightReport(sessionItem.results.raw_result);
        setReport(parsed);
      } else {
        setReport(sessionItem.results);
      }
    }
    setStatus('completed');
  };

  const handleSearch = async (query: string) => {
    setCurrentSessionId(null);
    setActiveTopic(query);
    setErrorMessage('');
    setRouterDecision(null);
    setReport({});
    
    // Check if backend is active, wake it up if hibernating
    let isReady = isBackendHealthy;
    if (isReady !== true) {
      isReady = await checkBackendHealth(3000);
    }

    if (!isReady) {
      // Backend is asleep on Render, set waking state
      setStatus('waking');
      setWakeupNoticeState('waking');

      // Poll until backend comes online
      let healthy = false;
      while (!healthy) {
        await new Promise((r) => setTimeout(r, 3000));
        healthy = await checkBackendHealth(3000);
      }

      setIsBackendHealthy(true);
      setWakeupNoticeState('ready');
      await new Promise((r) => setTimeout(r, 2000));
      setWakeupNoticeState(null);
    } else {
      setIsBackendHealthy(true);
    }

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
      await streamInsightReport(
        targetTopic,
        '',
        (accumulatedText) => {
          const partial = parsePartialInsightReport(accumulatedText);
          setReport(partial);
        },
        user?.id
      );

      setStatus('completed');
      setRefreshKey((prev) => prev + 1);
    } catch (err: unknown) {
      console.error('Error during market analysis execution:', err);
      const message = err instanceof Error ? err.message : 'Đã có lỗi xảy ra khi gọi hệ thống backend.';
      setErrorMessage(message);
      setStatus('error');
      setRefreshKey((prev) => prev + 1);
    }
  };

  return (
    <div className="min-h-screen flex bg-white dark:bg-slate-950 text-slate-800 dark:text-slate-100 bg-grid-pattern relative selection:bg-indigo-500 selection:text-white transition-colors duration-200">
      {/* Glow Effects */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-96 bg-gradient-to-b from-indigo-500/10 via-indigo-500/5 to-transparent blur-3xl pointer-events-none -z-10" />

      {/* ChatGPT-style Collapsible Sidebar */}
      <Sidebar
        currentSessionId={currentSessionId}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        onOpenAuth={() => setIsAuthOpen(true)}
        onSignOut={handleNewSession}
        user={user}
        refreshKey={refreshKey}
      />

      {/* Auth Modal */}
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onSuccess={(u) => setUser(u)}
      />

      {/* Right Content Area */}
      <div className="flex-1 flex flex-col pl-16 md:pl-72 transition-all duration-300">
        {/* Header */}
        <Header />

        {/* Main Content Container */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
          {/* Hero Banner */}
          <section className="text-center space-y-4 pt-4 pb-2">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-50 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 text-indigo-600 dark:text-indigo-400 text-xs font-semibold shadow-xs">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Nền Tảng Phân Tích & Nghiên Cứu Thị Trường Doanh Nghiệp</span>
            </div>

            <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight max-w-3xl mx-auto leading-tight text-slate-900 dark:text-slate-100">
              Nền Tảng Phân Tích Thị Trường & Xây Dựng Chiến Lược Kinh Doanh
            </h2>

            <p className="text-slate-600 dark:text-slate-400 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed">
              Nhập sản phẩm hoặc ngách kinh doanh để nhận báo cáo chiến lược toàn diện bao gồm: Thị trường ngách, Chiến lược giá tối ưu, Đánh giá rủi ro và Bộ từ khóa SEO.
            </p>
          </section>

          {/* Search Input Box */}
          <section>
            <SearchInput onSearch={handleSearch} isLoading={status === 'routing' || status === 'analyzing' || status === 'waking'} />
          </section>

          {/* Server Hibernation / Wakeup Notice */}
          {wakeupNoticeState && (
            <section className="animate-in fade-in slide-in-from-top-2 duration-300">
              <ServerWakeupNotice state={wakeupNoticeState} />
            </section>
          )}

          {/* Progress Stepper */}
          <section>
            <AnalysisProgress status={status} currentStep={currentStep} />
          </section>

          {/* Error State display */}
          {status === 'error' && (
            <div className="w-full max-w-4xl mx-auto bg-rose-50 dark:bg-rose-950/20 border border-rose-200 dark:border-rose-500/30 rounded-2xl p-6 text-slate-800 dark:text-slate-200 flex items-start space-x-3 shadow-md">
              <AlertCircle className="w-6 h-6 text-rose-500 dark:text-rose-400 shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-rose-700 dark:text-rose-300">Lỗi kết nối hoặc xử lý dữ liệu</h4>
                <p className="text-xs text-slate-700 dark:text-slate-300">{errorMessage}</p>
                <p className="text-[11px] text-slate-500 dark:text-slate-400 pt-1">
                  Vui lòng kiểm tra lại kết nối mạng hoặc thử lại sau ít phút.
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
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-3">
                <div className="flex items-center space-x-2">
                  <BarChart3 className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
                    Báo Cáo Phân Tích Chiến Lược: <span className="text-indigo-600 dark:text-indigo-400">{activeTopic}</span>
                  </h3>
                </div>
                {status === 'analyzing' && (
                  <div className="flex items-center space-x-2 text-xs text-indigo-600 dark:text-indigo-400 font-mono animate-pulse">
                    <span className="w-2 h-2 rounded-full bg-indigo-600 dark:bg-indigo-400"></span>
                    <span>Đang xây dựng báo cáo trực tiếp...</span>
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
              <div className="bg-slate-50 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-5 space-y-2 hover:border-indigo-300 dark:hover:border-slate-700 transition-all shadow-xs">
                <div className="w-8 h-8 rounded-lg bg-indigo-100 dark:bg-indigo-500/10 border border-indigo-200 dark:border-indigo-500/20 flex items-center justify-center text-indigo-600 dark:text-indigo-400 font-bold text-sm">
                  01
                </div>
                <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">Phân tích Ngách & Thị trường</h4>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  Xác định khoảng trống thị trường, cơ hội cạnh tranh và mô tả chi tiết tệp khách hàng mục tiêu.
                </p>
              </div>

              <div className="bg-slate-50 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-5 space-y-2 hover:border-indigo-300 dark:hover:border-slate-700 transition-all shadow-xs">
                <div className="w-8 h-8 rounded-lg bg-orange-100 dark:bg-orange-500/10 border border-orange-200 dark:border-orange-500/20 flex items-center justify-center text-orange-600 dark:text-orange-400 font-bold text-sm">
                  02
                </div>
                <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">Định giá & Hạn chế Rủi ro</h4>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  Đề xuất khoảng giá kinh doanh tối ưu kèm đánh giá các rủi ro vận hành, tài chính & đối thủ.
                </p>
              </div>

              <div className="bg-slate-50 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-800/80 rounded-2xl p-5 space-y-2 hover:border-indigo-300 dark:hover:border-slate-700 transition-all shadow-xs">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 flex items-center justify-center text-emerald-600 dark:text-emerald-400 font-bold text-sm">
                  03
                </div>
                <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200">Tối ưu hóa Thương mại & SEO</h4>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  Cung cấp bộ từ khóa tìm kiếm hàng đầu và gợi ý nội dung marketing hiệu quả cao.
                </p>
              </div>
            </section>
          )}
        </main>

        {/* Footer */}
        <footer className="w-full border-t border-slate-200 dark:border-slate-800/80 bg-slate-50 dark:bg-slate-950/80 py-6 mt-12 transition-colors">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
            <p>© 2026 AMA Market Intelligence Platform. All rights reserved.</p>
            <div className="flex items-center space-x-4">
              <span className="hover:text-slate-700 dark:hover:text-slate-400 cursor-pointer">Báo cáo Phân tích Kinh doanh</span>
              <span>•</span>
              <span className="hover:text-slate-700 dark:hover:text-slate-400 cursor-pointer">Bảo mật Enterprise</span>
              <span>•</span>
              <span className="hover:text-slate-700 dark:hover:text-slate-400 cursor-pointer">Dữ liệu Thời gian thực</span>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
