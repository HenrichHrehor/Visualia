"""Texas v2: photos keep their own shape, and each slide has an editable fact underneath."""

from __future__ import annotations

from pathlib import Path

import pymupdf
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Mm, Pt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "export" / "texas" / "ver2.pptx"
PHOTOS = ROOT / "Texas" / "slides"

NAVY = RGBColor(0x12, 0x3A, 0x63)
GOLD = RGBColor(0xE8, 0xB8, 0x4A)
INK = RGBColor(0x14, 0x20, 0x2C)
WHITE = RGBColor(0xFF, 0xFD, 0xF8)
PAPER = RGBColor(0xF6, 0xEF, 0xE2)
FOOT = RGBColor(0x5C, 0x4B, 0x32)
CREAM = RGBColor(0xFF, 0xF4, 0xDC)
GREEN = RGBColor(0x15, 0x80, 0x3D)
FONT = "Segoe UI"
SEMI = "Segoe UI Semibold"

AUTHOR = "Maxim Hrehor  ·  Kvinta  ·  Lutheran Grammar School of J.A. Comenius"
SCHOOL = "Maxim Hrehor\nLutheran Grammar School of J.A. Comenius · Kvinta"


def fill(shape, color, line=None):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1.25)


def textbox(slide, x, y, w, h, name, anchor="t"):
    shape = slide.shapes.add_textbox(Mm(x), Mm(y), Mm(w), Mm(h))
    shape.name = name
    frame = shape.text_frame
    frame.word_wrap = True
    frame.auto_size = None
    frame.margin_left = Mm(0.8)
    frame.margin_right = Mm(0.8)
    frame.margin_top = Mm(0.4)
    frame.margin_bottom = Mm(0.2)
    frame._txBody.bodyPr.set("anchor", {"t": "t", "ctr": "ctr", "b": "b"}[anchor])
    return shape


def write(shape, paragraphs, align=PP_ALIGN.LEFT, anchor=None):
    frame = shape.text_frame
    frame.clear()
    if anchor:
        frame._txBody.bodyPr.set("anchor", anchor)
    first = True
    for paragraph in paragraphs:
        p = frame.paragraphs[0] if first else frame.add_paragraph()
        first = False
        p.alignment = paragraph.get("align", align)
        p.space_before = Pt(paragraph.get("before", 0))
        p.space_after = Pt(paragraph.get("after", 0))
        for item in paragraph["runs"]:
            run = p.add_run()
            run.text = item["t"]
            run.font.name = item.get("f", SEMI)
            run.font.size = Pt(item["s"])
            run.font.bold = item.get("b", False)
            run.font.italic = item.get("i", False)
            run.font.color.rgb = item.get("c", INK)
            if item.get("u"):
                run.font.underline = True
                rpr = run._r.get_or_add_rPr()
                line = etree.SubElement(rpr, qn("a:uFill"))
                paint = etree.SubElement(line, qn("a:solidFill"))
                etree.SubElement(paint, qn("a:srgbClr")).set("val", "C2410C")
    return shape


def R(text, size, bold=False, color=INK, italic=False, underline=False, font=None):
    return {"t": text, "s": size, "b": bold, "c": color, "i": italic, "u": underline, "f": font or (FONT if bold else SEMI)}


def P(*runs, align=PP_ALIGN.LEFT, before=0, after=0):
    return {"runs": list(runs), "align": align, "before": before, "after": after}


def plain(shape, text, size, color, bold=False, align=PP_ALIGN.LEFT, anchor=None, italic=False):
    return write(shape, [P(R(text, size, bold, color, italic), align=align)], align=align, anchor=anchor)


def photo_box(path: Path, box_w: float, box_h: float):
    pix = pymupdf.Pixmap(str(path))
    scale = min(box_w / pix.width, box_h / pix.height)
    return pix.width * scale, pix.height * scale


