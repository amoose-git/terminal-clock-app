"""
app.py is the entry point - a generic split-screen dispatcher. The
clock panel is always shown (it hosts the exit/config buttons - see
clock/clockPanel.py); flags (-todo, ...) add other registered panels
(see panels/registry.py) alongside it, each with its own share of
the screen and, if it wants one, its own input line.

Run it with: python app.py [-todo]
"""
import argparse
import asyncio
import os

from prompt_toolkit import Application
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Dimension, Layout, VSplit

import appConfig
from panels.registry import panelClasses

scriptDir = os.path.dirname(os.path.abspath(__file__))
configPath = os.path.join(scriptDir, "config.json")

tickSeconds = 1.0
defaultPanelWeight = 50  # used when a shown panel has no weight configured in config.json

# clock is always on (it's the buttons' home, not just another optional
# panel), so it never gets its own -clock flag - every other registry
# entry does.
optionalPanelNames = [name for name in panelClasses if name != "clock"]


def parseArgs():
    """-<panelName> flags (besides clock, which is always on) into
    an ordered list of active panel names, clock first."""
    parser = argparse.ArgumentParser(
        description="Terminal split-screen apps - clock (always on), todo, and whatever else is registered.")
    for name in optionalPanelNames:
        parser.add_argument(f"-{name}", action="store_true", help=f"show the {name} panel")
    args = parser.parse_args()

    return ["clock"] + [name for name in optionalPanelNames if getattr(args, name)]


def main():
    """Builds the active panels into one split-screen layout, then
    runs the app until exit - see the chunk comments below for each stage."""
    activeNames = parseArgs()
    panels = [panelClasses[name](scriptDir) for name in activeNames]

    # each panel's column width is a live-mutable Dimension so a config.json
    # edit (watched below in tickLoop) can resize the split without a restart
    startingConfig = appConfig.loadConfig(configPath)
    weightsMTime = appConfig.getConfigMTime(configPath)

    weightDimensions = {}
    panelWindows = []
    for panel in panels:
        weight = startingConfig["panelWeights"].get(panel.name, defaultPanelWeight)
        # min reserves a panel's required width (if it has one, e.g. the clock
        # box) before weight divides whatever's left - so it never gets clipped
        dimension = Dimension(weight=weight, min=panel.minWidth)
        weightDimensions[panel.name] = dimension
        container = panel.container()
        container.width = dimension
        panelWindows.append(container)

    columns = VSplit(panelWindows, padding=1) if len(panelWindows) > 1 else panelWindows[0]

    # a panel with its own input line (todo has one; clock doesn't) exposes
    # it as .inputWindow - default focus lands there, and global e/c below
    # get suppressed while any of them is focused, so typing "exercise"
    # into a todo item can't accidentally quit.
    inputWindows = [panel.inputWindow for panel in panels if panel.inputWindow is not None]
    initialFocus = inputWindows[0] if inputWindows else panels[0].focusWindow

    layout = Layout(columns, focused_element=initialFocus)
    inputFocused = Condition(lambda: layout.current_window in inputWindows)

    # e/c only fire when no panel's input line is focused; Ctrl+C always works regardless.
    bindings = KeyBindings()

    @bindings.add("c-c")
    def _(event):
        event.app.exit()

    @bindings.add("e", filter=~inputFocused)
    def _(event):
        event.app.exit()

    @bindings.add("c", filter=~inputFocused)
    def _(event):
        clockPanel.launchConfigEditor()

    @bindings.add("tab")
    def _(event):
        event.app.layout.focus_next()

    @bindings.add("s-tab")
    def _(event):
        event.app.layout.focus_previous()

    application = Application(layout=layout, key_bindings=bindings, mouse_support=True,
                               full_screen=True)

    clockPanel = panels[0]  # always present, always first - see parseArgs
    clockPanel.attachExit(application.exit)

    async def tickLoop():
        """Once a second: refresh every panel, and re-check config.json
        for a panelWeights edit so the split resizes without a restart."""
        nonlocal weightsMTime
        while True:
            await asyncio.sleep(tickSeconds)
            for panel in panels:
                panel.tick()

            newMTime = appConfig.getConfigMTime(configPath)
            if newMTime is not None and newMTime != weightsMTime:
                weightsMTime = newMTime
                newWeights = appConfig.loadConfig(configPath)["panelWeights"]
                for name, dimension in weightDimensions.items():
                    dimension.weight = newWeights.get(name, defaultPanelWeight)

            application.invalidate()

    async def runner():
        """Runs tickLoop alongside the UI, and stops it when the UI exits."""
        background = asyncio.create_task(tickLoop())
        try:
            await application.run_async()
        finally:
            background.cancel()

    asyncio.run(runner())
    print("Goodbye.")


if __name__ == "__main__":
    main()
