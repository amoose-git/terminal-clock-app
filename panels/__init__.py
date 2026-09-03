"""
panels defines the pluggable "app panel" contract app.py's
split-screen layout builds on. Each registered panel (clock,
todo, ...) is a small class that owns its own prompt_toolkit
container, including its own input line if it wants one - see
panels/registry.py to add a new one.
"""


class Panel:
    """Base contract every panel subclasses. name is the CLI flag
    (-<name>) app.py wires up automatically from the registry."""

    name = "panel"

    # set to a panel's own text-input Window (see panels/todoPanel.py)
    # if it has one - app.py checks this so global keys like "e"/"c"
    # know not to fire while that window is focused and being typed into.
    inputWindow = None

    # a hard column-width floor this panel needs to render without
    # clipping (see clock/clockPanel.py) - None means "no floor,
    # split purely by weight" (see app.py's Dimension(min=...) use).
    minWidth = None

    # a concrete focusable Window app.py can fall back to focusing when
    # no panel has an inputWindow - only needed if container() returns
    # something other than a plain Window (e.g. clock's HSplit).
    focusWindow = None

    def __init__(self, scriptDir):
        """scriptDir is the app's own directory, for panels that
        read/write files next to config.json (see appConfig.py)."""
        self.scriptDir = scriptDir

    def container(self):
        """This panel's prompt_toolkit Container; app.py sizes it,
        panels don't manage their own width."""
        raise NotImplementedError

    def tick(self):
        """Called roughly once a second to refresh timed content.
        Default: no-op."""
        pass
