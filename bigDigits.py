"""
bigDigits builds the large clock glyphs. Every character is
defined as two lists of spreadsheet-style cell codes (a column
letter plus a row number, like 'C4') - one for solid fill, one
for the soft "shadow" tint - rather than computed rectangles.
This is what lets a glyph (like 4's diagonal) take any shape,
not just straight horizontal/vertical bars.
"""

digitHeight = 10  # shared by every glyph, so rows line up when joined
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


# each glyph: which cells are solid fill, and which are shadowed.
# Hand-designed cell by cell (not computed from 7-segment rules),
# so shapes here can be anything - diagonals, curves, tapers.
glyphCells = {
    "0": {
        "fill": ["B1", "C1", "D1", "E1", "F1", "G1",
                 "A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2",
                 "A3", "B3", "C3", "F3", "G3", "H3",
                 "A4", "B4", "G4", "H4",
                 "A5", "B5", "G5", "H5",
                 "A6", "B6", "G6", "H6",
                 "A7", "B7", "C7", "F7", "G7", "H7",
                 "A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8",
                 "B9", "C9", "D9", "E9", "F9", "G9"],
        "shadow": ["D3", "E3", "I3", "C4", "D4", "I4", "C5", "I5", "C6", "I6", "D7", "I7", "I8",
                   "H9", "I9", "C10", "D10", "E10", "F10", "G10", "H10"],
    },
    "1": {
        "fill": ["E1", "F1", "G1",
                 "D2", "E2", "F2", "G2",
                 "C3", "D3", "F3", "G3",
                 "F4", "G4",
                 "F5", "G5",
                 "F6", "G6",
                 "F7", "G7",
                 "C8", "D8", "E8", "F8", "G8", "H8", "I8",
                 "C9", "D9", "E9", "F9", "G9", "H9", "I9"],
        "shadow": ["G2", "D3", "G3", "D4", "E4", "H4", "H5", "H6", "H7", "J9",
                   "D10", "E10", "F10", "G10", "H10", "I10", "J10"],
    },
    "2": {
        "fill": ["B1", "C1", "D1", "E1", "F1", "G1",
                 "A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2",
                 "A3", "B3", "G3", "H3",
                 "G4", "H4",
                 "C5", "D5", "E5", "F5", "G5", "H5",
                 "A6", "B6", "C6", "D6", "E6", "F6",
                 "A7", "B7",
                 "A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8",
                 "A9", "B9", "C9", "D9", "E9", "F9", "G9", "H9"],
        "shadow": ["C3", "I3", "I4", "I5", "G6", "H6", "C7", "D7", "E7", "I9",
                   "B10", "C10", "D10", "E10", "F10", "G10", "H10", "I10"],
    },
    "3": {
        "fill": ["B1", "C1", "D1", "E1", "F1", "G1",
                 "A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2",
                 "A3", "B3", "F3", "G3", "H3",
                 "G4", "H4",
                 "A5", "B5", "C5", "D5", "E5", "F5", "G5", "H5",
                 "G6", "H6",
                 "A7", "B7", "F7", "G7", "H7",
                 "A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8",
                 "A9", "B9", "C9", "D9", "E9", "F9", "G9"],
        "shadow": ["C3", "I3", "I4", "I5", "B6", "C6", "D6", "E6", "F6", "I6", "I7", "I8",
                   "H9", "I9", "B10", "C10", "D10", "E10", "F10", "G10", "H10"],
    },
    "4": {
        "fill": ["E1", "F1", "G1", "H1", "D2", "E2", "G2", "H2", "C3", "D3", "G3", "H3",
                 "B4", "C4", "G4", "H4",
                 "A5", "B5", "C5", "D5", "E5", "F5", "G5", "H5",
                 "A6", "B6", "C6", "D6", "E6", "F6", "G6", "H6",
                 "G7", "H7", "G8", "H8", "G9", "H9"],
        "shadow": ["F2", "I2", "E3", "I3", "D4", "I4", "I5", "I6", "B7", "C7", "D7", "E7", "F7",
                   "I7", "I8", "I9", "H10", "I10"],
    },
    "5": {
        "fill": ["A1", "B1", "C1", "D1", "E1", "F1", "G1", "H1", "I1",
                 "A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2", "I2",
                 "A3", "B3",
                 "A4", "B4", "C4", "D4", "E4", "F4", "G4", "H4",
                 "A5", "B5", "C5", "D5", "E5", "F5", "G5", "H5", "I5",
                 "H6", "I6",
                 "A7", "B7", "H7", "I7",
                 "A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8", "I8",
                 "B9", "C9", "D9", "E9", "F9", "G9", "H9"],
        "shadow": ["J2", "C3", "D3", "E3", "F3", "G3", "H3", "I3", "J3", "J6", "J7", "J8",
                   "I9", "J9", "C10", "D10", "E10", "F10", "G10", "H10", "I10"],
    },
    "6": {
        "fill": ["B1", "C1", "D1", "E1", "F1", "G1",
                 "A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2",
                 "A3", "B3",
                 "A4", "B4", "C4", "D4", "E4", "F4", "G4",
                 "A5", "B5", "C5", "D5", "E5", "F5", "G5", "H5",
                 "A6", "B6", "G6", "H6",
                 "A7", "B7", "G7", "H7",
                 "A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8",
                 "B9", "C9", "D9", "E9", "F9", "G9"],
        "shadow": ["I2", "C3", "D3", "E3", "F3", "G3", "H3", "I3", "J3", "I5", "C6", "I6", "J6",
                   "C7", "I7", "J7", "I8", "J8", "H9", "I9", "C10", "D10", "E10", "F10", "G10", "H10"],
    },
    "7": {
        "fill": ["A1", "B1", "C1", "D1", "E1", "F1", "G1", "H1", "I1", "J1",
                 "A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2", "I2", "J2",
                 "A3", "B3", "I3", "J3",
                 "H4", "I4",
                 "G5", "H5",
                 "F6", "G6",
                 "E7", "F7",
                 "D8", "E8",
                 "C9", "D9"],
        "shadow": ["K2", "C3", "D3", "E3", "F3", "G3", "H3", "K3", "B4", "C4", "J4", "K4",
                   "I5", "J5", "H6", "I6", "G7", "H7", "F8", "G8", "E9", "F9", "D10", "E10"],
    },
    "8": {
        "fill": ["B1", "C1", "D1", "E1", "F1", "G1",
                 "A2", "B2", "C2", "F2", "G2", "H2",
                 "A3", "B3", "G3", "H3",
                 "A4", "B4", "C4", "F4", "G4", "H4",
                 "B5", "C5", "D5", "E5", "F5", "G5",
                 "A6", "B6", "C6", "F6", "G6", "H6",
                 "A7", "B7", "G7", "H7",
                 "A8", "B8", "C8", "F8", "G8", "H8",
                 "B9", "C9", "D9", "E9", "F9"],
        "shadow": ["D2", "E2", "I2", "C3", "D3", "E3", "I3", "J3", "D4", "I4", "J4",
                   "H5", "I5", "J5", "D6", "E6", "I6", "C7", "D7", "I7", "J7", "I8", "J8",
                   "G9", "H9", "I9", "D10", "E10", "F10", "G10", "H10"],
    },
    "9": {
        "fill": ["B1", "C1", "D1", "E1", "F1", "G1", "H1",
                 "A2", "B2", "C2", "G2", "H2", "I2",
                 "A3", "B3", "H3", "I3",
                 "A4", "B4", "C4", "G4", "H4", "I4",
                 "B5", "C5", "D5", "E5", "F5", "G5", "H5", "I5",
                 "G6", "H6", "I6",
                 "A7", "B7", "G7", "H7", "I7",
                 "A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8",
                 "C9", "D9", "E9", "F9", "G9"],
        "shadow": ["D2", "E2", "F2", "J2", "C3", "D3", "E3", "J3", "K3", "D4", "J4", "K4",
                   "J5", "K5", "D6", "E6", "F6", "J6", "K6", "J7", "K7", "I8", "J8", "K8",
                   "H9", "I9", "J9", "D10", "E10", "F10", "G10", "H10", "I10"],
    },
    ":": {
        "fill": ["A3", "B3", "A4", "B4", "A7", "B7", "A8", "B8"],
        "shadow": ["C4", "B5", "C5", "C8", "B9", "C9"],
    },
}


def buildGlyphGrid(character):
    """Rasterizes one character's cell codes into display-ready rows."""
    cells = glyphCells.get(character)
    if not cells:
        return [" "] * digitHeight

    allCodes = cells["fill"] + cells["shadow"]
    width = max(parseCellCode(code)[1] for code in allCodes) + 1
    grid = [[" "] * width for _ in range(digitHeight)]

    for code in cells["fill"]:
        row, col = parseCellCode(code)
        grid[row][col] = fillChar
    for code in cells["shadow"]:
        row, col = parseCellCode(code)
        grid[row][col] = shadowChar

    return ["".join(row) for row in grid]


def renderBigTime(timeText):
    """Renders a string like '14:07:32' into the big glyph rows."""
    columns = [buildGlyphGrid(character) for character in timeText]
    rows = []
    for rowIndex in range(digitHeight):
        rows.append(" ".join(column[rowIndex] for column in columns))
    return rows
