"""
clock.py is the entry point. It lays out the flavor-text box,
the big-digit clock box and the exit/config buttons, then loops
watching the clock, config.json and console input for changes.

Run it with: python clock.py
"""
import ctypes
import os
import subprocess
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from blessed import Terminal

import appConfig
import bigDigits
import buttons
import layoutBoxes
import textProviders
import winConsoleInput

scriptDir = os.path.dirname(os.path.abspath(__file__))
configPath = os.path.join(scriptDir, "config.json")

term = Terminal()
notepadProcess = None


def enableUtf8Console():
    """Switches stdout and the console codepage to UTF-8.

    Without this, em dashes/curly quotes from fetched text can
    come out mangled on the legacy Windows console codepage.
    """
    try:
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass


def resolveNow(timezoneName):
    """Gets the current time in the configured timezone.

    Falls back to local system time if the name is invalid.
    """
    try:
        return datetime.now(ZoneInfo(timezoneName))
    except Exception:
        return datetime.now().astimezone()


def placeText(rowChars, startCol, text):
    """Overwrites a plain (unstyled) row segment in place."""
    for offset, character in enumerate(text):
        rowChars[startCol + offset] = character


def buildButtonRows(positions, rowWidth):
    """Draws the exit/config button rows side by side.

    positions already holds absolute terminal columns, so these
    rows are built at full width rather than needing a margin.
    """
    exitLines = buttons.buildButtonLines("exit")
    configLines = buttons.buildButtonLines("config")
    rows = []
    for rowOffset in range(buttons.buttonHeight):
        rowChars = [" "] * rowWidth
        placeText(rowChars, positions["exit"]["left"], exitLines[rowOffset])
        placeText(rowChars, positions["config"]["left"], configLines[rowOffset])
        rows.append("".join(rowChars))
    return rows


def buildFrame(config, displayText):
    """Builds every visible row of the app as one list of strings.

    Also returns the button hit-boxes and the HH:MM:SS last drawn,
    so the caller knows when a redraw is actually needed.
    """
    margin = layoutBoxes.computeCenterMargin(term.width, layoutBoxes.boxWidth)
    indent = " " * margin

    quoteLines = layoutBoxes.wrapToBox(displayText)
    flavorBox = layoutBoxes.buildBox(quoteLines, italic=config["italics"], term=term)

    now = resolveNow(config["timezone"])
    timeString = now.strftime("%H:%M:%S")
    digitLines = bigDigits.renderBigTime(timeString)
    clockBox = layoutBoxes.buildDoubleWallBox(digitLines, minHeight=16)

    frame = ["", ""]  # 2-line gap above the whole UI
    frame.extend(indent + row for row in flavorBox)
    frame.append("")  # 1-line gap kept between the two boxes
    clockBoxTop = len(frame)
    frame.extend(indent + row for row in clockBox)

    clockBoxLeft = margin
    clockBoxRight = margin + layoutBoxes.boxWidth - 1
    buttonTop = clockBoxTop + len(clockBox) + buttons.buttonGapBelowClock
    positions = buttons.buttonPositions(clockBoxLeft, clockBoxRight, buttonTop)

    frame.extend([""] * buttons.buttonGapBelowClock)
    frame.extend(buildButtonRows(positions, margin + layoutBoxes.boxWidth))

    return frame, positions, timeString


def redraw(frame):
    """Clears the screen and prints the freshly built frame."""
    print(term.home + term.clear + "\n".join(frame))


def launchConfigEditor():
    """Opens config.json in Notepad, unless it's already open."""
    global notepadProcess
    if notepadProcess is not None and notepadProcess.poll() is None:
        return
    notepadProcess = subprocess.Popen(["notepad.exe", configPath])


def handleInputEvent(event, positions):
    """Turns one raw input event into 'exit', 'config' or None."""
    kind, value = event
    if kind == "click":
        x, y = value
        if buttons.pointInButton(x, y, positions["exit"]):
            return "exit"
        if buttons.pointInButton(x, y, positions["config"]):
            return "config"
    elif kind == "key":
        lowerKey = value.lower()
        if lowerKey == "e":
            return "exit"
        if lowerKey == "c":
            return "config"
    return None


def main():
    enableUtf8Console()
    if term.width < layoutBoxes.boxWidth:
        sys.exit(f"This clock needs a terminal at least {layoutBoxes.boxWidth} columns wide.")

    config = appConfig.loadConfig(configPath)
    displayText = textProviders.fetchDisplayText(config["textSource"])
    configMTime = appConfig.getConfigMTime(configPath)
    frame, positions, lastTimeString = buildFrame(config, displayText)

    handle, originalMode = winConsoleInput.enableRawMouseMode()
    try:
        with term.fullscreen(), term.hidden_cursor():
            redraw(frame)
            running = True
            while running:
                time.sleep(0.2)

                event = winConsoleInput.pollInputEvent(handle)
                action = handleInputEvent(event, positions) if event else None
                if action == "exit":
                    running = False
                    continue
                if action == "config":
                    launchConfigEditor()

                newMTime = appConfig.getConfigMTime(configPath)
                configChanged = newMTime is not None and newMTime != configMTime
                nowTimeString = resolveNow(config["timezone"]).strftime("%H:%M:%S")
                timeChanged = nowTimeString != lastTimeString

                if configChanged:
                    configMTime = newMTime
                    config = appConfig.loadConfig(configPath)
                    displayText = textProviders.fetchDisplayText(config["textSource"])
                    frame, positions, lastTimeString = buildFrame(config, displayText)
                    redraw(frame)
                elif timeChanged:
                    frame, positions, lastTimeString = buildFrame(config, displayText)
                    redraw(frame)
    finally:
        winConsoleInput.restoreConsoleMode(handle, originalMode)

    print("Goodbye.")


if __name__ == "__main__":
    main()