def chrome(slide, index, total, fact, credit):
    paper = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Mm(297), Mm(210))
    paper.name = "Paper"
    fill(paper, PAPER)
    rail = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(10), Mm(12), Mm(13), Mm(184))
    rail.name = "Texas"
    fill(rail, NAVY)
    try:
        rail.adjustments[0] = 0.5
    except Exception:
        pass
    letters = textbox(slide, 10, 48, 13, 110, "Texas title", "ctr")
    write(letters, [P(R(ch, 15, True, GOLD), align=PP_ALIGN.CENTER, before=0, after=0) for ch in "Texas"], align=PP_ALIGN.CENTER, anchor="ctr")
    frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(30), Mm(12), Mm(108), Mm(74))
    frame.name = f"Photo mat {index + 1}"
    fill(frame, WHITE)
    try:
        frame.adjustments[0] = 0.08
    except Exception:
        pass
    path = PHOTOS / f"{index + 1:02d}.jpg"
    pw, ph = photo_box(path, 100, 66)
    picture = slide.shapes.add_picture(str(path), Mm(30 + (108 - pw) / 2), Mm(12 + (74 - ph) / 2), Mm(pw), Mm(ph))
    picture.name = f"Photo {index + 1:02d}"
    cap = textbox(slide, 30, 87, 108, 8, f"Credit {index + 1}")
    plain(cap, credit, 10, FOOT, True)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(30), Mm(98), Mm(1.6), Mm(22))
    bar.name = f"Fact rule {index + 1}"
    fill(bar, GOLD)
    quote = textbox(slide, 33, 96, 105, 28, "Fact")
    plain(quote, fact, 16, NAVY, True)
    left = textbox(slide, 30, 198, 180, 8, "Footer")
    plain(left, AUTHOR, 11, FOOT, True, anchor="ctr")
    right = textbox(slide, 230, 198, 55, 8, "Slide number")
    plain(right, f"Slide {index + 1}/{total}", 11, FOOT, True, PP_ALIGN.RIGHT, "ctr")


def header(slide, tag, title):
    tag_box = textbox(slide, 148, 12, 136, 7, "Section")
    plain(tag_box, tag.upper(), 12, RGBColor(0xB5, 0x81, 0x2E), True)
    title_box = textbox(slide, 148, 19, 136, 20, "Title")
    plain(title_box, title, 24, NAVY, True)
    rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(148), Mm(40), Mm(132), Mm(1.2))
    rule.name = "Title rule"
    fill(rule, GOLD)


def hero(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"])
    star = slide.shapes.add_shape(MSO_SHAPE.STAR_5_POINT, Mm(148), Mm(18), Mm(14), Mm(14))
    star.name = "Lone star"
    fill(star, GOLD)
    kicker = textbox(slide, 148, 36, 136, 8, "School")
    plain(kicker, "LUTHERAN GRAMMAR SCHOOL", 12, RGBColor(0xB5, 0x81, 0x2E), True)
    title = textbox(slide, 148, 46, 136, 24, "Hero title")
    plain(title, item["title"], 40, NAVY, True)
    sub = textbox(slide, 148, 74, 136, 28, "Subtitle")
    plain(sub, item["subtitle"], 20, INK)
    who = textbox(slide, 148, 108, 136, 22, "Author")
    write(who, [P(R(line, 16, True, NAVY), before=1) for line in SCHOOL.split("\n")])


def bignum(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"])
    header(slide, item["tag"], item["title"])
    width = (132 - 8) / 3
    for i, box in enumerate(item["boxes"]):
        x = 148 + i * (width + 4)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(x), Mm(52), Mm(width), Mm(120))
        card.name = f"Number card {i + 1}"
        fill(card, WHITE)
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(x + 4), Mm(56), Mm(width - 8), Mm(1.5))
        accent.name = f"Number accent {i + 1}"
        fill(accent, GOLD)
        value = textbox(slide, x + 1, 78, width - 2, 24, f"Number {box['value']}")
        bits = [R(box["value"], 28, True, NAVY)]
        if box.get("unit"):
            bits.append(R(" " + box["unit"], 13, True, RGBColor(0xC4, 0x92, 0x2E)))
        write(value, [P(*bits, align=PP_ALIGN.CENTER)], align=PP_ALIGN.CENTER, anchor="ctr")
        label = textbox(slide, x + 1, 106, width - 2, 36, f"Number label {box['value']}")
        plain(label, box["label"], 14, INK, align=PP_ALIGN.CENTER)


def story(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"])
    header(slide, item["tag"], item["title"])
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(148), Mm(50), Mm(136), Mm(136))
    card.name = "Story card"
    fill(card, WHITE)
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(156), Mm(56), Mm(120), Mm(1.5))
    accent.name = "Story accent"
    fill(accent, GOLD)
    heading = textbox(slide, 154, 62, 124, 18, "Story heading")
    plain(heading, item["heading"], 20, NAVY, True)
    mark = item.get("mark")
    if mark:
        cap = textbox(slide, 154, 84, 14, 18, "Drop cap")
        plain(cap, item["body"][0], 32, GOLD, True)
        body = textbox(slide, 168, 84, 110, 92, "Story")
        rest = item["body"][1:].lstrip()
        before, after = rest.split(mark, 1)
        runs = []
        if before:
            runs.append(R(before, 16))
        runs.append(R(mark, 16, True, NAVY, underline=True))
        if after:
            runs.append(R(after, 16))
        write(body, [P(*runs)])
    else:
        body = textbox(slide, 154, 84, 124, 92, "Story")
        plain(body, item["body"], 18, INK)


