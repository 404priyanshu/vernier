import Link from "next/link";
import { Reveal } from "./reveal";

export function CloseCta() {
  return (
    <section className="mx-auto max-w-[1120px] px-4 py-24 text-center">
      <Reveal>
        <h2 className="text-[2.4rem] font-semibold leading-[1.05] tracking-[-0.03em] text-primary text-balance md:text-[4.5rem]">
          Point it at a pull request
        </h2>
        <p className="mt-5 text-[18px] text-primary">Vernier reads your diffs like a flight plan.</p>
        <Link
          href="/bench/scan"
          className="mt-8 inline-flex bg-primary px-6 py-3 text-[15px] text-white transition-colors duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] hover:bg-[oklch(0.36_0.19_261)] active:scale-[0.98]"
        >
          Scan a pull request
        </Link>
      </Reveal>
    </section>
  );
}
