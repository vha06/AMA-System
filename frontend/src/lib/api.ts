import { RouterDecision } from '../types/market';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  '';

async function handleResponseError(response: Response, defaultMsg: string): Promise<never> {
  let detailMessage = defaultMsg;
  try {
    const text = await response.text();
    try {
      const json = JSON.parse(text);
      detailMessage = json.detail || json.message || `${defaultMsg} (${response.status})`;
    } catch {
      if (response.status === 502 || response.status === 504) {
        detailMessage = `Máy chủ Backend (Render) đang khởi động lại từ trạng thái ngủ đông. Vui lòng thử lại sau 30 giây! (${response.status})`;
      } else {
        detailMessage = `${defaultMsg} (${response.status}: ${text.slice(0, 150)})`;
      }
    }
  } catch {
    detailMessage = `${defaultMsg} (${response.status})`;
  }
  throw new Error(detailMessage);
}

export async function analyzeRouterQuery(query: string): Promise<RouterDecision> {
  const response = await fetch(`${API_BASE_URL}/api/v1/router/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    await handleResponseError(response, 'Lỗi kết nối máy chủ phân tích');
  }

  const raw = await response.json();
  const isInvalid = raw.intent === 'OUT_OF_SCOPE' || raw.intent === 'INVALID';

  return {
    intent: isInvalid ? 'INVALID' : 'VALID',
    reasoning: raw.reasoning || (isInvalid ? 'Truy vấn không thuộc phạm vi phân tích thị trường.' : ''),
    topic: raw.niche_or_topic || raw.topic || query,
    suggested_action: raw.clarification_needed || raw.suggested_action || '',
  };
}

export async function streamInsightReport(
  topic: string,
  contextData: string = '',
  onChunk: (accumulatedText: string) => void,
  userId?: string
): Promise<string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (userId) {
    headers['x-user-id'] = userId;
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/insight/stream`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ topic, context_data: contextData, user_id: userId }),
  });

  if (!response.ok) {
    await handleResponseError(response, 'Lỗi kết nối tạo báo cáo');
  }

  if (!response.body) {
    throw new Error('Không thể khởi tạo luồng dữ liệu (response body null).');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let fullAccumulatedText = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunkStr = decoder.decode(value, { stream: true });
    fullAccumulatedText += chunkStr;
    onChunk(fullAccumulatedText);
  }

  return fullAccumulatedText;
}

export async function streamCrewAnalysis(
  query: string,
  onEvent: (event: any) => void,
  userId?: string
): Promise<void> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (userId) {
    headers['x-user-id'] = userId;
  }

  const response = await fetch(`${API_BASE_URL}/api/v1/crew/stream`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ query, user_id: userId }),
  });

  if (!response.ok) {
    await handleResponseError(response, 'Lỗi kết nối luồng đa tác tử CrewAI');
  }

  if (!response.body) return;

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = decoder.decode(value, { stream: true });
    const lines = text.split('\n');
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const jsonStr = line.replace('data: ', '').trim();
          if (jsonStr) {
            const data = JSON.parse(jsonStr);
            onEvent(data);
          }
        } catch {
          // Skip partial json parse errors
        }
      }
    }
  }
}

export async function checkBackendHealth(timeoutMs = 4000): Promise<boolean> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const healthUrl = `${API_BASE_URL}/api/v1/health`;
    const response = await fetch(healthUrl, {
      method: 'GET',
      headers: { 'Cache-Control': 'no-cache' },
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    if (response.ok) return true;

    // Fallback to /health endpoint
    const fallbackResponse = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: { 'Cache-Control': 'no-cache' },
    });
    return fallbackResponse.ok;
  } catch {
    clearTimeout(timeoutId);
    return false;
  }
}
