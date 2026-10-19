# Architektúra: 3 nezávislé vrstvy

Celý systém stojí na oddelení troch vecí, ktoré sa v pôvodných (ručne písaných) prezentáciách miešali dokopy do jedného súboru. Ich rozdelenie je dôvod, prečo sa dá pridať nová téma alebo šablóna bez rizika, že sa niečo pokazí inde.

## Vrstva 1 — Engine (nemenná)

Zaručuje jedinú vec, na ktorej všetko stojí: **1 slide = 1 tlačená strana**, vždy A4 landscape, nikdy pretečený ani orezaný obsah.

Obsahuje:
- `@page { size: A4 landscape; margin: 0 }`
- `.slide` s pevným rozmerom `297mm × 210mm`, flex-column vnútro
- `page-break-after: always` na každom slide (Static verzia)
- `print-color-adjust: exact` — zachová farby pri tlači/PDF exporte
- anti-overflow pravidlo: `.content { flex: 1 }` — obsah sa vždy natiahne presne na dostupný priestor, nikdy nepretečie ani nezostane prázdny

Táto vrstva sa **nikdy needituje** pri tvorbe novej prezentácie. Zmena tu = zmena pre všetky doterajšie aj budúce decky naraz, preto sa robí len zámerne a naraz vo všetkých master súboroch.

## Vrstva 2 — Šablóny obsahu (rozšíriteľná knižnica)

Definujú, ako sa `.content` rozdelí na boxy. Každá šablóna je vopred vyladená tak, aby sa jej typický obsah vždy zmestil do pevného kontajnera z vrstvy 1.

Plný zoznam a presný tvar dát pre každú: [`TEMPLATE-LIBRARY.md`](TEMPLATE-LIBRARY.md).

Pridanie novej šablóny = jeden nový CSS blok + jedna render funkcia v `renderers` objekte. Nezasahuje do enginu ani do ostatných šablón.

## Vrstva 3 — Témy (farby podľa inštitúcie × publika)

Rieši len farby, zaoblenie rohov a mieru formálnosti typografie — nikdy nie štruktúru rozloženia. 10 konkrétnych kombinácií: [`THEME-MATRIX.md`](THEME-MATRIX.md).

Kľúčové pravidlo: **inštitúcia (hue) sa nemení podľa publika** — mení sa len "tier" v rámci tej istej farebnej rodiny. Vlastník bytu má vidieť tú istú "Hviezdicu" ako člen rady, len v prívetivejšom prevedení.

## Ako sa osi kombinujú

Jeden slide = `{ theme: "sosa-formal", template: "grid-4", ... }`. Téma a šablóna sa volia **nezávisle** — ktorákoľvek šablóna funguje s ktoroukoľvek témou bez úprav CSS. Výber je vždy explicitný (ručne v dátach), nie automatický podľa dĺžky textu — automatické zmenšovanie/zalamovanie textu za behu je zámerne vylúčené, pretože je nespoľahlivé pri tlačovom exporte (prehliadač meria layout inak než tlačový engine).

## Vzťah Static ↔ Dynamic

Nie je to jeden súbor s `@media print` prepínačom, ale **dva samostatné HTML súbory** zdieľajúce identickú vrstvu 2 a 3 (renderery aj CSS premenné tém sú zámerne rovnaké, len vrstva 1 sa líši — Static má `page-break-after`, Dynamic má `.slide.active` + navigáciu). Content dáta (`const data = [...]`) sú kompatibilné medzi oboma bez úprav.