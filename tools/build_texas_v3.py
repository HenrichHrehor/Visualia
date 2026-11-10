"""Texas v3: .gov photographs, place name in the white window, ISO 690 list after the close."""

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
OUT = ROOT / "export" / "texas" / "ver3.pptx"
PHOTOS = ROOT / "Texas" / "gov"

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


def chrome(slide, index, total, fact, credit, place, image=None):
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
    frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(30), Mm(20), Mm(108), Mm(134))
    frame.name = f"Photo mat {index + 1}"
    fill(frame, WHITE)
    try:
        frame.adjustments[0] = 0.08
    except Exception:
        pass
    where = textbox(slide, 34, 23, 100, 16, f"Place {index + 1}")
    plain(where, place, 13, NAVY, True)
    path = PHOTOS / image if image else PHOTOS / f"{index + 1:02d}.jpg"
    pw, ph = photo_box(path, 100, 72)
    picture = slide.shapes.add_picture(str(path), Mm(34 + (100 - pw) / 2), Mm(40 + (72 - ph) / 2), Mm(pw), Mm(ph))
    picture.name = f"Photo {index + 1:02d}"
    cap = textbox(slide, 34, 114, 100, 34, f"Credit {index + 1}")
    plain(cap, credit, 11, FOOT, True)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(30), Mm(158), Mm(1.6), Mm(22))
    bar.name = f"Fact rule {index + 1}"
    fill(bar, GOLD)
    quote = textbox(slide, 33, 156, 105, 26, "Fact")
    plain(quote, fact, 16, NAVY, True)
    left = textbox(slide, 30, 198, 180, 8, "Footer")
    plain(left, AUTHOR, 11, FOOT, True, anchor="ctr")
    right = textbox(slide, 230, 198, 55, 8, "Slide number")
    plain(right, f"Slide {index + 1}/{total}", 11, FOOT, True, PP_ALIGN.RIGHT, "ctr")


def header(slide, tag, title):
    tag_box = textbox(slide, 148, 28, 136, 7, "Section")
    plain(tag_box, tag.upper(), 12, RGBColor(0xB5, 0x81, 0x2E), True)
    title_box = textbox(slide, 148, 35, 136, 18, "Title")
    plain(title_box, title, 24, NAVY, True)
    rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(148), Mm(54), Mm(132), Mm(1.2))
    rule.name = "Title rule"
    fill(rule, GOLD)


def hero(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"], item["place"], item.get("image"))
    star = slide.shapes.add_shape(MSO_SHAPE.STAR_5_POINT, Mm(148), Mm(48), Mm(14), Mm(14))
    star.name = "Lone star"
    fill(star, GOLD)
    kicker = textbox(slide, 148, 66, 136, 8, "School")
    plain(kicker, "LUTHERAN GRAMMAR SCHOOL", 12, RGBColor(0xB5, 0x81, 0x2E), True)
    title = textbox(slide, 148, 76, 136, 24, "Hero title")
    plain(title, item["title"], 40, NAVY, True)
    sub = textbox(slide, 148, 104, 136, 28, "Subtitle")
    plain(sub, item["subtitle"], 20, INK)
    who = textbox(slide, 148, 136, 136, 22, "Author")
    write(who, [P(R(line, 16, True, NAVY), before=1) for line in SCHOOL.split("\n")])


def bignum(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"], item["place"], item.get("image"))
    header(slide, item["tag"], item["title"])
    width = (132 - 8) / 3
    for i, box in enumerate(item["boxes"]):
        x = 148 + i * (width + 4)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(x), Mm(62), Mm(width), Mm(114))
        card.name = f"Number card {i + 1}"
        fill(card, WHITE)
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(x + 4), Mm(68), Mm(width - 8), Mm(1.5))
        accent.name = f"Number accent {i + 1}"
        fill(accent, GOLD)
        value = textbox(slide, x + 1, 92, width - 2, 24, f"Number {box['value']}")
        bits = [R(box["value"], 28, True, NAVY)]
        if box.get("unit"):
            bits.append(R(" " + box["unit"], 13, True, RGBColor(0xC4, 0x92, 0x2E)))
        write(value, [P(*bits, align=PP_ALIGN.CENTER)], align=PP_ALIGN.CENTER, anchor="ctr")
        label = textbox(slide, x + 1, 120, width - 2, 40, f"Number label {box['value']}")
        plain(label, box["label"], 14, INK, align=PP_ALIGN.CENTER)


