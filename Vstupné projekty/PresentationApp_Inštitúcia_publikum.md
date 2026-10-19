# Systém 10 matíc — inštitúcia × publikum

Dve nezávislé osi: **inštitúcia** (pevná farebná kotva, nemení sa podľa publika) a **tier** (mení sa podľa toho, kto v danej chvíli prezentáciu vidí).

- **formal** (Tier 1) — odborné/externé publikum: komisia, externí experti, formálne hlasovanie. Najvyšší kontrast, "sviatočný" tón.
- **internal** (Tier 2) — interné pracovné publikum: kolegovia, vedenie, rada. Profesionálne, bez okázalosti.
- **public** (Tier 3) — laické/verejné publikum: obyvatelia, žiaci, klienti. Najprístupnejšie, najteplejšie, najviac vysvetľujúce.

V rámci jednej inštitúcie sa farebná rodina len "otvára" (formal) alebo "zjemňuje" (public) — nikdy nemení úplne inú farbu, aby publikum vždy rozpoznalo, "od koho" prezentácia je.

## Tabuľka

| # | CSS trieda | Inštitúcia | Tier | Primary | Secondary (okraj) | Gold-color (text) | BG | Radius | Kedy použiť |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `theme-ksk-formal` | KSK / Odbor sociálnych vecí | formal | `#0f172a` | `#c5a059` | `#c5a059` | `#f8fafc` | 8px | Odborná komisia, externí experti |
| 2 | `theme-ksk-internal` | KSK | internal | `#0f172a` | `#94a3b8` | `#475569` | `#f8fafc` | 10px | Kolegovia, vedenie odboru |
| 3 | `theme-ksk-public` | KSK | public | `#1e3a5f` | `#f59e0b` | `#b45309` | `#f4f8fb` | 14px | Klienti, verejnosť |
| 4 | `theme-sosa-formal` | SOŠ automobilová | formal | `#1c1917` | `#ea580c` | `#c2410c` | `#f5f5f4` | 4px | Vedenie školy, pedagogická rada |
| 5 | `theme-sosa-internal` | SOŠ automobilová | internal | `#292524` | `#fb923c` | `#ea580c` | `#fafaf9` | 8px | Kolegovia, predmetová komisia |
| 6 | `theme-sosa-public` | SOŠ automobilová | public | `#1e293b` | `#fbbf24` | `#d97706` | `#f8fafc` | 14px | Žiaci, študenti |
| 7 | `theme-hviezdica-formal` | SVB Hviezdica | formal | `#1c1917` | `#7c2d12` | `#7c2d12` | `#fafaf9` | 6px | Zhromaždenie vlastníkov, hlasovanie |
| 8 | `theme-hviezdica-internal` | SVB Hviezdica | internal | `#57534e` | `#9a3412` | `#9a3412` | `#f7f5f3` | 10px | Vedenie a členovia rady |
| 9 | `theme-hviezdica-public` | SVB Hviezdica | public | `#78350f` | `#c2410c` | `#9a3412` | `#fef3e2` | 18px | Obyvatelia bytového domu |
| 10 | `theme-neutral` | Neviazané | — | `#334155` | `#0ea5e9` | `#0369a1` | `#f8fafc` | 10px | Ad-hoc obsah bez inštitucionálnej väzby |

## Prečo `secondary` ≠ `gold-color`

`--secondary` sa používa ako okrajový akcent boxov (`border-left`) — tam môže byť aj svetlejší odtieň, funguje dekoratívne. `--gold-color` sa používa na farbu textu v `<strong>` — tam musí mať dostatočný kontrast na bielom/svetlom pozadí, preto je pri svetlejších `secondary` farbách (napr. `#94a3b8`, `#fbbf24`) zámerne tmavší.

## Pridanie 11. matice

Nový CSS blok v `engine/STATIC_master_template.html` (Vrstva 3) + záznam do `identity_matrix` v `prompts/system_instructions.json`. Nezasahuje do žiadnej existujúcej matice.