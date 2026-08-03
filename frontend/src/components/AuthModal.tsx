'use client';

import React, { useState } from 'react';
import { User, Key, Envelope, X, GoogleLogo, ArrowRight, CircleNotch } from '@phosphor-icons/react';
import { createClient } from '@/lib/supabase/client';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (user: any) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const supabase = createClient();

  const handleEmailAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      if (isSignUp) {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
        setSuccessMsg('Đăng ký thành công! Vui lòng kiểm tra email để xác nhận (nếu có).');
        if (data.user && onSuccess) onSuccess(data.user);
      } else {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
        setSuccessMsg('Đăng nhập thành công!');
        if (data.user && onSuccess) onSuccess(data.user);
        setTimeout(() => onClose(), 600);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Đã xảy ra lỗi khi xác thực.');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleAuth = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      });
      if (error) throw error;
    } catch (err: any) {
      setErrorMsg(err.message || 'Đã xảy ra lỗi khi đăng nhập với Google.');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div
        className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden"
        role="dialog"
        aria-modal="true"
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 rounded-full transition-colors"
        >
          <X size={20} />
        </button>

        {/* Modal Header */}
        <div className="p-6 pb-4 border-b border-slate-800/60">
          <div className="flex items-center space-x-2 text-emerald-400 mb-1">
            <User size={24} weight="bold" />
            <span className="text-xs font-bold uppercase tracking-wider">Tài khoản</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100">
            {isSignUp ? 'Tạo tài khoản AMA-System' : 'Đăng nhập AMA-System'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Lưu trữ lịch sử các phiên phân tích thị trường & tra cứu lại mọi lúc.
          </p>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4">
          {errorMsg && (
            <div className="p-3 text-xs text-rose-400 bg-rose-950/40 border border-rose-800/50 rounded-lg">
              {errorMsg}
            </div>
          )}

          {successMsg && (
            <div className="p-3 text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/50 rounded-lg">
              {successMsg}
            </div>
          )}

          {/* Social Google Login Button */}
          <button
            type="button"
            onClick={handleGoogleAuth}
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 bg-slate-800 hover:bg-slate-750 text-slate-200 border border-slate-700 rounded-xl text-sm font-medium transition-all shadow-sm hover:border-slate-600 disabled:opacity-50"
          >
            <GoogleLogo size={20} weight="bold" className="text-rose-400" />
            <span>Tiếp tục với Google</span>
          </button>

          {/* Divider */}
          <div className="flex items-center my-4">
            <div className="flex-grow border-t border-slate-800"></div>
            <span className="px-3 text-[11px] text-slate-500 uppercase tracking-widest">hoặc Email</span>
            <div className="flex-grow border-t border-slate-800"></div>
          </div>

          {/* Email / Password Form */}
          <form onSubmit={handleEmailAuth} className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Email</label>
              <div className="relative">
                <Envelope size={18} className="absolute left-3 top-3 text-slate-500" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full pl-10 pr-4 py-2 bg-slate-950/80 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Mật khẩu</label>
              <div className="relative">
                <Key size={18} className="absolute left-3 top-3 text-slate-500" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-2 bg-slate-950/80 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 flex items-center justify-center space-x-2 py-2.5 px-4 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-semibold rounded-xl text-sm transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-50"
            >
              {loading ? (
                <CircleNotch size={20} className="animate-spin text-slate-950" />
              ) : (
                <>
                  <span>{isSignUp ? 'Tạo tài khoản' : 'Đăng nhập'}</span>
                  <ArrowRight size={16} weight="bold" />
                </>
              )}
            </button>
          </form>
        </div>

        {/* Modal Footer / Switch Mode */}
        <div className="p-4 bg-slate-950/60 border-t border-slate-800/60 text-center text-xs text-slate-400">
          {isSignUp ? (
            <span>
              Đã có tài khoản?{' '}
              <button
                type="button"
                onClick={() => setIsSignUp(false)}
                className="text-emerald-400 hover:underline font-medium"
              >
                Đăng nhập
              </button>
            </span>
          ) : (
            <span>
              Chưa có tài khoản?{' '}
              <button
                type="button"
                onClick={() => setIsSignUp(true)}
                className="text-emerald-400 hover:underline font-medium"
              >
                Đăng ký ngay
              </button>
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
