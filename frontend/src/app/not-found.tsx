import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-[640px] px-4 py-24">
      <h1 className="text-3xl font-semibold tracking-[-0.03em]">That review is not on the bench</h1>
      <p className="mt-3 text-[15px] text-muted">The id is missing, or the API is not running.</p>
      <Link href="/bench" className="mt-6 inline-block text-primary underline underline-offset-4">
        Back to the bench
      </Link>
    </div>
  );
}
