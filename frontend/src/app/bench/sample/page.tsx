import Link from "next/link";
import { ArrowRight, CaretRight, GitBranch } from "@phosphor-icons/react/dist/ssr";
import { FindingPanel } from "@/components/bench/finding-panel";
import { SAMPLE_FINDINGS } from "@/lib/sample";

export const metadata = { title: "Sample review" };

export default async function SamplePage({ searchParams }: { searchParams: Promise<{ finding?: string }> }) {
  const { finding } = await searchParams;
  return (
    <div className="page-container app-page">
      <nav className="breadcrumb" aria-label="Breadcrumb"><Link href="/bench">Bench</Link><CaretRight size={12} /><span>Sample review</span></nav>
      <div className="page-heading">
        <div><div className="review-repo"><GitBranch size={17} />harbor-labs / checkout-api <span>#1842</span></div>
          <h1 className="app-title">A finding you can patch.</h1>
          <p className="page-description">Explore a sample review. Select a file, inspect the issue, and compare the suggested fix.</p></div>
        <Link href="/bench/scan" className="button button-primary">Review your code <ArrowRight size={17} /></Link>
      </div>
      <div className="sample-summary"><span className="sample-label">Sample data</span><span>3 findings</span><span>3 files</span><span>A fix and test for every finding</span></div>
      <FindingPanel key={finding ?? "all"} findings={SAMPLE_FINDINGS} repoLabel="Pull Request #1842 · harbor-labs/checkout-api" initialFindingId={finding} />
    </div>
  );
}
