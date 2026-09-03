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


def styleLine(line, width, horizontalPadding=horizontalPadding):
    """Pads a line to the box's full inner width, centered.
    Styling (e.g. italics) is the caller's job, not this function's."""
    return line.center(innerTextWidth(width, horizontalPadding))


def buildBox(contentLines, width=boxWidth, minHeight=8,
             chars=None, horizontalPadding=horizontalPadding, verticalPadding=verticalPadding,
             rightBuffer=0, align="center"):
    """Builds a full box (top/bottom + padded sides) from already-wrapped
    contentLines; chars picks the corner/edge glyphs (default: plain ASCII).
    align picks where the leftover space (minHeight beyond contentLines)
    goes: "center" (default, split top/bottom) or "top" (all of it below)."""
    chars = chars or asciiBorderChars

    # the three border/blank row strings every other row is built from
    outerWidth = width + rightBuffer
    topBorder = chars["tl"] + chars["h"] * (outerWidth - 2) + chars["tr"]
    bottomBorder = chars["bl"] + chars["h"] * (outerWidth - 2) + chars["br"]
    blank = chars["v"] + " " * (outerWidth - 2) + chars["v"]

    # grows past minHeight if contentLines has more rows than it can hold
    minContentRows = max(minHeight - 2 - (verticalPadding * 2), 0)
    contentRows = max(len(contentLines), minContentRows)
    extraBlanks = contentRows - len(contentLines)
    topBlanks = 0 if align == "top" else extraBlanks // 2
    bottomBlanks = extraBlanks - topBlanks

    rows = [topBorder] + [blank] * verticalPadding
    rows += [blank] * topBlanks
    for line in contentLines:
        styled = styleLine(line, width, horizontalPadding)
        rows.append(chars["v"] + " " * horizontalPadding + styled +
                     " " * horizontalPadding + " " * rightBuffer + chars["v"])
    rows += [blank] * bottomBlanks
    rows += [blank] * verticalPadding + [bottomBorder]
    return rows


def buildDoubleWallBox(contentLines, width=boxWidth, minHeight=8, rightBuffer=0):
    """Draws a 'double-walled' box: an inner Unicode box inset one line
    inside an outer one, one character narrower than that horizontally."""
    innerWidth = width - 3
    innerMinHeight = minHeight - 2
    innerBox = buildBox(contentLines, width=innerWidth, minHeight=innerMinHeight,
                         chars=unicodeBorderChars, rightBuffer=rightBuffer)

    # the outer wall wraps the inner box's rows exactly, one wall-width
    # narrower than a regular border since it has no padding of its own
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
