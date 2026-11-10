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
OUT = ROOT / "export" / "texas" / "ver1.pptx"
PHOTOS = ROOT / "Texas" / "slides"

NAVY = RGBColor(0x12, 0x3A, 0x63)
CREAM = RGBColor(0xFF, 0xFD, 0xF8)
GOLD = RGBColor(0xE8, 0xB8, 0x4A)
GOLD_INK = RGBColor(0xC2, 0x41, 0x0C)
INK = RGBColor(0x14, 0x20, 0x2C)
SEMI = "Segoe UI Semibold"
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FELT = RGBColor(0xE7, 0xD7, 0xB1)
FOOT = RGBColor(0x5C, 0x4B, 0x32)
PILL = RGBColor(0xFF, 0xF4, 0xDC)
GREEN = RGBColor(0x15, 0x80, 0x3D)
SUN = RGBColor(0xFF, 0xE0, 0x8A)
FONT = "Segoe UI"

SKIES = ["1d6aa5", "0e7490", "14532d", "b45309", "9a3412", "1e3a5f", "7c2d12", "0369a1", "3f6212", "1e40af", "0f766e", "123a63", "166534"]
GROUNDS = ["e8b84a", "d6d3d1", "86efac", "fdba74", "fcd34d", "fde68a", "fdba74", "93c5fd", "fbbf24", "7dd3fc", "bae6fd", "e8b84a", "86efac"]

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
            run.font.name = item.get("f") or FONT
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


def run(text, size=16, bold=False, color=INK, underline=False, font=None):
    return {"t": text, "s": size, "b": bold, "c": color, "u": underline, "f": font or (FONT if bold else SEMI)}


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


def add_photo_card(slide, index: int, credit: str) -> None:
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
    plain(pip, "T ★", 14, WHITE, True)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(x + 1.8), Mm(y + h - 16), Mm(w - 3.6), Mm(14))
    bar.name = f"Credit bar {index + 1}"
    fill(bar, RGBColor(0x0C, 0x27, 0x44))
    note = textbox(slide, x + 2, y + h - 15.5, w - 4, 13, f"Photo credit {index + 1}", "ctr")
    plain(note, credit, 10, WHITE, True, anchor="ctr")


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
    plain(title_box, title, 22, NAVY, True)
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


def build_hero(slide, item, index, total):
    title, subtitle = item["title"], item["subtitle"]
    add_photo_card(slide, index, item["credit"])
    add_spine(slide)
    star = slide.shapes.add_shape(MSO_SHAPE.STAR_5_POINT, Mm(152), Mm(28), Mm(16), Mm(16))
    star.name = "Lone star"
    fill(star, GOLD)
    heading = textbox(slide, 148, 48, 132, 24, "Hero title")
    plain(heading, title, 40, NAVY, True)
    sub = textbox(slide, 148, 76, 132, 28, "Subtitle")
    plain(sub, subtitle, 22, INK)
    who = textbox(slide, 148, 112, 132, 22, "Author")
    write(who, [para(run(line, 16, True, NAVY), before=1) for line in SCHOOL.split("\n")])
    add_footer(slide, index, total)


def build_bignum(slide, slide_data, index, total):
    add_photo_card(slide, index, slide_data["credit"])
    add_spine(slide)
    add_header(slide, slide_data["tag"], slide_data["title"])
    cards = sheet_cards(slide, 58, 118, 3)
    for (x, y, w, h, _), box in zip(cards, slide_data["boxes"]):
        value = textbox(slide, x + 1, y + 28, w - 2, 28, f"Number {box['value']}")
        bits = [run(box["value"], 32, True, NAVY)]
        if box.get("unit"):
            bits.append(run(" " + box["unit"], 14, True, GOLD))
        write(value, [para(*bits, align=PP_ALIGN.CENTER)], align=PP_ALIGN.CENTER, anchor="ctr")
        label = textbox(slide, x + 1, y + 58, w - 2, 42, f"Number label {box['value']}")
        plain(label, box["label"], 15, INK, align=PP_ALIGN.CENTER)
    add_footer(slide, index, total)


