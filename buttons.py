"""
buttons defines the exit/config button boxes: their fixed
size, where they sit relative to the clock box, and simple
point-in-rectangle hit testing for mouse clicks.
"""
import layoutBoxes

buttonWidth = 18
buttonHeight = 3
buttonGapBelowClock = 3
clockBoxWallInset = 8


def buildButtonLines(label):
    """Draws one fully-walled button (roof, label, floor).

    Reuses buildBox with the clock's Unicode corners, but with
    no padding so the label sits flush inside a compact box.
    """
    return layoutBoxes.buildBox(
        [label.upper()], width=buttonWidth, minHeight=buttonHeight,
        chars=layoutBoxes.unicodeBorderChars,
        horizontalPadding=0, verticalPadding=0,
    )


def buttonPositions(clockBoxLeft, clockBoxRight, buttonTop):
    """Computes top-left corners for the exit and config buttons.

    Both are inset clockBoxWallInset characters from the clock
    box's own left/right edges, buttonTop lines from the top.
    """
    exitLeft = clockBoxLeft + clockBoxWallInset
    configRight = clockBoxRight - clockBoxWallInset
    configLeft = configRight - buttonWidth + 1
    return {
        "exit": {"top": buttonTop, "left": exitLeft},
        "config": {"top": buttonTop, "left": configLeft},
    }


def pointInButton(x, y, button):
    """True if console coordinates (x, y) fall inside a button."""
    withinX = button["left"] <= x < button["left"] + buttonWidth
    withinY = button["top"] <= y < button["top"] + buttonHeight
    return withinX and withinY
