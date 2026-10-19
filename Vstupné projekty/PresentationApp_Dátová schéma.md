# Dátová schéma

## Vstup pred generovaním (5 povinných polí)

| Pole | Hodnoty | Poznámka |
|---|---|---|
| `institution` | `ksk` \| `sosa` \| `hviezdica` \| `neutral` | Určuje farebnú rodinu (pozri THEME-MATRIX.md) |
| `audience_tier` | `formal` \| `internal` \| `public` | Určuje odstín + tón textu (pozri CONTENT-GUIDELINES.md) |
| `format` | `static` \| `dynamic` | Static = PDF/tlač, Dynamic = interaktívne premietanie |
| `author` | meno + inštitúcia | Používa sa v pätičke a v poďakovaní (rieši aj gramatický rod) |
| zdrojový text | voľný text/téma | Podklad, z ktorého sa generuje obsah slide-ov |

`institution` + `audience_tier` sa spoja na názov CSS triedy: `theme-{institution}-{tier}` (napr. `sosa` + `internal` → `theme-sosa-internal`). Výnimka: `neutral` nemá tier, používa sa vždy `theme-neutral`.

## Výstup: pole `data`

Každý prvok poľa `data` je jeden slide:

```ts
type Slide = {
  theme: string;        // "ksk-formal" | "sosa-internal" | ... | "neutral"
  template: string;      // "hero" | "grid-4" | "grid-3" | "grid-2-airy"
                          // | "grid-1" | "single-block" | "list" | "timeline-horizontal"
  tag?: string;           // label nad nadpisom (nie pri hero)
  title: string;
  subtitle?: string;      // len hero
  author?: string;        // len hero, inak sa berie globálna premenná AUTHOR
  boxes?: Box[];          // grid-4 / grid-3 / grid-2-airy / grid-1
  heading?: string;       // single-block
  body?: string;          // single-block — voľné HTML
  items?: ListItem[];     // list
  steps?: TimelineStep[]; // timeline-horizontal
}

type Box = { icon?: string; t: string; d: string }
type ListItem = { t: string; d: string }
type TimelineStep = { date: string; t: string; d: string }
```

## Štrukturálne pravidlá (vynucuje `presentation_structure_rules`)

1. Prvý slide vždy `template: "hero"`.
2. Predposledný slide = zhrnutie (odporúčané `grid-4` alebo `list`).
3. Posledný slide vždy `template: "hero"` (poďakovanie, gramatický rod podľa `AUTHOR`).
4. Ostatné slidy — ľubovoľná kombinácia zvyšných šablón podľa obsahu.

## Validácia pred renderom

- Počet `boxes` sedí so šablónou (grid-4 potrebuje presne 4 a pod.).
- Každé `theme` existuje v `THEME-MATRIX.md` (case-sensitive, presne 10 platných hodnôt).
- `icon` (ak je uvedený) odkazuje na existujúci kľúč v `ICONS` alebo obsahuje vlastné inline SVG s `viewBox="0 0 24 24"` bez `width`/`height`/`stroke`/`fill` atribútov.