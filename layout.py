import base64
import json
import logging
from pathlib import Path


class LayoutConfig:
    def __init__(self, file: str = "config/layout.json") -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

        self._file = file

    def load(self) -> tuple[bytes, bytes]:
        """Load geometry and state from config/layout.json.

        Returns:
            A (geometry, state) tuple of bytes.  Either value is b"" when not
            present or if the file does not exist yet.
        """
        path = Path(self._file)
        if not path.exists():
            self._logger.debug("load: layout file not found, returning empty values")
            return b"", b""

        try:
            with path.open("r") as f:
                data = json.load(f)
            geometry = base64.b64decode(data.get("geometry", ""))
            state = base64.b64decode(data.get("state", ""))
            self._logger.debug(
                "load: geometry=%d bytes, state=%d bytes", len(geometry), len(state)
            )
        except Exception:
            self._logger.exception("load: failed to load layout")
            return b"", b""
        else:
            return geometry, state

    def save(self, geometry: bytes, state: bytes) -> None:
        """Save geometry and state to config/layout.json."""
        path = Path(self._file)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "geometry": base64.b64encode(geometry).decode("ascii"),
            "state": base64.b64encode(state).decode("ascii"),
        }

        try:
            with path.open("w") as f:
                json.dump(data, f, indent=2)
            self._logger.debug(
                "save: geometry=%d bytes, state=%d bytes", len(geometry), len(state)
            )
        except Exception:
            self._logger.exception("save: failed to save layout")
