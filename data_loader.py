import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
STANDARDIZED_DIR = DATA_DIR / "standardized"

SLEEP_PATH = STANDARDIZED_DIR / "sleep" / "sleep_standardized.csv"
CVD_PATH = STANDARDIZED_DIR / "body" / "cardiovascular_body_standardized.csv"
HEART_PATH = STANDARDIZED_DIR / "disease" / "heart_disease_standardized.csv"
STROKE_PATH = STANDARDIZED_DIR / "disease" / "stroke_standardized.csv"
CANCER_PATH = STANDARDIZED_DIR / "disease" / "cancer_risk_standardized.csv"


def _load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def load_sleep():
    return _load_csv(SLEEP_PATH)


def load_cvd():
    return _load_csv(CVD_PATH)


def load_heart():
    return _load_csv(HEART_PATH)


def load_stroke():
    return _load_csv(STROKE_PATH)


def load_cancer():
    return _load_csv(CANCER_PATH)
