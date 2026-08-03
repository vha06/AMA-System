'use client';

import React, { useState, useEffect } from 'react';
import {
  SidebarSimple,
  Plus,
  Clock,
  CheckCircle,
  XCircle,
  CircleNotch,
  User,
  SignOut,
  CaretLeft,
  CaretRight,
  Sparkle
} from '@phosphor-icons/react';
import { createClient } from '@/lib/supabase/client';

export interface SessionLogItem {
  id: string;
  user_id: string;
  prompt: string;
  results: any;
  status: 'success' | 'error' | 'in_progress';
  source_links?: any[];
  created_at: string;
}

interface SidebarProps {
  currentSessionId?: string | null;
  onSelectSession: (session: SessionLogItem) => void;
  onNewSession: () => void;
  onOpenAuth: () => void;
  onSignOut?: () => void;
  user: any | null;
  refreshKey?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentSessionId,
  onSelectSession,
  onNewSession,
  onOpenAuth,
  onSignOut,
  user,
  refreshKey = 0,
}) => {
  const [isOpen, setIsOpen] = useState(true);
  const [sessions, setSessions] = useState<SessionLogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const supabase = createClient();

  useEffect(() => {
    fetchSessions();
  }, [user, refreshKey]);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const targetUserId = user?.id || 'anonymous';

      if (user) {
        const { data, error } = await supabase
          .from('session_logs')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(50);

        if (!error && data && data.length > 0) {
          setSessions(data as SessionLogItem[]);
          setLoading(false);
          return;
        }
      }

      const res = await fetch(`http://localhost:8000/api/v1/crew/sessions?user_id=${targetUserId}`);
      if (res.ok) {
        const body = await res.json();
        setSessions(body.sessions || []);
      }
    } catch (e) {
      console.warn('Could not fetch sessions:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    setSessions([]);
    if (onSignOut) {
      onSignOut();
    }
  };

  return (
    <>
      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 left-0 bottom-0 z-40 bg-slate-950/95 border-r border-slate-800/80 backdrop-blur-xl transition-all duration-300 flex flex-col ${
          isOpen ? 'w-72' : 'w-16'
        }`}
      >
        {/* Toggle Button Header */}
        <div className="h-16 px-4 flex items-center justify-between border-b border-slate-800/60">
          {isOpen && (
            <div className="flex items-center space-x-2 text-slate-200 font-bold text-sm">
              <Sparkle size={20} weight="fill" className="text-emerald-400" />
              <span>Phiên phân tích</span>
            </div>
          )}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-900 rounded-lg transition-colors ml-auto"
            title={isOpen ? 'Thu gọn thanh bên' : 'Mở rộng thanh bên'}
          >
            {isOpen ? <CaretLeft size={18} /> : <CaretRight size={18} />}
          </button>
        </div>

        {/* Action: New Analysis */}
        <div className="p-3">
          <button
            onClick={onNewSession}
            className={`w-full flex items-center justify-center space-x-2 py-2.5 px-3 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 hover:from-emerald-500/30 hover:to-teal-500/30 text-emerald-400 border border-emerald-500/30 rounded-xl text-xs font-semibold transition-all shadow-sm ${
              !isOpen && 'px-0'
            }`}
          >
            <Plus size={18} weight="bold" />
            {isOpen && <span>Tạo phân tích mới</span>}
          </button>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1 custom-scrollbar">
          {loading ? (
            <div className="flex justify-center p-4 text-slate-500">
              <CircleNotch size={20} className="animate-spin" />
            </div>
          ) : !user ? (
            isOpen && (
              <div className="p-4 text-center text-xs text-slate-400 space-y-2">
                <p>Đăng nhập để xem lịch sử phiên làm việc của bạn.</p>
                <button
                  onClick={onOpenAuth}
                  className="px-3 py-1.5 bg-emerald-500/20 text-emerald-400 rounded-lg border border-emerald-500/30 hover:bg-emerald-500/30 transition-colors text-xs font-medium"
                >
                  Đăng nhập ngay
                </button>
              </div>
            )
          ) : sessions.length === 0 ? (
            isOpen && (
              <div className="p-4 text-center text-xs text-slate-500">
                <Clock size={24} className="mx-auto mb-2 opacity-40" />
                <p>Chưa có lịch sử phân tích nào.</p>
              </div>
            )
          ) : (
            sessions.map((item) => {
              const isSelected = item.id === currentSessionId;
              return (
                <button
                  key={item.id}
                  onClick={() => onSelectSession(item)}
                  className={`w-full flex items-center space-x-2.5 p-2.5 rounded-xl text-left text-xs transition-colors ${
                    isSelected
                      ? 'bg-slate-800 text-slate-100 font-medium border border-slate-700'
                      : 'text-slate-400 hover:bg-slate-900/80 hover:text-slate-200'
                  }`}
                  title={item.prompt}
                >
                  {/* Status Indicator Icon */}
                  {item.status === 'success' ? (
                    <CheckCircle size={16} weight="fill" className="text-emerald-400 shrink-0" />
                  ) : item.status === 'error' ? (
                    <XCircle size={16} weight="fill" className="text-rose-400 shrink-0" />
                  ) : (
                    <CircleNotch size={16} className="text-amber-400 animate-spin shrink-0" />
                  )}

                  {isOpen && (
                    <div className="flex-1 min-w-0">
                      <p className="truncate text-slate-200">{item.prompt}</p>
                      <p className="text-[10px] text-slate-500">
                        {new Date(item.created_at).toLocaleDateString('vi-VN', {
                          day: '2-digit',
                          month: '2-digit',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </p>
                    </div>
                  )}
                </button>
              );
            })
          )}
        </div>

        {/* User Footer Section */}
        <div className="p-3 border-t border-slate-800/60 bg-slate-950/80">
          {user ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 min-w-0">
                <div className="w-8 h-8 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 font-bold text-xs shrink-0">
                  {user.email?.[0]?.toUpperCase() || 'U'}
                </div>
                {isOpen && (
                  <div className="min-w-0">
                    <p className="text-xs font-medium text-slate-200 truncate">{user.email}</p>
                    <p className="text-[10px] text-emerald-400">Đã đăng nhập</p>
                  </div>
                )}
              </div>
              {isOpen && (
                <button
                  onClick={handleSignOut}
                  className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-900 rounded-lg transition-colors"
                  title="Đăng xuất"
                >
                  <SignOut size={16} />
                </button>
              )}
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className={`w-full flex items-center justify-center space-x-2 py-2 px-3 bg-slate-900 hover:bg-slate-850 text-slate-300 border border-slate-800 rounded-xl text-xs transition-colors ${
                !isOpen && 'px-0'
              }`}
            >
              <User size={16} />
              {isOpen && <span>Tài khoản</span>}
            </button>
          )}
        </div>
      </aside>
    </>
  );
};