def story(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"], item["place"], item.get("image"))
    header(slide, item["tag"], item["title"])
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(148), Mm(62), Mm(136), Mm(114))
    card.name = "Story card"
    fill(card, WHITE)
    accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(156), Mm(70), Mm(120), Mm(1.5))
    accent.name = "Story accent"
    fill(accent, GOLD)
    heading = textbox(slide, 154, 76, 124, 18, "Story heading")
    plain(heading, item["heading"], 20, NAVY, True)
    mark = item.get("mark")
    if mark:
        cap = textbox(slide, 154, 98, 14, 18, "Drop cap")
        plain(cap, item["body"][0], 32, GOLD, True)
        body = textbox(slide, 168, 98, 110, 70, "Story")
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
        body = textbox(slide, 154, 98, 124, 70, "Story")
        plain(body, item["body"], 18, INK)


def grid(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"], item["place"], item.get("image"))
    header(slide, item["tag"], item["title"])
    gap = 6
    width = (136 - gap) / 2
    for i, box in enumerate(item["boxes"]):
        x = 148 + i * (width + gap)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(x), Mm(62), Mm(width), Mm(114))
        card.name = f"Card {i + 1}"
        fill(card, WHITE)
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(x + 4), Mm(70), Mm(width - 8), Mm(1.5))
        accent.name = f"Card accent {i + 1}"
        fill(accent, GOLD)
        title = textbox(slide, x + 2, 78, width - 4, 22, f"Card title {i + 1}")
        plain(title, box["t"], 18, NAVY, True)
        body = textbox(slide, x + 2, 102, width - 4, 66, f"Card text {i + 1}")
        plain(body, box["d"], 15, INK)


def timeline(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"], item["place"], item.get("image"))
    header(slide, item["tag"], item["title"])
    items = item["items"]
    left, width = 148, 136
    step = width / len(items)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(left + 8), Mm(100), Mm(width - 16), Mm(1.3))
    line.name = "Timeline"
    fill(line, GOLD)
    for i, entry in enumerate(items):
        x = left + i * step
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Mm(x + step / 2 - 3), Mm(96.8), Mm(6), Mm(6))
        dot.name = f"Timeline dot {i + 1}"
        fill(dot, GOLD if i % 2 else RGBColor(0xC2, 0x41, 0x0C), WHITE)
        label = textbox(slide, x, 108, step, 16, f"Timeline label {i + 1}")
        plain(label, entry["step"], 13, NAVY, True, PP_ALIGN.CENTER)
        body = textbox(slide, x, 124, step, 48, f"Timeline text {i + 1}")
        plain(body, entry["text"], 12, INK, align=PP_ALIGN.CENTER)


