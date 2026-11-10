"""Texas deck as a native PowerPoint file: every card, line, and picture is its own shape."""

from __future__ import annotations

from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Mm, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "export" / "texas-maxim.pptx"
PHOTOS = ROOT / "Texas" / "slides"

NAVY = RGBColor(0x12, 0x3A, 0x63)
CREAM = RGBColor(0xFF, 0xFD, 0xF8)
GOLD = RGBColor(0xE8, 0xB8, 0x4A)
GOLD_INK = RGBColor(0xC2, 0x41, 0x0C)
INK = RGBColor(0x3E, 0x4C, 0x5A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FELT = RGBColor(0xE7, 0xD7, 0xB1)
FOOT = RGBColor(0x5C, 0x4B, 0x32)
PILL = RGBColor(0xFF, 0xF4, 0xDC)
GREEN = RGBColor(0x15, 0x80, 0x3D)
SUN = RGBColor(0xFF, 0xE0, 0x8A)
FONT = "Segoe UI"

SKIES = ["1d6aa5", "0e7490", "b45309", "7c2d12", "1e3a5f", "0369a1", "9a3412", "1e40af", "115e59", "123a63"]
GROUNDS = ["e8b84a", "86efac", "fdba74", "fcd34d", "93c5fd", "fde68a", "fb923c", "7dd3fc", "5eead4", "fbbf24"]

AUTHOR = "Maxim Hrehor  ·  Kvinta  ·  Lutheran Grammar School of J.A. Comenius"
SCHOOL = "Maxim Hrehor\nLutheran Grammar School of J.A. Comenius · Kvinta"


def rgb(hex_color: str) -> RGBColor:
    return RGBColor.from_string(hex_color)


def mix(a: RGBColor, b: RGBColor, t: float) -> RGBColor:
    return RGBColor(*(int(x + (y - x) * t) for x, y in zip(a, b)))


def shadow(shape) -> None:
    effect = etree.SubElement(shape._element.spPr, qn("a:effectLst"))
    shade = etree.SubElement(effect, qn("a:outerShdw"))
    shade.set("blurRad", "50800")
    shade.set("dist", "63500")
    shade.set("dir", "5400000")
    shade.set("algn", "bl")
    shade.set("rotWithShape", "0")
    color = etree.SubElement(shade, qn("a:srgbClr"))
    color.set("val", "123A63")
    etree.SubElement(color, qn("a:alpha")).set("val", "20000")


def fill(shape, color: RGBColor, line: RGBColor | None = None, width: float = 1.5) -> None:
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(width)


def round_rect(slide, x, y, w, h, color, name, line=NAVY, radius=0.08):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(x), Mm(y), Mm(w), Mm(h))
    shape.name = name
    fill(shape, color, line)
    try:
        shape.adjustments[0] = radius
    except Exception:
        pass
    shadow(shape)
    return shape


def textbox(slide, x, y, w, h, name, anchor="t"):
    shape = slide.shapes.add_textbox(Mm(x), Mm(y), Mm(w), Mm(h))
    shape.name = name
    frame = shape.text_frame
    frame.word_wrap = True
    frame.auto_size = None
    frame.margin_left = Mm(1.2)
    frame.margin_right = Mm(1.2)
    frame.margin_top = Mm(0.6)
    frame.margin_bottom = Mm(0.4)
    frame._txBody.bodyPr.set("anchor", {"t": "t", "ctr": "ctr", "b": "b"}[anchor])
    return shape


def write(shape, runs, *, align=PP_ALIGN.LEFT, anchor=None):
    frame = shape.text_frame
    frame.clear()
    if anchor:
        frame._txBody.bodyPr.set("anchor", anchor)
    first = True
    for paragraph in runs:
        p = frame.paragraphs[0] if first else frame.add_paragraph()
        first = False
        p.alignment = paragraph.get("align", align)
        p.space_before = Pt(paragraph.get("before", 0))
        p.space_after = Pt(paragraph.get("after", 0))
        for item in paragraph["runs"]:
            run = p.add_run()
            run.text = item["t"]
            run.font.name = FONT
            run.font.size = Pt(item.get("s", 14))
            run.font.bold = item.get("b", False)
            run.font.color.rgb = item.get("c", INK)
            if item.get("u"):
                run.font.underline = True
                rpr = run._r.get_or_add_rPr()
                ufill = etree.SubElement(rpr, qn("a:uFillTx"))
                # underline color follows the run; also force a gold line
                rpr.set("u", "sng")
                solid = etree.SubElement(rpr, qn("a:solidFill"))
                # keep text color already set; add underline fill separately
                solid.getparent().remove(solid)
                line = etree.SubElement(rpr, qn("a:uFill"))
                paint = etree.SubElement(line, qn("a:solidFill"))
                etree.SubElement(paint, qn("a:srgbClr")).set("val", "C2410C")
    return shape


