# Terminal ASCII Clock

A second-accurate ASCII clock for the Windows terminal, with a
flavor-text box (Scryfall / Bible / ZenQuotes) above it and
mouse-or-keyboard exit/config buttons below.

## Requirements

- Windows, Python 3.9+, a terminal at least **80 columns** wide
  (the boxes are centered, so a wider terminal just adds margin).

## Run

**Option A — global `clock` command (recommended):** install it once as
an editable package, so `clock.exe` is placed on your Python Scripts
folder:

```
py -m pip install -e .
```

Make sure that Scripts folder is on your PATH (a one-time setup; open a
**new** terminal window afterward for PATH changes to take effect), then
run it from anywhere with just:

```
clock
```

**Option B — no install:** run it directly from this folder instead:

```
py -m pip install -r requirements.txt
py clock.py
```

## Layout

```
     +---------------- flavor text box (80 wide, ASCII) ----------------+
                                  (1 line gap)
     ┌════════════ double-walled clock box (80 wide) ═══════════════════┐
     ║  ┌──────────────────────────────────────────────────────────┐   ║
     ║  │                     the big digits live here              │   ║
     ║  └──────────────────────────────────────────────────────────┘   ║
     └════════════════════════════════════════════════════════════════┘
                                (3 line gap)
       [EXIT]                                                [CONFIG]
```

Both boxes are centered in the terminal. The clock box is drawn as two
nested Unicode-bordered frames one unit apart (`┌─┐│└┘`); the flavor box
keeps its plain ASCII `+`/`-`/`|` border. Buttons are single-walled
Unicode boxes (roof, label, floor) 8 columns in from the clock box's own
left/right edges, 3 blank lines below it.

- The flavor box grows downward if the fetched text needs more than its
  base height; the clock box grows if the digit font needs more room
  than its 16-line minimum.

## Controls

- **Exit**: click the EXIT button, or press `e`.
- **Config**: click the CONFIG button, or press `c` — opens
  `config.json` in Notepad. Saving that file (Ctrl+S) is what
  triggers the app to reload it and refresh.

## config.json

```json
{
    "textSource": "scryfall",
    "timezone": "Australia/Sydney",
    "italics": true
}
```

- `textSource`: `"scryfall"` (random card flavor text), `"bible"`
  (random ASV verse from bible-api.com) or `"zenquotes"` (random
  quote from zenquotes.io). Exactly one API call is made per
  launch/refresh, matching whichever source is selected.
- `timezone`: any IANA name (e.g. `"Australia/Sydney"`, `"UTC"`).
  Invalid names fall back to the system's local time.
- `italics`: `true`/`false`. Italics only render if the terminal
  actually supports them (checked via `blessed`); otherwise the
  text prints plain automatically.

Quoted text is padded off its quote marks by one space (`" like this "`).
Scryfall flavor text that already carries its own embedded quote marks
is left as-is rather than double-quoted.

## Modules

| File                | Responsibility                                   |
|---------------------|---------------------------------------------------|
| `clock.py`          | Entry point, main loop, ties everything together   |
| `bigDigits.py`      | Custom digit glyphs as spreadsheet-style cell codes |
| `layoutBoxes.py`    | Dashed box drawing + text wrapping                 |
| `buttons.py`        | Button geometry + click hit-testing                |
| `appConfig.py`      | Loads/saves `config.json`, detects Notepad saves   |
| `textProviders.py`  | Scryfall / bible-api.com / ZenQuotes fetchers      |
| `winConsoleInput.py`| Raw Windows console mouse + key reading (ctypes)   |
| `pyproject.toml`    | Packaging: makes `clock` installable as a command  |

## Notes / assumptions

- Mouse clicks are read via the native Windows console API
  (`ReadConsoleInputW`), since this app targets a Windows
  terminal specifically — this is why it won't run as-is on
  macOS/Linux.
- Function/variable names use camelCase (not the usual PEP 8
  snake_case) as the project's chosen naming convention.
- The clock updates once per second.
