"use client";
import { useMemo, useState } from "react";
import { CaretDown, FileCode, Files, Check, Copy, GitBranch } from "@phosphor-icons/react";
import type { Finding } from "@/lib/types";
import { severityRank } from "@/lib/format";

function CodeBlock({ code, label }: { code: string; label: string }) {
  const [copyState, setCopyState] = useState<"idle" | "copied" | "failed">("idle");
  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      setCopyState("copied");
    } catch {
      setCopyState("failed");
    }
  }
  return (
    <div className="finding-code-block">
      <div className="code-block-label"><span>{label}</span><button onClick={copy} type="button" aria-label={`Copy ${label.toLowerCase()}`}>
        {copyState === "copied" ? <Check size={15} /> : <Copy size={15} />}<span aria-live="polite">{copyState === "copied" ? "Copied" : copyState === "failed" ? "Select code to copy" : "Copy"}</span>
      </button></div>
      <pre><code>{code}</code></pre>
    </div>
  );
}

function FindingDetail({ finding }: { finding: Finding }) {
  return (
    <div className="finding-detail">
      <p className="finding-description">{finding.description}</p>
      {finding.snippet && <CodeBlock code={finding.snippet} label="Flagged code" />}
      <div className="finding-solution-grid">
        <CodeBlock code={finding.fix_suggestion || "No automatic fix for this detector."} label="Suggested fix" />
        <CodeBlock code={finding.test_stub || "Add a regression test around the failing path."} label="Test stub" />
      </div>
      <p className="finding-meta"><span>{finding.source}</span>{finding.cached && <span>Cache hit</span>}
        {finding.confidence > 0 && <span>{Math.round(finding.confidence * 100)}% confidence</span>}</p>
    </div>
  );
}

export function FindingPanel({ findings, repoLabel, initialFindingId }: {
  findings: Finding[]; repoLabel?: string; initialFindingId?: string;
}) {
  const sorted = useMemo(() => [...findings].sort((a, b) => severityRank(a.severity) - severityRank(b.severity)), [findings]);
  const files = useMemo(() => Array.from(new Set(findings.map((item) => item.file_path))), [findings]);
  const initial = sorted.find((item) => item.id === initialFindingId) ?? sorted[0];
  const [file, setFile] = useState(initialFindingId && initial ? initial.file_path : "all");
  const [openId, setOpenId] = useState<string | null>(initial?.id ?? null);
  const visible = sorted.filter((item) => file === "all" || item.file_path === file);

  function selectFile(path: string) {
    setFile(path);
    setOpenId(sorted.find((item) => path === "all" || item.file_path === path)?.id ?? null);
  }

  return (
    <div className="finding-panel">
      <div className="finding-toolbar"><span><GitBranch size={18} />{repoLabel || "Review findings"}</span><span>{findings.length} findings</span></div>
      <div className="finding-layout">
        <aside className="finding-files" aria-label="Filter findings by file">
          <p>Files changed <span>{files.length}</span></p>
          <button type="button" onClick={() => selectFile("all")} aria-pressed={file === "all"}><Files size={17} /><span>All findings</span><span>{findings.length}</span></button>
          {files.map((path) => <button key={path} type="button" onClick={() => selectFile(path)} aria-pressed={file === path} title={path}>
            <FileCode size={17} /><span>{path}</span><span>{findings.filter((item) => item.file_path === path).length}</span>
          </button>)}
        </aside>
        <div className="finding-list">
          {visible.length === 0 ? <div className="finding-empty"><Check size={27} /><h3>No findings in this file.</h3><p>There are no issues to display for this selection.</p></div> :
            visible.map((finding) => {
              const open = openId === finding.id;
              return (
                <article className={`finding-item ${open ? "is-open" : ""}`} key={finding.id}>
                  <button type="button" className="finding-toggle" aria-expanded={open} aria-controls={`detail-${finding.id}`} onClick={() => setOpenId(open ? null : finding.id)}>
                    <span className={`severity-badge severity-${finding.severity}`}>{finding.severity}</span>
                    <span className="finding-heading"><strong>{finding.title}</strong><span>{finding.file_path}{finding.start_line ? `:${finding.start_line}` : ""}</span></span>
                    <CaretDown size={17} className="finding-chevron" />
                  </button>
                  <div id={`detail-${finding.id}`} hidden={!open}>{open && <FindingDetail finding={finding} />}</div>
                </article>
              );
            })}
        </div>
      </div>
    </div>
  );
}
