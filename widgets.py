import logging
from enum import Enum, IntFlag

from PyQt6.QtCore import (
    QObject,
    QSize,
    Qt,
    QTimer,
    QUrl,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QAction,
    QContextMenuEvent,
    QDesktopServices,
    QKeyEvent,
    QMouseEvent,
    QTextCursor,
    QTextOption,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QProgressBar,
    QSizePolicy,
    QTextEdit,
    QToolBar,
    QToolButton,
    QWidget,
)

from config import Config
from game import GameState
from icons import Icons
from variables import Variables


class QCompass(QWidget):
    class CompassFlag(IntFlag):
        North = 1
        NorthEast = 2
        East = 4
        SouthEast = 8
        South = 16
        SouthWest = 32
        West = 64
        NorthWest = 128
        Out = 256
        Up = 512
        Down = 1024

    def __init__(self) -> None:
        super().__init__()

        self._logger = logging.getLogger(self.__class__.__name__)

        self._config = Config()
        self._variables = Variables()

        self._window = self._variables.get("widgets", "main_window", None)

        icon_size = self._config.get("presets", "compass.iconsize", 16)

        self.north_active = QCompassButton(QCompass.CompassFlag.North)
        self.north_active.setAccessibleDescription("North (Active)")
        self.north_active.setContentsMargins(0, 0, 0, 0)
        self.north_active.setPixmap(
            Icons().NorthActiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )
        self.north_active.setVisible(False)
        self.north_active.clicked.connect(self._on_compass_button_click)

        self.north_inactive = QLabel()
        self.north_inactive.setAccessibleDescription("North (Inactive)")
        self.north_inactive.setContentsMargins(0, 0, 0, 0)
        self.north_inactive.setPixmap(
            Icons().NorthInactiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.northeast_active = QCompassButton(QCompass.CompassFlag.NorthEast)
        self.northeast_active.setAccessibleDescription("Northeast (Active)")
        self.northeast_active.setContentsMargins(0, 0, 0, 0)
        self.northeast_active.setPixmap(
            Icons().NorthEastActiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )
        self.northeast_active.setVisible(False)
        self.northeast_active.clicked.connect(self._on_compass_button_click)

        self.northeast_inactive = QLabel()
        self.northeast_inactive.setAccessibleDescription("Northeast (Inactive)")
        self.northeast_inactive.setContentsMargins(0, 0, 0, 0)
        self.northeast_inactive.setPixmap(
            Icons().NorthEastInactiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.east_active = QCompassButton(QCompass.CompassFlag.East)
        self.east_active.setAccessibleDescription("East (Active)")
        self.east_active.setContentsMargins(0, 0, 0, 0)
        self.east_active.setPixmap(
            Icons().EastActiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )
        self.east_active.setVisible(False)
        self.east_active.clicked.connect(self._on_compass_button_click)

        self.east_inactive = QLabel()
        self.east_inactive.setAccessibleDescription("East (Inactive)")
        self.east_inactive.setContentsMargins(0, 0, 0, 0)
        self.east_inactive.setPixmap(
            Icons().EastInactiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.southeast_active = QCompassButton(QCompass.CompassFlag.SouthEast)
        self.southeast_active.setAccessibleDescription("Southeast (Active)")
        self.southeast_active.setContentsMargins(0, 0, 0, 0)
        self.southeast_active.setPixmap(
            Icons().SouthEastActiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )
        self.southeast_active.setVisible(False)
        self.southeast_active.clicked.connect(self._on_compass_button_click)

        self.southeast_inactive = QLabel()
        self.southeast_inactive.setAccessibleDescription("Southeast (Inactive)")
        self.southeast_inactive.setContentsMargins(0, 0, 0, 0)
        self.southeast_inactive.setPixmap(
            Icons().SouthEastInactiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.south_active = QCompassButton(QCompass.CompassFlag.South)
        self.south_active.setAccessibleDescription("South (Active)")
        self.south_active.setContentsMargins(0, 0, 0, 0)
        self.south_active.setPixmap(
            Icons().SouthActiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )
        self.south_active.setVisible(False)
        self.south_active.clicked.connect(self._on_compass_button_click)

        self.south_inactive = QLabel()
        self.south_inactive.setAccessibleDescription("South (Inactive)")
        self.south_inactive.setContentsMargins(0, 0, 0, 0)
        self.south_inactive.setPixmap(
            Icons().SouthInactiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.southwest_active = QCompassButton(QCompass.CompassFlag.SouthWest)
        self.southwest_active.setAccessibleDescription("Southwest (Active)")
        self.southwest_active.setContentsMargins(0, 0, 0, 0)
        self.southwest_active.setPixmap(
            Icons().SouthWestActiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )
        self.southwest_active.setVisible(False)
        self.southwest_active.clicked.connect(self._on_compass_button_click)

        self.southwest_inactive = QLabel()
        self.southwest_inactive.setAccessibleDescription("Southwest (Inactive)")
        self.southwest_inactive.setContentsMargins(0, 0, 0, 0)
        self.southwest_inactive.setPixmap(
            Icons().SouthWestInactiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.west_active = QCompassButton(QCompass.CompassFlag.West)
        self.west_active.setAccessibleDescription("West (Active)")
        self.west_active.setContentsMargins(0, 0, 0, 0)
        self.west_active.setPixmap(
            Icons().WestActiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )
        self.west_active.setVisible(False)
        self.west_active.clicked.connect(self._on_compass_button_click)

        self.west_inactive = QLabel()
        self.west_inactive.setAccessibleDescription("West (Inactive)")
        self.west_inactive.setContentsMargins(0, 0, 0, 0)
        self.west_inactive.setPixmap(
            Icons().WestInactiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.northwest_active = QCompassButton(QCompass.CompassFlag.NorthWest)
        self.northwest_active.setAccessibleDescription("Northwest (Active)")
        self.northwest_active.setContentsMargins(0, 0, 0, 0)
        self.northwest_active.setPixmap(
            Icons().NorthWestActiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )
        self.northwest_active.setVisible(False)
        self.northwest_active.clicked.connect(self._on_compass_button_click)

        self.northwest_inactive = QLabel()
        self.northwest_inactive.setAccessibleDescription("Northwest (Inactive)")
        self.northwest_inactive.setContentsMargins(0, 0, 0, 0)
        self.northwest_inactive.setPixmap(
            Icons().NorthWestInactiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.out_active = QCompassButton(QCompass.CompassFlag.Out)
        self.out_active.setAccessibleDescription("Out (Active)")
        self.out_active.setContentsMargins(0, 0, 0, 0)
        self.out_active.setPixmap(
            Icons().OutActiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )
        self.out_active.setVisible(False)
        self.out_active.clicked.connect(self._on_compass_button_click)

        self.out_inactive = QLabel()
        self.out_inactive.setAccessibleDescription("Out (Inactive)")
        self.out_inactive.setContentsMargins(0, 0, 0, 0)
        self.out_inactive.setPixmap(
            Icons().OutInactiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.up_active = QCompassButton(QCompass.CompassFlag.Up)
        self.up_active.setAccessibleDescription("Up (Active)")
        self.up_active.setContentsMargins(0, 0, 0, 0)
        self.up_active.setPixmap(
            Icons().UpActiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )
        self.up_active.setVisible(False)
        self.up_active.clicked.connect(self._on_compass_button_click)

        self.up_inactive = QLabel()
        self.up_inactive.setAccessibleDescription("Up (Inactive)")
        self.up_inactive.setContentsMargins(0, 0, 0, 0)
        self.up_inactive.setPixmap(
            Icons().UpInactiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.down_active = QCompassButton(QCompass.CompassFlag.Down)
        self.down_active.setAccessibleDescription("Down (Active)")
        self.down_active.setContentsMargins(0, 0, 0, 0)
        self.down_active.setPixmap(
            Icons().DownActiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )
        self.down_active.setVisible(False)
        self.down_active.clicked.connect(self._on_compass_button_click)

        self.down_inactive = QLabel()
        self.down_inactive.setAccessibleDescription("Down (Inactive)")
        self.down_inactive.setContentsMargins(0, 0, 0, 0)
        self.down_inactive.setPixmap(
            Icons().DownInactiveIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 0)
        layout.setRowStretch(2, 0)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)
        layout.setColumnStretch(2, 0)
        layout.setColumnStretch(3, 0)
        layout.addWidget(self.north_active, 0, 1)
        layout.addWidget(self.north_inactive, 0, 1)
        layout.addWidget(self.northeast_active, 0, 2)
        layout.addWidget(self.northeast_inactive, 0, 2)
        layout.addWidget(self.east_active, 1, 2)
        layout.addWidget(self.east_inactive, 1, 2)
        layout.addWidget(self.southeast_active, 2, 2)
        layout.addWidget(self.southeast_inactive, 2, 2)
        layout.addWidget(self.south_active, 2, 1)
        layout.addWidget(self.south_inactive, 2, 1)
        layout.addWidget(self.southwest_active, 2, 0)
        layout.addWidget(self.southwest_inactive, 2, 0)
        layout.addWidget(self.west_active, 1, 0)
        layout.addWidget(self.west_inactive, 1, 0)
        layout.addWidget(self.northwest_active, 0, 0)
        layout.addWidget(self.northwest_inactive, 0, 0)
        layout.addWidget(self.out_active, 1, 1)
        layout.addWidget(self.out_inactive, 1, 1)
        layout.addWidget(self.up_active, 0, 3)
        layout.addWidget(self.up_inactive, 0, 3)
        layout.addWidget(self.down_active, 2, 3)
        layout.addWidget(self.down_inactive, 2, 3)

        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("padding: 0px; margin: 0px;")
        self.setLayout(layout)

    _DIRECTION_COMMANDS = {
        CompassFlag.North: "north",
        CompassFlag.NorthEast: "northeast",
        CompassFlag.East: "east",
        CompassFlag.SouthEast: "southeast",
        CompassFlag.South: "south",
        CompassFlag.SouthWest: "southwest",
        CompassFlag.West: "west",
        CompassFlag.NorthWest: "northwest",
        CompassFlag.Out: "out",
        CompassFlag.Up: "up",
        CompassFlag.Down: "down",
    }

    def _on_compass_button_click(self, direction: CompassFlag) -> None:
        self._logger.debug(f"_on_compass_button_click({direction})")
        for flag, cmd in QCompass._DIRECTION_COMMANDS.items():
            if direction & flag:
                self._window.command.Parse(cmd)
                return

    def update_compass(self, directions: CompassFlag) -> None:
        self.north_active.setVisible(
            bool(directions & QCompass.CompassFlag.North),
        )
        self.north_inactive.setVisible(
            not (directions & QCompass.CompassFlag.North),
        )

        self.northeast_active.setVisible(
            bool(directions & QCompass.CompassFlag.NorthEast),
        )
        self.northeast_inactive.setVisible(
            not (directions & QCompass.CompassFlag.NorthEast),
        )

        self.east_active.setVisible(
            bool(directions & QCompass.CompassFlag.East),
        )
        self.east_inactive.setVisible(
            not (directions & QCompass.CompassFlag.East),
        )

        self.southeast_active.setVisible(
            bool(directions & QCompass.CompassFlag.SouthEast),
        )
        self.southeast_inactive.setVisible(
            not (directions & QCompass.CompassFlag.SouthEast),
        )

        self.south_active.setVisible(
            bool(directions & QCompass.CompassFlag.South),
        )
        self.south_inactive.setVisible(
            not (directions & QCompass.CompassFlag.South),
        )

        self.southwest_active.setVisible(
            bool(directions & QCompass.CompassFlag.SouthWest),
        )
        self.southwest_inactive.setVisible(
            not (directions & QCompass.CompassFlag.SouthWest),
        )

        self.west_active.setVisible(
            bool(directions & QCompass.CompassFlag.West),
        )
        self.west_inactive.setVisible(
            not (directions & QCompass.CompassFlag.West),
        )

        self.northwest_active.setVisible(
            bool(directions & QCompass.CompassFlag.NorthWest),
        )
        self.northwest_inactive.setVisible(
            not (directions & QCompass.CompassFlag.NorthWest),
        )

        self.out_active.setVisible(
            bool(directions & QCompass.CompassFlag.Out),
        )
        self.out_inactive.setVisible(
            not (directions & QCompass.CompassFlag.Out),
        )

        self.up_active.setVisible(
            bool(directions & QCompass.CompassFlag.Up),
        )
        self.up_inactive.setVisible(
            not (directions & QCompass.CompassFlag.Up),
        )

        self.down_active.setVisible(
            bool(directions & QCompass.CompassFlag.Down),
        )
        self.down_inactive.setVisible(
            not (directions & QCompass.CompassFlag.Down),
        )


class QCompassButton(QLabel):
    clicked = pyqtSignal(int)

    def __init__(
        self, direction: QCompass.CompassFlag | None = None,
    ) -> None:
        super().__init__()

        self.direction = direction if direction is not None else QCompass.CompassFlag(0)

    def mousePressEvent(self, ev: QMouseEvent | None) -> None:
        if not ev:
            return

        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.direction)


class QCustomTextEdit(QTextEdit):
    def __init__(self, widget_id: str) -> None:
        super().__init__()

        self._logger = logging.getLogger(self.__class__.__name__)

        self._config = Config()
        self._variables = Variables()

        self._window = self._variables.get("widgets", "main_window", None)

        self._id = widget_id

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setReadOnly(True)
        self.setUndoRedoEnabled(False)
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.updateStyle()

    def _clear(self) -> None:
        self._logger.debug("_clear: begin")
        self.clear()
        self._logger.debug("_clear: end")

    def _timestamp(self, checked: bool) -> bool:
        self._logger.debug(f"_timestamp: begin checked({checked})")
        self._logger.debug("_timestamp: end")
        return True

    def contextMenuEvent(self, e: QContextMenuEvent | None) -> None:
        # Get the default context menu
        context_menu = self.createStandardContextMenu()
        if not context_menu:
            return

        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self._clear)

        timestamp = self._config.get("windows", self._id, {}).get("timestamp", False)
        timestamp_action = QAction("Timestamp", self)
        timestamp_action.triggered.connect(self._timestamp)
        timestamp_action.setCheckable(True)
        timestamp_action.setChecked(timestamp)

        context_menu.addSeparator()
        context_menu.addAction(clear_action)
        context_menu.addAction(timestamp_action)

        if e:
            # Execute the context menu
            context_menu.exec(e.globalPos())

    def insertHtml(self, text: str | None, ignore_visiblity: bool = False) -> None:
        if text is None:
            return

        if not ignore_visiblity and not self.isVisible():
            return

        self.moveCursor(QTextCursor.MoveOperation.End)
        super().insertHtml(text)
        self.moveCursor(QTextCursor.MoveOperation.End)

    def mousePressEvent(self, e: QMouseEvent | None) -> None:
        if not e:
            return

        self.anchor: str = self.anchorAt(e.pos())
        if self.anchor:
            QApplication.instance().setOverrideCursor(Qt.CursorShape.PointingHandCursor)  # type: ignore[union-attr]
            return

        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e: QMouseEvent | None) -> None:
        if not e:
            return

        self.anchor: str = self.anchorAt(e.pos())
        if self.anchor:
            if self.anchor.startswith("http://") or self.anchor.startswith("https://"):
                QDesktopServices.openUrl(QUrl(self.anchor))
            else:
                if (
                    self._window
                    and self._window.game_client.state == GameState.Connected
                ):
                    self._window.command.Parse(self.anchor)

            QApplication.instance().setOverrideCursor(Qt.CursorShape.ArrowCursor)  # type: ignore[union-attr]
            self.anchor = ""
            return

        super().mouseReleaseEvent(e)

    def updateStyle(self) -> None:
        fontname = self._config.get("presets", "game.fontname")
        fontsize = self._config.get("presets", "game.fontsize")
        color = self._config.get("presets", "game.color")
        bgcolor = self._config.get("presets", "game.bgcolor")
        self.setStyleSheet(
            f"""
            QCustomTextEdit {{
                font-family: "{fontname}";
                font-size: {fontsize}; color: {color};
                background-color: {bgcolor};
            }}
            """,
        )


class QCustomTimer(QObject):
    def __init__(self, interval: int = 1000) -> None:
        super().__init__()
        self.interval = interval
        self._callbacks = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)

    def connect(self, function: object) -> None:
        self._callbacks.append(function)

    def start(self) -> None:
        self.timer.start(self.interval)

    def stop(self) -> None:
        self.timer.stop()

    def tick(self) -> None:
        for callback in self._callbacks:
            callback()


class QCustomToolBar(QToolBar):
    def __init__(self) -> None:
        super().__init__()
        self.setMovable(False)
        self.setObjectName("QCustomToolBar")
        self.setStyleSheet("QCustomToolBar { border: none; }")


class QIndicatorLabel(QLabel):
    def __init__(self, title: str) -> None:
        super().__init__()

        self._config = Config()
        self._variables = Variables()

        self.setAccessibleDescription(title)
        self.setContentsMargins(0, 0, 0, 0)
        self.setObjectName(title)
        self.setVisible(False)

    def setVisible(self, visible: bool) -> None:
        indicator = self.objectName().lower()
        self._variables.set("temporary", indicator, visible)

        super().setVisible(visible)


class QIndicators(QWidget):
    class IndicatorsFlag(IntFlag):
        Bleeding = 1
        Dead = 2
        Hidden = 4
        Invisible = 8
        Joined = 16
        Kneeling = 32
        Prone = 64
        Sitting = 128
        Standing = 256
        Stunned = 512
        Webbed = 1024

    def __init__(self) -> None:
        super().__init__()

        self._config = Config()
        self._variables = Variables()

        self._window = self._variables.get("widgets", "main_window", None)

        icon_size = self._config.get("presets", "indicator.iconsize", 28)

        self.bleeding = QIndicatorLabel("Bleeding")
        self.bleeding.setPixmap(
            Icons().BleedingIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.dead = QIndicatorLabel("Dead")
        self.dead.setPixmap(
            Icons().DeadIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.hidden = QIndicatorLabel("Hidden")
        self.hidden.setPixmap(
            Icons().HiddenIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.invisible = QIndicatorLabel("Invisible")
        self.invisible.setPixmap(
            Icons().InvisibleIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.joined = QIndicatorLabel("Joined")
        self.joined.setPixmap(
            Icons().JoinedIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.kneeling = QIndicatorLabel("Kneeling")
        self.kneeling.setPixmap(
            Icons().KneelingIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.prone = QIndicatorLabel("Prone")
        self.prone.setPixmap(
            Icons().ProneIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.sitting = QIndicatorLabel("Sitting")
        self.sitting.setPixmap(
            Icons().SittingIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.standing = QIndicatorLabel("Standing")
        self.standing.setPixmap(
            Icons().StandingIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.stunned = QIndicatorLabel("Stunned")
        self.stunned.setPixmap(
            Icons().StunnedIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        self.webbed = QIndicatorLabel("Webbed")
        self.webbed.setPixmap(
            Icons().WebbedIcon.pixmap(
                QSize(
                    icon_size,
                    icon_size,
                ),
            ),
        )

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.standing)
        layout.addWidget(self.kneeling)
        layout.addWidget(self.sitting)
        layout.addWidget(self.prone)
        layout.addWidget(self.dead)
        layout.addWidget(self.bleeding)
        layout.addWidget(self.stunned)
        layout.addWidget(self.webbed)
        layout.addWidget(self.hidden)
        layout.addWidget(self.invisible)
        layout.addWidget(self.joined)

        # self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("padding: 0px; margin: 0px;")
        self.setLayout(layout)

    def update_indicators(self, indicators: IndicatorsFlag) -> None:
        self.bleeding.setVisible(
            bool(indicators & QIndicators.IndicatorsFlag.Bleeding),
        )

        self.dead.setVisible(
            bool(indicators & QIndicators.IndicatorsFlag.Dead),
        )

        self.hidden.setVisible(
            bool(indicators & QIndicators.IndicatorsFlag.Hidden),
        )

        self.invisible.setVisible(
            bool(indicators & QIndicators.IndicatorsFlag.Invisible),
        )

        self.joined.setVisible(
            bool(indicators & QIndicators.IndicatorsFlag.Joined),
        )

        self.kneeling.setVisible(
            bool(indicators & QIndicators.IndicatorsFlag.Kneeling),
        )

        self.prone.setVisible(
            bool(indicators & QIndicators.IndicatorsFlag.Prone),
        )

        self.sitting.setVisible(
            bool(indicators & QIndicators.IndicatorsFlag.Sitting),
        )

        self.standing.setVisible(
            bool(indicators & QIndicators.IndicatorsFlag.Standing),
        )

        self.stunned.setVisible(
            bool(indicators & QIndicators.IndicatorsFlag.Stunned),
        )

        self.webbed.setVisible(
            bool(indicators & QIndicators.IndicatorsFlag.Webbed),
        )


class QMiniVital(QProgressBar):
    def __init__(self, vital_id: str, value: int, text: str) -> None:
        super().__init__()

        self._config = Config()

        self.id = vital_id
        color = self._config.get("presets", f"minivitals.{vital_id}.color", "white")
        bgcolor = self._config.get("presets", f"minivitals.{vital_id}.bgcolor", "black")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumWidth(150)
        self.setObjectName(f"MiniVital-{vital_id}")
        self.setStyleSheet(
            f"""
            QProgressBar#MiniVital-{vital_id} {{
                color: {color};
            }}
            QProgressBar#MiniVital-{vital_id}::chunk {{
                background-color: {bgcolor};
                margin: 1px;
            }}
            """,
        )
        self.setValue(value)
        self.setFormat(text)

    def do_update(self, value: int, text: str) -> None:
        self.setValue(value)
        self.setFormat(text)


class QTimerBar(QProgressBar):
    class TimerBarType(Enum):
        RoundTime = 1
        CastTime = 2

    def __init__(self, bar_type: TimerBarType) -> None:
        super().__init__()

        self._config = Config()
        self._variables = Variables()

        self._logger = logging.getLogger(self.__class__.__name__)

        self._type = bar_type
        self._current_seconds = 0
        self._total_seconds = 0

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFormat("")
        self.setMaximumHeight(4)
        self.setValue(0)

        if bar_type is self.TimerBarType.RoundTime:
            bgcolor = self._config.get("presets", "roundtime.bgcolor", "red")
            self.setObjectName("RoundTime")
            self.setStyleSheet(
                f"""
                QProgressBar#RoundTime {{
                    border: none;
                }}
                QProgressBar#RoundTime::chunk {{
                    background-color: {bgcolor};
                    margin: 0px;
                    margin-top: 1px;
                }}
                """,
            )
        elif bar_type is self.TimerBarType.CastTime:
            bgcolor = self._config.get("presets", "casttime.bgcolor", "blue")
            self.setObjectName("CastTime")
            self.setStyleSheet(
                f"""
                QProgressBar#CastTime {{
                    border: none;
                }}
                QProgressBar#CastTime::chunk {{
                    background-color: {bgcolor};
                    margin: 0px;
                    margin-top: 1px;
                }}
                """,
            )
        else:
            self._logger.error(f"QTimerBar unknown type: {bar_type}")

    def start(self, seconds: int) -> None:
        self._logger.debug(f"start: seconds({seconds})")
        if not seconds:
            self._current_seconds = 0
            self._total_seconds = 0
            self.setValue(0)
            return

        self._total_seconds = seconds
        self._current_seconds = 1
        self.setValue(100)

    def do_update(self) -> None:
        if not self._total_seconds:
            return

        seconds_left = self._total_seconds - self._current_seconds

        self._logger.debug(
            f"update: _total_seconds({self._total_seconds}) _current_seconds({self._current_seconds}) seconds_left({seconds_left})",
        )

        if self._type == self.TimerBarType.RoundTime:
            self._variables.set("temporary", "roundtime", seconds_left)
        elif self._type == self.TimerBarType.CastTime:
            self._variables.set("temporary", "casttime", seconds_left)

        if seconds_left <= 0:
            self._current_seconds = 0
            self._total_seconds = 0
            self.setValue(0)
        else:
            percentage = int((seconds_left / self._total_seconds) * 100)
            self.setValue(percentage)
            self._current_seconds += 1


class QScriptButton(QToolButton):
    def __init__(self, script: str) -> None:
        super().__init__()

        self._script = script

        resume_action = QAction(Icons().PlayIcon, "Resume", self)
        resume_action.triggered.connect(self.resume_action)

        pause_action = QAction(Icons().PauseIcon, "Pause", self)
        pause_action.triggered.connect(self.pause_action)

        abort_action = QAction(Icons().StopIcon, "Abort", self)
        abort_action.triggered.connect(self.abort_action)

        menu = QMenu()
        menu.addAction(resume_action)
        menu.addAction(pause_action)
        menu.addAction(abort_action)

        self.setIcon(Icons().PlayIcon)
        self.setMenu(menu)
        self.setObjectName("QScriptButton")
        self.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
        self.setStyleSheet("QScriptButton { margin-right: 6px; }")
        self.setText(self._script)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.clicked.connect(self.click_action)

    def click_action(self) -> None:
        print(f"DEBUG: QScriptButton script({self._script}) action(click)")

    def resume_action(self) -> None:
        print(f"DEBUG: QScriptButton script({self._script}) action(resume)")

    def pause_action(self) -> None:
        print(f"DEBUG: QScriptButton script({self._script}) action(pause)")

    def abort_action(self) -> None:
        print(f"DEBUG: QScriptButton script({self._script}) action(abort)")


class QHistoryLineEdit(QLineEdit):
    """A QLineEdit with up/down arrow command history navigation."""

    def __init__(self) -> None:
        super().__init__()

        self._config = Config()
        self._current_input: str = ""
        self._history: list[str] = []
        self._history_pos: int = 0
        self._variables = Variables()
        self._window = self._variables.get("widgets", "main_window", None)

    def add_to_history(self, text: str) -> None:
        """Add a command to history and reset navigation position."""
        max_length = self._config.get("client", "input.history_length", 100)
        if text and (not self._history or self._history[-1] != text):
            self._history.append(text)
            if len(self._history) > max_length:
                self._history.pop(0)
        self._history_pos = len(self._history)
        self._current_input = ""

    def keyPressEvent(self, a0: QKeyEvent | None) -> None:
        if not a0:
            return

        k = a0.key()
        m = a0.modifiers()

        if k in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and m & Qt.KeyboardModifier.ControlModifier:
            if self._history and self._window:
                self._window.command.parse(self._history[-1])
        elif k == Qt.Key.Key_Up:
            if self._history:
                if self._history_pos == len(self._history):
                    self._current_input = self.text()
                if self._history_pos > 0:
                    self._history_pos -= 1
                    self.setText(self._history[self._history_pos])
                    self.end(False)
        elif k == Qt.Key.Key_Down:
            if self._history_pos < len(self._history):
                self._history_pos += 1
                if self._history_pos == len(self._history):
                    self.setText(self._current_input)
                else:
                    self.setText(self._history[self._history_pos])
                self.end(False)
        else:
            super().keyPressEvent(a0)
