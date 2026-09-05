export const metadata = {
  title: "Docs",
};

export default function DocsPage() {
  return (
    <div className="page-container app-page">
      <h1 className="app-title">Under the instrument.</h1>
      <p className="page-description">How Vernier reads your diffs, reuses its work, and fits into your workflow.</p>
      <div className="docs-layout">
      <nav className="docs-nav" aria-label="Documentation sections">
        <a href="#pipeline">Pipeline</a><a href="#environment">Environment</a><a href="#webhooks">Webhooks</a><a href="#ci">Continuous integration</a>
      </nav>
      <div className="docs-content">
        <section id="pipeline">
          <h2 className="text-xl font-semibold">Pipeline</h2>
          <ol className="mt-3 list-decimal space-y-2 pl-5">
            <li>Parse a GitHub pull request URL or a unified diff into file hunks.</li>
            <li>Run heuristic detectors on added lines (injection, pickle, XSS, N+1, secrets, and more).</li>
            <li>Hash each hunk with the prompt version and model name.</li>
            <li>Skip Redis hits. Pack misses into character-bounded batches and call the LLM once per batch.</li>
            <li>Merge overlapping findings, attach a fix and a test stub, store the review in PostgreSQL.</li>
          </ol>
        </section>
        <section id="environment">
          <h2 className="text-xl font-semibold">Environment</h2>
          <p className="mt-3">
            Copy <code className="font-mono text-[13px]">.env.example</code> to{" "}
            <code className="font-mono text-[13px]">.env</code>. Default LLM endpoint is SpaceXAI at{" "}
            <code className="font-mono text-[13px]">https://api.x.ai/v1</code> using the OpenAI-compatible SDK. Set{" "}
            <code className="font-mono text-[13px]">LLM_BASE_URL</code> to{" "}
            <code className="font-mono text-[13px]">https://api.openai.com/v1</code> if you want OpenAI itself.
          </p>
        </section>
        <section id="webhooks">
          <h2 className="text-xl font-semibold">Webhooks</h2>
          <p className="mt-3">
            Send GitHub <code className="font-mono text-[13px]">pull_request</code> events to{" "}
            <code className="font-mono text-[13px]">POST /api/webhooks/github</code>. When{" "}
            <code className="font-mono text-[13px]">GITHUB_WEBHOOK_SECRET</code> is set, the handler requires{" "}
            <code className="font-mono text-[13px]">X-Hub-Signature-256</code>.
          </p>
        </section>
        <section id="ci">
          <h2 className="text-xl font-semibold">CI</h2>
          <p className="mt-3">
            <code className="font-mono text-[13px]">pytest</code> covers diff parsing, detectors, batching, Redis-style
            cache keys, and the review workflow. The GitHub Actions workflow also typechecks and builds the Next.js app.
          </p>
        </section>
      </div>
      </div>
    </div>
  );
}
