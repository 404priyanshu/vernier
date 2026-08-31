"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createReview } from "@/lib/api";

export function ScanForm() {
  const router = useRouter();
  const [prUrl, setPrUrl] = useState("");
  const [diff, setDiff] = useState("");
  const [heuristicsOnly, setHeuristicsOnly] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    if (!prUrl.trim() && !diff.trim()) {
      setError("Paste a GitHub pull request URL or a unified diff.");
      return;
    }
    setPending(true);
    try {
      const review = await createReview({
        pr_url: prUrl.trim() || undefined,
        diff: diff.trim() || undefined,
        heuristics_only: heuristicsOnly,
      });
      router.push(`/bench/${review.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan failed");
      setPending(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      <div className="flex flex-col gap-2">
        <label htmlFor="pr-url" className="text-[14px] font-medium">
          GitHub pull request URL
        </label>
        <input
          id="pr-url"
          name="pr_url"
          type="url"
          placeholder="https://github.com/org/repo/pull/12"
          value={prUrl}
          onChange={(event) => setPrUrl(event.target.value)}
          className="border border-rule bg-bg px-3 py-2.5 text-[15px] placeholder:text-muted"
        />
        <p className="text-[13px] text-muted">Public PRs work without a token. Private PRs need GITHUB_TOKEN on the API.</p>
      </div>
      <div className="flex flex-col gap-2">
        <label htmlFor="diff" className="text-[14px] font-medium">
          Or paste a unified diff
        </label>
        <textarea
          id="diff"
          name="diff"
          rows={10}
          value={diff}
          onChange={(event) => setDiff(event.target.value)}
          placeholder={"diff --git a/app.py b/app.py\n@@ -1,2 +1,3 @@\n+eval(user_input)"}
          className="border border-rule bg-bg px-3 py-2.5 font-mono text-[13px] placeholder:text-muted"
        />
      </div>
      <label className="flex items-center gap-2 text-[14px]">
        <input
          type="checkbox"
          checked={heuristicsOnly}
          onChange={(event) => setHeuristicsOnly(event.target.checked)}
        />
        Heuristics only (skip the model)
      </label>
      {error ? (
        <p role="alert" className="text-[14px] text-accent">
          {error}
        </p>
      ) : null}
      <button
        type="submit"
        disabled={pending}
        className="bg-primary px-5 py-3 text-[15px] text-white transition-colors duration-200 enabled:hover:bg-[oklch(0.36_0.19_261)] enabled:active:scale-[0.98] disabled:opacity-50"
      >
        {pending ? "Queuing scan" : "Scan a pull request"}
      </button>
    </form>
  );
}
