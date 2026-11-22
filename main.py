"""THE WORLD IN ONE DAY - Sunday 22 November 2026.

A dense dated broadsheet of 36 real, sourced world-news stories from
Sunday 22 November 2026, rendered at run time into a 1024x1024 PNG.

Everything is drawn by this program: a framebuffer, a hand-designed
5x7 bitmap font, a word wrapper, the broadsheet layout and a small
deterministic PNG encoder. Standard library only, no network, no
embedded image data, no other files read at run time. Two runs write
byte-identical files.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

NAVY = (13, 27, 62)
NAVY_DARK = (9, 20, 46)
RED = (178, 34, 34)
GOLD = (245, 183, 49)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GREY = (110, 110, 110)
LIGHT_GREY = (200, 200, 200)
PAPER = (255, 255, 255)

ASIA_C = (0, 102, 68)
EUROPE_C = (30, 70, 160)
MIDEAST_C = (178, 34, 34)
AFRICA_C = (146, 104, 20)
NAMER_C = (90, 60, 140)
SAMER_C = (128, 60, 150)
OCEANIA_C = (0, 120, 130)

# ---------------------------------------------------------------- framebuffer

fb = bytearray(WIDTH * HEIGHT * 3)


def set_pixel(x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        i = (y * WIDTH + x) * 3
        fb[i] = color[0]
        fb[i + 1] = color[1]
        fb[i + 2] = color[2]


def fill_rect(x, y, w, h, color):
    if w <= 0 or h <= 0:
        return
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(WIDTH, x + w)
    y1 = min(HEIGHT, y + h)
    for yy in range(y0, y1):
        base = (yy * WIDTH + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            fb[i] = color[0]
            fb[i + 1] = color[1]
            fb[i + 2] = color[2]


def rect_border(x, y, w, h, color, t=1):
    fill_rect(x, y, w, t, color)
    fill_rect(x, y + h - t, w, t, color)
    fill_rect(x, y, t, h, color)
    fill_rect(x + w - t, y, t, h, color)


# ---------------------------------------------------------------- bitmap font
# Each glyph is 5 pixels wide and 7 rows tall. Every row is a 5-bit
# number: the leftmost pixel is bit 4, the rightmost is bit 0.
# The advance is 6 pixels at scale 1, so about 52 characters fit on
# a 312-pixel column line.

FONT = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 21, 10),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
}

FONT.update({
    "a": (0, 0, 14, 1, 15, 17, 15),
    "b": (16, 16, 30, 17, 17, 17, 30),
    "c": (0, 0, 14, 16, 16, 17, 14),
    "d": (1, 1, 15, 17, 17, 17, 15),
    "e": (0, 0, 14, 17, 31, 16, 14),
    "f": (6, 8, 8, 30, 8, 8, 8),
    "g": (0, 15, 17, 17, 15, 1, 14),
    "h": (16, 16, 30, 17, 17, 17, 17),
    "i": (4, 0, 12, 4, 4, 4, 14),
    "j": (2, 0, 6, 2, 2, 18, 12),
    "k": (16, 16, 18, 20, 24, 20, 18),
    "l": (12, 4, 4, 4, 4, 4, 14),
    "m": (0, 0, 26, 21, 21, 21, 21),
    "n": (0, 0, 30, 17, 17, 17, 17),
    "o": (0, 0, 14, 17, 17, 17, 14),
    "p": (0, 0, 30, 17, 17, 30, 16),
    "q": (0, 0, 15, 17, 17, 15, 1),
    "r": (0, 0, 22, 25, 16, 16, 16),
    "s": (0, 0, 15, 16, 14, 1, 30),
    "t": (4, 4, 14, 4, 4, 18, 12),
    "u": (0, 0, 17, 17, 17, 19, 13),
    "v": (0, 0, 17, 17, 17, 10, 4),
    "w": (0, 0, 17, 17, 21, 21, 10),
    "x": (0, 0, 17, 10, 4, 10, 17),
    "y": (0, 0, 17, 17, 15, 1, 14),
    "z": (0, 0, 31, 2, 4, 8, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 6, 8, 16, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8),
    ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8),
    "-": (0, 0, 0, 14, 0, 0, 0),
    "'": (4, 4, 8, 0, 0, 0, 0),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 2, 4, 0, 4),
    "%": (25, 26, 2, 4, 8, 11, 19),
    "/": (1, 2, 2, 4, 8, 8, 16),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "&": (12, 18, 20, 8, 21, 18, 13),
})


# ---------------------------------------------------------------- text drawing


def draw_char(x, y, ch, color, scale=1, bold=False):
    glyph = FONT.get(ch)
    if glyph is None:
        return
    for row in range(7):
        bits = glyph[row]
        for col in range(5):
            if bits & (1 << (4 - col)):
                px = x + col * scale
                py = y + row * scale
                fill_rect(px, py, scale, scale, color)
                if bold:
                    fill_rect(px + 1, py, scale, scale, color)


def text_width(text, scale=1):
    return len(text) * 6 * scale


def draw_text(x, y, text, color, scale=1, bold=False):
    cx = x
    for ch in text:
        draw_char(cx, y, ch, color, scale, bold)
        cx += 6 * scale
    return cx - x


def draw_text_right(x_right, y, text, color, scale=1, bold=False):
    draw_text(x_right - text_width(text, scale), y, text, color, scale, bold)


def wrap_text(text, scale, max_width):
    """Greedy word wrap. Returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, text, color, scale, max_width, line_height):
    lines = wrap_text(text, scale, max_width)
    for i, line in enumerate(lines):
        draw_text(x, y + i * line_height, line, color, scale)
    return len(lines)


