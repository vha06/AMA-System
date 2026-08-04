import { InsightReport } from '../types/market';

/**
 * Safely parses raw streamed text chunk from Gemini API which might be incomplete JSON.
 * Returns a partial InsightReport so UI components can render incrementally without crashing.
 */
export function parsePartialInsightReport(rawText: string): Partial<InsightReport> {
  if (!rawText || typeof rawText !== 'string') {
    return {};
  }

  const cleaned = rawText.trim();
  if (!cleaned) return {};

  // First try direct standard JSON parse
  try {
    const parsed = JSON.parse(cleaned);
    if (typeof parsed === 'object' && parsed !== null) {
      return sanitizeReportObject(parsed);
    }
  } catch {
    // If incomplete, continue to robust repair/regex extraction below
  }

  // Attempt to fix incomplete JSON by auto-closing brackets & quotes
  const repaired = autoRepairJson(cleaned);
  if (repaired) {
    try {
      const parsed = JSON.parse(repaired);
      if (typeof parsed === 'object' && parsed !== null) {
        return sanitizeReportObject(parsed);
      }
    } catch {
      // Fallback to regex field extraction below
    }
  }

  // Regex fallback for extracting fields as they arrive in stream
  const partial: Partial<InsightReport> = {};

  // Extract niche_analysis
  const nicheMatch = cleaned.match(/"niche_analysis"\s*:\s*"((?:[^"\\]|\\.)*)/);
  if (nicheMatch && nicheMatch[1]) {
    partial.niche_analysis = unescapeJsonString(nicheMatch[1]);
  }

  // Extract pricing
  const suggestedPriceMatch = cleaned.match(/"suggested_price"\s*:\s*"((?:[^"\\]|\\.)*)/);
  const rationaleMatch = cleaned.match(/"rationale"\s*:\s*"((?:[^"\\]|\\.)*)/);
  if (suggestedPriceMatch || rationaleMatch) {
    partial.pricing = {
      suggested_price: suggestedPriceMatch ? unescapeJsonString(suggestedPriceMatch[1]) : '',
      rationale: rationaleMatch ? unescapeJsonString(rationaleMatch[1]) : '',
    };
  }

  // Extract risks array
  const risksMatch = cleaned.match(/"risks"\s*:\s*\[([\s\S]*?)(?:\]|$)/);
  if (risksMatch && risksMatch[1]) {
    partial.risks = extractStringArrayFromPartialJson(risksMatch[1]);
  }

  // Extract seo_keywords array
  const seoMatch = cleaned.match(/"seo_keywords"\s*:\s*\[([\s\S]*?)(?:\]|$)/);
  if (seoMatch && seoMatch[1]) {
    partial.seo_keywords = extractStringArrayFromPartialJson(seoMatch[1]);
  }

  // Extract ai_prompts array
  const promptsMatch = cleaned.match(/"ai_prompts"\s*:\s*\[([\s\S]*?)(?:\]|$)/);
  if (promptsMatch && promptsMatch[1]) {
    partial.ai_prompts = extractStringArrayFromPartialJson(promptsMatch[1]);
  }

  return partial;
}

function sanitizeReportObject(obj: Record<string, unknown>): Partial<InsightReport> {
  const result: Partial<InsightReport> = {};

  if (typeof obj.niche_analysis === 'string') {
    result.niche_analysis = obj.niche_analysis;
  }

  if (typeof obj.pricing === 'object' && obj.pricing !== null) {
    const p = obj.pricing as Record<string, unknown>;
    result.pricing = {
      suggested_price: typeof p.suggested_price === 'string' ? p.suggested_price : '',
      rationale: typeof p.rationale === 'string' ? p.rationale : '',
    };
  }

  if (Array.isArray(obj.risks)) {
    result.risks = obj.risks.filter((r): r is string => typeof r === 'string');
  }

  if (Array.isArray(obj.seo_keywords)) {
    result.seo_keywords = obj.seo_keywords.filter((k): k is string => typeof k === 'string');
  }

  if (Array.isArray(obj.ai_prompts)) {
    result.ai_prompts = obj.ai_prompts.filter((p): p is string => typeof p === 'string');
  }

  return result;
}

function extractStringArrayFromPartialJson(arrayContent: string): string[] {
  const items: string[] = [];
  const regex = /"((?:[^"\\]|\\.)*)"/g;
  let match;
  while ((match = regex.exec(arrayContent)) !== null) {
    if (match[1]) {
      items.push(unescapeJsonString(match[1]));
    }
  }
  return items;
}

function unescapeJsonString(str: string): string {
  try {
    return JSON.parse(`"${str}"`);
  } catch {
    return str.replace(/\\"/g, '"').replace(/\\\\/g, '\\').replace(/\\n/g, '\n');
  }
}

function autoRepairJson(jsonStr: string): string | null {
  let str = jsonStr.trim();
  if (!str.startsWith('{')) return null;

  // Balance quotes
  let inString = false;
  let escaped = false;
  for (let i = 0; i < str.length; i++) {
    const char = str[i];
    if (char === '\\' && !escaped) {
      escaped = true;
    } else {
      if (char === '"' && !escaped) {
        inString = !inString;
      }
      escaped = false;
    }
  }

  if (inString) {
    str += '"';
  }

  // Remove trailing comma if present
  str = str.replace(/,\s*$/, '');

  // Balance brackets
  let openBrackets = 0;
  let openBraces = 0;
  inString = false;
  escaped = false;

  for (let i = 0; i < str.length; i++) {
    const char = str[i];
    if (char === '\\' && !escaped) {
      escaped = true;
    } else {
      if (char === '"' && !escaped) {
        inString = !inString;
      } else if (!inString) {
        if (char === '{') openBraces++;
        if (char === '}') openBraces--;
        if (char === '[') openBrackets++;
        if (char === ']') openBrackets--;
      }
      escaped = false;
    }
  }

  while (openBrackets > 0) {
    str += ']';
    openBrackets--;
  }
  while (openBraces > 0) {
    str += '}';
    openBraces--;
  }

  return str;
}
