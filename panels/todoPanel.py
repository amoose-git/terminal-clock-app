"""
todoPanel is a todo-list Panel: a bordered box with a big-letter
"TODO" header (see panels/bigLetters.py) over the item list, a
solid bar, then this panel's own dedicated input line pinned to
the bottom of the screen (not shared with any other panel) - type
there and press Enter to add an item, click an item to toggle it
done/not-done.
"""
import json
import os

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, UIContent, UIControl
from prompt_toolkit.mouse_events import MouseEventType

import layoutBoxes
from panels import Panel, bigLetters

todosFileName = "todos.json"
placeholderText = "(no todo items yet - type below and press Enter)"


def isClick(mouseEvent):
    """True for a completed left-click (button release)."""
    return mouseEvent.event_type == MouseEventType.MOUSE_UP


class TodoPanel(Panel):
    """A todo list, persisted to todos.json next to config.json."""

    name = "todo"

    def __init__(self, scriptDir):
        super().__init__(scriptDir)
        self.todosPath = os.path.join(scriptDir, todosFileName)
        self.items = self._load()

        self._buffer = Buffer(multiline=False)
        self._buffer.accept_handler = self._onAccept
        self.inputWindow = Window(BufferControl(buffer=self._buffer), height=1,
                                   get_line_prefix=lambda lineno, wrapCount: [("bold", "► ")])

        self._container = HSplit([
            # no dont_extend_height/preferred_height here - this window is meant
            # to stretch and fill whatever's left, pinning the bar + input line
            # to the bottom of the screen (same shape the clock buttons had
            # before that got fixed - here it's the wanted behavior).
            Window(_TodoControl(self)),
            Window(height=1, char=layoutBoxes.unicodeBorderChars["h"]),  # solid bar, full column width
            self.inputWindow,
        ])

    def container(self):
        """Returns the boxed item list stacked over this panel's own input line."""
        return self._container

    def toggleItem(self, index):
        """Flips one item's done state (called by a click - see _TodoControl.mouse_handler)."""
        if 0 <= index < len(self.items):
            self.items[index]["done"] = not self.items[index]["done"]
            self._save()

    def _onAccept(self, buf):
        """Buffer's Enter handler: submits the typed line as a new, not-done item."""
        text = buf.text.strip()
        if text:
            self.items.append({"text": text, "done": False})
            self._save()
        buf.reset()
        return False  # don't keep the text as buffer history - start the next line fresh

    def _load(self):
        """Reads todos.json (starts empty if missing/invalid), upgrading any
        items saved by the old plain-string format to {"text", "done"}."""
        try:
            with open(self.todosPath, "r", encoding="utf-8") as todosFile:
                raw = json.load(todosFile)
        except (OSError, json.JSONDecodeError):
            return []
        return [item if isinstance(item, dict) else {"text": item, "done": False} for item in raw]

    def _save(self):
        """Writes the current item list back out to todos.json."""
        with open(self.todosPath, "w", encoding="utf-8") as todosFile:
            json.dump(self.items, todosFile, indent=4)


class _TodoControl(UIControl):
    """Draws the TODO header + item list in a bordered box, matching the
    clock panel's 2-line top gap so both columns start level with each other."""

    def __init__(self, panel):
        self.panel = panel
        self._rows = []  # last-rendered rows, so mouse_handler can find what was clicked


    """ 
    Creates specifically the box which contains the TODO list: the big box. 
    
    It's re-rendered every interaction/tick/click to see if something has changed. 
    
    It's a panel that list[str] elements are added to, in which builds out the design in 
    this one function, and that is returned in a conglomerated UI item at the end 
    of the function and the library prompt_toolkit can understand.
    """
    def create_content(self, width, height):
        panel = self.panel
        # box is inset 1 char each side, so the full-width bar below (see
        # TodoPanel.__init__) visibly continues 1 char past its left/right edges
        boxWidth = max(width - 2, 1)
        innerWidth = layoutBoxes.innerTextWidth(boxWidth)

        headerRows = bigLetters.renderBigText("TODO")
        headerBoxWidth = min(innerWidth, len(headerRows[0]) + 6)
        headerBox = layoutBoxes.buildBox(headerRows, width=headerBoxWidth, minHeight=0,
                                          verticalPadding=0, horizontalPadding=1,
                                          chars=layoutBoxes.unicodeBorderChars)

        # each item is left-aligned (ljust to the full inner width) rather than
        # centered - buildBox centers content lines by default, but centering
        # an already-full-width string is a no-op, so this defeats that safely.
        itemLines = [f"{'<*>' if item['done'] else '<.>'} {item['text']}".ljust(innerWidth)[:innerWidth]
                     for item in panel.items] or [placeholderText]

        # The divider under the title for the TODO list
        divider = list(headerBox) + [layoutBoxes.unicodeBorderChars["h"] * innerWidth]
        
        contentLines = list(divider) + [""] + itemLines
        minHeight=height - 2 
        box = layoutBoxes.buildBox(contentLines, width=boxWidth, minHeight=minHeight,
                                    verticalPadding=0, align="top",
                                    chars=layoutBoxes.unicodeBorderChars)

        # box[0] is the outer top border; box[1:] map 1:1 to contentLines in
        # order (verticalPadding=0 above keeps that offset exact).
        firstItemRow = 1 + len(divider) + 1
        
        # a list[str]
        rows = [[("", "")], [("", "")]]  # 2-line gap, matching the clock panel
        for i, boxRow in enumerate(box):
            text = " " + boxRow  # 1-char inset each side, see boxWidth above
            itemIndex = i - firstItemRow
            if panel.items and 0 <= itemIndex < len(panel.items):
                toggle = (lambda idx: lambda e: panel.toggleItem(idx) if isClick(e) else None)(itemIndex)
                if panel.items[itemIndex]["done"]:
                    style = "italic fg:#888888"
                else:
                    style=""
                rows.append([(style, text, toggle)])
            else:
                rows.append([("", text)])

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
