import { FindingPanel } from "@/components/bench/finding-panel";
import type { Finding } from "@/lib/types";
import { Reveal } from "./reveal";

const SAMPLE: Finding[] = [
  {
    id: "s1",
    category: "security",
    severity: "critical",
    title: "SQL Injection (CWE-89)",
    description:
      "Untrusted user_id is concatenated into a raw SQL string. An attacker can append OR 1=1 or UNION SELECT and read other customers' orders.",
    file_path: "src/db/queries.py",
    start_line: 142,
    end_line: 144,
    snippet: "query = f\"SELECT * FROM orders WHERE user_id = '{user_id}' AND status = 'active'\"\ncursor.execute(query)",
    confidence: 0.94,
    source: "merged",
    detector_id: "sql_fstring",
    fix_suggestion:
      "from sqlalchemy import text\n\nstmt = text(\"SELECT * FROM orders WHERE user_id = :user_id AND status = 'active'\")\ncursor.execute(stmt, {\"user_id\": user_id})",
    test_stub:
      "def test_get_user_orders_rejects_injection(client):\n    response = client.get(\"/orders\", params={\"user_id\": \"1' OR '1'='1\"})\n    assert response.status_code in {400, 404}",
    cached: false,
  },
  {
    id: "s2",
    category: "security",
    severity: "medium",
    title: "Hardcoded credential in config",
    description: "SECRET_KEY is committed in source.",
    file_path: "src/config.py",
    start_line: 4,
    end_line: 4,
    snippet: 'SECRET_KEY = "supersecret123456"',
    confidence: 0.8,
    source: "heuristic",
    detector_id: "hardcoded_secret",
    fix_suggestion: 'SECRET_KEY = os.environ["SECRET_KEY"]',
    test_stub: "def test_secret_comes_from_environment(monkeypatch):\n    monkeypatch.setenv(\"SECRET_KEY\", \"from-env\")",
    cached: false,
  },
  {
    id: "s3",
    category: "performance",
    severity: "low",
    title: "Query inside a loop",
    description: "Each order_id issues its own SELECT.",
    file_path: "src/api/orders.py",
    start_line: 42,
    end_line: 43,
    snippet: "items.append(db.query(Item).filter(Item.order_id == order_id).all())",
    confidence: 0.7,
    source: "heuristic",
    detector_id: "n_plus_one",
    fix_suggestion: "items = db.query(Item).filter(Item.order_id.in_(order_ids)).all()",
    test_stub: "def test_items_are_fetched_in_one_query(db):\n    with assert_max_queries(db, 2):\n        load_orders_with_items(order_ids)",
    cached: true,
  },
];

export function Showcase() {
  return (
    <section className="mx-auto max-w-[1120px] px-4 py-20">
      <Reveal>
        <h2 className="text-3xl font-semibold tracking-[-0.03em] text-ink md:text-4xl">A finding you can patch</h2>
        <p className="mt-3 max-w-[54ch] text-[16px] leading-relaxed text-ink">
          Every issue comes with the hunk, a fix, and a test stub. The bench is the same component the landing uses here.
        </p>
      </Reveal>
      <Reveal className="mt-8">
        <FindingPanel findings={SAMPLE} repoLabel="Pull Request #1842  harbor-labs/checkout-api" />
      </Reveal>
    </section>
  );
}