def build_grid(slide, slide_data, index, total, columns):
    add_photo_card(slide, index, slide_data["credit"])
    add_spine(slide)
    add_header(slide, slide_data["tag"], slide_data["title"])
    height = 128 if columns == 3 else 124
    cards = sheet_cards(slide, 52, height, columns, 3.2 if columns == 3 else 4)
    for i, ((x, y, w, h, _), box) in enumerate(zip(cards, slide_data["boxes"]), start=1):
        title = textbox(slide, x + 1, y + 6, w - 2, 22 if columns == 3 else 16, f"Card title {i}")
        plain(title, box["t"], 16 if columns == 3 else 18, NAVY, True)
        body = textbox(slide, x + 1, y + (28 if columns == 3 else 26), w - 2, h - (34 if columns == 3 else 32), f"Card text {i}")
        plain(body, box["d"], 14 if columns == 3 else 15, INK)
    add_footer(slide, index, total)


def build_timeline(slide, slide_data, index, total):
    add_photo_card(slide, index, slide_data["credit"])
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
        plain(label, item["step"], 13, NAVY, True, PP_ALIGN.CENTER)
        body = textbox(slide, x, 100, step, 70, f"Timeline text {i + 1}")
        plain(body, item["text"], 12, INK, align=PP_ALIGN.CENTER)
    add_footer(slide, index, total)


def body_runs(text: str, mark: str):
    size = 17
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
    add_photo_card(slide, index, slide_data["credit"])
    add_spine(slide)
    add_header(slide, slide_data["tag"], slide_data["title"])
    card = round_rect(slide, 146, 50, 136, 136, WHITE, "Story card", line=None, radius=0.06)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(152), Mm(54), Mm(124), Mm(1.5))
    bar.name = "Story accent"
    fill(bar, GOLD)
    heading = textbox(slide, 150, 58, 128, 22, "Story heading")
    plain(heading, slide_data["heading"], 20, NAVY, True)
    mark = slide_data.get("mark")
    if mark:
        letter = slide_data["body"][0]
        rest = slide_data["body"][1:].lstrip()
        cap = textbox(slide, 150, 84, 16, 20, "Drop cap")
        plain(cap, letter, 34, GOLD, True)
        body = textbox(slide, 166, 84, 110, 94, "Story")
        write(body, [para(*body_runs(rest, mark))])
    else:
        body = textbox(slide, 152, 84, 124, 94, "Story")
        plain(body, slide_data["body"], 18, INK)
    add_footer(slide, index, total)


def build_sources(slide, slide_data, index, total):
    add_photo_card(slide, index, slide_data["credit"])
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
        plain(words, item, 14, INK, anchor="ctr")
    add_footer(slide, index, total)


def felt(slide):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(0), Mm(0), Mm(297), Mm(210))
    shape.name = "Table"
    fill(shape, FELT)


