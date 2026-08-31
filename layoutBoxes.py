"""
layoutBoxes turns plain text/content into the dashed ASCII
boxes used across the app (the clock box and the flavor-text
box share this same builder).
"""
import textwrap

boxWidth = 80
horizontalPadding = 2
verticalPadding = 1

# two border-character sets: the flavor box keeps the plain
# ASCII look, while the clock box and buttons use Unicode
# single-line box-drawing glyphs instead of the '+' corner.
asciiBorderChars = {"tl": "+", "tr": "+", "bl": "+", "br": "+", "h": "-", "v": "|"}
unicodeBorderChars = {"tl": "┌", "tr": "┐", "bl": "└", "br": "┘", "h": "─", "v": "│"}


def innerTextWidth(width=boxWidth, horizontalPadding=horizontalPadding):
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


def styleLine(line, width, italic, term, horizontalPadding=horizontalPadding):
    """Pads a line to full width first, then italicises it.

    Padding first keeps escape codes out of the column math.
    """
    padded = line.center(innerTextWidth(width, horizontalPadding))
    if italic and term is not None:
        return term.italic(padded)
    return padded


def buildBox(contentLines, width=boxWidth, minHeight=8, italic=False, term=None,
             chars=None, horizontalPadding=horizontalPadding, verticalPadding=verticalPadding,
             rightBuffer=0):
    """Builds a full box (top/bottom + padded sides).

    contentLines are already-wrapped text rows; the box grows
    taller than minHeight if there are more lines than it can hold.
    chars picks the corner/edge glyphs (defaults to plain ASCII).
    rightBuffer adds extra blank columns before the right wall only -
    content is still centered against the original width, so this
    doesn't shift anything, it just pads the right side further out.
    """
    chars = chars or asciiBorderChars
    outerWidth = width + rightBuffer
    topBorder = chars["tl"] + chars["h"] * (outerWidth - 2) + chars["tr"]
    bottomBorder = chars["bl"] + chars["h"] * (outerWidth - 2) + chars["br"]
    blank = chars["v"] + " " * (outerWidth - 2) + chars["v"]

    minContentRows = max(minHeight - 2 - (verticalPadding * 2), 0)
    contentRows = max(len(contentLines), minContentRows)
    extraBlanks = contentRows - len(contentLines)
    topBlanks = extraBlanks // 2
    bottomBlanks = extraBlanks - topBlanks

    rows = [topBorder] + [blank] * verticalPadding
    rows += [blank] * topBlanks
    for line in contentLines:
        styled = styleLine(line, width, italic, term, horizontalPadding)
        rows.append(chars["v"] + " " * horizontalPadding + styled +
                     " " * horizontalPadding + " " * rightBuffer + chars["v"])
    rows += [blank] * bottomBlanks
    rows += [blank] * verticalPadding + [bottomBorder]
    return rows


def buildDoubleWallBox(contentLines, width=boxWidth, minHeight=8, italic=False, term=None,
                        rightBuffer=0):
    """Draws a 'double-walled' box: an inner Unicode box inset by
    exactly one line inside an outer one vertically (no blank
    buffer row between the two walls), and one character narrower
    than that horizontally.
    
    rightBuffer widens both walls by the same amount, purely as
    extra clearance on the right of the content (see buildBox).
    """
    innerWidth = width - 3
    innerMinHeight = minHeight - 2
    innerBox = buildBox(contentLines, width=innerWidth, minHeight=innerMinHeight,
                         italic=italic, term=term, chars=unicodeBorderChars,
                         rightBuffer=rightBuffer)

    chars = unicodeBorderChars
    outerWidth = width + rightBuffer
    outerTop = chars["tl"] + chars["h"] * (outerWidth - 3) + chars["tr"]
    outerBottom = chars["bl"] + chars["h"] * (outerWidth - 3) + chars["br"]

    rows = [outerTop]
    rows += [chars["v"] + innerRow + chars["v"] for innerRow in innerBox]
    rows.append(outerBottom)
    return rows


def computeCenterMargin(terminalWidth, contentWidth=boxWidth):
    """How many blank columns to indent so contentWidth sits centered."""
    return max(0, (terminalWidth - contentWidth) // 2)
