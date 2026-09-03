"""
buttons defines the exit/config button boxes' fixed size and
rendering. Click hit-testing used to live here too, but app.py's
footer now uses prompt_toolkit's own per-fragment mouse handlers
instead of manual point-in-rectangle math.
"""
import layoutBoxes

buttonWidth = 18
buttonHeight = 3
clockBoxWallInset = 9  # columns in from the clock box's own left/right edges
buttonGapBelowClock = 3  # blank lines between the clock box and the buttons


def buildButtonLines(label):
    """Draws one fully-walled button (roof, label, floor), reusing
    buildBox's Unicode corners with no padding so the label sits flush."""
    return layoutBoxes.buildBox(
        [label.upper()], width=buttonWidth, minHeight=buttonHeight,
        chars=layoutBoxes.unicodeBorderChars,
        horizontalPadding=0, verticalPadding=0,
    )
