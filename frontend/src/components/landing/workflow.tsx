import { GitDiff, Stack, CheckCircle } from "@phosphor-icons/react/dist/ssr";

const STEPS = [
  { title: "Fetch the diff", body: "Pull the GitHub patch and file context.", icon: GitDiff },
  { title: "Batch and cache", body: "Group related hunks and reuse cached analysis.", icon: Stack },
  { title: "Return findings", body: "Surface issues with a clear fix and regression test.", icon: CheckCircle },
];

export function Workflow() {
  return (
    <section id="how" className="workflow page-container">
      <div className="section-intro">
        <h2 className="section-heading">From pull request to<br />a clear next step.</h2>
        <p>Heuristics and model analysis, working together.</p>
      </div>
      <div className="workflow-steps">
        {STEPS.map((step, index) => (
          <article key={step.title}>
            <div className="step-line"><div className="step-icon"><step.icon size={27} weight="light" /></div><span>0{index + 1}</span></div>
            <h3>{step.title}</h3><p>{step.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
