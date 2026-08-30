"""
bigDigits builds the large 3-row-tall clock glyphs.
Each digit is expressed as a 7-segment set (a-g) so
new glyphs only need a segment list, not raw art.
"""

# segmentLayout maps each digit/char to which of the
# 7 classic segments (a=top, b=topRight, c=bottomRight,
# d=bottom, e=bottomLeft, f=topLeft, g=middle) are lit.
segmentLayout = {
    "0": set("abcdef"),
    "1": set("bc"),
    "2": set("abged"),
    "3": set("abgcd"),
    "4": set("fgbc"),
    "5": set("afgcd"),
    "6": set("afgecd"),
    "7": set("abc"),
    "8": set("abcdefg"),
    "9": set("abcdfg"),
}


def buildGlyph(character):
    """Turns one character into its 3-row, 3-wide glyph lines."""
    if character == ":":
        return ["o", " ", "o"]
    if character not in segmentLayout:
        return ["   ", "   ", "   "]

    segments = segmentLayout[character]
    topRow = " " + ("_" if "a" in segments else " ") + " "
    midRow = ("|" if "f" in segments else " ") + \
             ("_" if "g" in segments else " ") + \
             ("|" if "b" in segments else " ")
    lowRow = ("|" if "e" in segments else " ") + \
             ("_" if "d" in segments else " ") + \
             ("|" if "c" in segments else " ")
    return [topRow, midRow, lowRow]


def renderBigTime(timeText):
    """Renders a string like '14:07' into 3 wide display rows."""
    rows = ["", "", ""]
    for character in timeText:
        glyph = buildGlyph(character)
        for rowIndex in range(3):
            rows[rowIndex] += glyph[rowIndex] + " "
    # drop the trailing gap column added after the last glyph
    return [row[:-1] for row in rows]
