import os
import sys

from PyQt6.QtGui import QIcon


# Set the imaged directory path
ICONS_DIR = "images"
if hasattr(sys, "_MEIPASS"):
    # We're running from inside a pyinstaller binary
    ICONS_DIR = os.path.join(sys._MEIPASS, "images")


class Icons:
    def __init__(self) -> None:
        # General icons
        self.AppIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "pivuh.png",
            ),
        )

        self.LeftIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "left.png",
            ),
        )

        self.PauseIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "pause.png",
            ),
        )

        self.PlayIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "play.png",
            ),
        )

        self.RightIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "right.png",
            ),
        )

        self.SpellIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "spell.png",
            ),
        )

        self.StopIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "stop.png",
            ),
        )

        # Compass icons
        self.NorthActiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "north-active.png",
            ),
        )

        self.NorthInactiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "north-inactive.png",
            ),
        )

        self.NorthEastActiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "northeast-active.png",
            ),
        )

        self.NorthEastInactiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "northeast-inactive.png",
            ),
        )

        self.EastActiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "east-active.png",
            ),
        )

        self.EastInactiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "east-inactive.png",
            ),
        )

        self.SouthEastActiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "southeast-active.png",
            ),
        )

        self.SouthEastInactiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "southeast-inactive.png",
            ),
        )

        self.SouthActiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "south-active.png",
            ),
        )

        self.SouthInactiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "south-inactive.png",
            ),
        )

        self.SouthWestActiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "southwest-active.png",
            ),
        )

        self.SouthWestInactiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "southwest-inactive.png",
            ),
        )

        self.WestActiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "west-active.png",
            ),
        )

        self.WestInactiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "west-inactive.png",
            ),
        )

        self.NorthWestActiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "northwest-active.png",
            ),
        )

        self.NorthWestInactiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "northwest-inactive.png",
            ),
        )

        self.OutActiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "out-active.png",
            ),
        )

        self.OutInactiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "out-inactive.png",
            ),
        )

        self.UpActiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "up-active.png",
            ),
        )

        self.UpInactiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "up-inactive.png",
            ),
        )

        self.DownActiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "down-active.png",
            ),
        )

        self.DownInactiveIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "down-inactive.png",
            ),
        )

        # Status icons
        self.BleedingIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "bleeding.png",
            ),
        )

        self.DeadIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "dead.png",
            ),
        )

        self.HiddenIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "hidden.png",
            ),
        )

        self.InvisibleIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "invisible.png",
            ),
        )

        self.JoinedIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "joined.png",
            ),
        )

        self.StunnedIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "stunned.png",
            ),
        )

        self.WebbedIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "webbed.png",
            ),
        )

        # Position icons
        self.KneelingIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "kneeling.png",
            ),
        )

        self.ProneIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "prone.png",
            ),
        )

        self.SittingIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "sitting.png",
            ),
        )

        self.StandingIcon = QIcon(
            os.path.join(
                ICONS_DIR,
                "standing.png",
            ),
        )
