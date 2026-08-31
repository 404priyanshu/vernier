import Link from "next/link";
import { redirect } from "next/navigation";
import { getStats, listReviews } from "@/lib/api";
import { formatWhen, prLabel } from "@/lib/format";
import { StatusPill } from "@/components/bench/status-pill";
import type { ReviewSummary, Stats } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function BenchPage({
  searchParams,
}: {
  searchParams: Promise<{ sample?: string }>;
}) {
  const params = await searchParams;
  let reviews: ReviewSummary[] = [];
  let stats: Stats | null = null;
  let loadError: string | null = null;
  try {
    [reviews, stats] = await Promise.all([listReviews(), getStats()]);
  } catch (error) {
    loadError = error instanceof Error ? error.message : "API unreachable";
  }

  if (params.sample === "1" && reviews.length) {
    const sample = reviews.find((item) => item.status === "completed") || reviews[0];
    redirect(`/bench/${sample.id}`);
  }

  return (
    <div className="mx-auto max-w-[1120px] px-4 py-10">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-[-0.03em]">Bench</h1>
          <p className="mt-2 max-w-[50ch] text-[15px] text-muted">
            Every scan lands here. Open one to read findings, fixes, and test stubs.
          </p>
        </div>
        <Link href="/bench/scan" className="bg-primary px-4 py-2.5 text-[14px] text-white">
          Scan a pull request
        </Link>
      </div>
      {stats ? (
        <dl className="mt-8 grid grid-cols-2 gap-4 border-y border-rule py-5 text-[14px] sm:grid-cols-4">
          <div>
            <dt className="text-muted">Reviews</dt>
            <dd className="font-mono text-lg">{stats.reviews}</dd>
          </div>
          <div>
            <dt className="text-muted">Findings</dt>
            <dd className="font-mono text-lg">{stats.findings}</dd>
          </div>
          <div>
            <dt className="text-muted">Cache hits</dt>
            <dd className="font-mono text-lg">{stats.cache_hits}</dd>
          </div>
          <div>
            <dt className="text-muted">Model</dt>
            <dd className="font-mono text-lg">{stats.llm_configured ? stats.model : "heuristics"}</dd>
          </div>
        </dl>
      ) : null}
      {loadError ? (
        <p role="alert" className="mt-8 border border-accent px-4 py-3 text-[14px] text-accent">
          Could not reach the API at {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}. Start FastAPI, then
          refresh. {loadError}
        </p>
      ) : null}
      {!loadError && reviews.length === 0 ? (
        <div className="mt-12 max-w-[42ch]">
          <h2 className="text-xl font-semibold">No reviews yet</h2>
          <p className="mt-2 text-[15px] text-muted">
            Scan a public GitHub pull request or paste a unified diff. A sample review is seeded when the API boots with
            an empty database.
          </p>
        </div>
      ) : null}
      {reviews.length > 0 ? (
        <ul className="mt-6 divide-y divide-rule border-y border-rule">
          {reviews.map((review) => (
            <li key={review.id}>
              <Link href={`/bench/${review.id}`} className="grid gap-2 py-4 md:grid-cols-[7rem_minmax(0,1fr)_10rem] md:items-baseline">
                <StatusPill status={review.status} />
                <span>
                  <span className="block text-[16px] font-medium text-ink">{review.title}</span>
                  <span className="mt-1 block font-mono text-[12px] text-muted">
                    {prLabel(review.repo, review.pr_number)} / {review.finding_count} findings
                  </span>
                </span>
                <span className="text-[13px] text-muted md:text-right">{formatWhen(review.created_at)}</span>
              </Link>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}
