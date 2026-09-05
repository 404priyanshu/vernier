"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, SpinnerGap, GithubLogo, Code } from "@phosphor-icons/react";
import { createReview } from "@/lib/api";

type InputMode = "url" | "diff";

export function ScanForm() {
  const router = useRouter();
  const [mode, setMode] = useState<InputMode>("url");
  const [prUrl, setPrUrl] = useState("");
  const [diff, setDiff] = useState("");
  const [heuristicsOnly, setHeuristicsOnly] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  function changeMode(next: InputMode) {
    setMode(next);
    setError(null);
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (mode === "url") {
      try {
        const url = new URL(prUrl.trim());
        if (url.protocol !== "https:" || url.hostname !== "github.com" || !/^\/[^/]+\/[^/]+\/pull\/\d+\/?$/.test(url.pathname)) throw new Error();
      } catch {
        setError("Enter a GitHub pull request URL, such as https://github.com/org/repo/pull/12.");
        return;
      }
    } else if (!diff.trim()) {
      setError("Paste a unified diff to start a review.");
      return;
    }
    setPending(true);
    try {
      const review = await createReview({
        ...(mode === "url" ? { pr_url: prUrl.trim() } : { diff: diff.trim() }),
        heuristics_only: heuristicsOnly,
      });
      router.push(`/bench/${review.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The scan could not finish. Please try again.");
      setPending(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="scan-form" aria-busy={pending}>
      <div className="scan-tabs" role="tablist" aria-label="Review input">
        {([{ value: "url", label: "GitHub pull request", icon: GithubLogo }, { value: "diff", label: "Paste a diff", icon: Code }] as const).map((tab) => (
          <button key={tab.value} type="button" id={`tab-${tab.value}`} role="tab" aria-selected={mode === tab.value} aria-controls={`input-${tab.value}`} tabIndex={mode === tab.value ? 0 : -1} disabled={pending}
            onClick={() => changeMode(tab.value)}
            onKeyDown={(event) => {
              if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
                event.preventDefault();
                const next = event.key === "Home" ? "url" : event.key === "End" ? "diff" : mode === "url" ? "diff" : "url";
                changeMode(next);
                document.getElementById(`tab-${next}`)?.focus();
              }
            }}>
            <tab.icon size={18} />{tab.label}
          </button>
        ))}
      </div>
      <div className="scan-form-body">
        <div role="tabpanel" id={`input-${mode}`} aria-labelledby={`tab-${mode}`}>
          {mode === "url" ? (
            <div className="form-field">
              <label htmlFor="pr-url">Pull request URL</label>
              <input id="pr-url" name="pr_url" type="url" placeholder="https://github.com/org/repo/pull/12"
                value={prUrl} onChange={(event) => setPrUrl(event.target.value)} disabled={pending} aria-describedby="url-help scan-error" aria-invalid={!!error} />
              <p id="url-help">Use the full URL of the pull request you want to review.</p>
            </div>
          ) : (
            <div className="form-field">
              <label htmlFor="diff">Unified diff</label>
              <textarea id="diff" name="diff" rows={10} value={diff} onChange={(event) => setDiff(event.target.value)} disabled={pending}
                placeholder={"diff --git a/app.py b/app.py\n@@ -1,2 +1,3 @@\n+eval(user_input)"} spellCheck={false} aria-describedby="diff-help scan-error" aria-invalid={!!error} />
              <p id="diff-help">Paste a patch from git diff. Keep the file headers and changed lines.</p>
            </div>
          )}
        </div>
        <label className="scan-option">
          <input type="checkbox" checked={heuristicsOnly} disabled={pending} onChange={(event) => setHeuristicsOnly(event.target.checked)} />
          <span><strong>Heuristics only</strong><span>Skip model analysis for this review.</span></span>
        </label>
        <div id="scan-error">{error && <p role="alert" className="form-error">{error}</p>}</div>
        <button type="submit" disabled={pending} className="button button-primary scan-submit">
          {pending ? <><SpinnerGap size={20} className="spin" />Analyzing your code…</> : <>Scan a pull request <ArrowRight size={21} /></>}
        </button>
        {pending && <p className="pending-note" role="status">Reading the diff and checking for findings. This may take a moment.</p>}
      </div>
    </form>
  );
}
