export function formatWhen(iso: string | null | undefined) {
  if (!iso) return "pending";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function prLabel(repo: string | null, number: number | null) {
  if (repo && number) return `${repo}#${number}`;
  if (repo) return repo;
  return "Pasted diff";
}

export function severityRank(severity: string) {
  return { critical: 0, high: 1, medium: 2, low: 3, info: 4 }[severity] ?? 9;
}
