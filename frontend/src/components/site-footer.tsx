import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-rule">
      <div className="mx-auto flex max-w-[1120px] flex-col gap-3 px-4 py-8 text-[13px] text-muted sm:flex-row sm:items-center sm:justify-between">
        <p>Vernier measures pull request diffs. It does not merge them.</p>
        <nav className="flex gap-5" aria-label="Footer">
          <Link href="/" className="hover:text-ink">
            Vernier
          </Link>
          <Link href="/bench" className="hover:text-ink">
            Bench
          </Link>
          <Link href="/docs" className="hover:text-ink">
            Docs
          </Link>
        </nav>
      </div>
    </footer>
  );
}
