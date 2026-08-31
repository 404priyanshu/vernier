import Link from "next/link";
import { Reveal } from "./reveal";

const ROWS = [
  {
    lines: "142 158",
    file: "auth.go",
    note: "userSession.expiresAt comparison uses local time instead of UTC",
    extra: "+12ms drift",
    high: false,
  },
  {
    lines: "133 203",
    file: "metrics.go",
    note: "counter increment bypasses rate limiter on retry path",
    extra: "HIGH",
    high: true,
  },
  {
    lines: "89 91",
    file: "tests/cache_test.go",
    note: "mock clock not advanced in parallel test case",
    extra: "",
    high: false,
  },
];

export function Hero() {
  return (
    <section className="mx-auto max-w-[1120px] px-4 pb-20 pt-10 md:pt-14">
      <Reveal>
        <div className="grid items-start gap-8 md:grid-cols-[minmax(0,1fr)_220px]">
          <div>
            <h1 className="max-w-[14ch] text-[2.75rem] font-semibold leading-[1.05] tracking-[-0.03em] text-primary text-balance md:text-[4.25rem]">
              Measure every diff.
            </h1>
            <p className="mt-5 max-w-[42ch] text-[17px] leading-relaxed text-ink">
              Vernier reads GitHub pull request diffs for bugs, security issues, and slow patterns.
            </p>
          </div>
          <div className="flex flex-col items-start gap-3 md:items-end md:pt-3">
            <Link
              href="/bench/scan"
              className="inline-flex bg-primary px-5 py-3 text-[15px] text-white transition-colors duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] hover:bg-[oklch(0.36_0.19_261)] active:scale-[0.98]"
            >
              Scan a pull request
            </Link>
            <Link href="/bench?sample=1" className="text-[15px] text-ink underline underline-offset-4">
              View a sample
            </Link>
          </div>
        </div>
      </Reveal>
      <Reveal className="mt-14">
        <div className="border border-rule bg-paper px-5 py-6 md:px-8 md:py-8">
          <ul className="divide-y divide-rule">
            {ROWS.map((row) => (
              <li
                key={row.file}
                className="grid gap-2 py-4 first:pt-0 last:pb-0 md:grid-cols-[7rem_minmax(0,1fr)_auto] md:items-baseline md:gap-6"
              >
                <span className="font-mono text-[12px] text-muted">
                  {row.high ? (
                    <span className="mr-2 inline-block bg-accent px-1.5 py-0.5 text-[10px] font-sans font-semibold tracking-wide text-white">
                      HIGH
                    </span>
                  ) : null}
                  {row.lines}
                </span>
                <p className="text-[15px] leading-snug">
                  <span className="font-mono text-primary">{row.file}</span>{" "}
                  <span className="text-ink">{row.note}</span>
                </p>
                <span className="font-mono text-[12px] text-muted">{row.extra === "HIGH" ? "" : row.extra}</span>
              </li>
            ))}
          </ul>
        </div>
      </Reveal>
    </section>
  );
}
