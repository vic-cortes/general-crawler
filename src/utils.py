import re
from dataclasses import dataclass
from datetime import datetime, timedelta


class DateConverter:

    def __init__(self, raw_date: str) -> None:
        self.raw_date = raw_date.lower()
        self._digit = self._get_digit()

    def _get_digit(self) -> str:
        return "".join([el for el in list(self.raw_date) if el.isdigit()])

    @property
    def is_yesterday(self) -> bool:
        return "ayer" in self.raw_date

    @property
    def is_hour(self) -> bool:
        return "horas" in self.raw_date

    @property
    def is_days(self) -> bool:
        return "días" in self.raw_date

    def _convert_from_hour(self) -> datetime:
        pass

    def _convert_from_yesterday(self) -> datetime:
        pass

    def _convert_from_days(self) -> datetime:
        pass

    def convert_relative_date_to_absolute(self) -> str:
        """
        Convert a relative date string to an absolute date string.
        """
        value = [el for el in list(self.raw_date) if el.isdigit()]

        if value:
            pass

        if "horas" in self.raw_date:
            # Use regex to extract the number of hours
            match = re.search(r"(\d+) horas", self.raw_date)
            if match:
                hours = int(match.group(1))
                absolute_date = datetime.now() - timedelta(hours=hours)
                return absolute_date.strftime("%Y-%m-%d %H:%M:%S")
        return self.raw_date
