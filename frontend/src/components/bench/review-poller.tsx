"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getReview } from "@/lib/api";
import type { ReviewDetail } from "@/lib/types";
import { FindingPanel } from "./finding-panel";
import { StatusPill } from "./status-pill";
import { prLabel, formatWhen } from "@/lib/format";

export function ReviewPoller({ initial }: { initial: ReviewDetail }) {
  const [review, setReview] = useState(initial);

  useEffect(() => {
    if (review.status === "completed" || review.status === "failed") return;
    const timer = window.setInterval(async () => {
      try {
        const next = await getReview(review.id);
        setReview(next);
      } catch {
        /* keep last good snapshot */
      }
    }, 1500);
    return () => window.clearInterval(timer);
  }, [review.id, review.status]);

  const cacheTotal = review.cache_hits + review.cache_misses;

  return (
    <article>
      <header className="mb-8">
        <nav className="breadcrumb" aria-label="Breadcrumb"><Link href="/bench">Bench</Link><span>/</span><span>Review</span></nav>
        <div className="flex flex-wrap items-center gap-3">
          <StatusPill status={review.status} />
          <p className="font-mono text-[13px] text-muted">{prLabel(review.repo, review.pr_number)}</p>
        </div>
        <h1 className="app-title mt-4">{review.title}</h1>
        <p className="mt-2 max-w-[65ch] text-[15px] text-muted">
          {review.summary || (review.status === "failed" ? review.error : "Pipeline is still running.")}
        </p>
        <dl className="review-metadata grid gap-4 text-[13px] sm:grid-cols-4">
          <div>
            <dt className="text-muted">Author</dt>
            <dd>{review.author || "unknown"}</dd>
          </div>
          <div>
            <dt className="text-muted">Started</dt>
            <dd>{formatWhen(review.created_at)}</dd>
          </div>
          <div>
            <dt className="text-muted">Cache</dt>
            <dd>
              {review.cache_hits} hit / {review.cache_misses} miss
              {cacheTotal ? ` / ${review.batch_count} batches` : ""}
            </dd>
          </div>
          <div>
            <dt className="text-muted">Model</dt>
            <dd className="font-mono">
              {review.model || "heuristics"} / {review.prompt_version}
            </dd>
          </div>
        </dl>
      </header>
      {review.status === "failed" ? (
        <p role="alert" className="border border-accent px-4 py-3 text-[14px] text-accent">
          {review.error}
        </p>
      ) : null}
      {review.status === "queued" || review.status === "running" ? (
        <div className="space-y-3" aria-busy="true" aria-live="polite">
          <div className="h-12 bg-surface" />
          <div className="h-12 bg-surface" />
          <div className="h-12 bg-surface" />
          <p className="text-[13px] text-muted">Reading the diff, batching hunks, checking Redis.</p>
        </div>
      ) : (
        <FindingPanel
          findings={review.findings}
          repoLabel={review.pr_url ? prLabel(review.repo, review.pr_number) : "Pasted diff"}
        />
      )}
    </article>
  );
}
