import json
from pathlib import Path
from typing import Any


VARIABLES: dict[str, dict] = {}

# Variable groups listed here are kept only in memory and never written to disk.
TRANSIENT_GROUPS: set[str] = {
    "internal",
    "temporary",
}


class Variables:
    def __init__(self) -> None:
        global VARIABLES
        self._variables = VARIABLES

    def get(self, group: str, key: str, fallback: Any = None) -> Any:
        if group not in VARIABLES:
            VARIABLES[group] = {}
        return VARIABLES[group].get(key, fallback)

    def set(self, group: str, key: str, value: Any) -> None:
        if group not in VARIABLES:
            VARIABLES[group] = {}
        VARIABLES[group][key] = value

    def load(self, file: str = "config/variables.json") -> None:
        """Load all non-transient groups from disk, merging into current state."""
        if not Path(file).exists():
            return
        with open(file, "r") as json_file:
            data: dict = json.load(json_file)
        for group, values in data.items():
            if group not in TRANSIENT_GROUPS:
                if group not in VARIABLES:
                    VARIABLES[group] = {}
                VARIABLES[group].update(values)

    def save(self, file: str = "config/variables.json") -> None:
        """Save all non-transient groups to disk."""
        Path(file).parent.mkdir(parents=True, exist_ok=True)
        data = {
            group: values
            for group, values in VARIABLES.items()
            if group not in TRANSIENT_GROUPS
        }
        with open(file, "w") as json_file:
            json.dump(data, json_file, indent=2, sort_keys=True)
