import { CacheHit } from "@/components/landing/cache-hit";
import { CloseCta } from "@/components/landing/close-cta";
import { Hero } from "@/components/landing/hero";
import { Kinds } from "@/components/landing/kinds";
import { Showcase } from "@/components/landing/showcase";
import { Workflow } from "@/components/landing/workflow";

export default function HomePage() {
  return (
    <>
      <Hero />
      <Workflow />
      <Showcase />
      <CacheHit />
      <Kinds />
      <CloseCta />
    </>
  );
}
