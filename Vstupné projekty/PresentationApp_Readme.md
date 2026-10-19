# PDF Pres-Gen Engine

Systém na generovanie A4 landscape prezentácií (PDF-tlačiteľných aj interaktívnych), kde sa vizuálna identita automaticky odvodí od toho, **kto** prezentuje a **komu**.

## Ako to funguje (v troch krokoch)

1. **Vstup.** Zadáš 5 vecí: `institution`, `audience_tier`, `format` (Static/Dynamic), `author`, zdrojový text/téma. Presná definícia v [`docs/DATA-SCHEMA.md`](docs/DATA-SCHEMA.md).
2. **Generovanie obsahu.** `prompts/system_instructions.json` sa použije ako inštrukcia pre jazykový model — ten vráti pole `data = [...]` (obsah rozdelený do slide-ov, každý s priradenou šablónou a prípadne ikonami).
3. **Render.** Pole `data` sa vloží do `engine/STATIC_master_template.html` (alebo Dynamic verzie) — ten obsahuje fixný engine, všetky šablóny aj všetkých 10 farebných tém a z dát vyrenderuje hotový HTML dokument.

## Prečo je to takto rozdelené

Engine (rozmer strany, anti-overflow logika) sa **nikdy nemení**. Šablóny (rozloženie obsahu) a témy (farby podľa inštitúcie/publika) sú **nezávislé osi** — kombinujú sa voľne, pridanie novej z nich nezasahuje do ostatných. Detaily v [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Kam sa pozrieť podľa toho, čo riešiš

| Riešim... | Súbor |
|---|---|
| Aká farba/téma patrí ktorej situácii | `docs/THEME-MATRIX.md` |
| Aké rozloženie obsahu (šablóny) mám k dispozícii | `docs/TEMPLATE-LIBRARY.md` |
| Presný tvar JSON dát pre jeden slide | `docs/DATA-SCHEMA.md` |
| Ako má znieť text pre daný typ publika | `docs/CONTENT-GUIDELINES.md` |
| Ktoré ikony už existujú, nech negenerujem duplicity | `docs/ICON-LIBRARY.md` |
| Chcem upraviť prompt pre generujúci model | `prompts/system_instructions.json` |
| Chcem upraviť samotný render (CSS/JS) | `engine/STATIC_master_template.html` |

## Stav / ďalšie kroky

- [x] Static (tlač/PDF) master template — hotový, v4.3
- [x] Systém 10 farebných matíc (KSK / SOŠa automobilová / SVB Hviezdica / neutrálna)
- [x] Knižnica 8 šablón vrátane `timeline-horizontal`
- [x] SVG ikony s bázovou knižnicou 16 ikon
- [ ] Dynamic (interaktívny) master template — treba doplniť rovnaké vrstvy 2+3 ako v Static
- [ ] Skutočná "aplikácia" okolo tohto (formulár na vstup + volanie modelu + stiahnutie výstupu) — zatiaľ sa workflow spúšťa manuálne