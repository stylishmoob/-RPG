import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_NAME = os.environ.get(
    "DATABASE_PATH",
    str(BASE_DIR / "rpg_table.db")
)