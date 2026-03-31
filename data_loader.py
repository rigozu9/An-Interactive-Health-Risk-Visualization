import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

SLEEP_PATH = DATA_DIR / "sleep" / "Sleep_health_and_lifestyle_dataset.csv"
CVD_PATH = DATA_DIR / "body" / "CVD_cleaned.csv"
HEART_PATH = DATA_DIR / "disease" / "heart.csv"
STROKE_PATH = DATA_DIR / "disease" / "healthcare-dataset-stroke-data.csv"
CANCER_PATH = DATA_DIR / "disease" / "cancer-risk-factors.csv"

def load_sleep():
    return pd.read_csv(SLEEP_PATH)

def load_cvd():
    return pd.read_csv(CVD_PATH)

def load_heart():
    return pd.read_csv(HEART_PATH)

def load_stroke():
    return pd.read_csv(STROKE_PATH)

def load_cancer():
    return pd.read_csv(CANCER_PATH)