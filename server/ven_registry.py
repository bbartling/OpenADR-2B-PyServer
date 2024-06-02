# ven_registry.py

import json
import uuid
from collections import namedtuple
from pathlib import Path

VenInfo = namedtuple("VenInfo", ["ven_name", "ven_id", "registration_id"])

class DuplicateVenError(Exception):
    """Raised when adding a duplicate VEN to the registry."""

class UnknownVenError(Exception):
    """Raised when requesting info on an unknown VEN."""

class VenRegistry:
    def __init__(self, directory: Path):
        self._vens = dict()
        self._directory = directory
        self._filename = directory / "vens.json"
        if not self._directory.exists():
            self._directory.mkdir(parents=True)
        if self._filename.exists():
            self.load_from_file()

    def add_ven(self, ven_name: str):
        """Add a VEN to the registry.

        Registering a VEN consists of:
          - Adding it to this registry.
          - Persisting registry changes to file.
        """
        if ven_name in self._vens:
            raise DuplicateVenError

        self._vens[ven_name] = VenInfo(
            ven_name=ven_name,
            ven_id=str(uuid.uuid4()),
            registration_id=str(uuid.uuid4())
        )

        self.save_to_file()

    def get_ven_info_from_name(self, ven_name: str) -> VenInfo:
        """Return information on a registered VEN from its name."""
        try:
            return self._vens[ven_name]
        except KeyError:
            raise UnknownVenError

    def get_ven_info_from_id(self, ven_id: str) -> VenInfo:
        """Return information on a registered VEN from its ID."""
        for ven in self._vens.values():
            if ven.ven_id == ven_id:
                return ven
        raise UnknownVenError

    def save_to_file(self):
        """Save the registry to the file system."""
        with open(self._filename, mode="w") as file:
            vens = {k: v._asdict() for k, v in self._vens.items()}
            json.dump(vens, file)

    def load_from_file(self):
        """Load a registry from the file system."""
        with open(self._filename, mode="r") as file:
            vens = json.load(file)
            self._vens = {k: VenInfo(**v) for k, v in vens.items()}

    def remove_ven(self, ven_name):
        if ven_name not in self._vens:
            raise UnknownVenError(f"VEN {ven_name} not found")
        del self._vens[ven_name]
        self.save_to_file()

    def get_all_vens(self):
        return list(self._vens.values())
