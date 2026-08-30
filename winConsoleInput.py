"""
winConsoleInput reads mouse clicks and key presses straight
from the Windows console input buffer via ctypes, so both
input types come from one place and never fight each other.
"""
import ctypes
from ctypes import wintypes

kernel32 = ctypes.windll.kernel32

stdInputHandle = -10
enableExtendedFlags = 0x0080
enableMouseInput = 0x0010
enableQuickEditMode = 0x0040

keyEventType = 0x0001
mouseEventType = 0x0002
leftMouseButton = 0x0001


class Coord(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]


class KeyEventRecord(ctypes.Structure):
    _fields_ = [
        ("bKeyDown", wintypes.BOOL),
        ("wRepeatCount", wintypes.WORD),
        ("wVirtualKeyCode", wintypes.WORD),
        ("wVirtualScanCode", wintypes.WORD),
        ("uChar", wintypes.WCHAR),
        ("dwControlKeyState", wintypes.DWORD),
    ]


class MouseEventRecord(ctypes.Structure):
    _fields_ = [
        ("dwMousePosition", Coord),
        ("dwButtonState", wintypes.DWORD),
        ("dwControlKeyState", wintypes.DWORD),
        ("dwEventFlags", wintypes.DWORD),
    ]


class WindowBufferSizeRecord(ctypes.Structure):
    _fields_ = [("dwSize", Coord)]


class MenuEventRecord(ctypes.Structure):
    _fields_ = [("dwCommandId", wintypes.UINT)]


class FocusEventRecord(ctypes.Structure):
    _fields_ = [("bSetFocus", wintypes.BOOL)]


class InputEventUnion(ctypes.Union):
    _fields_ = [
        ("KeyEvent", KeyEventRecord),
        ("MouseEvent", MouseEventRecord),
        ("WindowBufferSizeEvent", WindowBufferSizeRecord),
        ("MenuEvent", MenuEventRecord),
        ("FocusEvent", FocusEventRecord),
    ]


class InputRecord(ctypes.Structure):
    _fields_ = [("EventType", wintypes.WORD), ("Event", InputEventUnion)]


def enableRawMouseMode():
    """Switches the console into raw mouse-reporting mode.

    Returns the handle + original mode so it can be restored later.
    """
    handle = kernel32.GetStdHandle(stdInputHandle)
    originalMode = wintypes.DWORD()
    kernel32.GetConsoleMode(handle, ctypes.byref(originalMode))

    newMode = originalMode.value | enableExtendedFlags | enableMouseInput
    newMode &= ~enableQuickEditMode
    kernel32.SetConsoleMode(handle, newMode)
    return handle, originalMode.value


def restoreConsoleMode(handle, originalMode):
    """Puts the console's input mode back the way it was found."""
    kernel32.SetConsoleMode(handle, originalMode)


def pollInputEvent(handle):
    """Non-blocking check for a left-click or a plain key press.

    Returns ('click', (x, y)), ('key', char) or None.
    """
    pendingCount = wintypes.DWORD()
    kernel32.GetNumberOfConsoleInputEvents(handle, ctypes.byref(pendingCount))
    if pendingCount.value == 0:
        return None

    records = (InputRecord * pendingCount.value)()
    readCount = wintypes.DWORD()
    kernel32.ReadConsoleInputW(handle, records, pendingCount.value,
                                ctypes.byref(readCount))

    result = None
    for index in range(readCount.value):
        record = records[index]
        if record.EventType == mouseEventType:
            mouse = record.Event.MouseEvent
            isLeftPress = mouse.dwButtonState & leftMouseButton
            isPlainClick = mouse.dwEventFlags == 0
            if isLeftPress and isPlainClick:
                position = (mouse.dwMousePosition.X, mouse.dwMousePosition.Y)
                result = ("click", position)
        elif record.EventType == keyEventType:
            key = record.Event.KeyEvent
            if key.bKeyDown and key.uChar:
                result = ("key", key.uChar)
    return result
