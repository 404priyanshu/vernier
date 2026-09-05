import Link from "next/link";
import { ArrowRight } from "@phosphor-icons/react/dist/ssr";
import { ReviewPreview } from "./review-preview";

export function Hero() {
  return (
    <section className="hero">
      <div className="measurement-rail measurement-rail-left" aria-hidden="true"><span>0</span><span>100</span><span>200</span><span>300</span></div>
      <div className="measurement-rail measurement-rail-right" aria-hidden="true" />
      <div className="page-container">
        <div className="hero-copy">
          <h1>Measure every diff.<br /><span>Catch issues before they ship.</span></h1>
          <p>Catch bugs, security issues, and slow patterns before they ship.</p>
          <div className="hero-actions">
            <Link href="/bench/scan" className="button button-primary">Scan a pull request</Link>
            <Link href="/bench/sample" className="button button-secondary">Explore a sample <ArrowRight size={17} /></Link>
          </div>
          <p className="hero-note">A finding. A fix. A test. All in context.</p>
        </div>
        <ReviewPreview />
      </div>
    </section>
  );
}
