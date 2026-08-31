export type ReviewStatus = "queued" | "running" | "completed" | "failed";

export type Finding = {
  id: string;
  category: "security" | "bug" | "performance" | string;
  severity: "critical" | "high" | "medium" | "low" | "info" | string;
  title: string;
  description: string;
  file_path: string;
  start_line: number | null;
  end_line: number | null;
  snippet: string | null;
  confidence: number;
  source: string;
  detector_id: string | null;
  fix_suggestion: string | null;
  test_stub: string | null;
  cached: boolean;
};

export type ReviewSummary = {
  id: string;
  source: string;
  status: ReviewStatus;
  repo: string | null;
  pr_number: number | null;
  pr_url: string | null;
  title: string;
  author: string | null;
  summary: string | null;
  error: string | null;
  model: string | null;
  prompt_version: string;
  cache_hits: number;
  cache_misses: number;
  batch_count: number;
  hunk_count: number;
  file_count: number;
  finding_count: number;
  created_at: string;
  completed_at: string | null;
};

export type ReviewDetail = ReviewSummary & {
  findings: Finding[];
  head_sha: string | null;
  base_ref: string | null;
};

export type Stats = {
  reviews: number;
  completed: number;
  findings: number;
  cache_hits: number;
  cache_misses: number;
  llm_configured: boolean;
  model: string;
  prompt_version: string;
};