def sources(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"], item["place"], item.get("image"))
    header(slide, item["tag"], item["title"])
    for i, pill in enumerate(item["pills"]):
        x = 148 + i * 33
        chip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(x), Mm(62), Mm(31), Mm(9))
        chip.name = f"Pill {pill}"
        fill(chip, CREAM)
        try:
            chip.adjustments[0] = 0.5
        except Exception:
            pass
        label = textbox(slide, x, 62.3, 31, 8, f"Pill label {pill}", "ctr")
        plain(label, pill, 11, NAVY, True, PP_ALIGN.CENTER, "ctr")
    for i, text in enumerate(item["items"]):
        y = 76 + i * 24
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
    {"kind": "hero", "title": "Texas", "subtitle": "The Lone Star State. A place, its people, and one hard question.", "place": "Texas State Capitol, Austin", "credit": "Carol M. Highsmith · public domain · loc.gov", "fact": "One star on the flag. Many stories behind it."},
    {"kind": "bignum", "tag": "Geographic orientation", "title": "Texas at a glance", "place": "Shackelford County Courthouse, Albany", "credit": "Carol M. Highsmith · public domain · loc.gov", "fact": "Only Alaska covers more ground.", "boxes": [
        {"value": "2nd", "label": "largest state, after Alaska"},
        {"value": "Austin", "label": "the capital"},
        {"value": "30", "unit": "million+", "label": "people, and still growing"},
    ]},
    {"kind": "story", "tag": "Physical geography", "title": "Rain, pines, and the Gulf", "heading": "The wet east", "place": "Big Thicket National Preserve", "credit": "National Park Service · public domain · nps.gov", "fact": "The east gets the rain the west never sees.", "body": "Pine woods and the Gulf coast get the most rain. Summers are hot and humid. Hurricanes can reach the shore."},
    {"kind": "story", "tag": "Physical geography", "title": "Rivers and rolling land", "heading": "Hills and plains", "place": "Texas Hill Country, near Burnet", "credit": "Carol M. Highsmith · public domain · loc.gov", "fact": "The Hill Country rolls. It does not lie flat.", "body": "The Hill Country sits between rivers and open plains. Winters are usually mild. Storms and a sudden cold can still arrive."},
    {"kind": "story", "tag": "Physical geography", "title": "Desert, canyons, little water", "heading": "The dry west", "place": "Santa Elena Canyon, Big Bend National Park", "credit": "National Park Service · public domain · nps.gov", "fact": "Out here, water is the real border.", "body": "Big Bend holds desert, canyons, and mountains. Days are very hot. Nights can be cold, and water is scarce."},
    {"kind": "timeline", "tag": "History", "title": "How Texas became Texas", "place": "The Alamo, San Antonio", "credit": "Carol M. Highsmith · public domain · loc.gov", "fact": "A republic in 1836. A state in 1845.", "items": [
        {"step": "First nations", "text": "Caddo, Comanche, and Apache peoples lived here for centuries."},
        {"step": "Spain and Mexico", "text": "Missions came first. Later, Texas was part of Mexico."},
        {"step": "1836", "text": "Texas became an independent republic."},
        {"step": "1845", "text": "It joined the United States as the 28th state."},
        {"step": "1901", "text": "Oil at Spindletop changed the towns and the jobs."},
    ]},
    {"kind": "story", "tag": "Cultural identity", "title": "Many stories, one star", "heading": "More than one people", "mark": "Lone Star", "place": "Mission San José, San Antonio", "credit": "Carol M. Highsmith · public domain · loc.gov", "fact": "The Lone Star is a symbol, not the whole people.", "body": "Many nations knew this land before any flag. Spanish and Mexican families built towns and a Tejano culture that is still here. Later came Anglo settlers, African Americans, Czechs, and Germans. The Lone Star is one symbol, not the whole story."},
    {"kind": "story", "tag": "Economy", "title": "Oil, gas, and the wind", "heading": "Energy", "place": "Pantex Wind Farm, Amarillo", "credit": "U.S. Department of Energy · public domain · energy.gov", "fact": "Oil under the ground. Wind above it.", "body": "Texas produces oil and natural gas. It also leads the United States in wind power. That strength comes with a duty to use it carefully."},
    {"kind": "grid", "tag": "Economy", "title": "Cities, ports, and ranches", "place": "Lyndon B. Johnson National Historical Park", "credit": "National Park Service · public domain · nps.gov", "fact": "A ranch and a space center share one state.", "boxes": [
        {"t": "Cities of ideas", "d": "Austin builds technology. Houston runs a great port and the Johnson Space Center."},
        {"t": "Land and cattle", "d": "Cotton and cattle still matter. Ranches keep an older picture of Texas alive."},
    ]},
    {"kind": "story", "tag": "Demographics and society", "title": "A state that keeps growing", "heading": "Cities and open country", "mark": "more than 30 million", "place": "Houston", "credit": "Carol M. Highsmith · public domain · loc.gov", "fact": "About two in five Texans are Hispanic or Latino.", "body": "Texas is home to more than 30 million people. Houston, Dallas, San Antonio, and Austin are huge, while much of the land is still ranches and small towns. About two in five residents are Hispanic or Latino. People move here for work, so schools and languages keep changing."},
    {"kind": "grid", "tag": "A current challenge", "title": "The week the power stopped", "place": "Dallas–Fort Worth", "credit": "National Weather Service · public domain · noaa.gov", "fact": "In 2021, cold stopped the power.", "boxes": [
        {"t": "What happened", "d": "In February 2021, extreme cold froze equipment. Millions of homes lost heat. Most of the grid is run by ERCOT, not by the national networks."},
        {"t": "A fair next step", "d": "Some want Texas to stay independent. Others want links to neighboring states. One practical step is to prepare plants and fuel lines for freezing weather."},
    ]},
    {"kind": "sources", "tag": "Evidence", "title": "Where these facts come from", "place": "Texas State Capitol rotunda, Austin", "credit": "Carol M. Highsmith · public domain · loc.gov", "fact": "If it has no source, it is not a fact yet.", "pills": ["Geography", "History", "Economy", "Society"], "items": [
        "U.S. Census Bureau — population and communities",
        "Texas State Historical Association — the republic, 1845, and Spindletop",
        "National Weather Service — climate and the February 2021 storm",
        "ERCOT public reports — how most of the Texas grid is organized",
    ]},
    {"kind": "hero", "title": "Thank you", "subtitle": "Ask me one question: a place, a date, or the winter storm.", "place": "Marble Falls, Texas Hill Country", "credit": "Carol M. Highsmith · public domain · loc.gov", "fact": "Leave me one question."},
    {"kind": "refs", "tag": "References", "title": "Works cited", "place": "Texas Capitol rotunda, Austin", "credit": "Carol M. Highsmith · public domain · loc.gov", "fact": "A fact needs a record someone else can open.", "image": "12.jpg", "items": [
        "1. UNITED STATES. Census Bureau. QuickFacts: Texas [online]. Washington, D.C.: U.S. Census Bureau, 2025 [cit. 2026-11-10]. Available from: https://www.census.gov/quickfacts/Texas",
        "2. NANCE, Joseph M. Republic of Texas. In: Handbook of Texas Online [online]. Austin: Texas State Historical Association [cit. 2026-11-10]. Available from: https://www.tshaonline.org/handbook/entries/republic-of-texas",
        "3. WOOSTER, Robert and SANDERS, Christine Moor. Spindletop Oilfield. In: Handbook of Texas Online [online]. Austin: Texas State Historical Association [cit. 2026-11-10]. Available from: https://www.tshaonline.org/handbook/entries/spindletop-oilfield",
        "4. NATIONAL WEATHER SERVICE. February 2021: Historic Winter Storm and Arctic Outbreak [online]. Fort Worth: National Weather Service, 2021 [cit. 2026-11-10]. Available from: https://www.weather.gov/fwd/Feb-2021-WinterEvent",
        "5. ELECTRIC RELIABILITY COUNCIL OF TEXAS. February 2021 Extreme Weather Event [online]. Austin: ERCOT, 2021 [cit. 2026-11-10]. Available from: https://www.ercot.com/news/february2021",
    ]},
    {"kind": "refs", "tag": "References", "title": "Photographs", "place": "Marble Falls, Texas Hill Country", "credit": "Carol M. Highsmith · public domain · loc.gov", "fact": "Every picture names its place and its source.", "image": "13.jpg", "columns": 2, "items": [
        "1. HIGHSMITH, Carol M. Texas State Capitol, Austin [photograph]. Library of Congress, 2014 [cit. 2026-11-10]. loc.gov/item/2014632686. Public domain.",
        "2. HIGHSMITH, Carol M. Shackelford County Courthouse, Albany [photograph]. Library of Congress, 2014 [cit. 2026-11-10]. loc.gov/item/2014631724. Public domain.",
        "3. NATIONAL PARK SERVICE. Big Thicket National Preserve [photograph]. 2015 [cit. 2026-11-10]. npgallery.nps.gov. Public domain.",
        "4. HIGHSMITH, Carol M. Texas Hill Country near Burnet [photograph]. Library of Congress, 2014 [cit. 2026-11-10]. loc.gov/item/2014633069. Public domain.",
        "5. NATIONAL PARK SERVICE. Santa Elena Canyon, Big Bend [photograph]. 2012 [cit. 2026-11-10]. npgallery.nps.gov. Public domain.",
        "6. HIGHSMITH, Carol M. The Alamo, San Antonio [photograph]. Library of Congress [cit. 2026-11-10]. loc.gov/item/2011630482. Public domain.",
        "7. HIGHSMITH, Carol M. Mission San José, San Antonio [photograph]. Library of Congress [cit. 2026-11-10]. loc.gov/item/2011631194. Public domain.",
        "8. UNITED STATES. Department of Energy. Pantex Wind Farm, Amarillo [photograph]. 2022 [cit. 2026-11-10]. energy.gov. Public domain.",
        "9. NATIONAL PARK SERVICE. Lyndon B. Johnson National Historical Park [photograph]. [cit. 2026-11-10]. npgallery.nps.gov. Public domain.",
        "10. HIGHSMITH, Carol M. Houston [photograph]. Library of Congress, 2014 [cit. 2026-11-10]. loc.gov/item/2014632226. Public domain.",
        "11. NATIONAL WEATHER SERVICE. Dallas–Fort Worth, February 2021 [photograph]. NOAA, 2021 [cit. 2026-11-10]. noaa.gov. Public domain.",
        "12. HIGHSMITH, Carol M. Texas Capitol rotunda, Austin [photograph]. Library of Congress, 2014 [cit. 2026-11-10]. loc.gov/item/2014632081. Public domain.",
        "13. HIGHSMITH, Carol M. Marble Falls, Texas Hill Country [photograph]. Library of Congress, 2014 [cit. 2026-11-10]. loc.gov/item/2014633113. Public domain.",
    ]},
]


