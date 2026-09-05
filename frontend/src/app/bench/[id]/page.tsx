import { notFound } from "next/navigation";
import { getReview } from "@/lib/api";
import { ReviewPoller } from "@/components/bench/review-poller";

export const dynamic = "force-dynamic";

export default async function ReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const review = await getReview(id).catch(() => null);
  if (!review) notFound();
  return (
    <div className="page-container app-page">
      <ReviewPoller initial={review} />
    </div>
  );
}
