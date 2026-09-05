import Link from "next/link";
import { Mark } from "./mark";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="page-container">
        <Link href="/" className="footer-brand"><Mark />Vernier</Link>
        <p>Measure the diff. Keep the context.</p>
        <nav aria-label="Footer"><Link href="/bench">Bench</Link><Link href="/docs">Docs</Link></nav>
      </div>
    </footer>
  );
}