# ---------------------------------------------------------------- PNG encoder
# Deterministic: filter 0 on every scanline, no ancillary chunks, so
# the same framebuffer always compresses to the same bytes.


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png():
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(HEIGHT):
        raw.append(0)
        start = y * WIDTH * 3
        raw += fb[start:start + WIDTH * 3]
    idat = zlib.compress(bytes(raw), 9)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", idat)
    png += _chunk(b"IEND", b"")
    return png


# ---------------------------------------------------------------- the stories
# Every story happened or was first reported on Sunday 22 Nov 2026.
# (headline, summary, source outlet). Summaries are kept to one
# 312-pixel column line at scale 1 (about 52 characters).

LEADS = [
    ("MIDDLE EAST", MIDEAST_C,
     "IRAN STRIKES US BASES IN THE GULF",
     "Tehran hits US assets in Bahrain and Kuwait; two tankers struck in the Strait of Hormuz.",
     "AFP / Daily Jagran"),
    ("ASIA - EUROPE", EUROPE_C,
     "EU AND INDONESIA SIGN TRADE DEAL",
     "After 10 years of talks, the deal scraps 98.5% of tariffs for 730 million people.",
     "Reuters"),
    ("GLOBAL", NAVY,
     "COP31 NEARS A DEAL AT LAST",
     "After all-night talks in Antalya, a new text is put to nearly 200 nations on Sunday.",
     "Reuters"),
]

# (region, headline, summary, source)
ASIA = [
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
]

MIDDLE_EAST = [
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
]

EUROPE = [
    ("Russian strike on Lviv kills two",
     "Missile hits a building; ten people injured.", "Global Digest"),
    ("Denmark blames Russia for murder plot",
     "Plot to kill a US-Ukrainian citizen in Denmark.", "japako"),
    ("Estonia shuts border with Russia",
     "All road crossings closed for six months.", "japako"),
    ("EU budget plan cut by 224bn euros",
     "Council plan far below the Commission proposal.", "japako"),
    ("Croatians march in Zagreb",
     "Justice demanded over a hospital death.", "grand-star"),
    ("Finland restores Gulf flight curbs",
     "Restrictions return for the eastern Gulf.", "japako"),
]

AFRICA = [
    ("Sudan rebels seize Bau region",
     "Tasis Alliance takes a key Blue Nile area.", "grand-star"),
    ("25 deportees land in Liberia",
     "Migrants deported from the US reach Monrovia.", "AFP"),
]

NORTH_AMERICA = [
    ("Mexico captures 'El Chapo Isidro'",
     "Shoot-out: four soldiers, seven suspects killed.", "AFP"),
    ("US curbs defence ties with Canada",
     "Pentagon chief Hegseth restricts the partnership.", "japako"),
    ("Salvadoran troops retake stadium",
     "Gangs pushed out of a key stadium in Haiti.", "Dumpling News"),
    ("BYU survives Kansas in 3OT",
     "No. 10 BYU win 31-29; Nebraska stun Ohio State.", "Reuters"),
]

SOUTH_AMERICA = [
    ("France rout Argentina 45-17",
     "Les Bleus reach the Nations Championship final.", "World in Sport"),
    ("Peru counts quake damage",
     "Landslides after the Andes tremor; power cut.", "Bloomberg / Spiegel"),
]

OCEANIA = [
    ("Australia defends AUKUS pact",
     "Marles hits back at US budget office criticism.", "Reuters"),
    ("Pant ton powers India to 629-6",
     "India post their highest Test total in NZ.", "Reuters"),
    ("Cummins keeps captaincy",
     "Unanimous backing to stay Australia captain.", "Daily Jagran"),
]

NUMBERS = [
    ("629-6", "India's record Test total in NZ"),
    ("98.5%", "tariffs cut in EU-Indonesia deal"),
    ("5,700", "voters pick Hong Kong committee"),
    ("31-29", "BYU beat Kansas in triple OT"),
]

ALSO_TODAY = [
    ("UN weapons talks end with no binding rules", "Grand-Star"),
    ("Tech sell-off drags US markets down", "Dumpling News"),
    ("Muslims to outnumber Christians: Pew", "japako"),
    ("Ireland stun South Africa 20-17 in Dublin", "Reuters"),
]


# ---------------------------------------------------------------- layout

MARGIN = 24
COL_W = 312
COL_X = [24, 356, 688]
GUTTER = 20

HEAD_LH = 11
SUM_LH = 11
SRC_LH = 11
STORY_GAP = 10
SECTION_GAP = 12
HEADER_H = 28


