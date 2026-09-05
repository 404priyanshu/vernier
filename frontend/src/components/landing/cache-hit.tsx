import { CheckSquare } from "@phosphor-icons/react/dist/ssr";

export function CacheHit() {
  return (
    <section className="cache-band">
      <div className="page-container cache-inner">
        <div>
          <h2 className="section-heading">Same diff.<br /><span>Already measured.</span></h2>
          <p>Repeated hunks reuse cached results.<br />New code gets a fresh review.</p>
        </div>
        <dl className="cache-record" aria-label="Example cache key">
          <div><dt>prompt version</dt><dd>review-v1</dd></div>
          <div><dt>model</dt><dd>configured model</dd></div>
          <div><dt>hunk</dt><dd>sha256(file + added lines)</dd></div>
          <div className="cache-success"><dt className="sr-only">Result</dt><dd className="flex items-center gap-3"><CheckSquare size={20} /> CACHE HIT — model call skipped</dd></div>
        </dl>
      </div>
    </section>
  );
}
