"""Tlačové HTML zo vstupných projektov uloží ako PDF a ako PPTX so vzhľadom strany."""

from __future__ import annotations

import subprocess
from io import BytesIO
from pathlib import Path

import fitz
from pptx import Presentation
from pptx.util import Emu

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Vstupné projekty"
OUT = ROOT / "export"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

JOBS = [
    ("DOCTYPE_SVG_Static.html", "ksk-reforma-svg"),
    ("DOCTYPE_JUDr_07082026_c.html", "ksk-reforma-c"),
    ("DOCTYPE_JUDr_07082026.html", "ksk-reforma-original"),
    ("DOCTYPE_JUDr_07082026_b.html", "ksk-reforma-airy"),
    ("DOCTYPE_SOŠa_AdaptiveTiersDemo_Static.html", "sosa-skolsky-zakon"),
    ("DOCTYPE_Lightblue_AIRy_Static.html", "vuc-lightblue"),
    ("Demonštrácia rovnomerného pohybu_IV_Hrehor.html", "pohyb-rovnomerny"),
    ("Ukážka vizuálnych prvkov_Claude.html", "vizualne-prvky"),
]

SOSA_TIERS = {
    "sosa-tier1": [0, 3, 6, 9, 12],
    "sosa-tier2": [1, 4, 7, 10, 13],
    "sosa-tier3": [2, 5, 8, 11, 14],
}


def html_to_pdf(html: Path, pdf: Path) -> None:
    pdf.parent.mkdir(parents=True, exist_ok=True)
    if pdf.exists():
        pdf.unlink()
    cmd = [
        str(CHROME),
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--disable-extensions",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=12000",
        f"--print-to-pdf={pdf}",
        html.resolve().as_uri(),
    ]
    subprocess.run(cmd, check=True, timeout=180)
    if not pdf.exists() or pdf.stat().st_size < 1000:
        raise RuntimeError(f"PDF sa nevytvorilo: {pdf}")


def is_blank(page: fitz.Page) -> bool:
    if page.get_text().strip():
        return False
    pix = page.get_pixmap(matrix=fitz.Matrix(0.15, 0.15), alpha=False)
    return (sum(pix.samples) / len(pix.samples)) > 248


def trim_blank_pages(pdf: Path) -> int:
    doc = fitz.open(pdf)
    changed = False
    while len(doc) > 1 and is_blank(doc[-1]):
        doc.delete_page(-1)
        changed = True
    count = len(doc)
    if changed:
        tmp = pdf.with_suffix(".trim.pdf")
        doc.save(tmp, garbage=4, deflate=True)
        doc.close()
        tmp.replace(pdf)
    else:
        doc.close()
    return count


def pdf_to_pptx(pdf: Path, pptx: Path, pages: list[int] | None = None) -> int:
    doc = fitz.open(pdf)
    indexes = pages if pages is not None else list(range(len(doc)))
    first = doc[indexes[0]]
    prs = Presentation()
    prs.slide_width = Emu(int(first.rect.width / 72 * 914400))
    prs.slide_height = Emu(int(first.rect.height / 72 * 914400))
    blank = prs.slide_layouts[6]
    for index in indexes:
        page = doc[index]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.7, 1.7), alpha=False)
        slide = prs.slides.add_slide(blank)
        slide.shapes.add_picture(
            BytesIO(pix.tobytes("png")),
            0,
            0,
            prs.slide_width,
            prs.slide_height,
        )
    prs.save(pptx)
    doc.close()
    return len(indexes)


def split_sosa(pdf: Path) -> None:
    doc = fitz.open(pdf)
    if len(doc) < 15:
        doc.close()
        raise RuntimeError(f"SOŠa PDF má {len(doc)} strán, očakávam aspoň 15.")
    for name, pages in SOSA_TIERS.items():
        part = fitz.open()
        for index in pages:
            part.insert_pdf(doc, from_page=index, to_page=index)
        target = OUT / f"{name}.pdf"
        part.save(target, garbage=4, deflate=True)
        part.close()
        pdf_to_pptx(target, OUT / f"{name}.pptx")
        print(f"  {name}: {len(pages)} stran")
    doc.close()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for filename, stem in JOBS:
        html = SRC / filename
        pdf = OUT / f"{stem}.pdf"
        print(f"PDF  {filename}")
        html_to_pdf(html, pdf)
        pages = trim_blank_pages(pdf)
        count = pdf_to_pptx(pdf, OUT / f"{stem}.pptx")
        print(f"     {pages} stran -> {stem}.pptx ({count})")
        if stem == "sosa-skolsky-zakon":
            split_sosa(pdf)


if __name__ == "__main__":
    main()
