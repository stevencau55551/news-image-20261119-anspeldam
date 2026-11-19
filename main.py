#!/usr/bin/env python3
"""news-image-20261119: draw a one-page newspaper front page summarising
the world news of Thursday 19 November 2026.

Pure Python 3.13 standard library, no network, fully deterministic:
the same bytes are written on every run.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)   # newsprint off-white
WHITE = (255, 255, 255)
INK = (22, 22, 28)
RED = (178, 34, 34)
NAVY = (23, 52, 96)
BLUE = (31, 90, 168)
TEAL = (14, 116, 120)
GREEN = (34, 120, 62)
PURPLE = (96, 48, 148)
GREY = (90, 88, 84)
LIGHT = (238, 234, 224)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits. Uppercase only; lowercase maps to uppercase.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "\u2022": ("00000", "00000", "01100", "01100", "00000", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (6 px advance per char)."""
    return len(text) * 6 * scale - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split(" ")
    lines, cur = [], ""
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


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bytes(bg) * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x0, x1, y, color, thick=1):
        for yy in range(y, y + thick):
            for xx in range(x0, x1 + 1):
                self.set(xx, yy, color)

    def vline(self, x, y0, y1, color, thick=1):
        for xx in range(x, x + thick):
            for yy in range(y0, y1 + 1):
                self.set(xx, yy, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Bresenham line with square thickness."""
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        half = thick // 2
        while True:
            for oy in range(-half, half + 1):
                for ox in range(-half, half + 1):
                    self.set(x + ox, y + oy, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - thick) ** 2 <= d <= r * r:
                    self.set(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        """Filled triangle via scanline rasterisation."""
        pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / (by - ay) if by != ay else 0.0
                xa = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / (cy - by) if cy != by else 0.0
                xa = bx + (cx - bx) * t1
            t2 = (y - ay) / (cy - ay)
            xb = ax + (cx - ax) * t2
            lo, hi = (int(xa), int(xb)) if xa <= xb else (int(xb), int(xa))
            for x in range(lo, hi + 1):
                self.set(x, y, color)

    def text(self, x, y, s, scale, color):
        """Draw text; returns the x position after the last character."""
        cx = x
        for ch in s:
            glyph = FONT.get(ch.upper(), FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)

# ---------------------------------------------------------------- icons
# Each icon draws inside a 120x120 box whose top-left is (x, y).

def icon_controller(c, x, y):
    c.rect(x + 4, y + 34, 112, 52, PURPLE)
    c.rect(x + 4, y + 34, 112, 12, (122, 74, 178))
    c.circle(x + 36, y + 66, 11, WHITE)
    c.circle(x + 84, y + 66, 11, WHITE)
    c.rect(x + 52, y + 50, 7, 22, WHITE)   # d-pad vertical
    c.rect(x + 44, y + 57, 23, 7, WHITE)   # d-pad horizontal
    c.circle(x + 100, y + 48, 5, (255, 205, 80))
    c.circle(x + 108, y + 60, 5, (255, 205, 80))
    c.rect(x + 18, y + 92, 84, 7, (200, 190, 220))


def icon_scales(c, x, y):
    c.vline(x + 60, y + 14, y + 96, NAVY, 4)
    c.hline(x + 22, x + 98, y + 22, NAVY, 4)
    c.circle(x + 60, y + 16, 6, NAVY)
    c.line(x + 24, y + 24, x + 10, y + 58, NAVY, 3)
    c.line(x + 24, y + 24, x + 38, y + 58, NAVY, 3)
    c.line(x + 96, y + 24, x + 82, y + 58, NAVY, 3)
    c.line(x + 96, y + 24, x + 110, y + 58, NAVY, 3)
    c.triangle(x + 6, y + 58, x + 42, y + 58, x + 24, y + 78, NAVY)
    c.triangle(x + 78, y + 58, x + 114, y + 58, x + 96, y + 78, NAVY)
    c.rect(x + 34, y + 100, 52, 6, NAVY)


def icon_pin(c, x, y):
    c.circle(x + 60, y + 44, 34, RED)
    c.triangle(x + 32, y + 62, x + 88, y + 62, x + 60, y + 106, RED)
    c.circle(x + 60, y + 44, 15, WHITE)
    c.circle(x + 60, y + 44, 7, RED)


def icon_stars(c, x, y):
    c.circle(x + 60, y + 60, 52, BLUE)
    for i in range(12):
        a = 2 * math.pi * i / 12 - math.pi / 2
        sx = int(x + 60 + 36 * math.cos(a))
        sy = int(y + 60 + 36 * math.sin(a))
        c.circle(sx, sy, 5, (255, 215, 60))
    c.circle(x + 60, y + 60, 10, (255, 215, 60))


def icon_cyclone(c, x, y):
    c.ring(x + 60, y + 52, 46, TEAL, 6)
    c.ring(x + 68, y + 52, 34, TEAL, 6)
    c.ring(x + 60, y + 58, 22, TEAL, 6)
    c.circle(x + 60, y + 56, 9, TEAL)
    for dx in (26, 52, 78, 98):
        c.vline(x + dx, y + 96, y + 112, BLUE, 3)
        c.circle(x + dx, y + 114, 2, BLUE)


def icon_globe(c, x, y):
    c.circle(x + 60, y + 58, 46, GREEN)
    c.ring(x + 60, y + 58, 46, (20, 80, 40), 3)
    c.hline(x + 18, x + 102, y + 42, (20, 80, 40), 3)
    c.hline(x + 18, x + 102, y + 74, (20, 80, 40), 3)
    c.line(x + 60, y + 14, x + 60, y + 102, (20, 80, 40), 3)
    c.circle(x + 92, y + 26, 12, (255, 215, 60))
    c.circle(x + 96, y + 22, 10, GREEN)


# ---------------------------------------------------------------- stories
# Six stories, all first reported on Thursday 19 November 2026.
STORIES = [
    dict(kicker="GAMING", color=PURPLE, icon=icon_controller,
         headline="GTA VI LAUNCHES WORLDWIDE",
         body="Rockstar's blockbuster returns after 13 years. Gamers enter Vice City at midnight.",
         detail="PS5 AND XBOX \u2022 $79.99 \u2022 13-YEAR WAIT"),
    dict(kicker="JUSTICE", color=NAVY, icon=icon_scales,
         headline="WORLD COURT RULES ON ROHINGYA CASE",
         body="The ICJ delivers its genocide judgment on Myanmar in The Hague, seven years after Gambia filed.",
         detail="READING BEGINS 10:00 IN THE HAGUE"),
    dict(kicker="MIDDLE EAST", color=RED, icon=icon_pin,
         headline="ISRAELI GROUND OPERATION IN GAZA",
         body="Troops move into central Gaza. Displaced families flee tents and shelters.",
         detail="RARE GROUND PUSH UNDER CEASEFIRE"),
    dict(kicker="EUROPE", color=BLUE, icon=icon_stars,
         headline="EU EXTENDS RUSSIA SANCTIONS 3 YEARS",
         body="The bloc renews sanctions on about 3,000 people and organisations.",
         detail="TWO OLIGARCHS REMOVED FROM LIST"),
    dict(kicker="WEATHER", color=TEAL, icon=icon_cyclone,
         headline="CYCLONE AKVAN NEARS INDIA'S COAST",
         body="The storm is set to cross between Machilipatnam and Puri. Railways review storm readiness.",
         detail="LANDFALL EXPECTED ON EAST COAST"),
    dict(kicker="SOCIETY", color=GREEN, icon=icon_globe,
         headline="ISLAM ON TRACK TO BE LARGEST FAITH",
         body="Pew projects Islam to pass Christianity as the world's biggest religion by 2035.",
         detail="PEW RESEARCH CENTER \u2022 OUT TODAY"),
]


def draw_panel(c, x0, y0, story):
    w, h = 496, 258
    c.rect(x0, y0, w, h, WHITE)
    c.rect(x0, y0, w, 2, INK)
    c.rect(x0, y0 + h - 2, w, 2, INK)
    c.rect(x0, y0, 2, h, INK)
    c.rect(x0 + w - 2, y0, 2, h, INK)
    # kicker band
    c.rect(x0 + 2, y0 + 2, w - 4, 30, story["color"])
    c.text(x0 + 14, y0 + 11, story["kicker"], 2, WHITE)
    # icon
    story["icon"](c, x0 + 14, y0 + 46)
    # headline + body to the right of the icon
    tx = x0 + 148
    tw = w - 148 - 14
    y = y0 + 50
    for line in wrap_text(story["headline"], tw, 3):
        c.text(tx, y, line, 3, INK)
        y += 22
    y += 6
    for line in wrap_text(story["body"], tw, 2):
        c.text(tx, y, line, 2, (52, 50, 46))
        y += 18
    # detail strip at the bottom
    c.rect(x0 + 2, y0 + h - 46, w - 4, 44, LIGHT)
    c.hline(x0 + 2, x0 + w - 3, y0 + h - 46, story["color"], 3)
    c.text_center(x0 + w // 2, y0 + h - 34, story["detail"], 2,
                  story["color"])


def draw_page():
    c = Canvas(W, H, PAPER)
    # masthead
    c.text_center(W // 2, 26, "THE WORLD TODAY", 5, INK)
    c.hline(60, W - 61, 96, INK, 3)
    c.text_center(W // 2, 108, "THURSDAY 19 NOVEMBER 2026", 4, RED)
    c.text_center(W // 2, 148, "SIX STORIES THAT SHAPED THE DAY", 2, GREY)
    c.hline(60, W - 61, 172, INK, 2)
    # story grid: 2 columns x 3 rows
    for i, story in enumerate(STORIES):
        px = 8 + (i % 2) * 512
        py = 184 + (i // 2) * 272
        draw_panel(c, px, py, story)
    # footer
    c.text_center(W // 2, 998,
                  "ALL STORIES FIRST REPORTED ON 19 NOVEMBER 2026", 2, GREY)
    return c


# ---------------------------------------------------------------- PNG output
def png_bytes(c):
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", c.w, c.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(c.h):
        raw.append(0)  # filter: none
        raw += c.px[y * c.w * 3:(y + 1) * c.w * 3]
    idat = zlib.compress(bytes(raw), 9)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw_page())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()
