# Obsahové pravidlá

## Tón podľa tier

| Tier | Tón | Príklad publika |
|---|---|---|
| `formal` | Odborný, striktný, legislatívne presný | komisia, externí experti, formálne hlasovanie |
| `internal` | Kolegiálny, procesne orientovaný | kolegovia, vedenie, rada |
| `public` | Ľudský, vysvetľujúci, motivujúci | laici, žiaci, obyvatelia, klienti |

## Pravidlá pre text v poli `d` (popis boxu)

- Vždy plynulý súvislý text, **25 až 35 slov**. Nie strohé odrážky.
- Žiadne skratky v nadpisoch (`title`, `t`) okrem `SR` a `EUR` — odborné skratky (VÚC, ZpS a pod.) sa vždy rozpíšu na celé slová.

## Zvýrazňovanie (3 úrovne, nezamieňať)

| Značka | Farba | Použitie |
|---|---|---|
| `<strong>text</strong>` | `var(--gold-color)` | 1–2 kľúčové pojmy v boxe |
| `<span class="law-ref">§ X ods. Y</span>` | čierna, tučná | odkaz na konkrétne zákonné ustanovenie |
| `<span class="highlight-red">text</span>` | červená, tučná | **len** skutočne kritické upozornenia (nové sankcie, zmeny s okamžitou platnosťou) — používať striedmo |

## Poďakovanie (posledný hero slide)

- Analyzuj gramatický rod z `author` a uprav sloveso: *"Rád zodpoviem"* (muž) vs. *"Rada zodpoviem"* (žena). Ak rod nie je jasný, formuluj neutrálne (napr. *"Priestor pre otázky a diskusiu"*).
- Nepoužívať frázu "prečítajte si zákon" ani podobné odkazujúce na samoštúdium namiesto priamej pomoci.

## Keď je zdrojového textu málo

Negenerovať vymyslený obsah na doplnenie chýbajúcich slide-ov. Namiesto toho upozorniť používateľa, že podklad nestačí na požadovaný počet/rozsah slide-ov, a vyžiadať doplnenie.