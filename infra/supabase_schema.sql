-- ==========================================
-- Supabase Schema for AMA-System (Session Logs)
-- ==========================================

-- Enable UUID extension if not enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create session_logs table
CREATE TABLE IF NOT EXISTS public.session_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    prompt TEXT NOT NULL,
    results JSONB NOT NULL DEFAULT '{}'::jsonb,
    status VARCHAR(50) NOT NULL DEFAULT 'success', -- 'success', 'error', 'in_progress'
    source_links JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast user_id lookups and chronological ordering
CREATE INDEX IF NOT EXISTS idx_session_logs_user_id ON public.session_logs(user_id, created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.session_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for authenticated users
CREATE POLICY "Users can view their own session logs"
    ON public.session_logs FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own session logs"
    ON public.session_logs FOR INSERT
    TO authenticated
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own session logs"
    ON public.session_logs FOR DELETE
    TO authenticated
    USING (auth.uid() = user_id);

-- Note: Backend calls using SUPABASE_SERVICE_KEY bypass RLS automatically.