def run(text, size=14, bold=False, color=INK, underline=False):
    return {"t": text, "s": size, "b": bold, "c": color, "u": underline}


def para(*runs, align=PP_ALIGN.LEFT, before=0, after=0):
    return {"runs": list(runs), "align": align, "before": before, "after": after}


def plain(shape, text, size, color, bold=False, align=PP_ALIGN.LEFT, anchor=None):
    return write(shape, [para(run(text, size, bold, color), align=align)], align=align, anchor=anchor)


def photo_path(index: int) -> Path | None:
    stem = f"{index + 1:02d}"
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        path = PHOTOS / f"{stem}{ext}"
        if path.is_file() and path.stat().st_size > 0:
            return path
    return None


def add_photo_card(slide, index: int) -> None:
    x, y, w, h = 8, 8, 112, 190
    sky = rgb(SKIES[index])
    ground = rgb(GROUNDS[index])
    card = round_rect(slide, x, y, w, h, sky, f"Photo card {index + 1}", radius=0.06)
    card.line.width = Pt(1.75)
    sun = slide.shapes.add_shape(MSO_SHAPE.OVAL, Mm(x + w * 0.62), Mm(y + 16), Mm(18), Mm(18))
    sun.name = f"Sun {index + 1}"
    fill(sun, SUN)
    hill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(x + 1.4), Mm(y + h * 0.56), Mm(w - 2.8), Mm(h * 0.42))
    hill.name = f"Hill {index + 1}"
    fill(hill, ground)
    try:
        hill.adjustments[0] = 0.5
    except Exception:
        pass
    ridge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(x + 1.4), Mm(y + h * 0.74), Mm(w - 2.8), Mm(h * 0.24))
    ridge.name = f"Ridge {index + 1}"
    fill(ridge, mix(ground, NAVY, 0.38))
    try:
        ridge.adjustments[0] = 0.5
    except Exception:
        pass
    image = photo_path(index)
    if image:
        picture = slide.shapes.add_picture(str(image), Mm(x + 1.6), Mm(y + 1.6), Mm(w - 3.2), Mm(h - 3.2))
        picture.name = f"Photo {index + 1:02d}"
    frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(x), Mm(y), Mm(w), Mm(h))
    frame.name = f"Photo frame {index + 1}"
    frame.fill.background()
    frame.line.color.rgb = NAVY
    frame.line.width = Pt(1.75)
    try:
        frame.adjustments[0] = 0.06
    except Exception:
        pass
    pip = textbox(slide, x + 3, y + 2, 22, 8, f"Pip {index + 1}")
    plain(pip, "T ★", 13, WHITE, True)
    pip2 = textbox(slide, x + w - 25, y + h - 10, 22, 8, f"Pip {index + 1} bottom")
    plain(pip2, "T ★", 13, WHITE, True, PP_ALIGN.RIGHT)
    pip2.rotation = 180.0


def add_spine(slide) -> None:
    x, y, w, h = 127, 8, 162, 190
    card = round_rect(slide, x, y, w, h, CREAM, "Text card", radius=0.045)
    card.line.width = Pt(1.75)
    spine = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(x + 2.2), Mm(y + 2.2), Mm(14), Mm(h - 4.4))
    spine.name = "Texas"
    fill(spine, NAVY)
    letters = textbox(slide, x + 2.2, y + 42, 14, h - 84, "Texas title", "ctr")
    write(
        letters,
        [para(run(ch, 18, True, GOLD), align=PP_ALIGN.CENTER, before=0, after=0) for ch in "Texas"],
        align=PP_ALIGN.CENTER,
        anchor="ctr",
    )


def add_footer(slide, index: int, total: int) -> None:
    left = textbox(slide, 8, 199.5, 230, 8, "Footer")
    plain(left, AUTHOR, 11, FOOT, True, anchor="ctr")
    right = textbox(slide, 240, 199.5, 49, 8, "Slide number")
    plain(right, f"Slide {index + 1}/{total}", 11, FOOT, True, PP_ALIGN.RIGHT, "ctr")


