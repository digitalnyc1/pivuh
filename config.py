import json
from pathlib import Path
from typing import Any


CONFIG = {}


class Config:
    def __init__(self, file: str = "config/config.json") -> None:
        global CONFIG

        self.CONFIG = CONFIG

        if Path(file).exists():
            with open(file, "r") as json_file:
                CONFIG = json.load(json_file)
            return

        sections = CONFIG.keys()

        if "client" not in sections:
            CONFIG["client"] = {
                "bufsize.read": 10240,
                "geometry": b"\x01\xd9\xd0\xcb\x00\x03\x00\x00\x00\x00\x02\x80\x00\x00\x00\xf5\x00\x00\x07\x7f\x00\x00\x03\xe3\x00\x00\x02\x80\x00\x00\x01\x14\x00\x00\x07\x7f\x00\x00\x03\xe3\x00\x00\x00\x00\x00\x00\x00\x00\x07\x80\x00\x00\x02\x80\x00\x00\x01\x14\x00\x00\x07\x7f\x00\x00\x03\xe3",
                "ident": b"/FE:WRAYTH /VERSION:1.0.1.28 /P:WIN_UNKNOWN /XML",
                "input.history_length": 100,
                "name": "Pivuh",
                "state": b'\x00\x00\x00\xff\x00\x00\x00\x00\xfd\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x01\x06\x00\x00\x03\x0c\xfc\x02\x00\x00\x00\x03\xfb\x00\x00\x00\x0c\x00l\x00o\x00g\x00o\x00n\x00s\x01\x00\x00\x00@\x00\x00\x00\xf5\x00\x00\x00b\x01\x00\x00\x05\xfb\x00\x00\x00\n\x00d\x00e\x00a\x00t\x00h\x01\x00\x00\x01;\x00\x00\x01%\x00\x00\x00b\x01\x00\x00\x05\xfb\x00\x00\x00\x10\x00t\x00h\x00o\x00u\x00g\x00h\x00t\x00s\x01\x00\x00\x02f\x00\x00\x00\xe6\x00\x00\x00b\x01\x00\x00\x05\x00\x00\x00\x01\x00\x00\x01\x06\x00\x00\x03\x0c\xfc\x02\x00\x00\x00\x11\xfb\x00\x00\x00\x06\x00R\x00a\x00w\x02\x00\x00\x0f\x1d\x00\x00\x01-\x00\x00\x01\x06\x00\x00\x00\xc1\xfb\x00\x00\x00\n\x00D\x00e\x00b\x00u\x00g\x01\x00\x00\x00@\x00\x00\x00\xdc\x00\x00\x00\x00\x00\x00\x00\x00\xfb\x00\x00\x00\x0c\x00a\x00s\x00s\x00e\x00s\x00s\x00\x00\x00\x00@\x00\x00\x00\x96\x00\x00\x00b\x01\x00\x00\x05\xfb\x00\x00\x00\x18\x00a\x00t\x00m\x00o\x00s\x00p\x00h\x00e\x00r\x00i\x00c\x00s\x00\x00\x00\x00@\x00\x00\x00\xa5\x00\x00\x00b\x01\x00\x00\x05\xfc\x00\x00\x00@\x00\x00\x00\xb8\x00\x00\x00b\x00\xff\xff\xff\xfa\x00\x00\x00\x01\x01\x00\x00\x00\x02\xfb\x00\x00\x00\x0e\x00c\x00h\x00a\x00t\x00t\x00e\x00r\x02\x00\x00\x03+\x00\x00\x02N\x00\x00\x01\x06\x00\x00\x00\x8f\xfb\x00\x00\x00\x08\x00r\x00o\x00o\x00m\x01\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00L\x01\x00\x00\x05\xfb\x00\x00\x00\x10\x00f\x00a\x00m\x00i\x00l\x00i\x00a\x00r\x01\x00\x00\x00\xfe\x00\x00\x00\xc4\x00\x00\x00b\x01\x00\x00\x05\xfb\x00\x00\x00\x18\x00c\x00o\x00n\x00v\x00e\x00r\x00s\x00a\x00t\x00i\x00o\x00n\x01\x00\x00\x01\xc8\x00\x00\x00\xbf\x00\x00\x00b\x01\x00\x00\x05\xfb\x00\x00\x00\x0c\x00c\x00o\x00m\x00b\x00a\x00t\x00\x00\x00\x01x\x00\x00\x00b\x00\x00\x00b\x01\x00\x00\x05\xfb\x00\x00\x00\n\x00d\x00e\x00b\x00u\x00g\x00\x00\x00\x02\x7f\x00\x00\x00\x8a\x00\x00\x00b\x01\x00\x00\x05\xfb\x00\x00\x00\x14\x00e\x00x\x00p\x00e\x00r\x00i\x00e\x00n\x00c\x00e\x00\x00\x00\x02\xdc\x00\x00\x00\x80\x00\x00\x00b\x01\x00\x00\x05\xfb\x00\x00\x00\n\x00g\x00r\x00o\x00u\x00p\x00\x00\x00\x03\xaa\x00\x00\x00u\x00\x00\x00b\x01\x00\x00\x05\xfb\x00\x00\x00\x06\x00i\x00n\x00v\x02\x00\x00\x059\x00\x00\x03\x83\x00\x00\x01\x06\x00\x00\x00b\xfb\x00\x00\x00\x06\x00o\x00o\x00c\x00\x00\x00\x03+\x00\x00\x00\xb5\x00\x00\x00b\x01\x00\x00\x05\xfb\x00\x00\x00\x14\x00p\x00e\x00r\x00c\x00W\x00i\x00n\x00d\x00o\x00w\x01\x00\x00\x02\x8d\x00\x00\x00\xbf\x00\x00\x00b\x01\x00\x00\x05\xfb\x00\x00\x00\x06\x00r\x00a\x00w\x02\x00\x00\x04\xa8\x00\x00\x02\x89\x00\x00\x01\x06\x00\x00\x00\xc8\xfb\x00\x00\x00\x08\x00t\x00a\x00l\x00k\x00\x00\x00\x03\x07\x00\x00\x00\x89\x00\x00\x00b\x01\x00\x00\x05\xfb\x00\x00\x00\x10\x00w\x00h\x00i\x00s\x00p\x00e\x00r\x00s\x00\x00\x00\x03i\x00\x00\x00\'\x00\x00\x00b\x01\x00\x00\x05\x00\x00\x05\\\x00\x00\x03\x0c\x00\x00\x00\x04\x00\x00\x00\x04\x00\x00\x00\x08\x00\x00\x00\x08\xfc\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x1a\x00S\x00c\x00r\x00i\x00p\x00t\x00T\x00o\x00o\x00l\x00B\x00a\x00r\x01\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00"\x00M\x00i\x00n\x00i\x00V\x00i\x00t\x00a\x00l\x00s\x00T\x00o\x00o\x00l\x00B\x00a\x00r\x01\x00\x00\x00\x00\x00\x00\x04\xa9\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x03\x00\x00\x00\x1c\x00C\x00o\x00m\x00p\x00a\x00s\x00s\x00T\x00o\x00o\x00l\x00B\x00a\x00r\x01\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"\x00I\x00n\x00d\x00i\x00c\x00a\x00t\x00o\x00r\x00s\x00T\x00o\x00o\x00l\x00B\x00a\x00r\x01\x00\x00\x00R\x00\x00\x03/\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18\x00H\x00a\x00n\x00d\x00s\x00T\x00o\x00o\x00l\x00B\x00a\x00r\x01\x00\x00\x03\x81\x00\x00\x03\xea\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x18\x00I\x00n\x00p\x00u\x00t\x00T\x00o\x00o\x00l\x00B\x00a\x00r\x01\x00\x00\x00\x00\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00',
                "version": "0.0.1",
            }

        if "game" not in sections:
            CONFIG["game"] = {
                "eaccess.host": "eaccess.play.net",
                "eaccess.port": 7910,
            }

        if "presets" not in sections:
            CONFIG["presets"] = {
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
            }

        if "temporary" not in sections:
            CONFIG["temporary"] = {
                "gametime": 0,
            }

        if "variables" not in sections:
            CONFIG["variables"] = {}

        if "windows" not in sections:
            CONFIG["windows"] = {
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
                        "default_open": False,
                        "if_closed": "main",
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
                        "default_open": False,
                        "if_closed": None,
                        "timestamp": False,
                        "title": "Experience",
                    },
                    "familiar": {
                        "default_open": False,
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
                        "default_open": False,
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
            }

    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        if section not in CONFIG.keys():
            CONFIG[section] = {}
        return CONFIG[section].get(key, fallback)

    def set(self, section: str, key: str, value: Any) -> None:
        if section not in CONFIG.keys():
            CONFIG[section] = {}
        CONFIG[section][key] = value

    def save(self, file: str = "config/config.json") -> None:
        Path(file).parent.mkdir(parents=True, exist_ok=True)
        with open(file, "w") as json_file:
            json.dump(CONFIG, json_file, sort_keys=True)
