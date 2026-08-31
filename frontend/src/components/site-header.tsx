"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { List, X } from "@phosphor-icons/react";
import { Mark } from "./mark";

const LINKS = [
  { href: "/#how", label: "How it works" },
  { href: "/bench", label: "Bench" },
  { href: "/docs", label: "Docs" },
];

export function SiteHeader() {
  const path = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-20 border-b border-rule bg-bg/95 backdrop-blur-sm">
      <div className="mx-auto flex h-16 max-w-[1120px] items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2.5 text-ink">
          <Mark className="h-7 w-7" />
          <span className="text-[15px] font-semibold tracking-tight">Vernier</span>
        </Link>
        <nav className="hidden items-center gap-8 text-[14px] md:flex" aria-label="Primary">
          {LINKS.map((link) => {
            const active = path === link.href || (link.href !== "/" && path.startsWith(link.href));
            return (
              <Link
                key={link.href}
                href={link.href}
                className={active ? "text-ink" : "text-muted hover:text-ink"}
              >
                {link.label}
              </Link>
            );
          })}
          <Link
            href="/bench/scan"
            className="bg-primary px-3.5 py-2 text-white transition-colors duration-200 ease-[cubic-bezier(0.16,1,0.3,1)] hover:bg-[oklch(0.36_0.19_261)] active:scale-[0.98]"
          >
            Scan a pull request
          </Link>
        </nav>
        <button
          type="button"
          className="md:hidden"
          aria-expanded={open}
          aria-label={open ? "Close menu" : "Open menu"}
          onClick={() => setOpen((value) => !value)}
        >
          {open ? <X size={22} /> : <List size={22} />}
        </button>
      </div>
      {open ? (
        <nav className="flex flex-col gap-3 border-t border-rule px-4 py-4 md:hidden" aria-label="Mobile">
          {LINKS.map((link) => (
            <Link key={link.href} href={link.href} onClick={() => setOpen(false)} className="py-1">
              {link.label}
            </Link>
          ))}
          <Link
            href="/bench/scan"
            onClick={() => setOpen(false)}
            className="bg-primary px-3.5 py-2 text-center text-white"
          >
            Scan a pull request
          </Link>
        </nav>
      ) : null}
    </header>
  );
}