def add_header(slide, tag: str, title: str) -> float:
    tag_box = textbox(slide, 146, 13, 136, 6, "Section")
    plain(tag_box, tag.upper(), 11, GOLD, True)
    title_box = textbox(slide, 146, 19, 136, 22, "Title")
    plain(title_box, title, 20, NAVY, True)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(148), Mm(42.5), Mm(132), Mm(1.1))
    line.name = "Title rule"
    fill(line, GOLD)
    return 46


def sheet_cards(slide, top, height, count, gap=3.5):
    width = 136
    card_w = (width - gap * (count - 1)) / count
    boxes = []
    for i in range(count):
        x = 146 + i * (card_w + gap)
        boxes.append((x, top, card_w, height, round_rect(slide, x, top, card_w, height, WHITE, f"Card {i + 1}", line=None, radius=0.08)))
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(x + 3), Mm(top + 2.2), Mm(card_w - 6), Mm(1.4))
        bar.name = f"Card accent {i + 1}"
        fill(bar, GOLD)
    return boxes


def build_hero(slide, title, subtitle, index, total):
    add_photo_card(slide, index)
    add_spine(slide)
    star = slide.shapes.add_shape(MSO_SHAPE.STAR_5_POINT, Mm(152), Mm(28), Mm(16), Mm(16))
    star.name = "Lone star"
    fill(star, GOLD)
    heading = textbox(slide, 148, 48, 132, 24, "Hero title")
    plain(heading, title, 40, NAVY, True)
    sub = textbox(slide, 148, 76, 132, 28, "Subtitle")
    plain(sub, subtitle, 20, INK)
    who = textbox(slide, 148, 112, 132, 22, "Author")
    write(who, [para(run(line, 16, True, NAVY), before=1) for line in SCHOOL.split("\n")])
    add_footer(slide, index, total)


def build_bignum(slide, slide_data, index, total):
    add_photo_card(slide, index)
    add_spine(slide)
    add_header(slide, slide_data["tag"], slide_data["title"])
    cards = sheet_cards(slide, 58, 118, 3)
    for (x, y, w, h, _), box in zip(cards, slide_data["boxes"]):
        value = textbox(slide, x + 1, y + 28, w - 2, 28, f"Number {box['value']}")
        bits = [run(box["value"], 28, True, NAVY)]
        if box.get("unit"):
            bits.append(run(" " + box["unit"], 13, True, GOLD))
        write(value, [para(*bits, align=PP_ALIGN.CENTER)], align=PP_ALIGN.CENTER, anchor="ctr")
        label = textbox(slide, x + 1, y + 58, w - 2, 42, f"Number label {box['value']}")
        plain(label, box["label"], 13, INK, align=PP_ALIGN.CENTER)
    add_footer(slide, index, total)


def build_grid(slide, slide_data, index, total, columns):
    add_photo_card(slide, index)
    add_spine(slide)
    add_header(slide, slide_data["tag"], slide_data["title"])
    height = 128 if columns == 3 else 124
    cards = sheet_cards(slide, 52, height, columns, 3.2 if columns == 3 else 4)
    for i, ((x, y, w, h, _), box) in enumerate(zip(cards, slide_data["boxes"]), start=1):
        title = textbox(slide, x + 1, y + 6, w - 2, 22 if columns == 3 else 16, f"Card title {i}")
        plain(title, box["t"], 14 if columns == 3 else 16, NAVY, True)
        body = textbox(slide, x + 1, y + (28 if columns == 3 else 24), w - 2, h - (34 if columns == 3 else 30), f"Card text {i}")
        plain(body, box["d"], 12 if columns == 3 else 13, INK)
    add_footer(slide, index, total)


def build_timeline(slide, slide_data, index, total):
    add_photo_card(slide, index)
    add_spine(slide)
    add_header(slide, slide_data["tag"], slide_data["title"])
    items = slide_data["items"]
    left, width = 148, 132
    step = width / len(items)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(left + 6), Mm(78), Mm(width - 12), Mm(1.3))
    line.name = "Timeline"
    fill(line, GOLD)
    for i, item in enumerate(items):
        x = left + i * step
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Mm(x + step / 2 - 3.2), Mm(74.6), Mm(6.4), Mm(6.4))
        dot.name = f"Timeline dot {i + 1}"
        fill(dot, GOLD if i % 2 else GOLD_INK, WHITE, 1.25)
        label = textbox(slide, x, 84, step, 16, f"Timeline label {i + 1}")
        plain(label, item["step"], 12, NAVY, True, PP_ALIGN.CENTER)
        body = textbox(slide, x, 100, step, 70, f"Timeline text {i + 1}")
        plain(body, item["text"], 11, INK, align=PP_ALIGN.CENTER)
    add_footer(slide, index, total)


