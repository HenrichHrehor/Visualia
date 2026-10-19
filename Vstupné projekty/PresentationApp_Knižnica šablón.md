# Knižnica šablón obsahu

8 šablón. Výber je vždy ručný (explicitný v dátach), podľa objemu a povahy textu daného slide-u — nie automatický.

| Šablóna | Rozloženie | Kedy použiť |
|---|---|---|
| `hero` | Celoplošný gradient, centrovaný text | Úvod, záver/poďakovanie |
| `grid-4` | 2×2 mriežka, 4 boxy | 4 rovnocenné krátke body |
| `grid-3` | 1 rad, 3 boxy | 3 body, o niečo viac priestoru na box |
| `grid-2-airy` | 1 rad, 2 boxy, veľký padding | 2 husté/právne texty |
| `grid-1` | 1 veľký centrovaný box | Jedna dlhšia, zdôraznená myšlienka |
| `single-block` | 1 blok voľného obsahu (podporuje aj HTML tabuľku) | Dlhší súvislý text, sankcie/tabuľky |
| `list` | Zvislý zoznam s číslovaným markerom | Postupnosť krokov, chronológia |
| `timeline-horizontal` | Vodorovná os s prepojovacou čiarou | Harmonogram, etapy s dátumami |

## Tvar dát podľa šablóny

### `hero`
```json
{ "theme": "ksk-formal", "template": "hero",
  "title": "...", "subtitle": "...", "author": "..." }
```

### `grid-4` / `grid-3` / `grid-2-airy` / `grid-1`
```json
{ "theme": "sosa-internal", "template": "grid-4",
  "tag": "Voliteľný label nad nadpisom",
  "title": "...",
  "boxes": [
    { "icon": "ICONS.doc", "t": "Nadpis boxu", "d": "25–35 slov, môže obsahovať <strong> a <span class='law-ref'>" }
  ]
}
```
Počet položiek v `boxes` sa musí zhodovať so šablónou (grid-4 → 4, grid-3 → 3, grid-2-airy → 2, grid-1 → 1).

### `single-block`
```json
{ "theme": "ksk-public", "template": "single-block",
  "tag": "...", "title": "...",
  "heading": "Nadpis bloku",
  "body": "Voľný HTML obsah — text, <ul>, alebo celá <table>."
}
```

### `list`
```json
{ "theme": "hviezdica-internal", "template": "list",
  "tag": "...", "title": "...",
  "items": [ { "t": "...", "d": "..." } ]
}
```
Odporúčaný počet položiek: 3–6 (viac pôsobí natlačene, keďže výška sa delí rovnomerne).

### `timeline-horizontal`
```json
{ "theme": "sosa-formal", "template": "timeline-horizontal",
  "tag": "...", "title": "...",
  "steps": [ { "date": "31.12.2026", "t": "...", "d": "..." } ]
}
```

## Pridanie novej šablóny

1. Nový CSS blok pre `.content.<nazov>` vo Vrstve 2 (musí použiť `flex`/`grid` s `1fr`, nikdy pevnú výšku v px).
2. Nová položka v objekte `renderers` v JS.
3. Zápis do `template_vocabulary` v `system_instructions.json`.

Nezasahuje do enginu ani do žiadnej existujúcej šablóny.