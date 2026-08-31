# Product

## Register

product

## Platform

web

## Users

Staff engineers and security-minded reviewers who open a GitHub pull request and need a second pass before merge. They work from a laptop, often late, and already know how to read a diff. The landing page speaks to the same person before they point Vernier at a URL.

## Product Purpose

Vernier inspects a pull request diff for bugs, security issues, and performance anti-patterns. It combines local heuristic detectors with batched LLM analysis, caches prompt and result hashes in Redis, stores the review in PostgreSQL, and returns a fix plus a test stub for each finding. Success is a review the engineer can act on without paying the model twice for the same hunk.

## Positioning

Measure the diff once, cache the work, and ship the finding with a fix and a test.

## Brand Personality

Precise, calm, instrumental. Copy sounds like a bench note, not a launch post. Three words: measured, specific, quiet.

## Anti-references

Dark SOC dashboards with neon threat maps. Purple "AI copilot" marketing. Inter-on-slate SaaS templates. Three identical feature cards. Fake 99% accuracy meters.

## Design Principles

- Show the finding, not the theater.
- A measurement tool earns trust by being specific.
- Cache hits are a product feature, not an implementation detail.
- The landing page and the bench share one visual language.

## Accessibility & Inclusion

WCAG AA contrast on body and controls. Keyboard access for scan, list, and finding expansion. Honor prefers-reduced-motion. Severity is never color-only.