SLIDES = [
    {"kind": "hero", "title": "Texas", "subtitle": "The Lone Star State. A place, its people, and one hard question.", "credit": "CupWithSoda19 · CC BY-SA 4.0 · Wikimedia Commons"},
    {
        "kind": "bignum", "tag": "Geographic orientation", "title": "Texas at a glance",
        "credit": "Carol M. Highsmith · public domain · Wikimedia Commons",
        "boxes": [
            {"value": "2nd", "label": "largest state, after Alaska"},
            {"value": "Austin", "label": "the capital"},
            {"value": "30", "unit": "million+", "label": "people, and still growing"},
        ],
    },
    {"kind": "story", "tag": "Physical geography", "title": "Rain, pines, and the Gulf", "heading": "The wet east", "credit": "Maciej Kraus · CC BY 2.0 · Wikimedia Commons", "body": "Pine woods and the Gulf coast get the most rain. Summers are hot and humid. Hurricanes can reach the shore."},
    {"kind": "story", "tag": "Physical geography", "title": "Rivers and rolling land", "heading": "Hills and plains", "credit": "Lorenzo The Snail · CC BY-SA 4.0 · Wikimedia Commons", "body": "The Hill Country sits between rivers and open plains. Winters are usually mild. Storms and a sudden cold can still arrive."},
    {"kind": "story", "tag": "Physical geography", "title": "Desert, canyons, little water", "heading": "The dry west", "credit": "Martin Proll · public domain · Wikimedia Commons", "body": "Big Bend holds desert, canyons, and mountains. Days are very hot. Nights can be cold, and water is scarce."},
    {
        "kind": "timeline", "tag": "History", "title": "How Texas became Texas",
        "credit": "DatraxMada · CC BY-SA 4.0 · Wikimedia Commons",
        "items": [
            {"step": "First nations", "text": "Caddo, Comanche, and Apache peoples lived here for centuries."},
            {"step": "Spain and Mexico", "text": "Missions came first. Later, Texas was part of Mexico."},
            {"step": "1836", "text": "Texas became an independent republic."},
            {"step": "1845", "text": "It joined the United States as the 28th state."},
            {"step": "1901", "text": "Oil at Spindletop changed the towns and the jobs."},
        ],
    },
    {
        "kind": "story", "tag": "Cultural identity", "title": "Many stories, one star",
        "heading": "More than one people", "mark": "Lone Star",
        "credit": "Ashland Thomas · CC BY-SA 4.0 · Wikimedia Commons",
        "body": "Many nations knew this land before any flag. Spanish and Mexican families built towns and a Tejano culture that is still here. Later came Anglo settlers, African Americans, Czechs, and Germans. The Lone Star is one symbol, not the whole story.",
    },
    {"kind": "story", "tag": "Economy", "title": "Oil, gas, and the wind", "heading": "Energy", "credit": "Matthew T Rader · CC BY-SA 4.0 · Wikimedia Commons", "body": "Texas produces oil and natural gas. It also leads the United States in wind power. That strength comes with a duty to use it carefully."},
    {
        "kind": "grid", "columns": 2, "tag": "Economy", "title": "Cities, ports, and ranches",
        "credit": "U.S. Fish and Wildlife Service · public domain · Wikimedia Commons",
        "boxes": [
            {"t": "Cities of ideas", "d": "Austin builds technology. Houston runs a great port and the Johnson Space Center."},
            {"t": "Land and cattle", "d": "Cotton and cattle still matter. Ranches keep an older picture of Texas alive."},
        ],
    },
    {
        "kind": "story", "tag": "Demographics and society", "title": "A state that keeps growing",
        "heading": "Cities and open country", "mark": "more than 30 million",
        "credit": "David Daniel Turner · CC BY 4.0 · Wikimedia Commons",
        "body": "Texas is home to more than 30 million people. Houston, Dallas, San Antonio, and Austin are huge, while much of the land is still ranches and small towns. About two in five residents are Hispanic or Latino. People move here for work, so schools and languages keep changing.",
    },
    {
        "kind": "grid", "columns": 2, "tag": "A current challenge", "title": "The week the power stopped",
        "credit": "Jno.skinner · CC BY-SA 4.0 · Wikimedia Commons",
        "boxes": [
            {"t": "What happened", "d": "In February 2021, extreme cold froze equipment. Millions of homes lost heat. Most of the grid is run by ERCOT, not by the national networks."},
            {"t": "A fair next step", "d": "Some want Texas to stay independent. Others want links to neighboring states. One practical step is to prepare plants and fuel lines for freezing weather."},
        ],
    },
    {
        "kind": "sources", "tag": "Evidence", "title": "Where these facts come from",
        "credit": "Montysayshello · CC BY-SA 4.0 · Wikimedia Commons",
        "pills": ["Geography", "History", "Economy", "Society"],
        "items": [
            "U.S. Census Bureau — population and communities",
            "Texas State Historical Association — the republic, 1845, and Spindletop",
            "National Weather Service — climate and the February 2021 storm",
            "ERCOT public reports — how most of the Texas grid is organized",
        ],
    },
    {"kind": "hero", "title": "Thank you", "subtitle": "Ask me one question: a place, a date, or the winter storm.", "credit": "Carol M. Highsmith · public domain · Wikimedia Commons"},
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
            build_hero(slide, item, index, total)
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
