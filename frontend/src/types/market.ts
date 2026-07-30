export type IntentType = 'VALID' | 'INVALID';

export interface RouterDecision {
  intent: IntentType;
  reasoning: string;
  topic: string;
  suggested_action: string;
}

export interface PricingStrategy {
  suggested_price: string;
  rationale: string;
}

export interface InsightReport {
  niche_analysis: string;
  pricing: PricingStrategy;
  risks: string[];
  seo_keywords: string[];
  ai_prompts: string[];
}

export type AnalysisStatus = 'idle' | 'routing' | 'analyzing' | 'completed' | 'error';