def body_runs(text: str, mark: str):
    size = 15
    if mark not in text:
        return [run(text, size, False, INK)]
    before, after = text.split(mark, 1)
    parts = []
    if before:
        parts.append(run(before, size, False, INK))
    parts.append(run(mark, size, True, NAVY, True))
    if after:
        parts.append(run(after, size, False, INK))
    return parts


def build_story(slide, slide_data, index, total):
    add_photo_card(slide, index)
    add_spine(slide)
    add_header(slide, slide_data["tag"], slide_data["title"])
    card = round_rect(slide, 146, 50, 136, 136, WHITE, "Story card", line=None, radius=0.06)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(152), Mm(54), Mm(124), Mm(1.5))
    bar.name = "Story accent"
    fill(bar, GOLD)
    heading = textbox(slide, 150, 58, 128, 22, "Story heading")
    plain(heading, slide_data["heading"], 18, NAVY, True)
    letter = slide_data["body"][0]
    rest = slide_data["body"][1:]
    cap = textbox(slide, 150, 82, 16, 20, "Drop cap")
    plain(cap, letter, 32, GOLD, True)
    body = textbox(slide, 166, 82, 110, 96, "Story")
    mark = slide_data["mark"]
    # The drop cap already shows the first letter, so the paragraph continues without it.
    continued = rest.lstrip()
    write(body, [para(*body_runs(continued, mark))])
    add_footer(slide, index, total)


def build_sources(slide, slide_data, index, total):
    add_photo_card(slide, index)
    add_spine(slide)
    add_header(slide, slide_data["tag"], slide_data["title"])
    x = 146
    for i, pill in enumerate(slide_data["pills"]):
        px = x + i * 33
        round_rect(slide, px, 50, 31, 9, PILL, f"Pill {pill}", line=None, radius=0.5)
        label = textbox(slide, px, 50.4, 31, 8, f"Pill label {pill}", "ctr")
        plain(label, pill, 11, NAVY, True, PP_ALIGN.CENTER, "ctr")
    for i, item in enumerate(slide_data["items"]):
        y = 64 + i * 29
        row = round_rect(slide, 146, y, 136, 26, WHITE, f"Source {i + 1}", line=None, radius=0.12)
        mark = slide.shapes.add_shape(MSO_SHAPE.OVAL, Mm(151), Mm(y + 7), Mm(10), Mm(10))
        mark.name = f"Check {i + 1}"
        fill(mark, WHITE, GREEN, 1.5)
        tick = textbox(slide, 151, y + 7.2, 10, 9, f"Check mark {i + 1}", "ctr")
        plain(tick, "✓", 11, GREEN, True, PP_ALIGN.CENTER, "ctr")
        words = textbox(slide, 163, y + 2, 114, 22, f"Source text {i + 1}", "ctr")
        plain(words, item, 13, INK, anchor="ctr")
    add_footer(slide, index, total)


def felt(slide):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(0), Mm(0), Mm(297), Mm(210))
    shape.name = "Table"
    fill(shape, FELT)


