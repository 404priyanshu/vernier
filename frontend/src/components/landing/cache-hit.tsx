import { Reveal } from "./reveal";

const KEYS = [
  { label: "prompt version", value: "review-v1" },
  { label: "model", value: "grok-4.6" },
  { label: "normalized hunk hash", value: "sha256(file + added lines)" },
];

export function CacheHit() {
  return (
    <section className="mx-auto max-w-[1120px] px-4 py-20">
      <Reveal>
        <div className="grid items-center gap-10 md:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
          <div>
            <p className="font-semibold leading-none tracking-[-0.04em] text-primary text-[clamp(4.5rem,18vw,11rem)]">
              HIT
            </p>
            <div className="mt-2 h-2 w-40 bg-accent md:w-56" />
          </div>
          <div>
            <p className="max-w-[36ch] text-[1.35rem] font-medium leading-snug tracking-tight text-ink">
              Repeated model calls are skipped when the same hunk and prompt version already live in Redis.
            </p>
            <p className="mt-6 text-[12px] font-medium uppercase tracking-wide text-muted">Cache key parts</p>
            <dl className="mt-3 divide-y divide-rule border-y border-rule">
              {KEYS.map((item) => (
                <div key={item.label} className="flex items-baseline justify-between gap-4 py-3">
                  <dt className="text-[14px] text-ink">{item.label}</dt>
                  <dd className="font-mono text-[13px] text-primary">{item.value}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </Reveal>
    </section>
  );
}
