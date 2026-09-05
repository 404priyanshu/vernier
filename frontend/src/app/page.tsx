import { CacheHit } from "@/components/landing/cache-hit";
import { CloseCta } from "@/components/landing/close-cta";
import { Hero } from "@/components/landing/hero";
import { Kinds } from "@/components/landing/kinds";
import { Workflow } from "@/components/landing/workflow";

export default function HomePage() {
  return (
    <>
      <Hero />
      <Workflow />
      <CacheHit />
      <Kinds />
      <CloseCta />
    </>
  );
}
