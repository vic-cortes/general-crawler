from datetime import datetime, timedelta

MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

DEFAULT_FORMAT = "%Y-%m-%d %H:%M:%S"


class DateConverter:

    def __init__(self, raw_date: str) -> None:
        self.raw_date = raw_date.lower()
        self._digit = self._get_digit()
        self._current_date = datetime.now()

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
        return self._current_date - timedelta(hours=int(self._digit))

    def _convert_from_yesterday(self) -> datetime:
        return self._current_date - timedelta(days=1)

    def _convert_from_days(self) -> datetime:
        return self._current_date - timedelta(days=int(self._digit))

    def _default(self) -> datetime:
        month_name = [el for el in self.raw_date.split() if el in MONTHS][0]

        if not month_name:
            raise ValueError(f"Month not found in {self.raw_date}")

        month_number = MONTHS.get(month_name)
        day = int(self._digit)
        return datetime(self._current_date.year, month_number, day)

    def convert(self) -> str:
        """
        Convert a relative date string to an absolute date string.
        """
        if self.is_yesterday:
            standard_date = self._convert_from_yesterday()
        elif self.is_hour:
            standard_date = self._convert_from_hour()
        elif self.is_days:
            standard_date = self._convert_from_days()
        else:
            standard_date = self._default()

        return standard_date.strftime(DEFAULT_FORMAT)
