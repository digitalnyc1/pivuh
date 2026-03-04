import logging
import re
import struct
import time
from enum import Enum
from pathlib import Path
from typing import Union

import requests
from PyQt6.QtCore import (
    QEventLoop,
    QObject,
    QThread,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtNetwork import (
    QSslConfiguration,
    QSslError,
    QSslSocket,
    QTcpSocket,
)

from config import Config
from variables import Variables


class EAccessState(Enum):
    Disconnected = 0
    ListeningForKey = 1
    Unauthenticated = 2
    KeyAuthenticated = 3
    Authenticated = 4
    AuthenticationFailed = 5
    InvalidResponse = 6


class EAccessClient(QThread):
    connected = pyqtSignal(str)
    disconnected = pyqtSignal(str)
    message_received = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("__init__")

        self._config = Config()
        self._variables = Variables()

        self.state = EAccessState.Disconnected
        self._eaccess_host: str = ""
        self._eaccess_port: int = 0
        self._hash_key: bytes = b""
        self._account: bytes = b""
        self._password: bytes = b""
        self._character: bytes = b""
        self._instance: str = ""
        self._login_key: bytes = b""

        ssl_config = QSslConfiguration.defaultConfiguration()
        ssl_config.setPeerVerifyMode(QSslSocket.PeerVerifyMode.VerifyNone)

        self._socket = QSslSocket(self)
        self._socket.setSslConfiguration(ssl_config)
        self._socket.connected.connect(self._on_connected)
        self._socket.disconnected.connect(self._on_disconnected)
        self._socket.errorOccurred.connect(self._handle_error)
        self._socket.readyRead.connect(self._read_data)
        self._socket.sslErrors.connect(self._handle_ssl_errors)

    def _handle_error(self, socket_error: QSslSocket.SocketError) -> None:
        self._logger.debug("_handle_error: begin")

        self._logger.error(f"Socket error: {socket_error}")

        self._logger.debug("_handle_error: end")

    def _handle_ssl_errors(self, ssl_errors: list[QSslError]) -> None:
        self._logger.debug("_handle_ssl_errors: begin")

        ignored_errors = [
            "CertificateUntrusted",
            "HostNameMismatch",
        ]

        for error in ssl_errors:
            if error.error().name in ignored_errors:
                self._logger.debug(
                    f"_handle_ssl_errors: ignoring expected SSL error: {error.error().name}",
                )
                self._socket.ignoreSslErrors()
            else:
                self._logger.error(
                    f"Eaccess SSL socket error: {error.error().name}({error.error().value}): {error.errorString()}",
                )

        self._logger.debug("_handle_ssl_errors: end")

    def _hash_password(self) -> bytes:
        password = list(self._password[:32])
        hash_key = list(self._hash_key[:32])
        return b"".join(
            [
                struct.pack("B", ((char - 32) ^ hash_key[i]) + 32)
                for i, char in enumerate(password)
            ],
        )

    def _on_connected(self) -> None:
        self._logger.debug("_on_connected: begin")

        self.connected.emit(f"Connected to {self._eaccess_host}:{self._eaccess_port}.")

        self._logger.debug("_on_connected: end")

    def _on_disconnected(self) -> None:
        self._logger.debug("_on_disconnected: begin")

        self.do_disconnect()
        self.disconnected.emit(f"Connection to {self._eaccess_host} closed.")

        self._logger.debug("_on_disconnected: end")

    def _read_data(self) -> None:
        while self._socket.bytesAvailable():
            data = self._socket.readAll().data()

            if self.state == EAccessState.ListeningForKey:
                self._hash_key, _, _ = data.partition(b"\n")
                if len(self._hash_key) != 32:
                    self._logger.error(
                        f"Received invalid hash key from {self._eaccess_host}.",
                    )
                    self.message_received.emit(
                        f"Received invalid hash key from {self._eaccess_host}.",
                    )
                    self.state = EAccessState.InvalidResponse
                    self.do_disconnect()
                    return
                self.state = EAccessState.Unauthenticated
                a_cmd = b"A\t" + self._account + b"\t" + self._hash_password() + b"\n"
                self._socket.write(a_cmd)
                self._socket.flush()

            elif self.state == EAccessState.Unauthenticated:
                if b"KEY" not in data:
                    self.state = EAccessState.AuthenticationFailed

                    reason = "reason unknown"
                    if b"NORECORD" in data:
                        reason = "bad account name"
                    elif b"PASSWORD" in data:
                        reason = "bad password"

                    self._logger.error(f"Login failed: {reason}.")
                    self.message_received.emit(f"Login failed: {reason}.")
                    self.do_disconnect()

                else:
                    self.state = EAccessState.Authenticated
                    data, _, _ = data.partition(b"\n")
                    try:
                        parts = data.split(b"\t")
                        self._login_key = parts[3]
                    except IndexError:
                        self._logger.error(
                            "Failed to parse login key from server response.",
                        )
                        self.message_received.emit(
                            "Failed to parse login key from server response.",
                        )
                        self.do_disconnect()
                        return

                    g_cmd = f"G\t{self._instance}\n".encode("ascii")
                    self._socket.write(g_cmd)
                    self._socket.flush()

            elif self.state == EAccessState.Authenticated:
                if data.startswith(b"G\t"):
                    self._socket.write(b"C\n")
                    self._socket.flush()

                elif data.startswith(b"C\t"):
                    groups = re.finditer(rb"\t(W_\w+)\t(\w+)", data)

                    character_found = False
                    for group in groups:
                        character_id = group.group(1)
                        character_name = group.group(2)
                        if character_name == self._character:
                            character_found = True
                            l_cmd = b"L\t" + character_id + b"\tSTORM\n"
                            self._socket.write(l_cmd)
                            self._socket.flush()

                    if not character_found:
                        character = self._character.decode("ascii")
                        instance = self._instance
                        account = self._account.decode("ascii")

                        self._logger.error(
                            f"Character {character} does not exist in game instance {instance} on account {account}.",
                        )
                        self.message_received.emit(
                            f"Character {character} does not exist in game instance {instance} on account {account}.",
                        )
                        self.do_disconnect()

                elif data.startswith(b"L\t"):
                    if b"OK" not in data:
                        self._logger.error("Login failed.")
                        self.message_received.emit("Login failed.")
                        self.do_disconnect()
                    else:
                        self._logger.debug("_read_data: login successful")
                        try:
                            parts = data.split(b"\t")
                            game_host = parts[7]
                            game_port = parts[8]
                        except IndexError:
                            self._logger.error(
                                "Failed to parse game host/port from server response.",
                            )
                            self.message_received.emit(
                                "Failed to parse game host/port from server response.",
                            )
                            self.do_disconnect()
                            return
                        self._variables.set(
                            "temporary",
                            "game_host",
                            game_host.decode("ascii").replace("GAMEHOST=", ""),
                        )
                        self._variables.set(
                            "temporary",
                            "game_port",
                            int(game_port.decode("ascii").replace("GAMEPORT=", "")),
                        )
                        self._variables.set(
                            "protected", "login_key", self._login_key.decode("ascii"),
                        )
                        self.do_disconnect()

                elif data.startswith(b"X\t"):
                    self._logger.error(
                        "Login failed.  Please check that you have specified the correct account, password, character and game instance.",
                    )
                    self.message_received.emit(
                        "Login failed.  Please check that you have specified the correct account, password, character and game instance.",
                    )
                    self.do_disconnect()

    def connect(self) -> None:
        if self.state != EAccessState.Disconnected:
            self._logger.debug("connect: already connected")
            return

        self._logger.debug("connect: begin")

        self._eaccess_host = self._config.get("game", "eaccess.host", "")
        self._eaccess_port = self._config.get("game", "eaccess.port", 0)

        if not self._eaccess_host or not self._eaccess_port:
            self._logger.error("Missing Eaccess host and/or port.")
            return

        self._socket.connectToHostEncrypted(self._eaccess_host, self._eaccess_port)
        if not self._socket.waitForEncrypted(3000):
            self.connected.emit(
                f"Failed to connect to {self._eaccess_host}:{self._eaccess_port}.",
            )
            self._logger.error(
                f"Failed to connect to {self._eaccess_host}:{self._eaccess_port}.",
            )
            return

        self._logger.debug("connect: end")

    def authenticate(self) -> None:
        if not self._socket.isOpen():
            self._logger.error("Failed to authenticate: Not connected.")
            return

        self._logger.debug("authenticate: begin")

        self._account = self._variables.get("temporary", "account", "").encode("ascii")
        self._password = self._variables.get("protected", "password", "").encode(
            "ascii",
        )
        self._character = self._variables.get("temporary", "character", "").encode(
            "ascii",
        )
        self._instance = self._variables.get("temporary", "instance", "")

        self.state = EAccessState.ListeningForKey
        self._socket.write(b"K\n")
        self._socket.flush()

        self._logger.debug("authenticate: end")

    def do_disconnect(self) -> None:
        if self.state == EAccessState.Disconnected or not self._socket.isOpen():
            self._logger.debug("disconnect: already disconnected")
            return

        self._logger.debug("disconnect: begin")

        self._socket.disconnectFromHost()
        if self._socket.state() == QSslSocket.SocketState.ConnectedState:
            self._socket.waitForDisconnected(3000)

        self._variables.set("protected", "password", "")
        self.state = EAccessState.Disconnected

        self._logger.debug("disconnect: end")

    def wait_for_login_key(self, timeout: int) -> bool:
        self._logger.debug("wait_for_login_key: begin")

        loop = QEventLoop()
        self.disconnected.connect(loop.quit)
        QTimer.singleShot(timeout, loop.quit)
        loop.exec()
        self.disconnected.disconnect(loop.quit)

        result = bool(self._variables.get("protected", "login_key", ""))
        self._logger.debug(f"wait_for_login_key: end result({result})")
        return result


class GameState(Enum):
    Disconnected = 0
    SendSettings = 1
    Connected = 2


class GameClient(QThread):
    connected = pyqtSignal(str)
    disconnected = pyqtSignal(str)
    message_received = pyqtSignal(str)
    update_vitals = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("__init__")

        self._config = Config()
        self._variables = Variables()

        self.state = GameState.Disconnected
        self._write_buffer: str = ""
        self._game_host: str = ""
        self._game_port: int = 0
        self._login_key: str = ""

        self._socket = QTcpSocket(self)
        self._socket.connected.connect(self._on_connected)
        self._socket.disconnected.connect(self._on_disconnected)
        self._socket.errorOccurred.connect(self._handle_error)
        self._socket.readyRead.connect(self._read_data)

    def _handle_error(self, socket_error: QTcpSocket.SocketError) -> None:
        self._logger.error(f"Socket error: {socket_error}")

    def _on_connected(self) -> None:
        self._logger.debug("_on_connected: begin")

        self.connected.emit(f"Connected to {self._game_host}:{self._game_port}.")

        self._logger.debug("_on_connected: end")

    def _on_disconnected(self) -> None:
        self._logger.debug("_on_disconnected: begin")

        self.do_disconnect()
        self.disconnected.emit(f"Connection to {self._game_host} closed.")

        self._logger.debug("_on_disconnected: end")

    def _read_data(self) -> None:
        while self._socket.bytesAvailable():
            data = self._socket.readAll().data()

            if self.state == GameState.SendSettings:
                if re.search(
                    rb"^Invalid login key\.  Please relogin to the web site\.$",
                    data,
                ):
                    self._logger.error(
                        "Game server rejected the login key.  Please try again.",
                    )
                    self.message_received.emit(
                        "Game server rejected the login key.  Please try again.",
                    )
                    self.do_disconnect()
                    break

                elif re.search(rb"<settingsInfo.*?/>", data, flags=re.DOTALL):
                    self._socket.write(b"<sendSettings/>\n")
                    self._socket.flush()

                elif re.search(rb"<sentSettings/>", data, flags=re.DOTALL):
                    self._socket.write(b"\n\n")
                    self._socket.flush()
                    self.state = GameState.Connected
            else:
                try:
                    self.message_received.emit(data.decode("ascii"))
                except UnicodeDecodeError as e:
                    self._logger.error(
                        f"Error decoding message received from game server: {e}\nMessage contents: {repr(data)}",
                    )

    def authenticate(self) -> None:
        if not self._socket.isOpen():
            self._logger.error("Failed to authenticate: Not connected.")
            return

        if self.state == GameState.Connected:
            self._logger.debug("authenticate: already connected")
            return

        if not self._login_key:
            self._logger.error("Login key is not set.")
            return

        self._logger.debug("authenticate: begin")

        ident = self._config.get("client", "client.ident", "")
        self._socket.write(f"<c>{self._login_key}\n".encode("ascii"))
        self._socket.write(f"<c>{ident}\n".encode("ascii"))
        self._socket.flush()
        self._logger.debug("authenticate: end")

    def connect(self) -> None:
        if self.state != GameState.Disconnected:
            self._logger.debug("connect: already connected")
            return

        self._logger.debug("connect: begin")

        self._game_host = self._variables.get("temporary", "game_host", "")
        self._game_port = self._variables.get("temporary", "game_port", 0)
        self._login_key = self._variables.get("protected", "login_key", "")
        if not self._game_host or not self._game_port or not self._login_key:
            self._logger.error("Missing game host, game port or login key.")
            return

        self._socket.connectToHost(self._game_host, self._game_port)
        if not self._socket.waitForConnected(3000):
            self.connected.emit(
                f"Failed to connect to {self._game_host}:{self._game_port}.",
            )
            self._logger.error(
                f"Failed to connect to {self._game_host}:{self._game_port}.",
            )
            return

        self.state = GameState.SendSettings
        self._logger.debug("connect: end")

    def do_disconnect(self) -> None:
        if self.state == GameState.Disconnected or not self._socket.isOpen():
            self._logger.debug("disconnect: already disconnected")
            return

        self._logger.debug("disconnect: begin")

        self._socket.disconnectFromHost()
        if self._socket.state() == QTcpSocket.SocketState.ConnectedState:
            self._socket.waitForDisconnected(3000)

        self.state = GameState.Disconnected

        self._logger.debug("disconnect: end")

    def send(self, message: str) -> None:
        if not self._socket.isOpen():
            self._logger.debug("send: not connected")
            return
        self._socket.write(f"<c>{message}\n".encode("ascii"))
        self._socket.flush()


class GameParser(QObject):
    clear_window = pyqtSignal(str)
    update_casttime = pyqtSignal(int)
    update_compass = pyqtSignal(list)
    update_indicators = pyqtSignal(list)
    update_minivitals = pyqtSignal(str, int, str)
    update_roundtime = pyqtSignal(int)
    update_window = pyqtSignal(str, str)

    _room_attributes = [
        "roomname",
        "roomdesc",
        "roomobjs",
        "roomplayers",
        "roomexits",
        "roomextra",
    ]

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)

        self._config = Config()
        self._variables = Variables()

        self._buffer = ""
        self._window = self._variables.get("widgets", "main_window", None)

    def _download_portrait(self, portrait_id: str) -> bool:
        portrait_timeout = self._config.get("game", "portrait.timeout")
        portrait_url = self._config.get("game", "portrait.url")
        url = f"{portrait_url}/{portrait_id}.jpg"
        dest = Path.cwd() / "cache" / f"{portrait_id}.jpg"
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            dest.write_bytes(response.content)
            self._logger.debug(f"_download_portrait: saved portrait {portrait_id}")
            return True
        except Exception as e:
            self._logger.warning(f"_download_portrait: failed to download portrait {portrait_id}: {e}")
            return False

    def parse(self, message: str) -> None:
        self._buffer += message

        update_room = False

        groups = re.search(
            r"""<prompt time=['"](\d+)['"]>(.*?)</prompt>\n?""",
            self._buffer,
            flags=re.DOTALL,
        )

        # Buffer until we receive the prompt tag
        if not groups:
            return

        remaining = self._buffer[groups.end() :]
        self._buffer = self._buffer[: groups.end()]

        start_time = time.perf_counter()

        gametime = int(groups.group(1))
        prompt = groups.group(2)
        self._logger.debug(f"Prompt received: gametime({gametime}) prompt({prompt})")

        # Remove ANSI control characters and escape sequences, but leave newlines
        self._buffer = re.sub(
            r"(?:\x07|\x08|\x0D|\x1b\[[0-9;]*m)",
            "",
            self._buffer.rstrip(),
        )

        # Process the buffer
        # Note: Order of tag processing is important in certain cases
        self._logger.debug(f"Parse before: {repr(self._buffer)}")

        # <prompt></prompt>
        self._variables.set("temporary", "gametime", gametime)
        self._variables.set("temporary", "prompt", prompt)
        self._buffer = re.sub(
            r"""<prompt time=['"](\d+)['"]>(.*?)</prompt>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <settingsInfo/>
        self._buffer = re.sub(
            r"""<settingsInfo.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <sentSettings/>
        self._buffer = re.sub(
            r"""<sentSettings/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <mode/>
        self._buffer = re.sub(
            r"""<mode.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <settings><settings/>
        self._buffer = re.sub(
            r"""<settings.*?>.*?</settings>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <playerID/>
        self._buffer = re.sub(
            r"""<playerID.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <app/>
        self._buffer = re.sub(
            r"""<app.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <pushBold/>
        color = self._config.get("presets", "monsterbold.color", "")
        bgcolor = self._config.get("presets", "monsterbold.bgcolor", "")
        self._buffer = re.sub(
            r"""<pushBold/>""",
            rf"""<span style="color: {color}; background-color: {bgcolor};">""",
            self._buffer,
            flags=re.DOTALL,
        )

        # <popBold/>
        self._buffer = re.sub(
            r"""<popBold/>""",
            "</span>",
            self._buffer,
            flags=re.DOTALL,
        )

        # <output/>
        fontname = self._config.get("presets", "monospace.fontname")
        fontsize = self._config.get("presets", "monospace.fontsize")
        self._buffer = re.sub(
            r"""<output class=['"]mono['"]/>""",
            rf"""<pre style='font-family: "{fontname}"; font-size: {fontsize}; white-space: pre-wrap; word-wrap: break-word;'>""",
            self._buffer,
            flags=re.DOTALL,
        )

        self._buffer = re.sub(
            r"""\n?<output.*?/>\n?""",
            "</pre>",
            self._buffer,
            flags=re.DOTALL,
        )

        # <style/>
        for groups in re.finditer(
            r"""<style id=['"](.*?)['"].*?/>(.*?)\n?<style id=['"]['"]/>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            style_id = groups.group(1).lower()
            content = groups.group(2)
            self._logger.debug(f"style: style_id({style_id}) content({content})")

            color = self._config.get("presets", f"{style_id}.color", "")
            bgcolor = self._config.get("presets", f"{style_id}.bgcolor", "")

            self._buffer = re.sub(
                rf"""<style id=['"].*?['"].*?/>(.*?)\n?<style id=['"]['"]/>\n?""",
                rf"""<span style="color: {color}; background-color: {bgcolor};">\1</span><br/>""",
                self._buffer,
                flags=re.DOTALL,
            )

        # <preset></preset>
        for groups in re.finditer(
            r"""<preset id=['"](.*?)['"]>(.*?)\n?</preset>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            preset_id = groups.group(1).lower()
            content = groups.group(2)
            self._logger.debug(f"preset: preset_id({preset_id}) content({content})")

            color = self._config.get("presets", f"{preset_id}.color", "")
            bgcolor = self._config.get("presets", f"{preset_id}.bgcolor", "")

            end = ""
            if preset_id == "roomdesc":
                end = "<br/>"

            self._buffer = re.sub(
                rf"""<preset id=['"].*?['"]>\n?(.*?)\n?</preset>\s*\n?""",
                rf"""<span style="color: {color}; background-color: {bgcolor};">\1{end}</span>""",
                self._buffer,
                flags=re.DOTALL,
            )

        # <clearContainer/>
        for groups in re.finditer(
            r"""<clearContainer id=['"](.*?)['"]/>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            contaner_id = groups.group(1)
            self.clear_window.emit(contaner_id)

        self._buffer = re.sub(
            r"""<clearContainer.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <clearStream/>
        for groups in re.finditer(
            r"""<clearStream id=['"](.*?)['"].*?/>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            stream_id = groups.group(1)
            self.clear_window.emit(stream_id)
            self._logger.debug(f"clearStream: stream_id({stream_id})")

        self._buffer = re.sub(
            r"""<clearStream.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <streamWindow/>
        for groups in re.finditer(
            r"""<streamWindow id=['"](.*?)['"] title=['"](.*?)['"] subtitle=['"] - \[(.*?)\](?:\s\((\d+)\))?['"].*?/>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            stream_id = groups.group(1)
            title = groups.group(2)
            subtitle = groups.group(3)
            roomid = groups.group(4) or "**"
            self._logger.debug(
                f"streamWindow: stream_id({stream_id}) title({title}) subtitle({subtitle}) roomid({roomid})",
            )
            if stream_id == "room":
                if subtitle:
                    self._variables.set("temporary", "roomname", subtitle)
                    self._variables.set("temporary", "roomid", roomid)
                    update_room = True

        self._buffer = re.sub(
            r"""<streamWindow.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <pushStream/><popStream/>
        for groups in re.finditer(
            r"""<pushStream id=['"](.*?)['"].*?/>(.*?)<popStream.*?/>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            stream_id = groups.group(1)
            content = groups.group(2)
            content = content.replace("\n", "<br/>").replace("</pre><br/>", "</pre>")
            self._logger.debug(
                f"pushStream/popStream: stream_id({stream_id}) content({repr(content)})",
            )
            if stream_id != "room" and content:
                self.update_window.emit(stream_id, content)

        self._buffer = re.sub(
            r"""<pushStream.*?/>.*?<popStream.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <compDef/>
        for groups in re.finditer(
            r"""<compDef id=['"](.*?)['"]/>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            compdef_id = groups.group(1)
            guild = "Commoner"
            if "Astrology" in compdef_id:
                guild = "Moon Mage"
            elif "Backstab" in compdef_id:
                guild = "Thief"
            elif "Bardic Lore" in compdef_id:
                guild = "Bard"
            elif "Conviction" in compdef_id:
                guild = "Paladin"
            elif "Empathy" in compdef_id:
                guild = "Empath"
            elif "Expertise" in compdef_id:
                guild = "Barbarian"
            elif "Instinct" in compdef_id:
                guild = "Ranger"
            elif "Summoning" in compdef_id:
                guild = "Warrior Mage"
            elif "Thanatology" in compdef_id:
                guild = "Necromancer"
            elif "Theurgy" in compdef_id:
                guild = "Cleric"
            elif "Trading" in compdef_id:
                guild = "Trader"

            self._logger.debug(f"compDef: compdef_id({compdef_id}) guild({guild})")
            if guild != "Commoner":
                self._variables.set("temporary", "guild", guild)
                self._logger.debug(f"guild({guild})")

        self._buffer = re.sub(
            r"""<compDef.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <component></component>
        for groups in re.finditer(
            r"""<component id=['"](.*?)['"]>(.*?)\n?</component>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            component_id = groups.group(1)
            content = groups.group(2)
            # TODO: HTML tags are needed for the room window, but complicate the roomobjs variable
            # content = re.sub(r"<[^>]*>", "", content)
            self._logger.debug(f"component: component_id({component_id}) content({content})")

            if component_id.startswith("room "):
                component_id = component_id.replace(" ", "")

                self._variables.set("temporary", component_id, content)

                update_room = True

            elif component_id.startswith("exp "):
                skill = component_id.replace("exp ", "").replace(" ", "_")

                if content:
                    self.update_window.emit("experience", f"{content}<br/>")

                # Normal experience style
                groups = re.match(
                    rf"^\s+{skill}:\s+(\d+)\s(\d+)%\s+(.*?)\s*$",
                    content,
                    flags=re.DOTALL,
                )
                if not groups:
                    # ExpBrief experience style
                    groups = re.match(
                        r"^.*?:\s+(\d+)\s(\d+)%\s+\[\s?(\d+)/34]$",
                        content,
                        flags=re.DOTALL,
                    )

                if groups:
                    ranks = float(
                        ".".join(
                            [
                                groups.group(1),
                                groups.group(2),
                            ],
                        ),
                    )
                    mindstate = int(MindState.to_int(groups.group(3)))
                    if skill and ranks and mindstate:
                        self._variables.set("temporary", f"{skill}.Ranks", ranks)
                        self._variables.set(
                            "temporary",
                            f"{skill}.LearningRate",
                            mindstate,
                        )
                        self._logger.debug(
                            f"Updating skill info: skill({skill}) ranks({ranks}) mindstate({mindstate})",
                        )

        self._buffer = re.sub(
            r"""<component.*?>.*?</component>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <exposeContainer/>
        self._buffer = re.sub(
            r"""<exposeContainer.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <container/>
        self._buffer = re.sub(
            r"""<container.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <inv></inv>
        for groups in re.finditer(
            r"""<inv id=['"](.*?)['"]>(.*?)</inv>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            inv_id = groups.group(1)
            content = groups.group(2)
            self._logger.debug(f"inv: inv_id({inv_id}) content({content})")
            self.update_window.emit(inv_id, f"{content}<br/>")

        self._buffer = re.sub(
            r"""<inv id=['"].*?['"]>.*?</inv>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <openDialog></<openDialog>
        self._buffer = re.sub(
            r"""<openDialog.*?>.*?</openDialog>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <dialogData></dialogData>
        for groups in re.finditer(
            r"""<dialogData id=['"](.*?)['"].*?>(.*?)</dialogData>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            dialog_id = groups.group(1)
            content = groups.group(2)

            if dialog_id == "minivitals":
                content = re.sub(r"""<skin.*?/>""", "", content, flags=re.DOTALL)
                for content_groups in re.finditer(
                    r"""<progressBar id=['"](\w+)['"] value=['"](\d+)['"] text=['"](.*?)['"].*?/>""",
                    content,
                ):
                    minivitals_id = content_groups.group(1)
                    minivitals_value = int(content_groups.group(2))
                    minivitals_text = content_groups.group(3).title()

                    self._variables.set("temporary", minivitals_id, minivitals_value)
                    self._variables.set(
                        "temporary",
                        f"{minivitals_id}BarText",
                        minivitals_text,
                    )

                    self.update_minivitals.emit(
                        minivitals_id,
                        minivitals_value,
                        minivitals_text,
                    )
                content = re.sub(r"""<progressBar.*?/>""", "", content, flags=re.DOTALL)
            else:
                self._logger.debug(
                    f"dialogData: ignoring content with unsupported dialogData id: {dialog_id}",
                )

        # <dialogData></dialogData>
        self._buffer = re.sub(
            r"""<dialogData.*?>.*?</dialogData>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <switchQuickBar/>
        self._buffer = re.sub(
            r"""<switchQuickBar.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <indicator/>
        has_indicator_update = bool(re.search(r"""<indicator""", self._buffer))
        indicators = []
        for groups in re.finditer(
            r"""<indicator id=['"](\w*)['"] visible=['"]y['"]/>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            indicator_id = groups.group(1)
            indicators.append(indicator_id)
        if has_indicator_update:
            self.update_indicators.emit(indicators)

        self._buffer = re.sub(
            r"""<indicator.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <spell></spell>
        for groups in re.finditer(
            r"""<spell(?:\s+exist=['"](.*?)['"])?>(.*?)</spell>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            spell = groups.group(2)
            self._window.spell.setText(spell)

        self._buffer = re.sub(
            r"""<spell.*?>.*?</spell>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <left></left>
        for groups in re.finditer(
            r"""<left(?:\s+exist=['"](\d+)['"]\s+noun=['"](\w+)['"])?>(.*?)</left>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            lefthand = groups.group(3)
            self._variables.set("temporary", "lefthand", lefthand)
            self._variables.set("temporary", "lefthandid", groups.group(1))
            self._variables.set("temporary", "lefthandnoun", groups.group(2))
            self._window.left.setText(lefthand)

        self._buffer = re.sub(
            r"""<left.*?>.*?</left>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <right></right>
        for groups in re.finditer(
            r"""<right(?:\s+exist=['"](\d+)['"]\s+noun=['"](\w+)['"])?>(.*?)</right>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            righthand = groups.group(3)
            self._variables.set("temporary", "righthand", righthand)
            self._variables.set("temporary", "righthandid", groups.group(1))
            self._variables.set("temporary", "righthandnoun", groups.group(2))
            self._window.right.setText(righthand)

        self._buffer = re.sub(
            r"""<right.*?>.*?</right>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <endSetup/>
        self._buffer = re.sub(
            r"""<endSetup/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <d></d>
        color = self._config.get("presets", "link.color", "")
        bgcolor = self._config.get("presets", "link.bgcolor", "")
        self._buffer = re.sub(
            r"""<d>(.*?)</d>""",
            rf"""<a href="\1" style="color: {color}; background-color: {bgcolor};">\1</a>""",
            self._buffer,
            flags=re.DOTALL,
        )
        self._buffer = re.sub(
            r"""<d cmd=['"](.*?)['"]>(.*?)</d>""",
            rf"""<a href="\1" style="color: {color}; background-color: {bgcolor};"><font color="{color}">\2</font></a>""",
            self._buffer,
            flags=re.DOTALL,
        )

        # <nav/>
        self._buffer = re.sub(
            r"""<nav/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <resource/>
        for groups in re.finditer(
            r"""<resource picture=['"](\d+)['"]/>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            picture_id = groups.group(1)
            self._logger.debug(f"resource: picture({picture_id})")
            if picture_id != "0":
                file_name = Path.cwd() / "cache" / f"{picture_id}.jpg"
                if not file_name.exists():
                    self._download_portrait(picture_id)
                if file_name.exists():
                    file_uri = file_name.as_uri()
                    self._buffer = re.sub(
                        rf"""<resource picture=['"]{picture_id}['"]/>\n?""",
                        f"""<img src="{file_uri}"/><br/>""",
                        self._buffer,
                        flags=re.DOTALL,
                    )

        self._buffer = re.sub(
            r"""<resource.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <compass><dir/></compass>
        for groups in re.finditer(
            r"""<compass>(.*?)</compass>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            directions = []
            content = groups.group(1)
            for content_groups in re.finditer(
                r"""<dir value=['"](\w+)['"]/>""",
                content,
            ):
                direction = content_groups.group(1)
                directions.append(direction)
            self.update_compass.emit(directions)

        self._buffer = re.sub(
            r"""<compass>.*?</compass>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <roundTime/>
        for groups in re.finditer(
            r"""<roundTime value=['"](\d+)['"]/>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            value = int(groups.group(1))
            roundtime = value - gametime
            self._variables.set("temporary", "roundtime", roundtime)
            self._logger.debug(
                f"roundtime: value({value}) gametime({gametime}) roundtime({roundtime})",
            )
            self.update_roundtime.emit(roundtime)

        self._buffer = re.sub(
            r"""<roundTime.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # <castTime/>
        for groups in re.finditer(
            r"""<castTime value=['"](\d+)['"]/>""",
            self._buffer,
            flags=re.DOTALL,
        ):
            value = int(groups.group(1))
            casttime = value - gametime
            self._variables.set("temporary", "casttime", casttime)
            self._logger.debug(
                f"casttime: value({value}) gametime({gametime}) castime({casttime})",
            )
            self.update_casttime.emit(casttime)

        self._buffer = re.sub(
            r"""<castTime.*?/>\n?""",
            "",
            self._buffer,
            flags=re.DOTALL,
        )

        # Set variables from exp output
        for groups in re.finditer(
            r"""\s+SKILL: Rank/Percent towards next rank/Amount learning/Mindstate Fraction\n(.*?)\nEXP HELP for more information""",
            self._buffer,
            flags=re.DOTALL,
        ):
            content = groups.group(1)
            for content_groups in re.finditer(
                r"""\s+(.*?):\s+(\d+)\s(\d+)%\s.*?\((\d+)/34\)""",
                content,
                flags=re.DOTALL,
            ):
                skill = content_groups.group(1).replace(" ", "_")
                ranks = float(
                    ".".join(
                        [
                            content_groups.group(2),
                            content_groups.group(3),
                        ],
                    ),
                )
                mindstate = int(content_groups.group(4))
                self._variables.set("temporary", f"{skill}.Ranks", ranks)
                self._variables.set("temporary", f"{skill}.LearningRate", mindstate)
                self._logger.debug(
                    f"Updating skill info: skill({skill}) ranks({ranks}) mindstate({mindstate})",
                )

        # Check if room window needs to be updated
        if update_room:
            self.clear_window.emit("room")

            roomname_color = self._config.get("presets", "roomname.color", "")
            roomname_bgcolor = self._config.get("presets", "roomname.bgcolor", "")

            roomdesc_color = self._config.get("presets", "roomdesc.color", "")
            roomdesc_bgcolor = self._config.get("presets", "roomdesc.bgcolor", "")

            content = ""
            for key in self._room_attributes:
                value = self._variables.get("temporary", key, "Unknown")

                if key == "roomname":
                    color = roomname_color
                    bgcolor = roomname_bgcolor
                    value = f"[{value}]"
                else:
                    color = roomdesc_color
                    bgcolor = roomdesc_bgcolor

                if value:
                    content += f"""<span style="color: {color}; background-color: {bgcolor};">{value}</span><br/>"""

            self.update_window.emit("room", content)

        # Final check if there are any XML tags we missed
        allowed_tags = ["a", "br", "font", "img", "pre", "span"]
        for tag in re.findall(r"<([^\s>/]+)", self._buffer):
            if tag.lower() not in allowed_tags:
                self._logger.warning(
                    f"Found disallowed tag: {tag}\n{self._buffer}\n---\n",
                )

        # Final buffer cleanup
        self._buffer = self._buffer.removeprefix("\n").replace("\n", "<br/>")

        self._logger.debug(f"Parse after: {repr(self._buffer)}")

        # If all we have is a prompt, don't display it
        if self._buffer:
            self.update_window.emit("main", self._buffer)

        end_time = time.perf_counter()
        exec_time = (end_time - start_time) * 1000

        self._logger.debug(f"execution time: {exec_time}")

        self._buffer = ""

        if remaining:
            self.parse(remaining)


class MindState:
    _mapping = {
        "clear": 0,
        "dabbling": 1,
        "perusing": 2,
        "learning": 3,
        "thoughtful": 4,
        "thinking": 5,
        "considering": 6,
        "pondering": 7,
        "ruminating": 8,
        "concentrating": 9,
        "attentive": 10,
        "deliberative": 11,
        "interested": 12,
        "examining": 13,
        "understanding": 14,
        "absorbing": 15,
        "intrigued": 16,
        "scrutinizing": 17,
        "analyzing": 18,
        "studious": 19,
        "focused": 20,
        "very focused": 21,
        "engaged": 22,
        "very engaged": 23,
        "cogitating": 24,
        "fascinated": 25,
        "captivated": 26,
        "engrossed": 27,
        "riveted": 28,
        "very riveted": 29,
        "rapt": 30,
        "very rapt": 31,
        "enthralled": 32,
        "nearly locked": 33,
        "mind lock": 34,
    }

    @classmethod
    def to_int(cls, key: Union[str, int]) -> int:
        key = str(key)
        if key in cls._mapping:
            return cls._mapping[key]

        try:
            key = int(key)
        except ValueError:
            return 0
        if 0 <= key <= 34:
            return key

        return 0
