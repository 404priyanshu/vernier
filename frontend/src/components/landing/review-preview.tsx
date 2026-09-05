"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowRight, FileCode, GitBranch } from "@phosphor-icons/react";
import { SAMPLE_FINDINGS } from "@/lib/sample";

const PREVIEWS = [
  {
    title: "SQL injection",
    description: "User input is interpolated directly into the SQL query. This can be exploited to read or modify data.",
    lines: ["def get_orders_for_user(user_id):", '    query = "SELECT * FROM orders "', "    query += f\"WHERE user_id = '{user_id}'\"",
      "    cursor.execute(query)", "    return cursor.fetchall()", ""],
    start: 140, highlight: 2,
  },
  {
    title: "Hardcoded credential",
    description: "A secret is committed in source. Load it from the environment so it can be rotated without a code change.",
    lines: ["import os", "", 'SECRET_KEY = "supersecret123456"', "", 'DEBUG = os.getenv("DEBUG", "false")', ""],
    start: 2, highlight: 2,
  },
  {
    title: "Query inside a loop",
    description: "Each order triggers another database query. Fetch the items together to avoid an N+1 query pattern.",
    lines: ["items = []", "for order_id in order_ids:", "    items.append(db.query(Item)", "        .filter(Item.order_id == order_id)", "        .all())", ""],
    start: 40, highlight: 2,
  },
];

export function ReviewPreview() {
  const [selected, setSelected] = useState(0);
  const finding = SAMPLE_FINDINGS[selected];
  const preview = PREVIEWS[selected];
  return (
    <div className="review-preview">
      <div className="preview-toolbar">
        <span><GitBranch size={22} /> harbor-labs <span className="text-muted">/</span> checkout-api</span>
        <span className="preview-sample-label">Sample review · #1842</span>
      </div>
      <div className="preview-body">
        <aside className="preview-files">
          <p>Files reviewed</p>
          {SAMPLE_FINDINGS.map((item, index) => (
            <button key={item.id} onClick={() => setSelected(index)} aria-pressed={selected === index} className={selected === index ? "selected" : ""}>
              <FileCode size={18} /><span>{item.file_path}</span>
            </button>
          ))}
        </aside>
        <div className="preview-code">
          <div className="preview-filename">{finding.file_path}</div>
          <div className="code-lines" aria-label={`Example code in ${finding.file_path}`}>
            {preview.lines.map((line, i) => (
              <div key={i} className={i === preview.highlight ? "code-line vulnerable" : "code-line"}>
                <span className="line-number">{preview.start + i}</span><code>{line || " "}</code>
              </div>
            ))}
          </div>
        </div>
        <div className="preview-finding" aria-live="polite">
          <span className={`severity-text severity-${finding.severity}`}>{finding.severity}</span>
          <h2>{preview.title}</h2>
          <p>{preview.description}</p>
          <Link href={`/bench/sample?finding=${finding.id}`} className="text-link">Inspect finding <ArrowRight size={16} /></Link>
        </div>
      </div>
      <div className="preview-footer"><span>3 findings</span><span>Review the diff. Keep the context.</span></div>
    </div>
  );
}
