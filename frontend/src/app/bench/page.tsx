import Link from "next/link";
import { redirect } from "next/navigation";
import { ArrowRight, GitPullRequest, Plugs } from "@phosphor-icons/react/dist/ssr";
import { getStats, listReviews } from "@/lib/api";
import { formatWhen, prLabel } from "@/lib/format";
import { StatusPill } from "@/components/bench/status-pill";
import { RetryButton } from "@/components/bench/retry-button";
import type { ReviewSummary, Stats } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function BenchPage({ searchParams }: { searchParams: Promise<{ sample?: string }> }) {
  const params = await searchParams;
  if (params.sample === "1") redirect("/bench/sample");
  let reviews: ReviewSummary[] = [];
  let stats: Stats | null = null;
  let loadError = false;
  try {
    [reviews, stats] = await Promise.all([listReviews(), getStats()]);
  } catch {
    loadError = true;
  }
  return (
    <div className="page-container app-page">
      <div className="page-heading">
        <div><h1 className="app-title">Your review bench.</h1>
          <p className="page-description">Every diff, measured. Your findings, fixes, and test stubs in one place.</p></div>
        <Link href="/bench/scan" className="button button-primary">Scan a pull request <ArrowRight size={17} /></Link>
      </div>
      {stats && <dl className="stats-strip">
        <div><dt>Reviews</dt><dd>{stats.reviews}</dd></div>
        <div><dt>Findings</dt><dd>{stats.findings}</dd></div>
        <div><dt>Cache hits</dt><dd>{stats.cache_hits}</dd></div>
        <div><dt>Analysis engine</dt><dd className="model-value">{stats.llm_configured ? stats.model : "Heuristics"}</dd></div>
      </dl>}
      {loadError ? (
        <div className="empty-state" role="status"><Plugs size={35} weight="light" /><h2>The review service is offline.</h2>
          <p>Your bench will be available when the API reconnects. You can still explore a complete sample review.</p>
          <div className="empty-actions"><Link href="/bench/sample" className="button button-primary">Explore a sample <ArrowRight size={17} /></Link><RetryButton /></div>
        </div>
      ) : reviews.length === 0 ? (
        <div className="empty-state"><GitPullRequest size={35} weight="light" /><h2>A clean slate. A closer look.</h2>
          <p>Your reviews will appear here. Start with a GitHub pull request or paste a unified diff.</p>
          <div className="empty-actions"><Link href="/bench/scan" className="button button-primary">Start your first review</Link><Link href="/bench/sample" className="button button-secondary">Explore a sample</Link></div>
        </div>
      ) : (
        <><div className="bench-section-label"><span>Recent reviews</span><span>{reviews.length} total</span></div>
          <ul className="review-list">{reviews.map((review) => (
            <li key={review.id}><Link href={`/bench/${review.id}`}>
              <StatusPill status={review.status} />
              <span><span className="review-list-title">{review.title}</span><span className="review-list-meta">{prLabel(review.repo, review.pr_number)} · {review.finding_count} findings</span></span>
              <time dateTime={review.created_at}>{formatWhen(review.created_at)}</time><ArrowRight size={17} />
            </Link></li>
          ))}</ul></>
      )}
    </div>
  );
}
