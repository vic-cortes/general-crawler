import json

import pytest

from config import DATA_PATH


def test_data_path_exists():
    # Read data and check its contents
    file_name = DATA_PATH / "compu_trabajo_job_offers_20250819_01_00.json"

    with open(file_name) as file:
        data = json.load(file)

    print(f"{data=}")