def refs(slide, item, index, total):
    chrome(slide, index, total, item["fact"], item["credit"], item["place"], item.get("image"))
    header(slide, item["tag"], item["title"])
    entries = item["items"]
    columns = item.get("columns", 1)
    rows = (len(entries) + columns - 1) // columns
    width = (136 - 4 * (columns - 1)) / columns
    row_h = 112 / rows
    size = 10 if columns == 2 else 11
    for i, text in enumerate(entries):
        col, row = i % columns, i // columns
        x = 148 + col * (width + 4)
        y = 62 + row * row_h
        box = textbox(slide, x, y, width, row_h - 1, f"Reference {i + 1}")
        plain(box, text, size, INK)


def build() -> Path:
    prs = Presentation()
    prs.slide_width = Mm(297)
    prs.slide_height = Mm(210)
    prs.core_properties.title = "Texas"
    prs.core_properties.author = "Maxim Hrehor"
    blank = prs.slide_layouts[6]
    total = len(SLIDES)
    makers = {"hero": hero, "bignum": bignum, "story": story, "grid": grid, "timeline": timeline, "sources": sources, "refs": refs}
    for index, item in enumerate(SLIDES):
        slide = prs.slides.add_slide(blank)
        makers[item["kind"]](slide, item, index, total)
    OUT.parent.mkdir(exist_ok=True)
    prs.save(OUT)
    return OUT


if __name__ == "__main__":
    print(build())