def grid(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"])
    header(slide, item["tag"], item["title"])
    gap = 6
    width = (136 - gap) / 2
    for i, box in enumerate(item["boxes"]):
        x = 148 + i * (width + gap)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(x), Mm(50), Mm(width), Mm(132))
        card.name = f"Card {i + 1}"
        fill(card, WHITE)
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(x + 4), Mm(55), Mm(width - 8), Mm(1.5))
        accent.name = f"Card accent {i + 1}"
        fill(accent, GOLD)
        title = textbox(slide, x + 2, 60, width - 4, 18, f"Card title {i + 1}")
        plain(title, box["t"], 18, NAVY, True)
        body = textbox(slide, x + 2, 80, width - 4, 90, f"Card text {i + 1}")
        plain(body, box["d"], 15, INK)


def timeline(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"])
    header(slide, item["tag"], item["title"])
    items = item["items"]
    left, width = 148, 136
    step = width / len(items)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(left + 8), Mm(78), Mm(width - 16), Mm(1.3))
    line.name = "Timeline"
    fill(line, GOLD)
    for i, entry in enumerate(items):
        x = left + i * step
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Mm(x + step / 2 - 3), Mm(74.8), Mm(6), Mm(6))
        dot.name = f"Timeline dot {i + 1}"
        fill(dot, GOLD if i % 2 else RGBColor(0xC2, 0x41, 0x0C), WHITE)
        label = textbox(slide, x, 84, step, 16, f"Timeline label {i + 1}")
        plain(label, entry["step"], 13, NAVY, True, PP_ALIGN.CENTER)
        body = textbox(slide, x, 100, step, 72, f"Timeline text {i + 1}")
        plain(body, entry["text"], 12, INK, align=PP_ALIGN.CENTER)


def sources(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"])
    header(slide, item["tag"], item["title"])
    for i, pill in enumerate(item["pills"]):
        x = 148 + i * 33
        chip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(x), Mm(48), Mm(31), Mm(9))
        chip.name = f"Pill {pill}"
        fill(chip, CREAM)
        try:
            chip.adjustments[0] = 0.5
        except Exception:
            pass
        label = textbox(slide, x, 48.3, 31, 8, f"Pill label {pill}", "ctr")
        plain(label, pill, 11, NAVY, True, PP_ALIGN.CENTER, "ctr")
    for i, text in enumerate(item["items"]):
        y = 62 + i * 30
        row = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(148), Mm(y), Mm(136), Mm(26))
        row.name = f"Source {i + 1}"
        fill(row, WHITE)
        mark = slide.shapes.add_shape(MSO_SHAPE.OVAL, Mm(153), Mm(y + 8), Mm(9), Mm(9))
        mark.name = f"Check {i + 1}"
        fill(mark, WHITE, GREEN)
        tick = textbox(slide, 153, y + 8.2, 9, 8, f"Check mark {i + 1}", "ctr")
        plain(tick, "✓", 11, GREEN, True, PP_ALIGN.CENTER, "ctr")
        words = textbox(slide, 164, y + 2, 116, 22, f"Source text {i + 1}", "ctr")
        plain(words, text, 14, INK, anchor="ctr")


