"""
clockPanel wraps the original flavor-text-plus-big-digits display
(what clock.py used to draw as the whole app) as a Panel: given
whatever width prompt_toolkit hands it - its share of the split
screen - it centers the same two boxes inside that width instead
of the whole terminal.

The clock panel is always shown (see app.py) and owns the app's
exit/config buttons - see attachActions() - since it's the one
panel guaranteed to be on screen to host them.
"""
import os
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

from prompt_toolkit.layout import HSplit, Window
from prompt_toolkit.layout.controls import UIContent, UIControl
from prompt_toolkit.mouse_events import MouseEventType

import appConfig
import layoutBoxes
from clock import bigDigits, buttons, textProviders
from panels import Panel

# the clock box is wider than the quote box's default boxWidth,
# widened so the uniform 11-wide digits (bigDigits.digitWidth) fit with room to spare.
clockBoxWidth = 90
clockRightBuffer = 1
quoteBoxWidth = layoutBoxes.boxWidth


def resolveNow(timezoneName):
    """Current time in timezoneName, or local system time if that name is invalid."""
    try:
        return datetime.now(ZoneInfo(timezoneName))
    except Exception:
        return datetime.now().astimezone()


def isClick(mouseEvent):
    """True for a completed left-click (button release)."""
    return mouseEvent.event_type == MouseEventType.MOUSE_UP


def clockBoxEdges(width):
    """The clock box's own left/right columns once centered in width -
    shared by _ClockControl and _ButtonsControl so both agree on where it is."""
    margin = layoutBoxes.computeCenterMargin(width, clockBoxWidth + clockRightBuffer)
    return margin, margin + clockBoxWidth + clockRightBuffer - 1


class ClockPanel(Panel):
    """The clock panel: config-driven flavor text above a live digit
    clock, plus the app's exit/config buttons below (see attachActions)."""

    name = "clock"
    minWidth = clockBoxWidth + clockRightBuffer  # never split narrower than the clock box itself needs

    def __init__(self, scriptDir):
        super().__init__(scriptDir)
        self.configPath = os.path.join(scriptDir, "config.json")
        self.config = appConfig.loadConfig(self.configPath)
        self.displayText = textProviders.fetchDisplayText(self.config["textSource"])
        self.configMTime = appConfig.getConfigMTime(self.configPath)
        self.now = resolveNow(self.config["timezone"])
        self._onExit = lambda: None
        self._notepadProcess = None
        # dont_extend_height stops this window claiming the terminal's full
        # height (it's the HSplit's only flexible child otherwise), which
        # was pushing the buttons down to the bottom of the screen instead
        # of sitting right under the clock box.
        self.focusWindow = Window(_ClockControl(self), dont_extend_height=True)
        self._container = HSplit([
            self.focusWindow,
            Window(height=buttons.buttonGapBelowClock),
            Window(_ButtonsControl(self), height=buttons.buttonHeight),
        ])

    def attachExit(self, onExit):
        """Wires the exit button to Application.exit - called once from
        app.py, since the Application doesn't exist until after this panel does."""
        self._onExit = onExit

    def container(self):
        return self._container

    def launchConfigEditor(self):
        """Opens config.json in Notepad, unless it's already open."""
        if self._notepadProcess is not None and self._notepadProcess.poll() is None:
            return
        self._notepadProcess = subprocess.Popen(["notepad.exe", self.configPath])

    def tick(self):
        # re-fetch config + flavor text only when config.json's mtime actually
        # changed (a Notepad save) - the clock time itself updates every tick.
        newMTime = appConfig.getConfigMTime(self.configPath)
        if newMTime is not None and newMTime != self.configMTime:
            self.configMTime = newMTime
            self.config = appConfig.loadConfig(self.configPath)
            self.displayText = textProviders.fetchDisplayText(self.config["textSource"])
        self.now = resolveNow(self.config["timezone"])


class _ClockControl(UIControl):
    """Builds the flavor-box + clock-box rows fresh each render, sized
    to whatever width the layout actually gives this panel this frame."""

    def __init__(self, panel):
        self.panel = panel

    def preferred_height(self, width, max_available_height, wrap_lines, get_line_prefix):
        # without this, the base UIControl reports no opinion and HSplit
        # stretches this window to fill the screen instead of just its content.
        return self.create_content(width, max_available_height).line_count

    def create_content(self, width, height):
        """Renders the flavor box + clock box centered in width, as one UIContent."""
        panel = self.panel
        margin, _ = clockBoxEdges(width)
        indent = " " * margin

        # the clock box is wider than the quote box, so nudge the quote
        # box over by half the difference to center it under the clock
        quoteBoxOffset = (clockBoxWidth + clockRightBuffer - quoteBoxWidth) // 2
        quoteIndent = " " * (margin + quoteBoxOffset)

        quoteLines = layoutBoxes.wrapToBox(panel.displayText, width=quoteBoxWidth)
        flavorBox = layoutBoxes.buildBox(quoteLines, width=quoteBoxWidth)

        digitLines = bigDigits.renderBigTime(panel.now.strftime("%H:%M:%S"))
        clockBox = layoutBoxes.buildDoubleWallBox(digitLines, width=clockBoxWidth, minHeight=16,
                                                   rightBuffer=clockRightBuffer)

        italic = panel.config.get("italics", False)
        style = "italic" if italic else ""

        rows = [[("", "")], [("", "")]]  # 2-line gap, matching the original layout
        for row in flavorBox:
            rows.append([(style, quoteIndent + row)])
        rows.append([("", "")])  # 1-line gap kept between the two boxes
        for row in clockBox:
            rows.append([("", indent + row)])

        return UIContent(get_line=lambda lineIndex: rows[lineIndex],
                          line_count=len(rows), show_cursor=False)


class _ButtonsControl(UIControl):
    """Draws the exit/config buttons, each fragment wired to its
    action - no manual point-in-rectangle math needed."""

    def __init__(self, panel):
        self.panel = panel
        self._rows = []  # last-rendered rows, so mouse_handler can find what was clicked

    def create_content(self, width, height):
        panel = self.panel
        clockBoxLeft, clockBoxRight = clockBoxEdges(width)
        exitLeft = clockBoxLeft + buttons.clockBoxWallInset
        configRight = clockBoxRight - buttons.clockBoxWallInset
        configLeft = configRight - buttons.buttonWidth + 1

        exitLines = buttons.buildButtonLines("exit")
        configLines = buttons.buildButtonLines("config")
        rows = []
        for exitRow, configRow in zip(exitLines, configLines):
            rows.append([
                ("", " " * exitLeft + exitRow, lambda e: panel._onExit() if isClick(e) else None),
                ("", " " * (configLeft - (exitLeft + buttons.buttonWidth))),
                ("", configRow, lambda e: panel.launchConfigEditor() if isClick(e) else None),
            ])
        self._rows = rows
        return UIContent(get_line=lambda lineIndex: rows[lineIndex],
                          line_count=len(rows), show_cursor=False)

    def mouse_handler(self, mouseEvent):
        # a plain UIControl (unlike FormattedTextControl) doesn't dispatch
        # fragment-embedded click handlers on its own - this is that dispatch,
        # walking the last-rendered row to find which fragment covers the click.
        try:
            fragments = self._rows[mouseEvent.position.y]
        except IndexError:
            return NotImplemented
        offset = 0
        for fragment in fragments:
            offset += len(fragment[1])
            if offset > mouseEvent.position.x:
                return fragment[2](mouseEvent) if len(fragment) >= 3 else NotImplemented
        return NotImplemented
