"""
bigLetters builds the todo panel's blocky "TODO" header, the same
way clock/bigDigits.py builds the clock digits: each character is
spreadsheet-style cell codes (fill + a soft shadow), hand-placed
rather than computed from a font. Only T/O/D exist here since the
header is the only thing that currently needs big letters - kept
as its own small file rather than sharing bigDigits.py's, since
that module is clock-exclusive (see clock/__init__.py).
"""

letterHeight = 8  # 7 rows of letter + 1 for the shadow spilling past the bottom
fillChar = "█"
shadowChar = "░"


def parseCellCode(code):
    """Turns a code like 'C4' into 0-indexed (row, col)."""
    letters = "".join(ch for ch in code if ch.isalpha())
    digits = code[len(letters):]

    col = 0
    for ch in letters.upper():
        col = col * 26 + (ord(ch) - ord("A") + 1)
    return int(digits) - 1, col - 1


# hand-placed like bigDigits.glyphCells - which cells are solid fill,
# which are the soft drop-shadow, for each letter TODO needs.
glyphCells = {
    "T": {
        "fill": ["A1", "B1", "C1", "D1", "E1", "C2", "C3", "C4", "C5", "C6", "C7"],
        "shadow": ["B2", "D2", "E2", "F2", "D3", "D4", "D5", "D6", "D7", "D8"],
    },
    "O": {
        "fill": ["B1", "C1", "D1", "A2", "E2", "A3", "E3", "A4", "E4", "A5", "E5",
                 "A6", "E6", "B7", "C7", "D7"],
        "shadow": ["C2", "D2", "B3", "F3", "B4", "F4", "B5", "F5", "B6", "F6",
                   "F7", "C8", "D8", "E8"],
    },
    "D": {
        "fill": ["A1", "B1", "C1", "D1", "A2", "E2", "A3", "E3", "A4", "E4", "A5",
                 "E5", "A6", "E6", "A7", "B7", "C7", "D7"],
        "shadow": ["B2", "C2", "D2", "B3", "F3", "B4", "F4", "B5", "F5", "B6",
                   "F6", "F7", "B8", "C8", "D8", "E8"],
    },
}


def buildGlyphGrid(character):
    """Rasterizes one letter's cell codes into display-ready rows."""
    cells = glyphCells.get(character)
    if not cells:
        return [" "] * letterHeight

    allCodes = cells["fill"] + cells["shadow"]
    width = max(parseCellCode(code)[1] for code in allCodes) + 1
    grid = [[" "] * width for _ in range(letterHeight)]

    for code in cells["fill"]:
        row, col = parseCellCode(code)
        grid[row][col] = fillChar
    for code in cells["shadow"]:
        row, col = parseCellCode(code)
        grid[row][col] = shadowChar

    return ["".join(row) for row in grid]


def renderBigText(text):
    """Renders a string like 'TODO' into the big glyph rows, one
    space between letters (mirrors bigDigits.renderBigTime)."""
    columns = [buildGlyphGrid(character) for character in text]
    rows = []
    for rowIndex in range(letterHeight):
        rows.append(" ".join(column[rowIndex] for column in columns))
    return rows
