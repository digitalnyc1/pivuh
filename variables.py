import json
from pathlib import Path
from typing import Any

VARIABLES: dict[str, dict] = {}

# Variable groups listed here are kept only in memory and never written to disk.
TRANSIENT_GROUPS: set[str] = {
    "internal",
    "protected",
    "temporary",
    "widgets",
}


class Variables:
    def __init__(self, file: str = "config/variables.json") -> None:
        self._file = file

    def get(self, group: str, key: str, fallback: Any = None) -> Any:  # noqa: ANN401
        if group not in VARIABLES:
            VARIABLES[group] = {}
        return VARIABLES[group].get(key, fallback)

    def items(self, group: str) -> list:
        return list(VARIABLES.get(group, {}))

    def load(self) -> None:
        """Load all non-transient groups from disk, merging into current state."""
        if not Path(self._file).exists():
            return
        with Path(self._file).open("r") as json_file:
            data: dict = json.load(json_file)
        for group, values in data.items():
            if group not in TRANSIENT_GROUPS:
                if group not in VARIABLES:
                    VARIABLES[group] = {}
                VARIABLES[group].update(values)

    def save(self) -> None:
        """Save all non-transient groups to disk."""
        Path(self._file).parent.mkdir(parents=True, exist_ok=True)
        data = {
            group: values
            for group, values in VARIABLES.items()
            if group not in TRANSIENT_GROUPS
        }
        with Path(self._file).open("w") as json_file:
            json.dump(data, json_file, indent=2, sort_keys=True)

    def set(self, group: str, key: str, value: Any) -> None:  # noqa: ANN401
        if group not in VARIABLES:
            VARIABLES[group] = {}
        VARIABLES[group][key] = value
