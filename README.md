# Terminal ASCII Clock

A second-accurate ASCII clock for the terminal, with a flavor-text
box (Scryfall / Bible / ZenQuotes) above it. It's also a small
split-screen launcher: the clock is always on screen (it's also
where the exit/config buttons live), and flags add other panels
(currently just a todo list) alongside it, each with an adjustable
share of the screen.

## Requirements

- Python 3.9+, a terminal at least **91 columns** wide (the boxes
  are centered within whatever width their panel gets, so a wider
  terminal just adds margin).

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
py app.py
```

## Panels

The clock panel is always shown - it's not behind a flag, since it's
also the buttons' home. Flags add other panels alongside it:

```
clock          # clock only (the original behavior)
clock -todo    # clock + todo, split side by side
```

| Flag    | Panel                                                        |
|---------|----------------------------------------------------------------|
| (none)  | Flavor-text box + big-digit clock + exit/config buttons (see Layout below) - always present |
| `-todo` | A todo list in its own bordered box, with its own input line right below it - type there, Enter to add an item. Saved to `todos.json` next to `config.json`. |

Adding another panel later (e.g. `-notes`) means writing one new
`panels/*.py` file (following the contract in `panels/__init__.py`)
and one line in `panels/registry.py` - no changes needed in `app.py`.
A panel that wants its own text input exposes it as `self.inputWindow`
(see `panels/todoPanel.py`); one that doesn't just leaves it unset.

### Controls

- **Tab** / **Shift+Tab**: move focus between panels and any panel's
  own input line.
- **Exit**: click the EXIT button (on the clock panel), press `e`
  (unless a panel's input line is focused - typing "e" into a todo
  item shouldn't quit), or **Ctrl+C** at any time.
- **Config**: click the CONFIG button, or press `c` (same input-line
  exception as above) — opens `config.json` in Notepad. Saving that
  file (Ctrl+S) is what triggers the app to reload it and refresh.

## Layout - the clock panel

```
     +---------------- flavor text box (80 wide, ASCII) ----------------+
                                  (1 line gap)
     ┌════════════ double-walled clock box (80 wide) ═══════════════════┐
     ║  ┌──────────────────────────────────────────────────────────┐   ║
     ║  │                     the big digits live here              │   ║
     ║  └──────────────────────────────────────────────────────────┘   ║
     └════════════════════════════════════════════════════════════════┘
```

Both boxes are centered within the clock panel's own width (its
share of the split screen, or the full terminal when it's the only
panel shown). The clock box is drawn as two nested Unicode-bordered
frames one unit apart (`┌─┐│└┘`); the flavor box keeps its plain
ASCII `+`/`-`/`|` border.

- The flavor box grows downward if the fetched text needs more than its
  base height; the clock box grows if the digit font needs more room
  than its 16-line minimum.

Exit/config buttons are drawn as single-walled Unicode boxes (roof,
label, floor) inside the clock panel itself, below the clock box -
not a shared app-wide footer.

## config.json

```json
{
    "textSource": "scryfall",
    "timezone": "Australia/Sydney",
    "italics": true,
    "panelWeights": {}
}
```

- `textSource`: `"scryfall"` (random card flavor text), `"bible"`
  (random ASV verse from bible-api.com) or `"zenquotes"` (random
  quote from zenquotes.io). Exactly one API call is made per
  launch/refresh, matching whichever source is selected.
- `timezone`: any IANA name (e.g. `"Australia/Sydney"`, `"UTC"`).
  Invalid names fall back to the system's local time.
- `italics`: `true`/`false`. Only affects the clock panel's flavor
  text; degrades automatically if the terminal doesn't support it.
- `panelWeights`: relative split-screen widths, by panel name, e.g.
  `{"todo": 60, "clock": 40}` for a 60/40 split. These are *ratios*,
  not percentages - any panel left out defaults to a weight of 50.
  Edited the same way as the other settings (Notepad + save), and
  applied live without restarting.

Quoted text is padded off its quote marks by one space (`" like this "`).
Scryfall flavor text that already carries its own embedded quote marks
is left as-is rather than double-quoted.

## Modules

| File                        | Responsibility                                         |
|-----------------------------|---------------------------------------------------------|
| `app.py`                    | Entry point: clock (always) + flagged panels, split-screen layout, main loop |
| `panels/__init__.py`        | The `Panel` contract every panel implements             |
| `panels/registry.py`        | Maps `-<flag>` names to their `Panel` classes            |
| `panels/todoPanel.py`       | Todo-list panel: boxed item list + its own input line, persisted to `todos.json` |
| `clock/clockPanel.py`       | Flavor-text box + big-digit clock + exit/config buttons, as a panel |
| `clock/bigDigits.py`        | Custom digit glyphs as spreadsheet-style cell codes      |
| `clock/buttons.py`          | Exit/config button rendering                             |
| `clock/textProviders.py`    | Scryfall / bible-api.com / ZenQuotes fetchers            |
| `layoutBoxes.py`            | Dashed box drawing + text wrapping (shared by every panel) |
| `appConfig.py`              | Loads/saves `config.json`, detects Notepad saves         |
| `pyproject.toml`            | Packaging: makes `clock` installable as a command        |

`clock/` holds everything used *only* by the clock panel (its digit
glyphs, quote fetchers, and now the buttons too, since they moved
into the clock panel). `layoutBoxes.py` and `appConfig.py` stay at
the top level because every panel depends on them, not just clock's.

## Notes / assumptions

- Rendering, input (keyboard + mouse) and layout all go through
  `prompt_toolkit`, which is cross-platform - unlike the previous
  version, this no longer depends on Windows-specific console APIs.
- Function/variable names use camelCase (not the usual PEP 8
  snake_case) as the project's chosen naming convention.
- The clock updates once per second.
