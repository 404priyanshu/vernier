import type { ReviewDetail, ReviewSummary, Stats } from "./types";

export function getApiUrl() {
  if (typeof window !== "undefined") {
    return "";
  }
  const internal = process.env.BACKEND_INTERNAL_URL?.replace(/\/$/, "");
  if (internal) return internal;
  const configured = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
  if (configured) return configured;
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`;
  return "http://localhost:8000";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiUrl()}${path}`, {
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
  return request<ReviewSummary[]>("/api/reviews");
}

export function getReview(id: string) {
  return request<ReviewDetail>(`/api/reviews/${id}`);
}

export function getStats() {
  return request<Stats>("/api/reviews/stats");
}

export function createReview(payload: {
  pr_url?: string;
  diff?: string;
  title?: string;
  heuristics_only?: boolean;
}) {
  return request<ReviewSummary>("/api/reviews", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
