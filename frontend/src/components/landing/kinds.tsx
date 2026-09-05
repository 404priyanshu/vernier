const KINDS = [
  { name: "Security", body: "Injection, exposed secrets, unsafe deserialization, and XSS.", code: 'query = f"SELECT * FROM users\n  WHERE name = \'{user_input}\'"\ncursor.execute(query)' },
  { name: "Bugs", body: "Mutable defaults, swallowed exceptions, and unfinished paths.", code: "def parse(items, acc=[]):\n    try: return [acc.append(i) for i in items]\n    except Exception: pass" },
  { name: "Performance", body: "N+1 queries, blocking I/O, and accidental quadratic work.", code: "for order_id in order_ids:\n    items = db.query(Item).filter(\n        Item.order_id == order_id).all()" },
];
export function Kinds() {
  return (
    <section className="kinds page-container">
      <h2 className="section-heading">A second pass, where it matters.</h2>
      <div className="kind-table">
        {KINDS.map((kind, index) => (
          <article key={kind.name} className="kind-row">
            <span className="kind-number">0{index + 1}</span>
            <div className="kind-copy"><h3>{kind.name}</h3><p>{kind.body}</p></div>
            <pre><code>{kind.code}</code></pre>
          </article>
        ))}
      </div>
    </section>
  );
}
