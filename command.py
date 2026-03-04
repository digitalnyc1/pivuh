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

    def parse(self, input: str) -> None:
        input = re.sub(r"\s+", " ", input.strip())

        try:
            command, args = input.split(" ", 1)
        except ValueError:
            command = input
            args = ""

        if command.startswith("#"):
            if command == "#connect":
                if self._window.game_client.state.name == "Connected":
                    self._logger.debug("#connect: already connected")
                    return

                args_list = args.split(" ")
                if len(args_list) != 4:
                    self._window.main.insertHtml(
                        "<br/>Usage: #connect [account] [password] [character] [instance]",
                    )
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
                usage = f"<br/>Usage: {command} [load|save]"
                args_list = args.split(" ") if args else []
                if len(args_list) != 1 or not args_list[0]:
                    self._window.main.insertHtml(usage)
                    return
                subcommand = args_list[0]
                if subcommand.startswith("l"):
                    self._config.load()
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

            elif command == "#layout":
                usage = f"<br/>Usage: {command} [load|save]"
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
                usage = f"<br/>Usage: {command} [command|game]"
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
                    old_parser.clear_window.disconnect(self._window._on_clear_window)
                    old_parser.update_casttime.disconnect(self._window._on_update_casttime)
                    old_parser.update_compass.disconnect(self._window._on_update_compass)
                    old_parser.update_indicators.disconnect(self._window._on_update_indicators)
                    old_parser.update_minivitals.disconnect(self._window._on_update_minivitals)
                    old_parser.update_roundtime.disconnect(self._window._on_update_roundtime)
                    old_parser.update_window.disconnect(self._window._on_update_window)
                    importlib.reload(_game_module)
                    self._window.game_parser = _game_module.GameParser()
                    self._window.game_parser.clear_window.connect(self._window._on_clear_window)
                    self._window.game_parser.update_casttime.connect(self._window._on_update_casttime)
                    self._window.game_parser.update_compass.connect(self._window._on_update_compass)
                    self._window.game_parser.update_indicators.connect(self._window._on_update_indicators)
                    self._window.game_parser.update_minivitals.connect(self._window._on_update_minivitals)
                    self._window.game_parser.update_roundtime.connect(self._window._on_update_roundtime)
                    self._window.game_parser.update_window.connect(self._window._on_update_window)
                    self._window.main.insertHtml("<br/>Game parser reloaded.")
                else:
                    self._window.main.insertHtml(usage)

            elif command == "#toolbar" or command == "#toolbars":
                usage = f"<br/>Usage: {command} [lock|unlock]"
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
                usage = f"<br/>Usage: {command} [load|save]"
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
                usage = f"<br/>Usage: {command} [list|show|hide] (name)"
                args_list = args.split(" ") if args else []
                if len(args_list) < 1:
                    self._window.main.insertHtml(usage)
                    return

                subcommand = args_list[0]
                if not subcommand.startswith("l") and len(args_list) != 2:
                    self._window.main.insertHtml(usage)
                    return

                windows_list = [w for w in self._variables.items("widgets") if w != "main_window" and w != "main"]
                if subcommand.startswith("l"):
                    self._window.main.insertHtml(f"<br/>Available windows: {", ".join(windows_list)}")
                    return

                window_name = args_list[1]
                if window_name == "main_window" or window_name == "main":
                    self._window.main.insertHtml(f"<br/>Window {window_name} cannot be shown/hidden.")
                    return

                window = self._variables.get("widgets", window_name, None)
                if not window:
                    self._window.main.insertHtml(f"<br/>Window {window_name} not found: {", ".join(windows_list)}")
                    return

                if not isinstance(window, QDockWidget):
                    window = window.parentWidget() or window

                if subcommand.startswith("s"):
                    window.show()
                elif subcommand.startswith("h"):
                    window.hide()
                else:
                    self._window.main.insertHtml(usage)

            elif command == "#test":
                self._window.main.insertHtml("<br/>It works!")

            else:
                self._window.main.insertHtml(f"<br/>Unknown command: {input}")

        else:
            self._variables.set("temporary", "lastcommand", input)
            if self._window.game_client.state.name != "Connected":
                self._window.main.insertHtml(f"<br/>({input})")
            else:
                color = self._config.get("presets", "commands.color", "")
                bgcolor = self._config.get("presets", "commands.bgcolor", "")

                self._window.main.insertHtml(
                    f"""<span style="color: {color}; background-color: {bgcolor};">{input}</span>""",
                )
                self._window.game_client.send(input)
