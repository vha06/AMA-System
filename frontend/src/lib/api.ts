import { RouterDecision } from '../types/market';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export async function analyzeRouterQuery(query: string): Promise<RouterDecision> {
  const response = await fetch(`${API_BASE_URL}/api/v1/router/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network request failed' }));
    throw new Error(errorData.detail || `Server error (${response.status})`);
  }

  return response.json();
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
    const errorData = await response.json().catch(() => ({ detail: 'Stream request failed' }));
    throw new Error(errorData.detail || `Stream server error (${response.status})`);
  }

  if (!response.body) {
    throw new Error('Response body is null, stream cannot be established.');
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
    const errorData = await response.json().catch(() => ({ detail: 'Crew stream failed' }));
    throw new Error(errorData.detail || `Crew stream error (${response.status})`);
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

