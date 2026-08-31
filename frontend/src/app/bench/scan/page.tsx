import { ScanForm } from "@/components/bench/scan-form";

export const metadata = {
  title: "Scan",
};

export default function ScanPage() {
  return (
    <div className="mx-auto max-w-[720px] px-4 py-10">
      <h1 className="text-3xl font-semibold tracking-[-0.03em]">Scan a pull request</h1>
      <p className="mt-2 max-w-[54ch] text-[15px] text-muted">
        Point Vernier at a GitHub URL or paste a unified diff. Heuristics always run. The model runs only for uncached
        hunks.
      </p>
      <div className="mt-8">
        <ScanForm />
      </div>
    </div>
  );
}
