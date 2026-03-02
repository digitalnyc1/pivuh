#!/usr/bin/env python3

import html
import logging
import os
import sys
import time

from PyQt6.QtCore import (
    Qt,
    QEvent,
    QSize,
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
    QSplashScreen,
    QVBoxLayout,
)
from datetime import datetime
from logging import LogRecord
from typing import Any

from config import Config
from command import CommandParser
from game import (
    EAccessClient,
    GameClient,
    GameParser,
)
from icons import (
    Icons,
    ICONS_DIR,
)
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
    def __init__(self) -> None:
        super().__init__()

        self._logger = logging.getLogger(self.__class__.__name__)

        self._config = Config()
        self._variables = Variables()

        self._variables.set("internal", "main_window", self)

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

        self.game_parser = GameParser()
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

        self.command = CommandParser()

        client_name = self._config.get("client", "name", "Pivuh")
        client_version = self._config.get("client", "version", "(dev)")

        # Main window components
        main_label = QLabel("Story")

        self.main = QCustomTextEdit("main")
        self.main.setAccessibleDescription("Story Window")
        self.main.setObjectName("Story")

        self.debug = QCustomTextEdit("debug")
        self.debug.setAccessibleDescription("Debug Window")
        self.debug.setObjectName("Debug")

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
        self.indicators_toolbar.setStyleSheet("padding: 0px; margin: 0px; border: none;")

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
        while len(self.status_label) < 5:
            self.status_label.append(QLabel())
        self.status_label[0].setText("Disconnected")

        self.status_bar = self.statusBar()
        for status_label in self.status_label:
            self.status_bar.addWidget(status_label)

        # "Windows" aka Dock Widgets
        self.windows = {}
        for id, settings in self._config.get("windows", "settings", {}).items():
            if id not in self.windows:
                self.windows[id] = settings
                if id == "main":
                    self.windows[id]["widget"] = self.main
                elif id == "debug":
                    self.windows[id]["widget"] = self.debug
                else:
                    self.windows[id]["widget"] = QCustomTextEdit(id)

                    title = settings.get("title", "Unknown")
                    dock_widget = QDockWidget(title, self)
                    dock_widget.setAccessibleDescription(f"{title} Window")
                    dock_widget.setContentsMargins(3,3,3,3)
                    dock_widget.setObjectName(id)
                    dock_widget.setWidget(self.windows[id]["widget"])
                    self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_widget)

                    if not settings.get("default_open", True):
                        dock_widget.hide()

        self.setDockNestingEnabled(True)

        # Menu Bar
        menu = self.menuBar()

        file_exit_action = QAction("&Exit", self)
        file_exit_action.setCheckable(False)
        file_exit_action.triggered.connect(self.close)

        self.file_menu = menu.addMenu("&File")
        self.file_menu.addAction(file_exit_action)

        edit_unlock_toolbars_action = QAction("&Unlock Toolbars", self)
        edit_unlock_toolbars_action.setCheckable(True)
        edit_unlock_toolbars_action.triggered.connect(self._on_unlock_toolbars)

        self.edit_menu = menu.addMenu("&Edit")
        self.edit_menu.addAction(edit_unlock_toolbars_action)

        # Finish main window components
        self.setCentralWidget(main_frame)

        self.restoreState(self._config.get("client", "state", b""))

        self.setWindowTitle(f"[Disconnected] - {client_name} v{client_version}")

        self.main.insertHtml(f"{client_name} v{client_version}", ignore_visiblity=True)

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
            "IconINVISIBLE": self.indicators.IndicatorsFlag.Invivisble,
            "IconJOINED": self.indicators.IndicatorsFlag.Joined,
            "IconPRONE": self.indicators.IndicatorsFlag.Prone,
            "IconSITTING": self.indicators.IndicatorsFlag.Sitting,
            "IconSTANDING": self.indicators.IndicatorsFlag.Standing,
            "IconSTUNNED": self.indicators.IndicatorsFlag.Stunned,
            "IconWEBBED": self.indicators.IndicatorsFlag.Webbed,
        }

        self.input.setFocus()

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        k = event.key()

        if k != Qt.Key.Key_Control:
            # Don't setFocus() if only the Ctrl key is pressed
            # Interferes with copying text from QTextEdit widgets
            self.input.setFocus()

        if not self.input.hasFocus():
            # Echo the key press event to the input box
            self.input.keyReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        k = event.key()

        if k in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            # Key Press: Enter
            text = self.input.text()
            if text != "":
                self.input.add_to_history(text)
                self.command.Parse(text)
            self.input.clear()

        if not self.input.hasFocus():
            # Echo the key press event to the input box
            self.input.keyPressEvent(event)

    def closeEvent(self, event: QEvent) -> None:
        self.eaccess_client.disconnect()
        self.game_client.disconnect()
        time.sleep(1)
        event.accept()

    def _on_eaccess_connected(self, message: str) -> None:
        if message:
            self.main.insertHtml(f"<br/>{message}")

    def _on_eaccess_disconnected(self, message: str) -> None:
        if message:
            self.main.insertHtml(f"<br/>{message}")

    def _on_eaccess_message_received(self, message: str) -> None:
        if message:
            self.main.insertHtml(f"<br/>{message}")

    def _on_game_connected(self, message: str) -> None:
        if message:
            self.main.insertHtml(f"<br/>{message}")

        character = self._variables.get("temporary", "character", "")
        instance = self._variables.get("temporary", "instance", "")
        client_name = self._config.get("client", "name", "Pivuh")
        client_version = self._config.get("client", "version", "(dev)")
        self.setWindowTitle(f"{instance}: {character} [Connected] - {client_name} v{client_version}")

        self.status_label[0].setText("Connected")

    def _on_game_disconnected(self, message: str) -> None:
        if message:
            self.main.insertHtml(f"<br/>{message}")

        client_name = self._config.get("client", "name", "Pivuh")
        client_version = self._config.get("client", "version", "(dev)")
        self.setWindowTitle(f"[Disconnected] - {client_name} v{client_version}")

        self.status_label[0].setText("Disconnected")

        self.reset_compass()
        self.reset_minivitals()

    def _on_game_message_received(self, message: str) -> None:
        self.windows["raw"]["widget"].insertHtml(f"{repr(html.escape(message))}<br/>")
        self.game_parser.Parse(message)

    def _on_clear_window(self, window: str) -> None:
        if window not in self.windows:
            return
        self._logger.debug(f"_on_clear_window: window({window})")
        self.windows[window]["widget"].setHtml("")

    def _on_update_casttime(self, timestamp: int) -> None:
        self._logger.debug(f"_on_update_casttime: timestamp({timestamp})")
        self.casttime.start(timestamp)

    def _on_update_compass(self, directions: list) -> None:
        self._logger.debug(f"_on_update_compass: directions({directions})")
        direction_flags = 0
        for direction in directions:
            if direction in self._direction_mapping:
                direction_flags |= self._direction_mapping[direction]
            else:
                self._logger.error(f"_on_update_compass: Invalid compass direction: {direction}")
        self.compass.update_compass(direction_flags)

    def _on_update_indicators(self, indicators: list) -> None:
        self._logger.debug(f"_on_update_indicators: indicators({indicators})")
        indicators_flags = 0
        for indicator in indicators:
            if indicator in self._indicators_mapping:
                indicators_flags |= self._indicators_mapping[indicator]
            else:
                self._logger.error(f"_on_update_indicators: Invalid indicator: {indicator}")
        self.indicators.update_indicators(indicators_flags)

    def _on_update_minivitals(self, id: str, value: str, text: str) -> None:
        self._logger.debug(f"_on_update_minivitals: id({id}) value({value}) text({text})")
        if id not in self.minivitals:
            self.minivitals[id] = QMiniVital(id, value, text)
            self.minivitals_toolbar.addWidget(self.minivitals[id])
        else:
            self.minivitals[id].update(value, text)

    def _on_update_roundtime(self, seconds: int) -> None:
        self._logger.debug(f"_on_update_roundtime: seconds({seconds})")
        self.roundtime.start(seconds)

    def _on_update_window(self, window: str, message: str) -> None:
        if window not in self.windows:
            return

        if self.windows[window].get("timestamp", False):
            timestamp = datetime.now().strftime("[%H:%M]&nbsp;")
            message = f"{timestamp}{message}"

        if window == "main":
            message = f"<br/>{message}"

        message = message.replace("<br/><pre", "<pre")

        self._logger.debug(f"_on_update_window: window({window}) message({message})")
        self.windows[window]["widget"].insertHtml(message)

    def _on_unlock_toolbars(self, checked) -> None:
        self._logger.debug(f"_on_unlock_toolbars")
        self.compass_toolbar.setMovable(checked)
        self.hands_toolbar.setMovable(checked)
        self.indicators_toolbar.setMovable(checked)
        self.input_toolbar.setMovable(checked)
        self.minivitals_toolbar.setMovable(checked)
        self.script_toolbar.setMovable(checked)

    def reset_compass(self) -> None:
        self._on_update_compass([])

    def reset_indicators(self) -> None:
        self._on_update_indicators([])

    def reset_minivitals(self) -> None:
        for id, minivital in self.minivitals.items():
            self._logger.debug(f"reset_minivitals: destory {id}")
            minivital.destroy()
        self.minivitals_toolbar.clear()
        self.minivitals = {}
        self.minivitals["health"] = QMiniVital("health", 0, "Health 0%")
        self.minivitals_toolbar.addWidget(self.minivitals["health"])

    def update_style(self) -> None:
        fontname = self._config.get("presets", "ui.fontname")
        fontsize = self._config.get("presets", "ui.fontsize")
        self._logger.debug(f"update_style: fontname({fontname}) fontsize({fontsize})")
        font = QFont()
        font.setFamily(fontname)
        font.setPointSize(int(fontsize.replace("pt", "")))
        self.setFont(font)

    def timerbars_callback(self):
        self.casttime.update()
        self.roundtime.update()


class DebugWindowHandler(logging.Handler):
    def __init__(self, window: Any):
        super().__init__()
        self._window = window

    def emit(self, record: LogRecord) -> None:
        try:
            msg = repr(html.escape(self.format(record)))
            self._window.windows["debug"]["widget"].insertHtml(f"{msg}<br/>")
        except Exception as e:
            self.handleError(record)


def _show_splash_screen() -> QSplashScreen:
    splash_pixmap = QPixmap(os.path.join(ICONS_DIR, "pivuh.png"))

    splash = QSplashScreen(splash_pixmap, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()

    QTimer.singleShot(2000, splash.close)
    return splash


if __name__ == "__main__":
    # Set up logging
    formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(name)s: %(message)s")
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    # Set up PyQt application
    app = QApplication(sys.argv)
    app.setStyle("fusion")

    # Show splash screen
    splash = _show_splash_screen()

    # Set up application main window
    w = MainWindow()
    w.show()

    # Set up debug window logging
    handler = DebugWindowHandler(w)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Let's go!
    app.setWindowIcon(Icons().AppIcon)
    app.exec()
