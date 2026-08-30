"""
appConfig loads/saves config.json and detects when the user
has saved a fresh copy in Notepad (by watching its mtime).
"""
import json
import os

defaultConfig = {
    "textSource": "scryfall",
    "timezone": "Australia/Sydney",
    "italics": True,
}

validSources = ("scryfall", "bible", "zenquotes")


def loadConfig(configPath):
    """Reads config.json, creating it with defaults if missing."""
    if not os.path.exists(configPath):
        saveConfig(configPath, defaultConfig)
        return dict(defaultConfig)

    try:
        with open(configPath, "r", encoding="utf-8") as configFile:
            userConfig = json.load(configFile)
    except (json.JSONDecodeError, OSError):
        # a mid-edit save can briefly be invalid JSON;
        # fall back to defaults rather than crash the app
        return dict(defaultConfig)

    merged = dict(defaultConfig)
    merged.update(userConfig)
    if merged["textSource"] not in validSources:
        merged["textSource"] = defaultConfig["textSource"]
    return merged


def saveConfig(configPath, configData):
    """Writes config.json back out, pretty-printed for editing."""
    with open(configPath, "w", encoding="utf-8") as configFile:
        json.dump(configData, configFile, indent=4)
        configFile.write("\n")


def getConfigMTime(configPath):
    """Returns the file's last-modified time, or None if missing."""
    try:
        return os.path.getmtime(configPath)
    except OSError:
        return None
