import { Reveal } from "./reveal";

const STEPS = [
  {
    title: "Fetch the diff",
    body: "Pull the GitHub patch, split it into hunks, and keep the surrounding file context.",
  },
  {
    title: "Batch and cache",
    body: "Pack hunks into model batches. Redis stores the prompt identity and the result so repeats cost nothing.",
  },
  {
    title: "Return findings",
    body: "Merge heuristic hits with the model, then attach a concrete fix and a test stub.",
  },
];

export function Workflow() {
  return (
    <section id="how" className="mx-auto max-w-[1120px] px-4 py-20">
      <Reveal>
        <h2 className="text-3xl font-semibold tracking-[-0.03em] text-primary md:text-4xl">How Vernier works</h2>
      </Reveal>
      <Reveal className="mt-10">
        <div className="grid bg-surface md:grid-cols-3">
          {STEPS.map((step, index) => (
            <article
              key={step.title}
              className={`px-6 py-8 md:px-8 ${index > 0 ? "border-t border-rule md:border-t-0 md:border-l" : ""}`}
            >
              <h3 className="text-2xl font-semibold tracking-tight text-primary">{step.title}</h3>
              <p className="mt-3 max-w-[36ch] text-[15px] leading-relaxed text-ink">{step.body}</p>
            </article>
          ))}
        </div>
      </Reveal>
    </section>
  );
}
