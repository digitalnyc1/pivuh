import shutil
import sys
from pathlib import Path

from PyQt6.QtGui import QIcon

# Ensure the local images directory exists, copying from PyInstaller bundle if needed.
ICONS_DIR = Path("images")
if not ICONS_DIR.exists():
    if hasattr(sys, "_MEIPASS"):
        bundled_images = Path(sys._MEIPASS) / "images"  # pyright: ignore[reportAttributeAccessIssue]  # noqa: SLF001
        if bundled_images.exists():
            shutil.copytree(bundled_images, ICONS_DIR)
        else:
            error = f"Images directory not found at '{ICONS_DIR}' or in the PyInstaller bundle ('{bundled_images}')."
            raise FileNotFoundError(error)
    else:
        error = f"Images directory not found at '{ICONS_DIR}'."
        raise FileNotFoundError(error)


class Icons:
    _instance = None

    def __new__(cls) -> "Icons":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        # General icons
        self.AppIcon = QIcon(
            str(ICONS_DIR / "pivuh.png"),
        )

        self.LeftIcon = QIcon(
            str(ICONS_DIR / "left.png"),
        )

        self.PauseIcon = QIcon(
            str(ICONS_DIR / "pause.png"),
        )

        self.PlayIcon = QIcon(
            str(ICONS_DIR / "play.png"),
        )

        self.RightIcon = QIcon(
            str(ICONS_DIR / "right.png"),
        )

        self.SpellIcon = QIcon(
            str(ICONS_DIR / "spell.png"),
        )

        self.StopIcon = QIcon(
            str(ICONS_DIR / "stop.png"),
        )

        # Compass icons
        self.NorthActiveIcon = QIcon(
            str(ICONS_DIR / "north-active.png"),
        )

        self.NorthInactiveIcon = QIcon(
            str(ICONS_DIR / "north-inactive.png"),
        )

        self.NorthEastActiveIcon = QIcon(
            str(ICONS_DIR / "northeast-active.png"),
        )

        self.NorthEastInactiveIcon = QIcon(
            str(ICONS_DIR / "northeast-inactive.png"),
        )

        self.EastActiveIcon = QIcon(
            str(ICONS_DIR / "east-active.png"),
        )

        self.EastInactiveIcon = QIcon(
            str(ICONS_DIR / "east-inactive.png"),
        )

        self.SouthEastActiveIcon = QIcon(
            str(ICONS_DIR / "southeast-active.png"),
        )

        self.SouthEastInactiveIcon = QIcon(
            str(ICONS_DIR / "southeast-inactive.png"),
        )

        self.SouthActiveIcon = QIcon(
            str(ICONS_DIR / "south-active.png"),
        )

        self.SouthInactiveIcon = QIcon(
            str(ICONS_DIR / "south-inactive.png"),
        )

        self.SouthWestActiveIcon = QIcon(
            str(ICONS_DIR / "southwest-active.png"),
        )

        self.SouthWestInactiveIcon = QIcon(
            str(ICONS_DIR / "southwest-inactive.png"),
        )

        self.WestActiveIcon = QIcon(
            str(ICONS_DIR / "west-active.png"),
        )

        self.WestInactiveIcon = QIcon(
            str(ICONS_DIR / "west-inactive.png"),
        )

        self.NorthWestActiveIcon = QIcon(
            str(ICONS_DIR / "northwest-active.png"),
        )

        self.NorthWestInactiveIcon = QIcon(
            str(ICONS_DIR / "northwest-inactive.png"),
        )

        self.OutActiveIcon = QIcon(
            str(ICONS_DIR / "out-active.png"),
        )

        self.OutInactiveIcon = QIcon(
            str(ICONS_DIR / "out-inactive.png"),
        )

        self.UpActiveIcon = QIcon(
            str(ICONS_DIR / "up-active.png"),
        )

        self.UpInactiveIcon = QIcon(
            str(ICONS_DIR / "up-inactive.png"),
        )

        self.DownActiveIcon = QIcon(
            str(ICONS_DIR / "down-active.png"),
        )

        self.DownInactiveIcon = QIcon(
            str(ICONS_DIR / "down-inactive.png"),
        )

        # Status icons
        self.BleedingIcon = QIcon(
            str(ICONS_DIR / "bleeding.png"),
        )

        self.DeadIcon = QIcon(
            str(ICONS_DIR / "dead.png"),
        )

        self.HiddenIcon = QIcon(
            str(ICONS_DIR / "hidden.png"),
        )

        self.InvisibleIcon = QIcon(
            str(ICONS_DIR / "invisible.png"),
        )

        self.JoinedIcon = QIcon(
            str(ICONS_DIR / "joined.png"),
        )

        self.StunnedIcon = QIcon(
            str(ICONS_DIR / "stunned.png"),
        )

        self.WebbedIcon = QIcon(
            str(ICONS_DIR / "webbed.png"),
        )

        # Position icons
        self.KneelingIcon = QIcon(
            str(ICONS_DIR / "kneeling.png"),
        )

        self.ProneIcon = QIcon(
            str(ICONS_DIR / "prone.png"),
        )

        self.SittingIcon = QIcon(
            str(ICONS_DIR / "sitting.png"),
        )

        self.StandingIcon = QIcon(
            str(ICONS_DIR / "standing.png"),
        )
