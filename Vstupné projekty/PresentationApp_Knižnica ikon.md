# Knižnica ikon

## Pravidlo opätovného použitia

Pred generovaním novej ikony vždy over, či niektorá z existujúcich 16 sémanticky sedí. Nová ikona sa generuje len vtedy, keď žiadna z knižnice nevyhovuje — cieľom je vizuálna konzistencia naprieč jedným aj naprieč viacerými deckami.

## Bázová knižnica (16 ikon)

| Kľúč | Motív | Typické použitie |
|---|---|---|
| `doc` | dokument | všeobecný odkaz na dokument/podanie |
| `trend` | rastúci graf | trendy, vývoj, nárast |
| `building` | budova | inštitúcia, zariadenie, VÚC |
| `money` | bankovka/euro | financovanie, úhrady, rozpočet |
| `users` | skupina ľudí | klienti, zamestnanci, tím |
| `shield` | štít | ochrana, bezpečnosť, garancia |
| `contract` | dokument s fajkou | zmluva, schválenie |
| `home` | dom | bývanie, domácnosť |
| `calendar` | kalendár | termín, lehota, harmonogram |
| `system` | databáza/systém | IS SoS, register, evidencia |
| `alert` | výstražný trojuholník | riziko, upozornenie |
| `scale` | váhy | právo, spravodlivosť, rovnováha |
| `chart` | stĺpcový graf | štatistika, porovnanie |
| `heart` | srdce | starostlivosť, humánny rozmer |
| `arrowRight` | šípka | postup, ďalší krok |
| `history` | hodiny/história | minulosť, vývoj v čase |

## Technické pravidlá

- `viewBox="0 0 24 24"` povinné.
- Žiadne `width`/`height` atribúty priamo na `<svg>` — veľkosť rieši CSS `.card-icon`.
- Žiadne `stroke`/`fill` atribúty priamo v SVG kóde — farbu dedí `.card-icon svg { stroke: currentColor; fill: none }` z CSS, takže tá istá ikona funguje vo všetkých 10 témach bez úpravy.
- Ikona a nadpis boxu (`box-title`) sa renderujú vždy spolu v jednom riadku cez `.card-header` (flex row) — rieši funkcia `card()` v engine, negeneruje sa ručne.

## Štýl ikony podľa tier (keď treba generovať novú)

| Tier | Štýl | Motívy |
|---|---|---|
| `formal` | Minimalistické, tenké čiary (line-art), technické | paragrafy, váhy, grafy, dokumenty, štíty |
| `internal` | Procesné, štruktúrované, hrubšie čiary | ozubené kolesá, siete, checklisty, foldre |
| `public` | Priateľské, zaoblené, plnšie tvary | srdce, dom, rodina, podaná ruka, žiarovka |

## Pridanie ikony do bázovej knižnice natrvalo

Ak sa nová ikona ukáže ako opakovane potrebná (použitá 2+ krát naprieč rôznymi deckami), pridaj ju do objektu `ICONS` v `engine/STATIC_master_template.html` a zapíš do tabuľky vyššie — inak zostáva len jednorazovo inline v dátach daného slide-u.