"""
buttons defines the exit/config button boxes: their fixed
size, where they sit relative to the clock box, and simple
point-in-rectangle hit testing for mouse clicks.
"""

buttonWidth = 18
buttonHeight = 2
buttonGapBelowClock = 3
leftWallOffset = 14
rightWallInset = 14


def buildButtonLines(label):
    """Draws one 2-line bordered button with a centered label."""
    top = "+" + "-" * (buttonWidth - 2) + "+"
    labelRow = "|" + label.upper().center(buttonWidth - 2) + "|"
    return [top, labelRow]


def buttonPositions(clockBoxTop, clockBoxHeight, clockBoxWidth=120):
    """Computes top-left corners for the exit and config buttons.

    Both sit buttonGapBelowClock blank lines under the clock box.
    """
    buttonTop = clockBoxTop + clockBoxHeight + buttonGapBelowClock
    exitLeft = leftWallOffset
    configRight = (clockBoxWidth - 1) - rightWallInset
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
