# Design

## Product

Vernier is a pull-request review bench. Surfaces: marketing landing, scan form, review list, review detail.

## Color

Strategy: restrained on the bench, committed cobalt type on the landing. Seed hue 261.

| Role | Token | Value |
| --- | --- | --- |
| Background | `--bg` | `oklch(1 0 0)` |
| Surface | `--surface` | `oklch(0.965 0.008 261)` |
| Ink | `--ink` | `oklch(0.22 0.04 261)` |
| Primary | `--primary` | `oklch(0.42 0.20 261)` |
| Accent | `--accent` | `oklch(0.55 0.18 330)` |
| Muted | `--muted` | `oklch(0.52 0.024 261)` |

White text on primary and accent fills. Light theme locked. Magenta is reserved for critical severity and one landing underline.

## Typography

Geist Sans for interface and display. Geist Mono for diffs, hashes, line numbers. Fixed rem scale. Display tracking `-0.03em`.

## Layout

Landing: open white field, hairline cobalt rules, one paper artifact in the hero. Bench: 64px header, main column max 1120px, file rail plus findings.

## Components

Radius 4px everywhere. Primary button is a filled cobalt rectangle, not a pill. Findings expand inline. No nested cards.

## Motion

150-250ms opacity/transform on landing reveals. Bench transitions are state-only. Reduced motion disables both.
