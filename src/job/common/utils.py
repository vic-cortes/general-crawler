from datetime import datetime, timedelta

from .constants import DECIMAL_PLACES, DEFAULT_FORMAT, MONTHS


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
        return "horas" in self.raw_date or "hora" in self.raw_date

    @property
    def is_minutes(self) -> bool:
        return "minutos" in self.raw_date or "minuto" in self.raw_date

    @property
    def is_days(self) -> bool:
        return "días" in self.raw_date

    def _convert_from_minutes(self) -> datetime:
        return self._current_date - timedelta(minutes=int(self._digit))

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
        elif self.is_minutes:
            standard_date = self._convert_from_minutes()
        else:
            print(self.raw_date)
            standard_date = self._default()

        return standard_date.strftime(DEFAULT_FORMAT)


class SalaryConverter:

    def __init__(self, raw_salary: str) -> None:
        self.raw_salary = raw_salary or ""
        self.raw_salary = self.raw_salary.strip().lower()

    def _get_digit(self) -> str:
        return "".join([el for el in list(self.raw_salary) if el.isdigit()])

    @property
    def is_monthly(self) -> bool:
        return "mensual" in self.raw_salary

    @property
    def is_hourly(self) -> bool:
        return "horas" in self.raw_salary

    @property
    def has_commission(self) -> bool:
        return "comisión" in self.raw_salary

    def _convert_from_monthly(self) -> float:
        return float(self._get_digit()) / DECIMAL_PLACES

    def _convert_from_hourly(self) -> float:
        return self._get_digit() / DECIMAL_PLACES

    def _default(self) -> float:
        return 0.0

    def convert(self) -> dict:
        salary = {}

        if self.is_monthly:
            value = self._convert_from_monthly()
        elif self.is_hourly:
            value = self._convert_from_hourly()
        else:
            value = self._default()

        salary["base"] = value
        salary["has_commission"] = self.has_commission

        return salary
