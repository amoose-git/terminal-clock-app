"""
registry maps CLI flag names to their Panel classes - the single
place a new panel gets wired in. app.py builds its -<name> flags
straight from these keys, so adding a panel (e.g. "notes") is one
new file (following panels/__init__.py's Panel contract) plus one
line here - no changes needed in app.py itself.
"""
from clock.clockPanel import ClockPanel
from panels.todoPanel import TodoPanel

panelClasses = {
    "clock": ClockPanel,
    "todo": TodoPanel,
}
