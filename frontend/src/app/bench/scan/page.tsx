import Link from "next/link";
import { ArrowRight, CaretRight, FileMagnifyingGlass, Code, Flask, GitPullRequest } from "@phosphor-icons/react/dist/ssr";
import { ScanForm } from "@/components/bench/scan-form";

export const metadata = { title: "New review" };

export default function ScanPage() {
  return (
    <div className="app-page page-container scan-page">
      <nav className="breadcrumb" aria-label="Breadcrumb"><Link href="/bench">Bench</Link><CaretRight size={12} /><span>New review</span></nav>
      <div className="scan-heading"><h1 className="app-title">A closer look at your code.</h1>
        <p className="page-description">Start with a pull request or a diff. Leave with a clear next step.</p></div>
      <div className="scan-layout">
        <div>
          <ScanForm />
          <p className="sample-invitation">Want to look around first? <Link href="/bench/sample" className="text-link">Explore a sample review <ArrowRight size={15} /></Link></p>
        </div>
        <aside className="scan-explainer">
          <h2>What comes back</h2>
          {[{ icon: FileMagnifyingGlass, title: "The finding", body: "What went wrong, and exactly where." },
            { icon: Code, title: "A suggested fix", body: "A concrete change you can review." },
            { icon: Flask, title: "A test stub", body: "A starting point for a regression test." }].map((item) => (
            <div className="scan-benefit" key={item.title}>
              <item.icon size={29} weight="light" /><div><h3>{item.title}</h3><p>{item.body}</p></div>
            </div>
          ))}
          <p className="scan-note"><GitPullRequest size={19} />Vernier reviews your code. You decide what merges.</p>
        </aside>
      </div>
    </div>
  );
}
