const STYLES: Record<string, string> = {
  queued: "text-muted",
  running: "text-primary",
  completed: "text-ink",
  failed: "text-accent",
};

export function StatusPill({ status }: { status: string }) {
  return <span className={`text-[12px] font-medium uppercase tracking-wide ${STYLES[status] || "text-muted"}`}>{status}</span>;
}
