from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"
SQL_DIR = BASE_DIR / "sql"

RANDOM_SEED = 42

EXCEPTION_TYPES = [
    "Missing Reference Data",
    "Stale Price",
    "Price Outlier",
    "Trade Match Break",
    "Position Reconciliation Break",
    "Duplicate Record",
    "Invalid Currency",
    "Missing Client Mapping",
    "Delayed Source Load",
    "Performance Return Outlier",
    "Unknown / Needs SME Review",
]

SEVERITY_WEIGHTS = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
