#!/usr/bin/env python3

import html
import logging
import re
import sys
import traceback
import types
from datetime import UTC, datetime

from PyQt6.QtCore import (
    QEvent,
    QSize,
    Qt,
    QTimer,
)
from PyQt6.QtGui import (
    QAction,
    QFont,
    QKeyEvent,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplashScreen,
    QVBoxLayout,
    QWidget,
)

from command import CommandParser
from config import Config
from game import (
    EAccessClient,
    GameClient,
    GameParser,
)
from icons import (
    ICONS_DIR,
    Icons,
)
from layout import LayoutConfig
from utils import traced
from variables import Variables
from widgets import (
    QCompass,
    QCustomTextEdit,
    QCustomTimer,
    QCustomToolBar,
    QHistoryLineEdit,
    QIndicators,
    QMiniVital,
    QTimerBar,
)


class MainWindow(QMainWindow):
    @traced(show_args=False)
    def __init__(self) -> None:
        super().__init__()

        self._logger = logging.getLogger(self.__class__.__name__)

        self._config = Config()
        self._variables = Variables()
        self._window: MainWindow = self

        self.setContentsMargins(6, 6, 6, 6)
        self.update_style()

        self.timer = QCustomTimer()
        self.timer.connect(self.timerbars_callback)
        self.timer.start()

        self.eaccess_client = EAccessClient()
        self.eaccess_client.connected.connect(self._on_eaccess_connected)
        self.eaccess_client.disconnected.connect(self._on_eaccess_disconnected)
        self.eaccess_client.message_received.connect(self._on_eaccess_message_received)
        self.eaccess_client.start()

        self.game_parser = GameParser(self._window)
        self.game_parser.clear_window.connect(self._on_clear_window)
        self.game_parser.update_casttime.connect(self._on_update_casttime)
        self.game_parser.update_compass.connect(self._on_update_compass)
        self.game_parser.update_indicators.connect(self._on_update_indicators)
        self.game_parser.update_minivitals.connect(self._on_update_minivitals)
        self.game_parser.update_roundtime.connect(self._on_update_roundtime)
        self.game_parser.update_window.connect(self._on_update_window)

        self.game_client = GameClient()
        self.game_client.connected.connect(self._on_game_connected)
        self.game_client.disconnected.connect(self._on_game_disconnected)
        self.game_client.message_received.connect(self._on_game_message_received)
        self.game_client.start()

        self.command = CommandParser(self._window)

        client_name = self._config.get("client", "client.name", "Pivuh")
        client_version = self._config.get("client", "client.version", "(dev)")

        # Main window components
        main_label = QLabel("Story")

        self.main = QCustomTextEdit("main")
        self.main.setAccessibleDescription("Story Window")
        self.main.setObjectName("Story")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(3, 1, 3, 3)
        main_layout.setSpacing(1)
        main_layout.addWidget(main_label)
        main_layout.addWidget(self.main)

        main_frame = QFrame()
        main_frame.setFrameShape(QFrame.Shape.NoFrame)
        main_frame.setLayout(main_layout)

        # Toolbars: Script toolbar
        self.script_toolbar = QCustomToolBar()
        self.script_toolbar.setAccessibleDescription("Scripts Toolbar")
        self.script_toolbar.setObjectName("ScriptsToolBar")
        self.script_toolbar.setWindowTitle("Scripts")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.script_toolbar)

        # Toolbars: Input toolbar
        self.input = QHistoryLineEdit()
        self.input.setFrame(False)

        self.roundtime = QTimerBar(QTimerBar.TimerBarType.RoundTime)

        self.casttime = QTimerBar(QTimerBar.TimerBarType.CastTime)

        input_toolbar_layout = QVBoxLayout()
        input_toolbar_layout.setContentsMargins(0, 0, 0, 0)
        input_toolbar_layout.setSpacing(0)
        input_toolbar_layout.addWidget(self.input)
        input_toolbar_layout.addWidget(self.roundtime)
        input_toolbar_layout.addWidget(self.casttime)

        input_toolbar_widget = QFrame()
        input_toolbar_widget.setContentsMargins(1, 1, 1, 1)
        input_toolbar_widget.setFrameShape(QFrame.Shape.StyledPanel)
        input_toolbar_widget.setLayout(input_toolbar_layout)

        self.input_toolbar = QCustomToolBar()
        self.input_toolbar.setAccessibleDescription("Input Toolbar")
        self.input_toolbar.setObjectName("InputToolBar")
        self.input_toolbar.setWindowTitle("Input")
        self.input_toolbar.addWidget(input_toolbar_widget)

        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.input_toolbar)

        # Toolbars: Compass toolbar
        self.compass = QCompass()

        compass_toolbar_layout = QHBoxLayout()
        compass_toolbar_layout.addWidget(self.compass)
        compass_toolbar_layout.setContentsMargins(0, 0, 0, 0)
        compass_toolbar_layout.setStretch(0, 0)

        compass_toolbar_widget = QFrame()
        compass_toolbar_widget.setFrameShape(QFrame.Shape.NoFrame)
        compass_toolbar_widget.setLayout(compass_toolbar_layout)
        compass_toolbar_widget.setStyleSheet("padding: 0px; margin: 0px;")

        self.compass_toolbar = QCustomToolBar()
        self.compass_toolbar.setAccessibleDescription("Compass Toolbar")
        self.compass_toolbar.setObjectName("CompassToolBar")
        self.compass_toolbar.setWindowTitle("Compass")
        self.compass_toolbar.addWidget(compass_toolbar_widget)
        self.compass_toolbar.setStyleSheet("padding: 0px; margin: 0px; border: none;")

        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.compass_toolbar)

        # Toolbars: Indicators toolbar
        self.indicators = QIndicators()

        indicators_toolbar_layout = QHBoxLayout()
        indicators_toolbar_layout.addWidget(self.indicators)
        indicators_toolbar_layout.setStretch(0, 0)

        indicators_toolbar_widget = QFrame()
        indicators_toolbar_widget.setFrameShape(QFrame.Shape.NoFrame)
        indicators_toolbar_widget.setLayout(indicators_toolbar_layout)
        indicators_toolbar_widget.setStyleSheet("padding: 0px; margin: 0px;")

        self.indicators_toolbar = QCustomToolBar()
        self.indicators_toolbar.setAccessibleDescription("Indicators Toolbar")
        self.indicators_toolbar.setObjectName("IndicatorsToolBar")
        self.indicators_toolbar.setWindowTitle("Indicators")
        self.indicators_toolbar.addWidget(indicators_toolbar_widget)
        self.indicators_toolbar.setStyleSheet(
            "padding: 0px; margin: 0px; border: none;",
        )

        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.indicators_toolbar)

        # Toolbars: Hands toolbar
        left_icon = QLabel()
        left_icon.setPixmap(Icons().LeftIcon.pixmap(QSize(28, 28)))
        left_icon.setMaximumWidth(28)

        self.left = QLabel()
        self.left.setText("Empty")
        self.left.setMinimumWidth(150)

        right_icon = QLabel()
        right_icon.setPixmap(Icons().RightIcon.pixmap(QSize(28, 28)))
        right_icon.setMaximumWidth(28)

        self.right = QLabel()
        self.right.setText("Empty")
        self.right.setMinimumWidth(150)

        spell_icon = QLabel()
        spell_icon.setPixmap(Icons().SpellIcon.pixmap(QSize(28, 28)))
        spell_icon.setMaximumWidth(28)

        self.spell = QLabel()
        self.spell.setText("None")
        self.spell.setMinimumWidth(150)

        hands_toolbar_layout = QHBoxLayout()
        hands_toolbar_layout.addWidget(left_icon)
        hands_toolbar_layout.addWidget(self.left)
        hands_toolbar_layout.addWidget(right_icon)
        hands_toolbar_layout.addWidget(self.right)
        hands_toolbar_layout.addWidget(spell_icon)
        hands_toolbar_layout.addWidget(self.spell)
        hands_toolbar_layout.setStretch(0, 1)

        hands_toolbar_widget = QFrame()
        hands_toolbar_widget.setContentsMargins(1, 1, 1, 1)
        hands_toolbar_widget.setFrameShape(QFrame.Shape.NoFrame)
        hands_toolbar_widget.setLayout(hands_toolbar_layout)

        self.hands_toolbar = QCustomToolBar()
        self.hands_toolbar.setAccessibleDescription("Hands Toolbar")
        self.hands_toolbar.setObjectName("HandsToolBar")
        self.hands_toolbar.setWindowTitle("Hands")
        self.hands_toolbar.addWidget(hands_toolbar_widget)

        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.hands_toolbar)

        # Toolbars: Minivitals toolbar
        self.minivitals = {}
        self.minivitals["health"] = QMiniVital("health", 0, "Health 0%")
        self.minivitals["health"].setFormat("Health 0%")
        self.minivitals["health"].setValue(0)

        self.minivitals_toolbar = QCustomToolBar()
        self.minivitals_toolbar.setAccessibleDescription("Vitals Toolbar")
        self.minivitals_toolbar.setObjectName("MiniVitalsToolBar")
        self.minivitals_toolbar.setWindowTitle("Vitals")
        self.minivitals_toolbar.addWidget(self.minivitals["health"])
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.minivitals_toolbar)

        # Status Bar
        self.status_label = []
        while len(self.status_label) < 5:  # noqa: PLR2004
            self.status_label.append(QLabel())
        self.status_label[0].setText("Disconnected")

        self.status_bar = self.statusBar()
        if self.status_bar:
            for status_label in self.status_label:
                self.status_bar.addWidget(status_label)

        # "Windows" aka Dock Widgets
        self.windows = {}
        for window_id in self._config.items("windows"):
            settings = self._config.get("windows", window_id, {})
            if window_id not in self.windows:
                self.windows[window_id] = settings
                if window_id == "main":
                    self._variables.set("widgets", window_id, self.main)
                else:
                    self._variables.set(
                        "widgets",
                        window_id,
                        QCustomTextEdit(window_id),
                    )

                    title = settings.get("title", "Unknown")
                    dock_widget = QDockWidget(title, self)
                    dock_widget.setAccessibleDescription(f"{title} Window")
                    dock_widget.setContentsMargins(3, 3, 3, 3)
                    dock_widget.setObjectName(window_id)
                    dock_widget.setWidget(self._variables.get("widgets", window_id))
                    self.addDockWidget(
                        Qt.DockWidgetArea.RightDockWidgetArea,
                        dock_widget,
                    )

                    if not settings.get("default_open", True):
                        dock_widget.hide()

        self.setDockNestingEnabled(True)

        # Menu Bar
        menu = self.menuBar()
        if menu is not None:
            file_exit_action = QAction("&Exit", self)
            file_exit_action.setCheckable(False)
            file_exit_action.triggered.connect(self.close)

            self.file_menu = menu.addMenu("&File")
            if self.file_menu is not None:
                self.file_menu.addAction(file_exit_action)

            edit_unlock_toolbars_action = QAction("&Unlock Toolbars", self)
            edit_unlock_toolbars_action.setCheckable(True)
            edit_unlock_toolbars_action.triggered.connect(self.unlock_toolbars)

            self.edit_menu = menu.addMenu("&Edit")
            if self.edit_menu is not None:
                self.edit_menu.addAction(edit_unlock_toolbars_action)

        # Finish main window components
        self.setCentralWidget(main_frame)

        _layout = LayoutConfig()
        _geometry, _state = _layout.load()
        if _geometry:
            self.restoreGeometry(_geometry)
        if _state:
            self.restoreState(_state)

        self.setWindowTitle(f"[Disconnected] - {client_name} v{client_version}")

        self.main.insertHtml(f"{client_name} v{client_version}", ignore_visibility=True)

        # Pre-build lookup dicts so signal handlers don't rebuild them on every call
        self._direction_mapping = {
            "n": self.compass.CompassFlag.North,
            "ne": self.compass.CompassFlag.NorthEast,
            "e": self.compass.CompassFlag.East,
            "se": self.compass.CompassFlag.SouthEast,
            "s": self.compass.CompassFlag.South,
            "sw": self.compass.CompassFlag.SouthWest,
            "w": self.compass.CompassFlag.West,
            "nw": self.compass.CompassFlag.NorthWest,
            "out": self.compass.CompassFlag.Out,
            "up": self.compass.CompassFlag.Up,
            "down": self.compass.CompassFlag.Down,
        }
        self._indicators_mapping = {
            "IconBLEEDING": self.indicators.IndicatorsFlag.Bleeding,
            "IconDEAD": self.indicators.IndicatorsFlag.Dead,
            "IconKNEELING": self.indicators.IndicatorsFlag.Kneeling,
            "IconHIDDEN": self.indicators.IndicatorsFlag.Hidden,
            "IconINVISIBLE": self.indicators.IndicatorsFlag.Invisible,
            "IconJOINED": self.indicators.IndicatorsFlag.Joined,
            "IconPRONE": self.indicators.IndicatorsFlag.Prone,
            "IconSITTING": self.indicators.IndicatorsFlag.Sitting,
            "IconSTANDING": self.indicators.IndicatorsFlag.Standing,
            "IconSTUNNED": self.indicators.IndicatorsFlag.Stunned,
            "IconWEBBED": self.indicators.IndicatorsFlag.Webbed,
        }

        self.input.setFocus()

    def closeEvent(self, a0: QEvent | None) -> None:  # noqa: N802
        if not a0:
            return

        self.eaccess_client.do_disconnect()
        self.game_client.do_disconnect()
        self.eaccess_client.quit()
        self.eaccess_client.wait()
        self.game_client.quit()
        self.game_client.wait()
        a0.accept()

    def keyPressEvent(self, a0: QKeyEvent | None) -> None:  # noqa: N802
        if not a0:
            return

        k = a0.key()
        m = a0.modifiers()

        if (
            k in (Qt.Key.Key_Plus, Qt.Key.Key_Equal)
            and m & Qt.KeyboardModifier.ControlModifier
        ):
            self._scale_font(1)
        elif (
            k in (Qt.Key.Key_Minus, Qt.Key.Key_Underscore)
            and m & Qt.KeyboardModifier.ControlModifier
        ):
            self._scale_font(-1)
        elif k in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            text = self.input.text()
            if text != "":
                self.input.add_to_history(text)
                self.command.parse(text)
            self.input.clear()

        if not self.input.hasFocus():
            self.input.keyPressEvent(a0)

    def keyReleaseEvent(self, a0: QKeyEvent | None) -> None:  # noqa: N802
        if not a0:
            return

        k = a0.key()

        if k != Qt.Key.Key_Control:
            # Don't setFocus() if only the Ctrl key is pressed
            # Interferes with copying text from QTextEdit widgets
            self.input.setFocus()

        if not self.input.hasFocus():
            # Echo the key press event to the input box
            self.input.keyReleaseEvent(a0)

    @traced(show_args=False)
    def reset_compass(self) -> None:
        self._on_update_compass([])

    @traced(show_args=False)
    def reset_indicators(self) -> None:
        self._on_update_indicators([])

    @traced(show_args=False)
    def reset_minivitals(self) -> None:
        self.minivitals_toolbar.clear()
        self.minivitals = {}
        self.minivitals["health"] = QMiniVital("health", 0, "Health 0%")
        self.minivitals_toolbar.addWidget(self.minivitals["health"])

    def timerbars_callback(self) -> None:
        self.casttime.do_update()
        self.roundtime.do_update()

    @traced(show_args=True)
    def unlock_toolbars(self, checked: bool) -> None:
        self.compass_toolbar.setMovable(checked)
        self.hands_toolbar.setMovable(checked)
        self.indicators_toolbar.setMovable(checked)
        self.input_toolbar.setMovable(checked)
        self.minivitals_toolbar.setMovable(checked)
        self.script_toolbar.setMovable(checked)

    @traced(show_args=False)
    def update_style(self) -> None:
        fontname = self._config.get("presets", "ui.fontname")
        fontsize = self._config.get("presets", "ui.fontsize")
        font = QFont()
        font.setFamily(fontname)
        font.setPointSize(int(fontsize.replace("pt", "")))
        self.setFont(font)

    @traced(show_args=True)
    def _apply_gags(self, message: str) -> str:
        """Remove <br/>-delimited lines matching any gag rule from message."""
        gags = self._config.get("gags", "rules", [])

        if not gags:
            return message

        compiled_patterns: list[re.Pattern] = []
        for g in gags:
            pattern = g.get("pattern", "")
            if not pattern:
                continue
            try:
                compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
            except re.error:
                continue

        if not compiled_patterns:
            return message

        def apply_gags_to_seg(html_seg: str) -> str:
            """Remove matched spans from a single <br/>-delimited segment."""
            # Split into html-tag tokens and plain-text tokens so we only
            # strip the matched text, leaving surrounding text and tags intact.
            tokens = re.split(r"(<[^>]+>)", html_seg)
            for p in compiled_patterns:
                new_tokens: list[str] = []
                for t in tokens:
                    if t.startswith("<"):
                        new_tokens.append(t)
                    else:
                        new_tokens.append(p.sub("", t))
                tokens = new_tokens
            return "".join(tokens)

        # Split on <br/> keeping delimiters
        parts = re.split(r"(<br/>)", message)

        result: list[str] = []
        i = 0

        # Initial text before the first <br/>
        if parts and parts[0] != "<br/>":
            result.append(apply_gags_to_seg(parts[0]))
            i = 1

        # Process <br/> + following-text pairs together
        while i < len(parts):
            br = parts[i]
            text = parts[i + 1] if i + 1 < len(parts) else ""
            if br == "<br/>":
                result.append(br)
                result.append(apply_gags_to_seg(text))
                i += 2
            else:
                result.append(br)
                i += 1

        return "".join(result).replace("<br/><br/>", "<br/>")

    @traced(show_args=True)
    def _apply_highlights(self, message: str) -> str:
        """Apply regex-based highlight rules to a message's text content."""
        highlights = self._config.get("highlights", "rules", [])

        if not highlights:
            return message

        for h in highlights:
            pattern = h.get("pattern", "")
            color = h.get("color", "")
            bgcolor = h.get("bgcolor", "")
            if not pattern:
                continue
            style_parts: list[str] = []
            if color:
                style_parts.append(f"color: {color};")
            if bgcolor:
                style_parts.append(f"background-color: {bgcolor};")
            if not style_parts:
                continue
            style = " ".join(style_parts)
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
            except re.error:
                continue

            # Split on HTML tags so we only replace inside text parts
            parts = re.split(r"(<[^>]+>)", message)
            result: list[str] = []
            for part in parts:
                if part.startswith("<"):
                    result.append(part)
                else:
                    result.append(
                        compiled.sub(
                            lambda m, s=style: f'<span style="{s}">{m.group()}</span>',
                            part,
                        ),
                    )

            message = "".join(result)
        return message

    @traced(show_args=True)
    def _apply_subs(self, message: str) -> str:
        """Replace text matching any substitution rule's pattern with its replacement."""
        subs = self._config.get("subs", "rules", [])

        if not subs:
            return message

        compiled: list[tuple[re.Pattern, str]] = []
        for s in subs:
            pattern = s.get("pattern", "")
            replacement = s.get("replacement", "")
            if not pattern:
                continue
            try:
                compiled.append((re.compile(pattern, re.IGNORECASE), replacement))
            except re.error:
                continue

        if not compiled:
            return message

        def apply_subs_to_seg(html_seg: str) -> str:
            tokens = re.split(r"(<[^>]+>)", html_seg)
            for p, repl in compiled:
                new_tokens: list[str] = []
                for t in tokens:
                    if t.startswith("<"):
                        new_tokens.append(t)
                    else:
                        new_tokens.append(p.sub(repl, t))
                tokens = new_tokens
            return "".join(tokens)

        parts = re.split(r"(<br/>)", message)
        result: list[str] = []
        i = 0

        if parts and parts[0] != "<br/>":
            result.append(apply_subs_to_seg(parts[0]))
            i = 1

        while i < len(parts):
            br = parts[i]
            text = parts[i + 1] if i + 1 < len(parts) else ""
            if br == "<br/>":
                result.append(br)
                result.append(apply_subs_to_seg(text))
                i += 2
            else:
                result.append(br)
                i += 1

        return "".join(result)

    @traced(show_args=True)
    def _on_clear_window(self, window: str) -> None:
        if window not in self.windows:
            return
        widget = self._variables.get("widgets", window, None)
        if widget:
            widget.setHtml("")

    @traced(show_args=False)
    def _on_eaccess_connected(self, message: str) -> None:
        if message:
            self.main.insertHtml(f"<br/>{message}")

    @traced(show_args=False)
    def _on_eaccess_disconnected(self, message: str) -> None:
        if message:
            self.main.insertHtml(f"<br/>{message}")

    @traced(show_args=False)
    def _on_eaccess_message_received(self, message: str) -> None:
        if message:
            self.main.insertHtml(f"<br/>{message}")

    @traced(show_args=False)
    def _on_game_connected(self, message: str) -> None:
        if message:
            self.main.insertHtml(f"<br/>{message}")

        character = self._variables.get("temporary", "character", "")
        instance = self._variables.get("temporary", "instance", "")
        client_name = self._config.get("client", "client.name", "Pivuh")
        client_version = self._config.get("client", "client.version", "(dev)")
        self.setWindowTitle(
            f"{instance}: {character} [Connected] - {client_name} v{client_version}",
        )

        self.status_label[0].setText("Connected")

    @traced(show_args=False)
    def _on_game_disconnected(self, message: str) -> None:
        if message:
            self.main.insertHtml(f"<br/>{message}")

        client_name = self._config.get("client", "client.name", "Pivuh")
        client_version = self._config.get("client", "client.version", "(dev)")
        self.setWindowTitle(f"[Disconnected] - {client_name} v{client_version}")

        self.status_label[0].setText("Disconnected")

        self.reset_compass()
        self.reset_indicators()
        self.reset_minivitals()

    @traced(show_args=False)
    def _on_game_message_received(self, message: str) -> None:
        widget = self._variables.get("widgets", "raw", None)
        if widget:
            widget.insertHtml(f"{html.escape(message)}<br/>")
        self.game_parser.parse(message)

    @traced(show_args=True)
    def _on_update_casttime(self, timestamp: int) -> None:
        self.casttime.start(timestamp)

    @traced(show_args=True)
    def _on_update_compass(self, directions: list) -> None:
        direction_flags = self.compass.CompassFlag(0)
        for direction in directions:
            if direction in self._direction_mapping:
                direction_flags |= self._direction_mapping[direction]
            else:
                self._logger.error(
                    "_on_update_compass: Invalid compass direction: %s", direction
                )
        self.compass.update_compass(direction_flags)

    @traced(show_args=True)
    def _on_update_indicators(self, indicators: list) -> None:
        indicators_flags = self.indicators.IndicatorsFlag(0)
        for indicator in indicators:
            if indicator in self._indicators_mapping:
                indicators_flags |= self._indicators_mapping[indicator]
            else:
                self._logger.error(
                    "_on_update_indicators: Invalid indicator: %s", indicator
                )
        self.indicators.update_indicators(indicators_flags)

    @traced(show_args=True)
    def _on_update_minivitals(self, minivital_id: str, value: int, text: str) -> None:
        if minivital_id not in self.minivitals:
            self.minivitals[minivital_id] = QMiniVital(minivital_id, value, text)
            self.minivitals_toolbar.addWidget(self.minivitals[minivital_id])
        else:
            self.minivitals[minivital_id].do_update(value, text)

    @traced(show_args=True)
    def _on_update_roundtime(self, seconds: int) -> None:
        self.roundtime.start(seconds)

    @traced(show_args=True)
    def _on_update_window(self, window: str, message: str) -> None:
        if window not in self.windows:
            return

        # Follow the if_closed chain until we find a visible widget
        target = window
        visited: set = set()
        while target and target not in visited:
            visited.add(target)
            widget = self._variables.get("widgets", target, None)
            if widget and widget.isVisible():
                # Apply timestamp based on the target window's setting
                if target in self.windows and self.windows[target].get(
                    "timestamp",
                    False,
                ):
                    timestamp = datetime.now(tz=UTC).strftime("[%H:%M]")
                    message = f"{timestamp}&nbsp;{message}"

                # Fix line breaks based on the target window
                if (
                    target == "main"
                    and not message.startswith("<br/>")
                    and not message.startswith("<pre")
                ):
                    message = f"<br/>{message}"
                elif target != "main" and not message.endswith("<br/>"):
                    message = f"{message}<br/>"

                # Add the current prompt to main window messages
                if target == "main":
                    prompt = self._variables.get("temporary", "prompt", "&gt;")
                    if not message.endswith(prompt):
                        message = f"{message}{prompt}"

                # Apply gags, subs, highlights
                message = self._apply_gags(message)
                if not message:
                    return
                message = self._apply_subs(message)
                message = self._apply_highlights(message)

                widget.insertHtml(message, ignore_visibility=True)
                return
            if target not in self.windows:
                break
            if_closed = self.windows[target].get("if_closed", None)
            if not if_closed:
                break
            target = if_closed

    @traced(show_args=True)
    def _scale_font(self, point_size: int) -> None:
        family = self.font().family()
        size = self.font().pointSize()

        font = QFont()
        font.setFamily(family)
        font.setPointSize(size + point_size)
        self.setFont(font)

        for widget in self.findChildren(QWidget):
            widget_family = widget.font().family()
            widget_size = widget.font().pointSize()

            widget_font = QFont()
            widget_font.setFamily(widget_family)
            widget_font.setPointSize(widget_size + point_size)
            widget.setFont(widget_font)


