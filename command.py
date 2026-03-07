import html
import logging
import re
import subprocess
from typing import TYPE_CHECKING

import psutil
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QDockWidget

from config import Config
from game import GameState
from layout import LayoutConfig
from utils import traced
from variables import Variables

if TYPE_CHECKING:
    from main import MainWindow


class CommandParser:
    @traced(show_args=False)
    def __init__(self, window: "MainWindow") -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

        self._config = Config()
        self._variables = Variables()
        self._window = window

    @traced(show_args=False)
    def parse(self, command_input: str) -> None:
        command_input = re.sub(r"\s+", " ", command_input.strip())

        tab = "&nbsp;&nbsp;&nbsp;&nbsp;"

        try:
            command, args = command_input.split(" ", 1)
        except ValueError:
            command = command_input
            args = ""

        if command.startswith("#"):
            if command == "#connect":
                usage = f"<br/>Usage:<br/>{tab}<code>{command} [account] [password] [character] [instance] (lich)</code>"
                if self._window.game_client.state == GameState.Connected:
                    self._logger.debug("#connect: already connected")
                    return

                args_list = args.split(" ")
                args_count = len(args_list)

                lich_mode = False

                if args_count == 5:  # noqa: PLR2004
                    account, password, character, instance, lich = args_list
                    if lich == "lich":
                        lich_mode = True
                elif args_count == 4:  # noqa: PLR2004
                    account, password, character, instance = args_list
                else:
                    self._window.main.insertHtml(usage)
                    return

                self._variables.set("protected", "login_key", "")

                self._variables.set("temporary", "account", account)
                self._variables.set("protected", "password", password)
                self._variables.set("temporary", "character", character)
                self._variables.set("temporary", "instance", instance)

                self._variables.set("temporary", "guild", "Commoner")

                self._window.eaccess_client.connect()
                self._window.eaccess_client.authenticate()
                self._window.eaccess_client.wait_for_login_key(3000)

                if lich_mode:
                    self._variables.set("temporary", "game_host", "127.0.0.1")

                    ruby_path = self._config.get("game", "lich.ruby_path")
                    lich_path = self._config.get("game", "lich.lich_path")
                    lich_args = self._config.get("game", "lich.lich_args", "").split(
                        " "
                    )
                    if instance == "DRF":
                        lich_args.append("--fallen")
                    elif instance == "DRT":
                        lich_args.append("--test")
                    elif instance == "DRX":
                        lich_args.append("--platinum")
                    self._logger.debug(
                        "lich connect: ruby_path(%s) lich_path(%s) lich_args(%s)",
                        ruby_path,
                        lich_path,
                        lich_args,
                    )

                    lich_running = False
                    for proc in psutil.process_iter(["pid", "cmdline"]):
                        try:
                            cmdline = proc.info["cmdline"] or []
                            if len(cmdline) > 0 and ruby_path in cmdline:
                                pid = proc.info["pid"] or 0
                                self._logger.debug(
                                    "lich_connect: found running lich instance with pid %d",
                                    pid,
                                )
                                lich_running = True
                        except (psutil.NoSuchProcess, psutil.AccessDenied):  # noqa: PERF203
                            pass

                    if not lich_running:
                        lich_process = subprocess.Popen(  # noqa: S603
                            [ruby_path, lich_path, *lich_args]
                        )
                        self._logger.debug(
                            "launched lich process with pid %d", lich_process.pid
                        )

                    def _connect_after_delay() -> None:
                        self._window.game_client.connect()
                        self._window.game_client.authenticate()

                    lich_delay = self._config.get("game", "lich.lich_delay", 5000)
                    QTimer.singleShot(lich_delay, _connect_after_delay)
                    return

                self._window.game_client.connect()
                self._window.game_client.authenticate()

            elif command == "#config":
                usage = f"<br/>Usage:<br/>{tab}<code>{command} [load|save]</code>"
                args_list = args.split(" ") if args else []
                if len(args_list) != 1 or not args_list[0]:
                    self._window.main.insertHtml(usage)
                    return
                subcommand = args_list[0]
                if subcommand.startswith("l"):
                    self._config.load(force_reload=True)
                    self._window.main.insertHtml("<br/>Config loaded.")
                elif subcommand.startswith("s"):
                    self._config.save()
                    self._window.main.insertHtml("<br/>Config saved.")
                else:
                    self._window.main.insertHtml(usage)

            elif command == "#disconnect":
                self._window.eaccess_client.do_disconnect()
                self._window.game_client.do_disconnect()

            elif command == "#exit":
                self._window.eaccess_client.do_disconnect()
                self._window.game_client.do_disconnect()
                self._window.close()

            elif command in ("#highlight", "#highlights"):
                usage = (
                    f"<br/>Usage:"
                    f"<br/>{tab}<code>{command} list</code>"
                    f"<br/>{tab}<code>{command} add {{[color](, bgcolor)}} {{[pattern]}}</code>"
                    f"<br/>{tab}<code>{command} remove [index]</code>"
                    f"<br/>{tab}<code>{command} clear\n</li></code>"
                )
                args_list = args.split(" ", 1) if args else []
                if not args_list or not args_list[0]:
                    self._window.main.insertHtml(usage)
                    return
                subcommand = args_list[0]
                highlights = list(self._config.get("highlights", "rules", []))

                if subcommand.startswith("l"):
                    if not highlights:
                        self._window.main.insertHtml("<br/>No highlights configured.")
                    else:
                        lines = ["<br/>Highlights:"]
                        for i, h in enumerate(highlights, 1):
                            pattern = html.escape(h.get("pattern", ""))
                            color = h.get("color", "") or "(none)"
                            bgcolor = h.get("bgcolor", "") or "(none)"
                            lines.append(
                                f"<br/>{tab}{i}. color={color} bgcolor={bgcolor} pattern=<code>{pattern}</code>",
                            )
                        self._window.main.insertHtml("".join(lines))

                elif subcommand.startswith("a"):
                    add_usage = (
                        f"<br/>Usage:"
                        f"<br/>{tab}<code>{command} add {{[color](, bgcolor)}} {{[pattern]}}</code>"
                        f"<br/>Examples:"
                        f"<br/>{tab}<code>{command} add {{yellow}} {{field goblin}}</code>"
                        f"<br/>{tab}<code>{command} add {{yellow, #300000}} {{field gobln}}</code>"
                    )
                    add_args = args_list[1].strip() if len(args_list) > 1 else ""
                    m = re.fullmatch(r"\{([^}]+)\}\s+\{([^}]+)\}", add_args)
                    if not m:
                        self._window.main.insertHtml(add_usage)
                        return

                    colors_raw = [c.strip() for c in m.group(1).split(",")]
                    color = colors_raw[0]
                    bgcolor = colors_raw[1] if len(colors_raw) > 1 else ""
                    pattern = m.group(2)
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        self._window.main.insertHtml(
                            f"<br/>Invalid regex pattern: {html.escape(str(e))}",
                        )
                        return

                    if any(h.get("pattern") == pattern for h in highlights):
                        self._window.main.insertHtml(
                            f"<br/>Highlight with pattern <code>{html.escape(pattern)}</code> already exists.",
                        )
                        return

                    highlights.append(
                        {"pattern": pattern, "color": color, "bgcolor": bgcolor},
                    )
                    self._config.set("highlights", "rules", highlights)
                    self._window.main.insertHtml(
                        f"<br/>Highlight #{len(highlights)} added:<br/>{tab}"
                        f"color={color or '(none)'} bgcolor={bgcolor or '(none)'} "
                        f"pattern=<code>{html.escape(pattern)}</code> ",
                    )

                elif subcommand.startswith("r"):
                    remove_usage = (
                        f"<br/>Usage:<br/>{tab}<code>{command} remove [index]</code>"
                    )
                    remove_args = args_list[1].strip() if len(args_list) > 1 else ""
                    if not remove_args:
                        self._window.main.insertHtml(remove_usage)
                        return
                    try:
                        i = int(remove_args) - 1
                    except ValueError:
                        self._window.main.insertHtml(
                            f"<br/>Invalid index: {html.escape(remove_args)}",
                        )
                        return
                    if i < 0 or i >= len(highlights):
                        self._window.main.insertHtml(
                            f"<br/>No highlight at index {i + 1}.",
                        )
                        return
                    removed = highlights.pop(i)
                    self._config.set("highlights", "rules", highlights)
                    self._window.main.insertHtml(
                        f"<br/>Highlight #{i + 1} removed:<br/>{tab}"
                        f"color={html.escape(removed.get('color', '') or '(none)')} "
                        f"bgcolor={html.escape(removed.get('bgcolor', '') or '(none)')} "
                        f"pattern=<code>{html.escape(removed.get('pattern', ''))}</code>",
                    )

                elif subcommand.startswith("c"):
                    self._config.set("highlights", "rules", [])
                    self._window.main.insertHtml("<br/>Highlights cleared.")

                else:
                    self._window.main.insertHtml(usage)

            elif command in ("#gag", "#gags"):
                usage = (
                    f"<br/>Usage:"
                    f"<br/>{tab}<code>{command} list</code>"
                    f"<br/>{tab}<code>{command} add {{[pattern]}}</code>"
                    f"<br/>{tab}<code>{command} remove [index]</code>"
                    f"<br/>{tab}<code>{command} clear</code>"
                )
                args_list = args.split(" ", 1) if args else []
                if not args_list or not args_list[0]:
                    self._window.main.insertHtml(usage)
                    return
                subcommand = args_list[0]
                gags = list(self._config.get("gags", "rules", []))

                if subcommand.startswith("l"):
                    if not gags:
                        self._window.main.insertHtml("<br/>No gags configured.")
                    else:
                        lines = ["<br/>Gags:"]
                        for i, g in enumerate(gags, 1):
                            pattern = html.escape(g.get("pattern", ""))
                            lines.append(
                                f"<br/>{tab}{i}. pattern=<code>{pattern}</code>",
                            )
                        self._window.main.insertHtml("".join(lines))

                elif subcommand.startswith("a"):
                    add_usage = (
                        f"<br/>Usage:"
                        f"<br/>{tab}<code>{command} add {{[pattern]}}</code>"
                        f"<br/>Examples:"
                        f"<br/>{tab}<code>{command} add {{you see a .*? goblin}}</code>"
                    )
                    add_args = args_list[1].strip() if len(args_list) > 1 else ""
                    m = re.fullmatch(r"\{([^}]+)\}", add_args)
                    if not m:
                        self._window.main.insertHtml(add_usage)
                        return

                    pattern = m.group(1)
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        self._window.main.insertHtml(
                            f"<br/>Invalid regex pattern: {html.escape(str(e))}",
                        )
                        return

                    if any(g.get("pattern") == pattern for g in gags):
                        self._window.main.insertHtml(
                            f"<br/>Gag with pattern <code>{html.escape(pattern)}</code> already exists.",
                        )
                        return

                    gags.append({"pattern": pattern})
                    self._config.set("gags", "rules", gags)
                    self._window.main.insertHtml(
                        f"<br/>Gag #{len(gags)} added:<br/>{tab}"
                        f"pattern=<code>{html.escape(pattern)}</code> ",
                    )

                elif subcommand.startswith("r"):
                    remove_usage = (
                        f"<br/>Usage:<br/>{tab}<code>{command} remove [index]</code>"
                    )
                    remove_args = args_list[1].strip() if len(args_list) > 1 else ""
                    if not remove_args:
                        self._window.main.insertHtml(remove_usage)
                        return
                    try:
                        i = int(remove_args) - 1
                    except ValueError:
                        self._window.main.insertHtml(
                            f"<br/>Invalid index: {html.escape(remove_args)}",
                        )
                        return
                    if i < 0 or i >= len(gags):
                        self._window.main.insertHtml(
                            f"<br/>No gag at index {i + 1}.",
                        )
                        return
                    removed = gags.pop(i)
                    self._config.set("gags", "rules", gags)
                    self._window.main.insertHtml(
                        f"<br/>Gag #{i + 1} removed:<br/>{tab}"
                        f"pattern=<code>{html.escape(removed.get('pattern', ''))}</code>",
                    )

                elif subcommand.startswith("c"):
                    self._config.set("gags", "rules", [])
                    self._window.main.insertHtml("<br/>Gags cleared.")

                else:
                    self._window.main.insertHtml(usage)

            elif command in ("#sub", "#subs"):
                usage = (
                    f"<br/>Usage:"
                    f"<br/>{tab}<code>{command} list</code>"
                    f"<br/>{tab}<code>{command} add {{[pattern]}} {{[replacement]}}</code>"
                    f"<br/>{tab}<code>{command} remove [index]</code>"
                    f"<br/>{tab}<code>{command} clear</code>"
                )
                args_list = args.split(" ", 1) if args else []
                if not args_list or not args_list[0]:
                    self._window.main.insertHtml(usage)
                    return
                subcommand = args_list[0]
                subs = list(self._config.get("subs", "rules", []))

                if subcommand.startswith("l"):
                    if not subs:
                        self._window.main.insertHtml("<br/>No subs configured.")
                    else:
                        lines = ["<br/>Subs:"]
                        for i, s in enumerate(subs, 1):
                            pattern = html.escape(s.get("pattern", ""))
                            replacement = html.escape(s.get("replacement", ""))
                            lines.append(
                                f"<br/>{tab}{i}. pattern=<code>{pattern}</code>"
                                f" replacement=<code>{replacement}</code>",
                            )
                        self._window.main.insertHtml("".join(lines))

                elif subcommand.startswith("a"):
                    add_usage = (
                        f"<br/>Usage:"
                        f"<br/>{tab}<code>{command} add {{[pattern]}} {{[replacement]}}</code>"
                        f"<br/>Examples:"
                        f"<br/>{tab}<code>{command} add {{attacks you}} {{ATTACKS YOU}}</code>"
                    )
                    add_args = args_list[1].strip() if len(args_list) > 1 else ""
                    m = re.fullmatch(r"\{([^}]+)\}\s+\{([^}]*)\}", add_args)
                    if not m:
                        self._window.main.insertHtml(add_usage)
                        return

                    pattern = m.group(1)
                    replacement = m.group(2)
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        self._window.main.insertHtml(
                            f"<br/>Invalid regex pattern: {html.escape(str(e))}",
                        )
                        return

                    if any(s.get("pattern") == pattern for s in subs):
                        self._window.main.insertHtml(
                            f"<br/>Sub with pattern <code>{html.escape(pattern)}</code> already exists.",
                        )
                        return

                    subs.append({"pattern": pattern, "replacement": replacement})
                    self._config.set("subs", "rules", subs)
                    self._window.main.insertHtml(
                        f"<br/>Sub #{len(subs)} added:<br/>{tab}"
                        f"pattern=<code>{html.escape(pattern)}</code>"
                        f" replacement=<code>{html.escape(replacement)}</code> ",
                    )

                elif subcommand.startswith("r"):
                    remove_usage = (
                        f"<br/>Usage:<br/>{tab}<code>{command} remove [index]</code>"
                    )
                    remove_args = args_list[1].strip() if len(args_list) > 1 else ""
                    if not remove_args:
                        self._window.main.insertHtml(remove_usage)
                        return
                    try:
                        i = int(remove_args) - 1
                    except ValueError:
                        self._window.main.insertHtml(
                            f"<br/>Invalid index: {html.escape(remove_args)}",
                        )
                        return
                    if i < 0 or i >= len(subs):
                        self._window.main.insertHtml(
                            f"<br/>No sub at index {i + 1}.",
                        )
                        return
                    removed = subs.pop(i)
                    self._config.set("subs", "rules", subs)
                    self._window.main.insertHtml(
                        f"<br/>Sub #{i + 1} removed:<br/>{tab}"
                        f"pattern=<code>{html.escape(removed.get('pattern', ''))}</code>"
                        f" replacement=<code>{html.escape(removed.get('replacement', ''))}</code>",
                    )

                elif subcommand.startswith("c"):
                    self._config.set("subs", "rules", [])
                    self._window.main.insertHtml("<br/>Subs cleared.")

                else:
                    self._window.main.insertHtml(usage)

            elif command == "#layout":
                usage = f"<br/>Usage:<br/>{tab}<code>{command} [load|save]</code>"
                args_list = args.split(" ")
                if len(args_list) != 1:
                    self._window.main.insertHtml(usage)
                    return
                subcommand = args_list[0]
                if subcommand.startswith("l"):
                    layout = LayoutConfig()
                    geometry, state = layout.load()
                    if geometry:
                        self._window.restoreGeometry(geometry)
                    if state:
                        self._window.restoreState(state)
                    self._window.main.insertHtml("<br/>Layout loaded.")
                elif subcommand.startswith("s"):
                    geometry = self._window.saveGeometry().data()
                    state = self._window.saveState().data()
                    LayoutConfig().save(geometry, state)
                    self._window.main.insertHtml("<br/>Layout saved.")
                else:
                    self._window.main.insertHtml(usage)

            elif command in ("#toolbar", "#toolbars"):
                usage = f"<br/>Usage:<br/>{tab}<code>{command} [lock|unlock]</code>"
                args_list = args.split(" ")
                if len(args_list) != 1:
                    self._window.main.insertHtml(usage)
                    return
                subcommand = args_list[0]
                if subcommand.startswith("l"):
                    self._window.unlock_toolbars(False)
                    self._window.main.insertHtml("<br/>Toolbars locked.")
                elif subcommand.startswith("u"):
                    self._window.unlock_toolbars(True)
                    self._window.main.insertHtml("<br/>Toolbars unlocked.")
                else:
                    self._window.main.insertHtml(usage)

            elif command == "#variables":
                usage = f"<br/>Usage:<br/>{tab}<code>{command} [load|save]</code>"
                args_list = args.split(" ") if args else []
                if len(args_list) != 1 or not args_list[0]:
                    self._window.main.insertHtml(usage)
                    return
                subcommand = args_list[0]
                if subcommand.startswith("l"):
                    self._variables.load()
                    self._window.main.insertHtml("<br/>Variables loaded.")
                elif subcommand.startswith("s"):
                    self._variables.save()
                    self._window.main.insertHtml("<br/>Variables saved.")
                else:
                    self._window.main.insertHtml(usage)

            elif command == "#window":
                usage = f"<br/>Usage:<br/>{tab}<code>{command} [list|show|hide] (name)</code>"
                args_list = args.split(" ") if args else []
                if len(args_list) < 1:
                    self._window.main.insertHtml(usage)
                    return

                subcommand = args_list[0]
                if not subcommand.startswith("l") and len(args_list) != 2:  # noqa: PLR2004
                    self._window.main.insertHtml(usage)
                    return

                windows_list = [
                    w for w in self._variables.items("widgets") if w != "main"
                ]
                if subcommand.startswith("l"):
                    self._window.main.insertHtml(
                        f"<br/>Available windows: {', '.join(windows_list)}",
                    )
                    return

                window_name = args_list[1]
                if window_name == "main":
                    self._window.main.insertHtml(
                        f"<br/>Window {window_name} cannot be shown/hidden.",
                    )
                    return

                window = self._variables.get("widgets", window_name, None)
                if not window:
                    self._window.main.insertHtml(
                        f"<br/>Window {window_name} not found: {', '.join(windows_list)}",
                    )
                    return

                if not isinstance(window, QDockWidget):
                    window = window.parentWidget() or window

                if subcommand.startswith("s"):
                    window.show()
                elif subcommand.startswith("h"):
                    window.hide()
                else:
                    self._window.main.insertHtml(usage)

            else:
                self._window.main.insertHtml(f"<br/>Unknown command: {command_input}")

        else:
            self._variables.set("temporary", "lastcommand", command_input)
            if self._window.game_client.state != GameState.Connected:
                self._window.main.insertHtml(f"<br/>({command_input})")
            else:
                color = self._config.get("presets", "commands.color", "")
                bgcolor = self._config.get("presets", "commands.bgcolor", "")

                self._window.main.insertHtml(
                    f"""<span style="color: {color}; background-color: {bgcolor};">{command_input}</span>""",
                )
                self._window.game_client.send(command_input)
