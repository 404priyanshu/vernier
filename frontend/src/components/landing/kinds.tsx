import { Reveal } from "./reveal";

const KINDS = [
  {
    name: "Security",
    open: true,
    body: "Injection, unsafe deserialization, leaked secrets, XSS sinks, skipped JWT verification.",
    code: "query = f\"SELECT * FROM orders WHERE user_id = '{user_id}'\"",
  },
  {
    name: "Bugs",
    open: false,
    body: "Mutable defaults, swallowed exceptions, identity checks written as equality, unfinished FIXME paths.",
    code: "def handle(items=[]):",
  },
  {
    name: "Performance",
    open: false,
    body: "Queries inside loops, blocking I/O in async handlers, accidental quadratic walks.",
    code: "for order_id in order_ids:\n    db.query(Item).filter(...)",
  },
];

export function Kinds() {
  return (
    <section className="mx-auto max-w-[1120px] px-4 py-20">
      <Reveal>
        <h2 className="text-3xl font-semibold tracking-[-0.03em] text-ink md:text-4xl">What it looks for</h2>
      </Reveal>
      <Reveal className="mt-8">
        <div className="divide-y divide-rule border-y border-rule">
          {KINDS.map((kind) => (
            <article key={kind.name} className="grid gap-4 py-6 md:grid-cols-[160px_minmax(0,1fr)_minmax(0,0.8fr)] md:items-start">
              <h3 className={`text-lg font-semibold ${kind.open ? "text-accent" : "text-ink"}`}>{kind.name}</h3>
              <p className="max-w-[48ch] text-[15px] leading-relaxed">{kind.body}</p>
              <pre className="overflow-x-auto bg-surface px-3 py-3 font-mono text-[12px] leading-relaxed text-ink">
                {kind.code}
              </pre>
            </article>
          ))}
        </div>
      </Reveal>
    </section>
  );
}
