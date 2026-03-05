import html
import importlib
import logging
import re

from PyQt6.QtWidgets import QDockWidget

from config import Config
from layout import LayoutConfig
from variables import Variables


class CommandParser:
    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

        self._config = Config()
        self._variables = Variables()

        self._window = self._variables.get("widgets", "main_window", None)

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
                usage = f"<br/>Usage:<br/>{tab}<code>{command} [account] [password] [character] [instance]</code>"
                if self._window.game_client.state.name == "Connected":
                    self._logger.debug("#connect: already connected")
                    return

                args_list = args.split(" ")
                if len(args_list) != 4:
                    self._window.main.insertHtml(usage)
                    return

                self._variables.set("protected", "login_key", "")

                account, password, character, instance = args_list
                self._variables.set("temporary", "account", account)
                self._variables.set("protected", "password", password)
                self._variables.set("temporary", "character", character)
                self._variables.set("temporary", "instance", instance)

                self._window.eaccess_client.connect()
                self._window.eaccess_client.authenticate()
                self._window.eaccess_client.wait_for_login_key(3000)

                self._variables.set("temporary", "guild", "Commoner")

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

            elif command == "#highlight" or command == "#highlights":
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

                    highlights.append({"pattern": pattern, "color": color, "bgcolor": bgcolor})
                    self._config.set("highlights", "rules", highlights)
                    self._window.main.insertHtml(
                        f"<br/>Highlight #{len(highlights)} added:<br/>{tab}"
                        f"color={color or '(none)'} bgcolor={bgcolor or '(none)'} "
                        f"pattern=<code>{html.escape(pattern)}</code> ",
                    )

                elif subcommand.startswith("r"):
                    remove_usage = (
                        f"<br/>Usage:"
                        f"<br/>{tab}<code>{command} remove [index]</code>"
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
                    geometry = self._window.saveGeometry()
                    self._window.main.insertHtml("<br/>Layout saved.")
                    self._logger.debug(f"MainWindow geometry: {geometry}")

                    state = self._window.saveState()
                    self._logger.debug(f"MainWindow state: {state}")

                    LayoutConfig().save(geometry, state)
                else:
                    self._window.main.insertHtml(usage)

            elif command == "#reload":
                usage = f"<br/>Usage:<br/>{tab}<code>{command} [command|game]</code>"
                args_list = args.split(" ") if args else []
                if len(args_list) != 1 or not args_list[0]:
                    self._window.main.insertHtml(usage)
                    return
                subcommand = args_list[0]
                if subcommand.startswith("c"):
                    import command as _command_module

                    importlib.reload(_command_module)
                    self._window.command = _command_module.CommandParser()
                    self._window.main.insertHtml("<br/>Command parser reloaded.")
                elif subcommand.startswith("g"):
                    import game as _game_module

                    old_parser = self._window.game_parser
                    old_parser.clear_window.disconnect(
                        self._window._on_clear_window,
                    )
                    old_parser.update_casttime.disconnect(
                        self._window._on_update_casttime,
                    )
                    old_parser.update_compass.disconnect(
                        self._window._on_update_compass,
                    )
                    old_parser.update_indicators.disconnect(
                        self._window._on_update_indicators,
                    )
                    old_parser.update_minivitals.disconnect(
                        self._window._on_update_minivitals,
                    )
                    old_parser.update_roundtime.disconnect(
                        self._window._on_update_roundtime,
                    )
                    old_parser.update_window.disconnect(
                        self._window._on_update_window,
                    )

                    importlib.reload(_game_module)
                    self._window.game_parser = _game_module.GameParser()
                    self._window.game_parser.clear_window.connect(
                        self._window._on_clear_window,
                    )
                    self._window.game_parser.update_casttime.connect(
                        self._window._on_update_casttime,
                    )
                    self._window.game_parser.update_compass.connect(
                        self._window._on_update_compass,
                    )
                    self._window.game_parser.update_indicators.connect(
                        self._window._on_update_indicators,
                    )
                    self._window.game_parser.update_minivitals.connect(
                        self._window._on_update_minivitals,
                    )
                    self._window.game_parser.update_roundtime.connect(
                        self._window._on_update_roundtime,
                    )
                    self._window.game_parser.update_window.connect(
                        self._window._on_update_window,
                    )
                    self._window.main.insertHtml("<br/>Game parser reloaded.")
                else:
                    self._window.main.insertHtml(usage)

            elif command == "#toolbar" or command == "#toolbars":
                usage = f"<br/>Usage:<br/>{tab}<code>{command} [lock|unlock]</code>"
                args_list = args.split(" ")
                if len(args_list) != 1:
                    self._window.main.insertHtml(usage)
                    return
                subcommand = args_list[0]
                if subcommand.startswith("l"):
                    self._window._on_unlock_toolbars(False)
                    self._window.main.insertHtml("<br/>Toolbars locked.")
                elif subcommand.startswith("u"):
                    self._window._on_unlock_toolbars(True)
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
                if not subcommand.startswith("l") and len(args_list) != 2:
                    self._window.main.insertHtml(usage)
                    return

                windows_list = [
                    w
                    for w in self._variables.items("widgets")
                    if w != "main_window" and w != "main"
                ]
                if subcommand.startswith("l"):
                    self._window.main.insertHtml(
                        f"<br/>Available windows: {', '.join(windows_list)}",
                    )
                    return

                window_name = args_list[1]
                if window_name == "main_window" or window_name == "main":
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
            if self._window.game_client.state.name != "Connected":
                self._window.main.insertHtml(f"<br/>({command_input})")
            else:
                color = self._config.get("presets", "commands.color", "")
                bgcolor = self._config.get("presets", "commands.bgcolor", "")

                self._window.main.insertHtml(
                    f"""<span style="color: {color}; background-color: {bgcolor};">{command_input}</span>""",
                )
                self._window.game_client.send(command_input)
