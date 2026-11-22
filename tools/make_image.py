#!/usr/bin/env python3
"""Draw the front page for Saturday 21 November 2026.

A single-page newspaper: masthead, date, one lead story, four shorter
stories in two rows of two, then an ALSO TODAY briefs column and a footer.
Everything is drawn with Pillow and the DejaVu family; the render is
deterministic (no clocks, no randomness, no network), so running this
script twice produces byte-identical PNGs.
"""

import os

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
MARGIN = 38
BORDER = 28
INK = (0, 0, 0)
RED = (196, 18, 18)
GREY = (110, 110, 110)
PAPER = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "entry.png")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(draw, text, face, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=face) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def fit_size(draw, text, face_path, max_width, start, floor=10):
    """Largest size (<= start) at which text fits max_width on one line."""
    size = start
    while size > floor:
        face = font(face_path, size)
        if draw.textlength(text, font=face) <= max_width:
            return face
        size -= 1
    return font(face_path, floor)


def draw_para(draw, text, face, x, y, max_width, leading, fill=INK):
    """Draw wrapped text; returns the y just below the last line."""
    for line in wrap_text(draw, text, face, max_width):
        draw.text((x, y), line, font=face, fill=fill)
        y += leading
    return y


def rule(draw, y, width=3, fill=INK, x0=None, x1=None):
    x0 = MARGIN if x0 is None else x0
    x1 = PAGE - MARGIN if x1 is None else x1
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)
    return y + width


def kicker(draw, text, x, y, size=20):
    face = font(SANS_BOLD, size)
    draw.text((x, y), text, font=face, fill=RED)
    return y + size + 6


def main():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)
    # Outer frame.
    d.rectangle([BORDER, BORDER, PAGE - BORDER, PAGE - BORDER],
                outline=INK, width=3)
    x = MARGIN
    right = PAGE - MARGIN
    width = right - x
    y = BORDER + 12

    # Eyebrow row: paper tag on the left, weekday on the right.
    brow = font(SANS_BOLD, 20)
    d.text((x, y), "THE WORLD IN ONE IMAGE", font=brow, fill=INK)
    day = "SATURDAY"
    d.text((right - d.textlength(day, font=brow), y), day,
           font=brow, fill=RED)
    y += 26

    # Masthead, fitted to the full width.
    mast = fit_size(d, "WORLD NEWS", SERIF_BOLD, width, 86)
    d.text((x, y), "WORLD NEWS", font=mast, fill=INK)
    y += mast.size + 10

    # Red rule, then the date in red serif.
    y = rule(d, y, width=4, fill=RED) + 8
    date_face = font(SERIF_BOLD, 34)
    d.text((x, y), "Saturday, 21 November 2026", font=date_face, fill=RED)
    y += 44
    y = rule(d, y, width=3) + 10

    # ---- Lead story: Mexico captures El Chapo Isidro. ----
    y = kicker(d, "MEXICO \u00b7 CARTEL CRACKDOWN", x, y, size=21)
    lead_head = font(SANS_BOLD, 40)
    y = draw_para(d, "Mexico captures FBI most-wanted cartel boss \u201cEl Chapo Isidro\u201d",
                  lead_head, x, y, width, 46)
    y += 4
    deck = font(SANS, 21)
    y = draw_para(d,
                  "Special forces seize Fausto Isidro Meza Flores in Guasave, "
                  "Sinaloa, in a night gunfight that kills 11; US intelligence "
                  "helped, and he is flown to Mexico City.",
                  deck, x, y, width, 26)
    y += 10
    y = rule(d, y, width=3) + 10

    # ---- Two rows of two stories. ----
    col_w = (width - 28) // 2
    col2 = x + col_w + 28

    def story(cx, cy, tag, head, body):
        cy = kicker(d, tag, cx, cy, size=19)
        hf = font(SANS_BOLD, 26)
        cy = draw_para(d, head, hf, cx, cy, col_w, 30)
        cy += 3
        bf = font(SANS, 19)
        cy = draw_para(d, body, bf, cx, cy, col_w, 23)
        return cy

    top1 = y
    end_l = story(x, top1, "CLIMATE TALKS",
                  "COP31 in overtime as fossil fuels vanish from draft",
                  "Talks pass Friday\u2019s deadline with no deal; the EU warns "
                  "of a \u201cfossil summit\u201d.")
    end_r = story(col2, top1, "UKRAINE WAR",
                  "Russian double-tap strike hits Zelenskyy\u2019s hometown",
                  "Two killed, 60 wounded; a second wave hit rescuers.")
    y = max(end_l, end_r) + 10
    d.line([(col2 - 14, top1), (col2 - 14, y)], fill=GREY, width=1)

    top2 = y
    end_l = story(x, top2, "CYBERATTACK",
                  "FBI probes hack of its national crime database",
                  "The NCIC system is breached; Trump calls it \u201cnot good\u201d. "
                  "The Agriculture Dept is also hit.")
    end_r = story(col2, top2, "GULF TENSIONS",
                  "Iran claims strikes on US bases in Bahrain",
                  "Guards say they hit US positions; Bahrain reports a fire.")
    y = max(end_l, end_r) + 10
    d.line([(col2 - 14, top2), (col2 - 14, y)], fill=GREY, width=1)
    y = rule(d, y, width=3) + 10

    # ---- Also today: briefs. ----
    y = kicker(d, "ALSO TODAY", x, y, size=21)
    brief_face = font(SANS, 20)
    brief_bold = font(SANS_BOLD, 20)
    briefs = [
        ("EU proposes 3% Big Tech tax", " in a budget plan to cut \u20ac204bn."),
        ("EU and Indonesia sign trade deal", " after a decade of talks."),
        ("Trump threatens a \u201ctremendous tax\u201d", " on firms building data centres abroad."),
        ("Trump vows a \u201cpermanent\u201d Iran deal", "."),
        ("Houthis and Saudi coalition trade strikes", "; 71 Saudi raids in a day."),
        ("Toxic alcohol kills 11", " and hospitalises 180 in India\u2019s Manipur."),
        ("Bolsonaro in intensive care", " with a bowel obstruction; he is stable."),
        ("Ukrainian drones set Russian ship ablaze", " in the Baltic; the Sparta II burns."),
    ]
    for lead, tail in briefs:
        full = lead + tail
        lines = wrap_text(d, full, brief_face, width)
        for i, line in enumerate(lines):
            if i == 0 and line.startswith(lead):
                d.text((x, y), lead, font=brief_bold, fill=INK)
                d.text((x + d.textlength(lead, font=brief_bold), y),
                       line[len(lead):], font=brief_face, fill=INK)
            else:
                d.text((x, y), line, font=brief_face, fill=INK)
            y += 22

    # Footer.
    y += 4
    y = rule(d, y, width=1, fill=GREY) + 7
    foot = font(SANS, 17)
    d.text((x, y), "All events happened or were first reported on Saturday 21 November 2026.",
           font=foot, fill=GREY)
    y += 20
    print("final y:", y, "bottom border:", PAGE - BORDER)

    img.save(OUT, "PNG")
    print("wrote", OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
