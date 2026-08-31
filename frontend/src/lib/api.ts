import type { ReviewDetail, ReviewSummary, Stats } from "./types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      /* keep statusText */
    }
    throw new Error(detail);
  }
  return response.json() as Promise<T>;
}

export function listReviews() {
  return request<ReviewSummary[]>("/reviews");
}

export function getReview(id: string) {
  return request<ReviewDetail>(`/reviews/${id}`);
}

export function getStats() {
  return request<Stats>("/reviews/stats");
}

export function createReview(payload: {
  pr_url?: string;
  diff?: string;
  title?: string;
  heuristics_only?: boolean;
}) {
  return request<ReviewSummary>("/reviews", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
