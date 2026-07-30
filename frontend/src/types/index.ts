// Export all TypeScript types for the AMA-System Frontend

export interface MarketAnalysisRequest {
  prompt: string;
}

export interface NicheRecommendation {
  topic: string;
  competitionIndex: number;
  searchVolumeGrowth: number;
}

export interface MarketAnalysisResponse {
  recommendations: NicheRecommendation[];
  riskWarnings: string[];
  optimalPricing: { min: number; max: number; recommended: number };
  aiPrompts: string[];
  seoKeywords: string[];
}
