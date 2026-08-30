"""
layoutBoxes turns plain text/content into the dashed ASCII
boxes used across the app (the clock box and the flavor-text
box share this same builder).
"""
import textwrap

boxWidth = 120
horizontalPadding = 2
verticalPadding = 1


def innerTextWidth(width=boxWidth):
    """Usable width for text once borders and padding are removed."""
    return width - 2 - (horizontalPadding * 2)


def wrapToBox(text, width=boxWidth):
    """Wraps free text to the box's inner width, line by line."""
    wrapWidth = innerTextWidth(width)
    wrapped = []
    for paragraph in text.split("\n"):
        pieces = textwrap.wrap(paragraph, wrapWidth) or [""]
        wrapped.extend(pieces)
    return wrapped


def styleLine(line, width, italic, term):
    """Pads a line to full width first, then italicises it.

    Padding first keeps escape codes out of the column math.
    """
    padded = line.center(innerTextWidth(width))
    if italic and term is not None:
        return term.italic(padded)
    return padded


def buildBox(contentLines, width=boxWidth, minHeight=8, italic=False, term=None):
    """Builds a full dashed box (top/bottom + padded sides).

    contentLines are already-wrapped text rows; the box grows
    taller than minHeight if there are more lines than it can hold.
    """
    border = "+" + "-" * (width - 2) + "+"
    blank = "|" + " " * (width - 2) + "|"

    minContentRows = max(minHeight - 2 - (verticalPadding * 2), 0)
    contentRows = max(len(contentLines), minContentRows)
    extraBlanks = contentRows - len(contentLines)
    topBlanks = extraBlanks // 2
    bottomBlanks = extraBlanks - topBlanks

    rows = [border] + [blank] * verticalPadding
    rows += [blank] * topBlanks
    for line in contentLines:
        styled = styleLine(line, width, italic, term)
        rows.append("|" + " " * horizontalPadding + styled +
                     " " * horizontalPadding + "|")
    rows += [blank] * bottomBlanks
    rows += [blank] * verticalPadding + [border]
    return rows


def centerBlockLines(blockLines, width=boxWidth):
    """Centers a small multi-line block (e.g. the big clock digits)."""
    return [line.center(innerTextWidth(width)) for line in blockLines]