def _show_splash_screen() -> QSplashScreen:
    splash_pixmap = QPixmap(str(ICONS_DIR / "pivuh.png"))

    splash = QSplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()

    QTimer.singleShot(2000, splash.close)
    return splash


def _exception_hook(
    exc_type: type, exc_value: BaseException, exc_traceback: types.TracebackType | None
) -> None:
    """Show a dialog for unhandled exceptions instead of crashing."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.getLogger(__name__).error("Unhandled exception:\n%s", tb_str)

    dialog = QMessageBox()
    dialog.setIcon(QMessageBox.Icon.Critical)
    dialog.setWindowTitle("Unhandled Exception")
    dialog.setText(f"An unexpected error occurred:\n\n{exc_value}")
    dialog.setDetailedText(tb_str)
    dialog.setStandardButtons(
        QMessageBox.StandardButton.Close | QMessageBox.StandardButton.Ignore
    )
    dialog.setDefaultButton(QMessageBox.StandardButton.Ignore)
    result = dialog.exec()
    if result == QMessageBox.StandardButton.Close:
        sys.exit(1)


if __name__ == "__main__":
    # Set up logging
    config = Config()
    log_level = config.get("client", "logging.log_level")
    formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s: %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(handler)

    # Set up PyQt application
    app = QApplication(sys.argv)
    app.setStyle("fusion")

    # Show splash screen
    splash = _show_splash_screen()

    # Set up application main window
    w = MainWindow()
    w.show()

    # Show a dialog instead of crashing on unhandled exceptions
    sys.excepthook = _exception_hook

    # Let's go!
    app.setWindowIcon(Icons().AppIcon)
    app.exec()
