import json
import logging
from pathlib import Path
from typing import Any


_logger = logging.getLogger("Config")

CONFIG: dict = {}

DEFAULTS: dict = {
    "client": {
        "bufsize.read": 10240,
        "client.ident": "/FE:WRAYTH /VERSION:1.0.1.28 /P:WIN_UNKNOWN /XML",
        "client.name": "Pivuh",
        "client.version": "0.0.1",
        "input.history_length": 100,
    },
    "game": {
        "eaccess.host": "eaccess.play.net",
        "eaccess.port": 7910,
    },
    "presets": {
        "commands.color": "silver",
        "commands.bgcolor": "dimgray",
        "game.color": "silver",
        "game.bgcolor": "#111111",
        "game.fontname": "Verdana",
        "game.fontsize": "9pt",
        "link.color": "dodgerblue",
        "link.bgcolor": "#111111",
        "minivitals.concentration.color": "white",
        "minivitals.concentration.bgcolor": "darkslategray",
        "minivitals.health.color": "white",
        "minivitals.health.bgcolor": "darkred",
        "minivitals.mana.color": "white",
        "minivitals.mana.bgcolor": "darkblue",
        "minivitals.spirit.color": "white",
        "minivitals.spirit.bgcolor": "purple",
        "minivitals.stamina.color": "white",
        "minivitals.stamina.bgcolor": "darkgreen",
        "monospace.fontname": "Courier New",
        "monospace.fontsize": "9pt",
        "monsterbold.color": "yellow",
        "monsterbold.bgcolor": "#111111",
        "roomdesc.color": "silver",
        "roomdesc.bgcolor": "#111111",
        "roomname.color": "white",
        "roomname.bgcolor": "darkblue",
        "speech.color": "lime",
        "speech.bgcolor": "#111111",
        "thought.color": "darkorange",
        "thought.bgcolor": "#111111",
        "ui.fontname": "Segoe UI",
        "ui.fontsize": "11pt",
        "watching.color": "yellow",
        "watching.bgcolor": "#111111",
        "whisper.color": "cyan",
        "whisper.bgcolor": "#111111",
    },
    "windows": {
        "settings": {
            "assess": {
                "default_open": False,
                "if_closed": "main",
                "timestamp": False,
                "title": "Assess",
            },
            "atmospherics": {
                "default_open": False,
                "if_closed": "main",
                "timestamp": False,
                "title": "Atmospherics",
            },
            "chatter": {
                "default_open": False,
                "if_closed": "main",
                "timestamp": True,
                "title": "Chatter",
            },
            "combat": {
                "default_open": False,
                "if_closed": "main",
                "timestamp": False,
                "title": "Combat",
            },
            "conversation": {
                "default_open": True,
                "if_closed": "none",
                "timestamp": True,
                "title": "Conversation",
            },
            "death": {
                "default_open": True,
                "if_closed": "main",
                "timestamp": True,
                "title": "Deaths",
            },
            "debug": {
                "if_closed": None,
                "timestamp": True,
                "title": "Debug",
            },
            "experience": {
                "default_open": True,
                "if_closed": None,
                "timestamp": False,
                "title": "Experience",
            },
            "familiar": {
                "default_open": True,
                "if_closed": "main",
                "timestamp": False,
                "title": "Familiar",
            },
            "group": {
                "default_open": False,
                "if_closed": None,
                "timestamp": False,
                "title": "Group",
            },
            "inv": {
                "default_open": False,
                "if_closed": None,
                "timestamp": False,
                "title": "Inventory",
            },
            "logons": {
                "default_open": True,
                "if_closed": "main",
                "timestamp": True,
                "title": "Arrivals",
            },
            "main": {
                "if_closed": None,
                "timestamp": False,
                "title": "Story",
            },
            "ooc": {
                "default_open": False,
                "if_closed": "conversation",
                "timestamp": True,
                "title": "OOC",
            },
            "percWindow": {
                "default_open": True,
                "if_closed": None,
                "title": "Spells",
            },
            "raw": {
                "default_open": False,
                "if_closed": None,
                "timestamp": True,
                "title": "Raw",
            },
            "room": {
                "default_open": True,
                "if_closed": None,
                "timestamp": False,
                "title": "Room",
            },
            "stow": {
                "default_open": True,
                "if_closed": None,
                "timestamp": False,
                "title": "Container",
            },
            "talk": {
                "default_open": False,
                "if_closed": "conversation",
                "timestamp": True,
                "title": "Talk",
            },
            "thoughts": {
                "default_open": True,
                "if_closed": "main",
                "timestamp": True,
                "title": "Thoughts",
            },
            "whispers": {
                "default_open": False,
                "if_closed": "conversation",
                "title": "Whispers",
            },
        },
    },
}


def _deep_merge(base: dict, overrides: dict) -> dict:
    """Recursively merge overrides on top of base, returning a new dict."""
    result = dict(base)
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Config:
    def __init__(self, file: str = "config/config.json") -> None:
        self.load(file)

    def load(self, file: str = "config/config.json") -> None:
        """Load configuration from disk, merging with built-in defaults."""
        global CONFIG

        merged = _deep_merge({}, DEFAULTS)

        if Path(file).exists():
            try:
                with open(file, "r") as json_file:
                    user = json.load(json_file)
                merged = _deep_merge(merged, user)
                _logger.debug(f"Config loaded from {file}")
            except (json.JSONDecodeError, OSError) as exc:
                _logger.warning(f"Could not read {file}: {exc}; using defaults")
        else:
            _logger.debug(f"Config file {file} not found; using defaults")

        CONFIG = merged
        self.CONFIG = CONFIG

    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        if section not in CONFIG:
            CONFIG[section] = {}
        return CONFIG[section].get(key, fallback)

    def set(self, section: str, key: str, value: Any) -> None:
        if section not in CONFIG:
            CONFIG[section] = {}
        CONFIG[section][key] = value

    def save(self, file: str = "config/config.json") -> None:
        Path(file).parent.mkdir(parents=True, exist_ok=True)
        with open(file, "w") as json_file:
            json.dump(CONFIG, json_file, indent=2, sort_keys=True)
        _logger.debug(f"Config saved to {file}")
