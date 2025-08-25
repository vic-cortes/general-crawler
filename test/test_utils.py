import pytest

from config import DATA_PATH


def test_data_path_exists():
    # Add breakpoint for debugging
    breakpoint()

    assert DATA_PATH.exists(), "DATA_PATH directory does not exist"
    assert DATA_PATH.is_dir(), "DATA_PATH is not a directory"
    assert str(DATA_PATH).endswith("/data"), "DATA_PATH should end with 'data'"