SLIDES = [
    {"kind": "hero", "title": "Texas", "subtitle": "The Lone Star State. A place, its people, and one hard question.", "credit": "CupWithSoda19 · CC BY-SA 4.0 · Wikimedia Commons", "fact": "One star on the flag. Many stories behind it."},
    {"kind": "bignum", "tag": "Geographic orientation", "title": "Texas at a glance", "credit": "Carol M. Highsmith · public domain · Wikimedia Commons", "fact": "Only Alaska covers more ground.", "boxes": [
        {"value": "2nd", "label": "largest state, after Alaska"},
        {"value": "Austin", "label": "the capital"},
        {"value": "30", "unit": "million+", "label": "people, and still growing"},
    ]},
    {"kind": "story", "tag": "Physical geography", "title": "Rain, pines, and the Gulf", "heading": "The wet east", "credit": "Maciej Kraus · CC BY 2.0 · Wikimedia Commons", "fact": "The east gets the rain the west never sees.", "body": "Pine woods and the Gulf coast get the most rain. Summers are hot and humid. Hurricanes can reach the shore."},
    {"kind": "story", "tag": "Physical geography", "title": "Rivers and rolling land", "heading": "Hills and plains", "credit": "Lorenzo The Snail · CC BY-SA 4.0 · Wikimedia Commons", "fact": "The Hill Country rolls. It does not lie flat.", "body": "The Hill Country sits between rivers and open plains. Winters are usually mild. Storms and a sudden cold can still arrive."},
    {"kind": "story", "tag": "Physical geography", "title": "Desert, canyons, little water", "heading": "The dry west", "credit": "Martin Proll · public domain · Wikimedia Commons", "fact": "Out here, water is the real border.", "body": "Big Bend holds desert, canyons, and mountains. Days are very hot. Nights can be cold, and water is scarce."},
    {"kind": "timeline", "tag": "History", "title": "How Texas became Texas", "credit": "DatraxMada · CC BY-SA 4.0 · Wikimedia Commons", "fact": "A republic in 1836. A state in 1845.", "items": [
        {"step": "First nations", "text": "Caddo, Comanche, and Apache peoples lived here for centuries."},
        {"step": "Spain and Mexico", "text": "Missions came first. Later, Texas was part of Mexico."},
        {"step": "1836", "text": "Texas became an independent republic."},
        {"step": "1845", "text": "It joined the United States as the 28th state."},
        {"step": "1901", "text": "Oil at Spindletop changed the towns and the jobs."},
    ]},
    {"kind": "story", "tag": "Cultural identity", "title": "Many stories, one star", "heading": "More than one people", "mark": "Lone Star", "credit": "Ashland Thomas · CC BY-SA 4.0 · Wikimedia Commons", "fact": "The Lone Star is a symbol, not the whole people.", "body": "Many nations knew this land before any flag. Spanish and Mexican families built towns and a Tejano culture that is still here. Later came Anglo settlers, African Americans, Czechs, and Germans. The Lone Star is one symbol, not the whole story."},
    {"kind": "story", "tag": "Economy", "title": "Oil, gas, and the wind", "heading": "Energy", "credit": "Matthew T Rader · CC BY-SA 4.0 · Wikimedia Commons", "fact": "Oil under the ground. Wind above it.", "body": "Texas produces oil and natural gas. It also leads the United States in wind power. That strength comes with a duty to use it carefully."},
    {"kind": "grid", "tag": "Economy", "title": "Cities, ports, and ranches", "credit": "U.S. Fish and Wildlife Service · public domain · Wikimedia Commons", "fact": "A ranch and a space center share one state.", "boxes": [
        {"t": "Cities of ideas", "d": "Austin builds technology. Houston runs a great port and the Johnson Space Center."},
        {"t": "Land and cattle", "d": "Cotton and cattle still matter. Ranches keep an older picture of Texas alive."},
    ]},
    {"kind": "story", "tag": "Demographics and society", "title": "A state that keeps growing", "heading": "Cities and open country", "mark": "more than 30 million", "credit": "David Daniel Turner · CC BY 4.0 · Wikimedia Commons", "fact": "About two in five Texans are Hispanic or Latino.", "body": "Texas is home to more than 30 million people. Houston, Dallas, San Antonio, and Austin are huge, while much of the land is still ranches and small towns. About two in five residents are Hispanic or Latino. People move here for work, so schools and languages keep changing."},
    {"kind": "grid", "tag": "A current challenge", "title": "The week the power stopped", "credit": "Jno.skinner · CC BY-SA 4.0 · Wikimedia Commons", "fact": "In 2021, cold stopped the power.", "boxes": [
        {"t": "What happened", "d": "In February 2021, extreme cold froze equipment. Millions of homes lost heat. Most of the grid is run by ERCOT, not by the national networks."},
        {"t": "A fair next step", "d": "Some want Texas to stay independent. Others want links to neighboring states. One practical step is to prepare plants and fuel lines for freezing weather."},
    ]},
    {"kind": "sources", "tag": "Evidence", "title": "Where these facts come from", "credit": "Montysayshello · CC BY-SA 4.0 · Wikimedia Commons", "fact": "If it has no source, it is not a fact yet.", "pills": ["Geography", "History", "Economy", "Society"], "items": [
        "U.S. Census Bureau — population and communities",
        "Texas State Historical Association — the republic, 1845, and Spindletop",
        "National Weather Service — climate and the February 2021 storm",
        "ERCOT public reports — how most of the Texas grid is organized",
    ]},
    {"kind": "hero", "title": "Thank you", "subtitle": "Ask me one question: a place, a date, or the winter storm.", "credit": "Carol M. Highsmith · public domain · Wikimedia Commons", "fact": "Leave me one question."},
]


def build() -> Path:
    prs = Presentation()
    prs.slide_width = Mm(297)
    prs.slide_height = Mm(210)
    prs.core_properties.title = "Texas"
    prs.core_properties.author = "Maxim Hrehor"
    blank = prs.slide_layouts[6]
    total = len(SLIDES)
    makers = {"hero": hero, "bignum": bignum, "story": story, "grid": grid, "timeline": timeline, "sources": sources}
    for index, item in enumerate(SLIDES):
        slide = prs.slides.add_slide(blank)
        makers[item["kind"]](slide, item, index, total)
    OUT.parent.mkdir(exist_ok=True)
    prs.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build())
