import json

from config import DATA_PATH
from src.job.compu_trabajo import CompuTrabajoDateConverter, CompuTrabajoSalaryConverter


def test_data_path_exists():
    # Read data and check its contents
    file_name = DATA_PATH / "compu_trabajo_job_offers_20250827_23_00.json"

    with open(file_name) as file:
        data = json.load(file)

    for job in data:
        relative_date = job["relative_date"]
        date_converter = CompuTrabajoDateConverter(relative_date)
        job["absolute_date"] = date_converter.convert()
        job["details"]["salary"] = CompuTrabajoSalaryConverter(
            job["details"].get("salary")
        ).convert()

    print(f"{data=}")
