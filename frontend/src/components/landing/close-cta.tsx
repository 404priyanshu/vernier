import Link from "next/link";
import { ArrowRight } from "@phosphor-icons/react/dist/ssr";

export function CloseCta() {
  return (
    <section className="close-cta page-container">
      <h2 className="section-heading">Your next merge,<br />with fewer unknowns.</h2>
      <div className="hero-actions">
        <Link href="/bench/scan" className="button button-primary">Scan a pull request</Link>
        <Link href="/bench" className="text-link">Explore the bench <ArrowRight size={17} /></Link>
      </div>
    </section>
  );
}
