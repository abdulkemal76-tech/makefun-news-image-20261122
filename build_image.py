#!/usr/bin/env python3
"""Build the 22 Nov 2026 world-news broadsheet (1024x1024, deterministic).

Layout: navy masthead naming the day, a 3-story lead band, then three
columns of region sections (Asia / Europe / Middle East / Africa /
Americas / Oceania), and an "Also today" strip along the bottom.
Every story is dated 22 November 2026 and carries its source outlet.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "image.png")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_MAST = font("DejaVuSans-Bold.ttf", 44)
F_DATE = font("DejaVuSans-Bold.ttf", 23)
F_META = font("DejaVuSans-Bold.ttf", 15)
F_KICK = font("DejaVuSans-Bold.ttf", 12)
F_LEAD_H = font("DejaVuSans-Bold.ttf", 19)
F_LEAD_B = font("DejaVuSans.ttf", 13)
F_LEAD_S = font("DejaVuSans.ttf", 11)
F_SEC = font("DejaVuSans-Bold.ttf", 15)
F_HEAD = font("DejaVuSans-Bold.ttf", 14)
F_BODY = font("DejaVuSans.ttf", 12)
F_SRC = font("DejaVuSans.ttf", 10)
F_ALSO_H = font("DejaVuSans-Bold.ttf", 13)
F_ALSO_B = font("DejaVuSans.ttf", 12)
F_FOOT = font("DejaVuSans.ttf", 10)

NAVY = (15, 32, 64)
RED = (178, 34, 34)
GOLD = (255, 214, 90)
PAPER = (247, 246, 241)
INK = (20, 28, 44)
GREY = (90, 90, 88)
LINE = (205, 203, 196)

# (region, colour, [(headline, summary, source), ...])
COLUMNS = [
    [
        ("ASIA", (0, 90, 70), [
            ("Hong Kong votes for Election Committee",
             "About 5,700 voters pick the powerful committee.", "Global Digest"),
            ("S. Korea navy chief visits Japan",
             "Adm. Kim starts a two-day Japan visit.", "Yonhap"),
            ("Cyclone Akvan's rains linger",
             "Heavy rain lingers over eastern India.", "IMD"),
            ("Nepal PM visits India",
             "Shah arrives in New Delhi for two days.", "Maverick News"),
            ("Goa festival screens animation",
             "New animation section shows five films.", "PIB"),
            ("Korea rail line reopens",
             "Trains resume after Friday's derailment.", "AJU Press"),
        ]),
        ("OCEANIA", (0, 110, 140), [
            ("Australia defends AUKUS pact",
             "Marles hits back at US budget office criticism.", "Reuters"),
            ("Pant ton powers India to 629-6",
             "India's highest Test total in New Zealand.", "Reuters"),
            ("Cummins keeps captaincy",
             "Unanimous backing to stay Australia captain.", "Daily Jagran"),
        ]),
    ],
    [
        ("EUROPE", (40, 70, 160), [
            ("Russian strike on Lviv kills two",
             "Missile hits a building; ten people injured.", "Global Digest"),
            ("Denmark blames Russia for murder plot",
             "Plot to kill a US-Ukrainian citizen on Danish soil.", "japako"),
            ("Estonia shuts border with Russia",
             "All road crossings closed for six months.", "japako"),
            ("EU budget plan cut by 224bn euros",
             "Council plan far below the Commission proposal.", "japako"),
            ("Croatians march in Zagreb",
             "Justice demanded over a hospital death.", "grand-star"),
            ("Finland restores Gulf flight curbs",
             "Restrictions return for the eastern Gulf.", "japako"),
        ]),
        ("AFRICA", (150, 100, 20), [
            ("Sudan rebels seize Bau region",
             "Tasis Alliance takes a key Blue Nile area.", "grand-star"),
            ("25 deportees land in Liberia",
             "Migrants deported from the US reach Monrovia.", "AFP"),
        ]),
        ("SOUTH AMERICA", (120, 60, 140), [
            ("France rout Argentina 45-17",
             "Les Bleus reach the Nations Championship final.", "World in Sport"),
            ("Peru counts quake damage",
             "Landslides after the Andes tremor; power cut.", "Bloomberg / Spiegel"),
        ]),
    ],
    [
        ("MIDDLE EAST", (178, 34, 34), [
            ("Bahrain: Iran hit industrial site",
             "Strike sparks a fire at a civilian plant.", "AFP"),
            ("Two tankers hit in Hormuz",
             "Vessels struck near Oman's Khasab in an hour.", "japako"),
            ("Seven killed in Gaza strikes",
             "Strikes kill seven despite the ceasefire.", "japako"),
            ("Iraq retakes militia stronghold",
             "Government moves on a Kataib base in Baghdad.", "japako"),
            ("UN warns over Yemen port strikes",
             "Attacks on Hudaydah threaten an aid lifeline.", "japako"),
            ("UN force hands over south Lebanon",
             "UNIFIL transfers duties to the Lebanese army.", "japako"),
        ]),
        ("NORTH AMERICA", (90, 60, 120), [
            ("Mexico captures 'El Chapo Isidro'",
             "Shoot-out: four soldiers, seven suspects killed.", "AFP"),
            ("US curbs defence ties with Canada",
             "Pentagon chief Hegseth restricts the partnership.", "japako"),
            ("Salvadoran troops retake stadium",
             "Gangs pushed out of a key stadium in Haiti.", "Dumpling News"),
            ("BYU survives Kansas in 3OT",
             "No. 10 BYU win 31-29; Nebraska stun Ohio State.", "Reuters"),
        ]),
    ],
]

LEADS = [
    ("MIDDLE EAST", RED, "IRAN STRIKES US BASES IN THE GULF",
     "Tehran hits US assets in Bahrain and Kuwait; two tankers struck in the Strait of Hormuz.",
     "AFP / Daily Jagran"),
    ("ASIA - EUROPE", (0, 90, 70), "EU AND INDONESIA SIGN TRADE DEAL",
     "After 10 years of talks, the deal scraps 98.5% of tariffs for 730 million people.",
     "Reuters"),
    ("GLOBAL", NAVY, "COP31 NEARS A DEAL AT LAST",
     "After all-night talks in Antalya, a new text is put to nearly 200 nations on Sunday.",
     "Reuters"),
]

ALSO = [
    ("UN weapons talks end with no rules", "Grand-Star"),
    ("Tech sell-off drags US markets down", "Dumpling News"),
    ("Muslims to outnumber Christians: Pew", "japako"),
    ("Ireland stun South Africa 20-17", "Reuters"),
]


def wrap(draw, text, fnt, width, max_lines=None):
    """Greedy word wrap to pixel width; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        # ellipsize last line
        while lines and draw.textlength(lines[-1] + "...", font=fnt) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] += "..."
    return lines


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    d.rectangle([0, 0, W, 100], fill=NAVY)
    d.rectangle([0, 100, W, 106], fill=RED)
    d.text((24, 12), "THE WORLD IN ONE DAY", font=F_MAST, fill=(255, 255, 255))
    d.text((24, 64), "SUNDAY  \u2022  22 NOVEMBER 2026", font=F_DATE, fill=GOLD)
    d.text((W - 24, 18), "36 STORIES", font=F_META, fill=(255, 255, 255), anchor="ra")
    d.text((W - 24, 40), "7 REGIONS", font=F_META, fill=(255, 255, 255), anchor="ra")
    d.text((W - 24, 64), "ALL DATED 22 NOV 2026", font=F_META, fill=(180, 200, 230), anchor="ra")

    # ---- Lead band: three boxes ----
    ly0, ly1 = 114, 250
    lw = (1000 - 24 - 32) // 3
    for i, (kick, col, head, body, src) in enumerate(LEADS):
        x0 = 24 + i * (lw + 16)
        x1 = x0 + lw
        d.rectangle([x0, ly0, x1, ly1], fill=(255, 255, 255), outline=LINE, width=1)
        d.rectangle([x0, ly0, x1, ly0 + 4], fill=col)
        d.text((x0 + 12, ly0 + 10), kick, font=F_KICK, fill=col)
        y = ly0 + 30
        for ln in wrap(d, head, F_LEAD_H, lw - 24, max_lines=2):
            d.text((x0 + 12, y), ln, font=F_LEAD_H, fill=INK)
            y += 23
        y += 2
        for ln in wrap(d, body, F_LEAD_B, lw - 24, max_lines=3):
            d.text((x0 + 12, y), ln, font=F_LEAD_B, fill=(60, 60, 60))
            y += 17
        d.text((x0 + 12, y + 4), "Source: " + src, font=F_LEAD_S, fill=GREY)

    # ---- Three columns of region sections ----
    col_x = [24, 352, 680]
    col_w = 320
    top = 262
    bottom = 918
    for ci, sections in enumerate(COLUMNS):
        x0 = col_x[ci]
        y = top
        for name, col, items in sections:
            d.rectangle([x0, y, x0 + col_w, y + 30], fill=col)
            d.text((x0 + 10, y + 7), name, font=F_SEC, fill=(255, 255, 255))
            y += 30 + 6
            for head, body, src in items:
                for ln in wrap(d, head, F_HEAD, col_w - 8, max_lines=2):
                    d.text((x0 + 4, y), ln, font=F_HEAD, fill=INK)
                    y += 17
                for ln in wrap(d, body, F_BODY, col_w - 8, max_lines=2):
                    d.text((x0 + 4, y), ln, font=F_BODY, fill=(60, 60, 60))
                    y += 15
                d.text((x0 + 4, y), "Source: " + src, font=F_SRC, fill=GREY)
                y += 13 + 7
            y += 2
        if ci == 0:
            # Day-in-numbers box fills the short column and adds craft.
            d.rectangle([x0, y + 6, x0 + col_w, y + 6 + 84], fill=(255, 255, 255),
                        outline=LINE, width=1)
            d.rectangle([x0, y + 6, x0 + col_w, y + 6 + 26], fill=NAVY)
            d.text((x0 + 10, y + 12), "THE DAY IN NUMBERS", font=F_SEC,
                   fill=GOLD)
            ny = y + 36
            for stat in ["629-6  India's record Test total in NZ",
                         "98.5%  tariffs cut in EU-Indonesia deal",
                         "5,700  voters pick Hong Kong committee",
                         "31-29  BYU beat Kansas in triple OT"]:
                d.text((x0 + 10, ny), stat, font=F_BODY, fill=INK)
                ny += 14
        # thin rule at column end
        d.line([(x0, bottom), (x0 + col_w, bottom)], fill=LINE, width=1)

    # ---- Also today strip ----
    ay0 = 928
    d.rectangle([24, ay0, 1000, ay0 + 26], fill=NAVY)
    d.text((34, ay0 + 5), "ALSO TODAY  \u2022  22 NOVEMBER 2026", font=F_ALSO_H,
           fill=GOLD)
    aw = (1000 - 24 - 48) // 4
    for i, (head, src) in enumerate(ALSO):
        x0 = 24 + i * (aw + 16)
        y = ay0 + 34
        for ln in wrap(d, head, F_ALSO_B, aw, max_lines=1):
            d.text((x0, y), ln, font=F_ALSO_B, fill=INK)
            y += 15
        d.text((x0, y), "Source: " + src, font=F_SRC, fill=GREY)

    # ---- Footer ----
    d.text((24, 1008), "All stories happened or were first reported on Sunday 22 November 2026.",
           font=F_FOOT, fill=GREY)

    img.save(OUT, "PNG", optimize=True)
    print(OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
