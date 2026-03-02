import logging
import re
import time

from PyQt6.QtGui import QTextCursor

from config import Config
from game import GameState


class CommandParser:
    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

        self._config = Config()

        self._window = self._config.get("temporary", "main_window", None)

    def Parse(self, input: str) -> None:
        input = re.sub(r"\s+", " ", input.strip())

        try:
            command, args = input.split(" ", 1)
        except ValueError:
            command = input
            args = ""

        if command.startswith("#"):
            if command == "#connect":
                if self._window.game_client.state == GameState.Connected:
                    self._logger.debug("#connect: already connected")
                    return

                args_list = args.split(" ")
                if len(args_list) != 4:
                    self._window.main.insertHtml(
                        "Usage: #connect [username] [password] [character] [instance]",
                    )
                    return

                self._config.set("temporary", "login_key", b"")

                username, password, character, instance = args_list
                self._config.set("temporary", "username", username)
                self._config.set("temporary", "password", password)
                self._config.set("temporary", "character", character)
                self._config.set("temporary", "instance", instance)

                self._window.eaccess_client.connect()
                self._window.eaccess_client.authenticate()
                self._window.eaccess_client.wait_for_login_key(3000)

                self._config.set("temporary", "guild", "Commoner")

                self._window.game_client.connect()
                self._window.game_client.authenticate()

            elif command == "#disconnect":
                self._window.eaccess_client.disconnect()
                self._window.game_client.disconnect()

            elif command == "#exit":
                self._window.eaccess_client.disconnect()
                self._window.game_client.disconnect()
                self._window.close()

            elif command == "#layout":
                usage = f"<br/>Usage: {command} [load|save]"
                args_list = args.split(" ")
                if len(args_list) != 1:
                    self._window.main.insertHtml(usage)
                    return
                subcommand = args_list[0]
                if subcommand.startswith("l"):
                    self._window.restoreState(self._config.get("client", "state", b""))
                elif subcommand.startswith("s"):
                    geometry = self._window.saveGeometry()
                    self._config.set("client", "geometry", geometry)
                    self._logger.debug(f"MainWindow geometry: {geometry}")

                    state = self._window.saveState()
                    self._config.set("client", "state", state)
                    self._logger.debug(f"MainWindow state: {state}")
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
                elif subcommand.startswith("u"):
                    self._window._on_unlock_toolbars(True)
                else:
                    self._window.main.insertHtml(usage)

            else:
                self._window.main.insertHtml(f"<br/>Unknown command: {input}")

        else:
            self._config.set("temporary", "lastcommand", input)
            if self._window.game_client.state != GameState.Connected:
                self._window.main.insertHtml(f"<br/>({input})")
            else:
                color = self._config.get("presets", "commands.color", "")
                bgcolor = self._config.get("presets", "commands.bgcolor", "")

                self._window.main.insertHtml(
                    f"""<span style="color: {color}; background-color: {bgcolor};">{input}</span>""",
                )

                self._window.game_client.send(input)

                self._window.main.textCursor().movePosition(
                    QTextCursor.MoveOperation.Left,
                    QTextCursor.MoveMode.MoveAnchor,
                )