def draw_masthead():
    fill_rect(0, 0, WIDTH, 108, NAVY)
    draw_text(24, 16, "THE WORLD IN ONE DAY", WHITE, 5, bold=True)
    draw_text(24, 62, "SUNDAY - 22 NOVEMBER 2026", GOLD, 3, bold=True)
    draw_text_right(1000, 16, "36 STORIES", WHITE, 2, bold=True)
    draw_text_right(1000, 42, "7 REGIONS", WHITE, 2, bold=True)
    draw_text_right(1000, 68, "ALL DATED 22 NOV 2026", GOLD, 2, bold=True)
    fill_rect(0, 108, WIDTH, 6, RED)


def draw_lead(x, y, kicker, color, headline, summary, source):
    h = 132
    rect_border(x, y, COL_W, h, LIGHT_GREY, 1)
    fill_rect(x, y, COL_W, 6, color)
    draw_text(x + 10, y + 14, kicker, color, 1, bold=True)
    lines = wrap_text(headline, 2, COL_W - 20)
    hy = y + 30
    for i, line in enumerate(lines):
        draw_text(x + 10, hy + i * 17, line, BLACK, 2, bold=True)
    sy = hy + len(lines) * 17 + 6
    draw_wrapped(x + 10, sy, summary, BLACK, 1, COL_W - 20, 11)
    draw_text(x + 10, y + h - 18, "Source: " + source, GREY, 1)
    return y + h


def draw_section_header(x, y, title, color):
    fill_rect(x, y, COL_W, HEADER_H, color)
    draw_text(x + 10, y + 7, title, WHITE, 2, bold=True)
    return y + HEADER_H + 10


def draw_story(x, y, headline, summary, source):
    n = draw_wrapped(x, y, headline, BLACK, 1, COL_W, HEAD_LH)
    y += n * HEAD_LH
    draw_text(x, y, summary, BLACK, 1)
    y += SUM_LH
    draw_text(x, y, "Source: " + source, GREY, 1)
    y += SRC_LH
    return y + STORY_GAP


def draw_section(x, y, title, color, stories):
    y = draw_section_header(x, y, title, color)
    for headline, summary, source in stories:
        y = draw_story(x, y, headline, summary, source)
    return y + SECTION_GAP - STORY_GAP


def draw_numbers(x, y):
    fill_rect(x, y, COL_W, HEADER_H, NAVY)
    draw_text(x + 10, y + 7, "THE DAY IN NUMBERS", GOLD, 2, bold=True)
    y += HEADER_H + 8
    for value, label in NUMBERS:
        draw_text(x, y, value, BLACK, 1, bold=True)
        draw_text(x + 62, y, label, BLACK, 1)
        y += 15
    return y + 8


def draw_also_today(y):
    fill_rect(24, y, 976, 30, NAVY)
    draw_text(34, y + 8, "ALSO TODAY - 22 NOVEMBER 2026", GOLD, 2, bold=True)
    y += 30 + 10
    item_w = 238
    max_lines = 1
    for i, (headline, source) in enumerate(ALSO_TODAY):
        x = 24 + i * (item_w + 8)
        n = draw_wrapped(x, y, headline, BLACK, 1, item_w, 11)
        max_lines = max(max_lines, n)
        draw_text(x, y + n * 11 + 2, "Source: " + source, GREY, 1)
    return y + max_lines * 11 + 13 + 10


def draw_footer(y):
    draw_text(24, y, "All stories happened or were first reported on Sunday 22 November 2026.",
              GREY, 1)
    return y + 12


def render():
    fill_rect(0, 0, WIDTH, HEIGHT, PAPER)
    draw_masthead()

    # Three lead boxes, one per column.
    ly = 126
    for i, (kicker, color, headline, summary, source) in enumerate(LEADS):
        draw_lead(COL_X[i], ly, kicker, color, headline, summary, source)

    y = 126 + 132 + 14
    end1 = draw_section(COL_X[0], y, "ASIA", ASIA_C, ASIA)
    end1 = draw_section(COL_X[0], end1, "AFRICA", AFRICA_C, AFRICA)
    end1 = draw_numbers(COL_X[0], end1)

    end2 = draw_section(COL_X[1], y, "EUROPE", EUROPE_C, EUROPE)
    end2 = draw_section(COL_X[1], end2, "OCEANIA", OCEANIA_C, OCEANIA)
    end2 = draw_section(COL_X[1], end2, "SOUTH AMERICA", SAMER_C, SOUTH_AMERICA)

    end3 = draw_section(COL_X[2], y, "MIDDLE EAST", MIDEAST_C, MIDDLE_EAST)
    end3 = draw_section(COL_X[2], end3, "NORTH AMERICA", NAMER_C, NORTH_AMERICA)

    strip_y = max(end1, end2, end3) + 10
    foot_y = draw_also_today(strip_y)
    draw_footer(foot_y + 6)


def main():
    render()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(encode_png())
    print("wrote", path)


if __name__ == "__main__":
    main()