SLIDES = [
    {"kind": "hero", "title": "Texas", "subtitle": "The Lone Star State — place, people, and one hard question."},
    {
        "kind": "bignum", "tag": "Geographic orientation", "title": "Texas at a glance",
        "boxes": [
            {"value": "2nd", "label": "largest U.S. state by area, after Alaska"},
            {"value": "Austin", "label": "the capital, in the Texas Hill Country"},
            {"value": "30", "unit": "million+", "label": "people live here, and the number is still growing"},
        ],
    },
    {
        "kind": "grid", "columns": 3, "tag": "Physical geography and climate",
        "title": "Three landscapes, three kinds of weather",
        "boxes": [
            {"t": "The wet east", "d": "Pine woods and the Gulf coast get heavy rain. Summers are hot and humid, and hurricanes can reach the shore."},
            {"t": "Hills and plains", "d": "The Hill Country rolls between rivers. Winters are usually mild, but storms and sudden cold can still arrive."},
            {"t": "The dry west", "d": "Big Bend holds desert, canyons, and mountains. Days are very hot, nights can be cold, and water is scarce."},
        ],
    },
    {
        "kind": "timeline", "tag": "History", "title": "How Texas became Texas",
        "items": [
            {"step": "First nations", "text": "Caddo, Comanche, Apache, and coastal peoples lived here for centuries."},
            {"step": "Spain and Mexico", "text": "Missions came first. Later, Texas was a region of Mexico."},
            {"step": "1836", "text": "Texas became an independent republic after the revolution."},
            {"step": "1845", "text": "The republic joined the United States as the 28th state."},
            {"step": "1901", "text": "Oil at Spindletop changed the towns, the jobs, and the future."},
        ],
    },
    {
        "kind": "story", "tag": "Cultural identity", "title": "Many stories under one star",
        "heading": "A place shaped by more than one people", "mark": "Lone Star",
        "body": "Many nations knew this land long before any flag. Spanish and Mexican families then built towns, ranches, and a Tejano culture that is still part of daily life. Later came Anglo settlers, African Americans, and European immigrants, including Czechs and Germans. The Lone Star is one symbol. The culture was never only one story.",
    },
    {
        "kind": "grid", "columns": 3, "tag": "Economy and industry", "title": "What keeps Texas working",
        "boxes": [
            {"t": "Energy", "d": "Texas produces oil and natural gas, and it also leads the United States in wind power. Energy is a strength and a responsibility."},
            {"t": "Cities of ideas", "d": "Austin builds technology. Houston runs one of the busiest ports in the country and the Johnson Space Center, home of NASA."},
            {"t": "Land and cattle", "d": "Cotton and cattle still matter. Ranches and farms connect today’s economy with the older picture of Texas."},
        ],
    },
    {
        "kind": "story", "tag": "Demographics and society", "title": "Cities, countryside, and new neighbors",
        "heading": "A large state that keeps growing", "mark": "more than 30 million",
        "body": "Texas is home to more than 30 million people. Houston, Dallas, San Antonio, and Austin are huge cities, while long stretches of the state are still ranches and small towns. About two in five residents are Hispanic or Latino. Many others are White, Black, or Asian. People move here for work, so neighborhoods, schools, and languages keep changing.",
    },
    {
        "kind": "grid", "columns": 2, "tag": "A current challenge", "title": "When a winter storm stopped the power",
        "boxes": [
            {"t": "What happened", "d": "In February 2021, extreme cold froze equipment across Texas. Millions of homes lost electricity and heat. Most of the state’s power is run by its own grid, ERCOT, not by the national networks."},
            {"t": "A fair next step", "d": "Some people want Texas to keep an independent grid. Others want stronger links to neighboring states. A practical step, supported by later reviews, is to prepare plants and fuel lines for freezing weather."},
        ],
    },
    {
        "kind": "sources", "tag": "Evidence", "title": "Where these facts come from",
        "pills": ["Geography", "History", "Economy", "Society"],
        "items": [
            "U.S. Census Bureau — population size and the mix of communities",
            "Texas State Historical Association — the republic, statehood in 1845, and Spindletop",
            "National Weather Service — climate regions and the February 2021 winter storm",
            "ERCOT public reports — how most of the Texas electricity grid is organized",
        ],
    },
    {"kind": "hero", "title": "Thank you", "subtitle": "Ask me one question: a place, a date, or the winter storm."},
]


def build() -> Path:
    prs = Presentation()
    prs.slide_width = Mm(297)
    prs.slide_height = Mm(210)
    prs.core_properties.title = "Texas"
    prs.core_properties.author = "Maxim Hrehor"
    blank = prs.slide_layouts[6]
    total = len(SLIDES)
    for index, item in enumerate(SLIDES):
        slide = prs.slides.add_slide(blank)
        felt(slide)
        kind = item["kind"]
        if kind == "hero":
            build_hero(slide, item["title"], item["subtitle"], index, total)
        elif kind == "bignum":
            build_bignum(slide, item, index, total)
        elif kind == "grid":
            build_grid(slide, item, index, total, item["columns"])
        elif kind == "timeline":
            build_timeline(slide, item, index, total)
        elif kind == "story":
            build_story(slide, item, index, total)
        elif kind == "sources":
            build_sources(slide, item, index, total)
    OUT.parent.mkdir(exist_ok=True)
    prs.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build())
