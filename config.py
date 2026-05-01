from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).parent
DATA_PATH = ROOT_DIR / "data"


class Config:
    DEEP_SEEK_API_KEY: str = os.getenv("DEEP_SEEK_API_KEY")
