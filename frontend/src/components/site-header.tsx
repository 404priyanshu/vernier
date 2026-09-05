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
    <header className="site-header">
      <div className="page-container header-inner">
        <Link href="/" className="wordmark" aria-label="Vernier home" onClick={() => setOpen(false)}>
          <Mark className="brand-mark" /><span>Vernier</span>
        </Link>
        <nav className="desktop-nav" aria-label="Primary">
          {LINKS.map((link) => (
            <Link key={link.href} href={link.href} aria-current={path.startsWith(link.href) ? "page" : undefined}>{link.label}</Link>
          ))}
          <Link href="/bench/scan" className="button button-primary button-small">Scan a pull request</Link>
        </nav>
        <button className="menu-toggle" aria-label={open ? "Close menu" : "Open menu"} aria-expanded={open} aria-controls="mobile-navigation" onClick={() => setOpen(!open)}>
          {open ? <X size={24} /> : <List size={24} />}
        </button>
      </div>
      {open && <nav id="mobile-navigation" className="mobile-nav" aria-label="Mobile">
        {LINKS.map((link) => <Link key={link.href} href={link.href} onClick={() => setOpen(false)}>{link.label}</Link>)}
        <Link href="/bench/scan" className="button button-primary" onClick={() => setOpen(false)}>Scan a pull request</Link>
      </nav>}
    </header>
  );
}
