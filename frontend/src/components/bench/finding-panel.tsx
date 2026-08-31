"use client";

import { useMemo, useState } from "react";
import type { Finding } from "@/lib/types";
import { severityRank } from "@/lib/format";

const SEVERITY_CLASS: Record<string, string> = {
  critical: "bg-accent text-white",
  high: "bg-primary text-white",
  medium: "border border-rule text-ink",
  low: "text-muted",
  info: "text-muted",
};

export function FindingPanel({
  findings,
  repoLabel,
}: {
  findings: Finding[];
  repoLabel?: string;
}) {
  const files = useMemo(() => {
    const unique = Array.from(new Set(findings.map((item) => item.file_path)));
    return unique;
  }, [findings]);
  const [file, setFile] = useState<string | "all">("all");
  const [openId, setOpenId] = useState<string | null>(findings[0]?.id ?? null);

  const visible = findings
    .filter((item) => (file === "all" ? true : item.file_path === file))
    .slice()
    .sort((a, b) => severityRank(a.severity) - severityRank(b.severity));

  return (
    <div className="border border-rule bg-bg">
      {repoLabel ? (
        <div className="border-b border-rule px-4 py-3 text-[14px] md:px-5">
          <p className="font-medium">{repoLabel}</p>
        </div>
      ) : null}
      <div className="grid md:grid-cols-[220px_minmax(0,1fr)]">
        <aside className="border-b border-rule md:border-b-0 md:border-r">
          <p className="px-4 pt-4 text-[12px] text-muted">Files changed ({files.length})</p>
          <ul className="px-2 py-2">
            <li>
              <button
                type="button"
                onClick={() => setFile("all")}
                className={`block w-full px-2 py-1.5 text-left font-mono text-[12px] ${file === "all" ? "bg-surface text-ink" : "text-muted hover:text-ink"}`}
              >
                all
              </button>
            </li>
            {files.map((path) => (
              <li key={path}>
                <button
                  type="button"
                  onClick={() => setFile(path)}
                  className={`block w-full truncate px-2 py-1.5 text-left font-mono text-[12px] ${file === path ? "bg-surface text-primary" : "text-muted hover:text-ink"}`}
                >
                  {path}
                </button>
              </li>
            ))}
          </ul>
        </aside>
        <div>
          {visible.length === 0 ? (
            <p className="px-5 py-10 text-sm text-muted">No findings in this file.</p>
          ) : (
            <ul>
              {visible.map((finding) => {
                const open = openId === finding.id;
                return (
                  <li key={finding.id} className="border-b border-rule last:border-b-0">
                    <button
                      type="button"
                      aria-expanded={open}
                      onClick={() => setOpenId(open ? null : finding.id)}
                      className="flex w-full items-start gap-3 px-4 py-4 text-left md:px-5"
                    >
                      <span
                        className={`mt-0.5 shrink-0 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${SEVERITY_CLASS[finding.severity] || "text-muted"}`}
                      >
                        {finding.severity}
                      </span>
                      <span>
                        <span className="block text-[15px] font-medium">{finding.title}</span>
                        <span className="mt-1 block font-mono text-[12px] text-muted">
                          {finding.file_path}
                          {finding.start_line ? `:${finding.start_line}` : ""}
                        </span>
                      </span>
                    </button>
                    {open ? (
                      <div className="space-y-4 px-4 pb-5 md:px-5">
                        <p className="max-w-[65ch] text-[14px] leading-relaxed">{finding.description}</p>
                        {finding.snippet ? (
                          <pre className="overflow-x-auto bg-surface px-3 py-3 font-mono text-[12px] leading-relaxed">
                            {finding.snippet}
                          </pre>
                        ) : null}
                        <div className="grid gap-4 md:grid-cols-2">
                          <div>
                            <p className="text-[12px] font-medium text-muted">Suggested fix</p>
                            <pre className="mt-2 overflow-x-auto bg-surface px-3 py-3 font-mono text-[12px] leading-relaxed">
                              {finding.fix_suggestion || "No automatic fix for this detector."}
                            </pre>
                          </div>
                          <div>
                            <p className="text-[12px] font-medium text-muted">Test stub</p>
                            <pre className="mt-2 overflow-x-auto bg-surface px-3 py-3 font-mono text-[12px] leading-relaxed">
                              {finding.test_stub || "Add a regression test around the failing path."}
                            </pre>
                          </div>
                        </div>
                        <p className="text-[12px] text-muted">
                          {finding.source}
                          {finding.cached ? " / cache hit" : ""}
                          {finding.confidence ? ` / ${Math.round(finding.confidence * 100)}% confidence` : ""}
                        </p>
                      </div>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
