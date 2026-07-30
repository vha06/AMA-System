'use client';

import React, { useState } from 'react';
import { Download, FileText, Check, Share2 } from 'lucide-react';
import { InsightReport } from '../types/market';

interface ReportToolbarProps {
  report: Partial<InsightReport>;
  topic: string;
}

export const ReportToolbar: React.FC<ReportToolbarProps> = ({ report, topic }) => {
  const [copiedMarkdown, setCopiedMarkdown] = useState(false);

  const generateMarkdownReport = () => {
    return `# Báo Cáo Phân Tích Chiến Lược Thị Trường: ${topic}

## 1. Phân Tích Ngách Thị Trường
${report.niche_analysis || 'Chưa có thông tin'}

## 2. Chiến Lược Định Giá
- **Mức giá đề xuất:** ${report.pricing?.suggested_price || 'N/A'}
- **Cơ sở định giá:** ${report.pricing?.rationale || 'N/A'}

## 3. Rủi Ro & Thách Thức
${report.risks?.map((r, i) => `${i + 1}. ${r}`).join('\n') || 'Chưa có thông tin'}

## 4. Từ Khóa SEO & Quảng Cáo
${report.seo_keywords?.map((k) => `- ${k}`).join('\n') || 'Chưa có thông tin'}

## 5. Câu Lệnh AI Đề Xuất (Prompts)
${report.ai_prompts?.map((p, i) => `### Prompt ${i + 1}:\n\`\`\`\n${p}\n\`\`\``).join('\n\n') || 'Chưa có thông tin'}

---
*Xuất từ AMA-System - Automated Market Analysis System*
`;
  };

  const handleCopyMarkdown = () => {
    const md = generateMarkdownReport();
    navigator.clipboard.writeText(md);
    setCopiedMarkdown(true);
    setTimeout(() => setCopiedMarkdown(false), 2000);
  };

  const handleDownloadJson = () => {
    const jsonStr = JSON.stringify({ topic, report }, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `AMA_Report_${topic.replace(/\s+/g, '_')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-slate-900/80 border border-slate-800 rounded-2xl p-4 backdrop-blur-xl flex flex-wrap items-center justify-between gap-4 shadow-xl">
      <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
        <Share2 className="w-4 h-4 text-emerald-400" />
        <span>Xuất dữ liệu báo cáo phân tích</span>
      </div>

      <div className="flex items-center space-x-3">
        <button
          onClick={handleCopyMarkdown}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 hover:text-white text-xs font-medium transition-colors cursor-pointer"
        >
          {copiedMarkdown ? (
            <>
              <Check className="w-4 h-4 text-emerald-400" />
              <span className="text-emerald-400">Đã chép Markdown!</span>
            </>
          ) : (
            <>
              <FileText className="w-4 h-4" />
              <span>Sao chép Markdown</span>
            </>
          )}
        </button>

        <button
          onClick={handleDownloadJson}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 text-xs font-semibold shadow-md shadow-emerald-500/20 transition-all cursor-pointer"
        >
          <Download className="w-4 h-4" />
          <span>Tải xuống JSON</span>
        </button>
      </div>
    </div>
  );
};
