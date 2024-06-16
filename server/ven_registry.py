# ven_registry.py

import json
import uuid
from collections import namedtuple
from pathlib import Path
from collections import deque
from datetime import datetime, timedelta

VenInfo = namedtuple("VenInfo", ["ven_name", "ven_id", "registration_id", "last_report", "last_report_units", "last_report_time", "check_in_times"])

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
        if ven_name in self._vens:
            raise DuplicateVenError

        self._vens[ven_name] = VenInfo(
            ven_name=ven_name,
            ven_id=str(uuid.uuid4()),
            registration_id=str(uuid.uuid4()),
            last_report=None,
            last_report_units=None,
            last_report_time=None,
            check_in_times=deque(maxlen=10)
        )
        self.save_to_file()

    def update_ven_report(self, ven_name: str, report_value: str, units: str, timestamp: str):
        if ven_name not in self._vens:
            raise UnknownVenError(f"VEN {ven_name} not found")
        ven_info = self._vens[ven_name]
        new_check_in_times = ven_info.check_in_times
        new_check_in_times.append(datetime.fromisoformat(timestamp))
        updated_ven_info = ven_info._replace(
            last_report=report_value,
            last_report_units=units,
            last_report_time=timestamp,
            check_in_times=new_check_in_times
        )
        self._vens[ven_name] = updated_ven_info
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
        with open(self._filename, mode="w") as file:
            vens = {k: {**v._asdict(), "check_in_times": list(map(str, v.check_in_times))} for k, v in self._vens.items()}
            json.dump(vens, file)

    def load_from_file(self):
        with open(self._filename, mode="r") as file:
            vens = json.load(file)
            self._vens = {k: VenInfo(**{**v, 'last_report': v.get('last_report', None), 'last_report_units': v.get('last_report_units', None), 'last_report_time': v.get('last_report_time', None), 'check_in_times': deque(map(datetime.fromisoformat, v.get('check_in_times', [])), maxlen=10)}) for k, v in vens.items()}

    def remove_ven(self, ven_name):
        if ven_name not in self._vens:
            raise UnknownVenError(f"VEN {ven_name} not found")
        del self._vens[ven_name]
        self.save_to_file()

    def get_all_vens(self):
        return list(self._vens.values())

    def calculate_connection_quality(self, ven_name: str) -> float:
        ven_info = self._vens[ven_name]
        check_in_times = ven_info.check_in_times

        if len(check_in_times) < 2:
            return 0.0

        intervals = [
            (check_in_times[i] - check_in_times[i-1]).total_seconds()
            for i in range(1, len(check_in_times))
        ]
        expected_interval = 10  # expected check-in interval in seconds
        max_interval = expected_interval * 2  # define a threshold for a "missed" check-in
        valid_intervals = [interval for interval in intervals if interval <= max_interval]
        connection_quality = len(valid_intervals) / len(intervals) * 100
        return connection_quality

    def get_all_vens_with_quality(self):
        ven_list = self.get_all_vens()
        return [
            {
                "ven_name": ven.ven_name,
                "ven_id": ven.ven_id,
                "registration_id": ven.registration_id,
                "last_report": ven.last_report,
                "last_report_units": ven.last_report_units,
                "last_report_time": ven.last_report_time,
                "connection_quality": self.calculate_connection_quality(ven.ven_name)
            }
            for ven in ven_list
        ]
