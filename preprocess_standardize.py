from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "standardized"
NOTES_PATH = BASE_DIR / "standardization_notes.md"

STANDARD_COLUMNS = [
    "age_group",
    "gender",
    "smoking_status",
    "alcohol_level",
    "sleep_category",
    "bmi_category",
    "activity_level",
    "blood_pressure_category",
    "glucose_category",
    "cholesterol_category",
    "disease_risk",
    "source_dataset",
]

UNKNOWN = "Unknown"


@dataclass
class DatasetResult:
    dataset_name: str
    output_name: str
    row_count: int
    populated_standardized_columns: list[str]
    original_columns_used: list[str]
    mapping_notes: list[str]
    assumptions: list[str]
    unmapped_columns: list[str]


def normalize_string(value) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "n/a", "na", "null"}:
        return None
    return text


def to_number(value) -> float | None:
    if pd.isna(value):
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped or stripped.lower() in {"nan", "n/a", "na", "none", "null"}:
            return None
        value = stripped
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def map_age_group_from_numeric(value) -> str:
    age = to_number(value)
    if age is None or age < 18:
        return UNKNOWN
    if age <= 24:
        return "18-24"
    if age <= 34:
        return "25-34"
    if age <= 44:
        return "35-44"
    if age <= 54:
        return "45-54"
    if age <= 64:
        return "55-64"
    return "65+"


def map_age_group_from_text(value) -> str:
    text = normalize_string(value)
    if text is None:
        return UNKNOWN

    compact = text.replace(" ", "")
    if compact in {"18-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79"}:
        if compact == "18-24":
            return "18-24"
        start = int(compact.split("-")[0])
        if 25 <= start <= 34:
            return "25-34"
        if 35 <= start <= 44:
            return "35-44"
        if 45 <= start <= 54:
            return "45-54"
        if 55 <= start <= 64:
            return "55-64"
        if start >= 65:
            return "65+"
    if compact == "80+":
        return "65+"
    return UNKNOWN


def map_gender(value) -> str:
    text = normalize_string(value)
    if text is None:
        return "Other/Unknown"

    lowered = text.lower()
    if lowered in {"m", "male", "man"}:
        return "Male"
    if lowered in {"f", "female", "woman"}:
        return "Female"
    if lowered in {"other", "non-binary", "nonbinary"}:
        return "Other/Unknown"
    return "Other/Unknown"


def map_gender_numeric_ambiguous(value) -> str:
    number = to_number(value)
    if number is None:
        return "Other/Unknown"
    return "Other/Unknown"


def map_smoking_yes_no(value) -> str:
    text = normalize_string(value)
    if text is None:
        return UNKNOWN
    lowered = text.lower()
    if lowered in {"no", "n", "false", "0"}:
        return "Non-smoker"
    if lowered in {"yes", "y", "true", "1"}:
        return "Light smoker"
    return UNKNOWN


def map_smoking_text(value) -> str:
    text = normalize_string(value)
    if text is None:
        return UNKNOWN
    lowered = text.lower()
    if lowered in {"never smoked", "never", "non-smoker", "nonsmoker"}:
        return "Non-smoker"
    if lowered in {"formerly smoked", "former smoker"}:
        return "Former smoker"
    if lowered in {"smokes", "current smoker", "smoker"}:
        return "Light smoker"
    if lowered == "unknown":
        return UNKNOWN
    return UNKNOWN


def map_smoking_scale_0_to_10(value) -> str:
    number = to_number(value)
    if number is None:
        return UNKNOWN
    if number <= 0:
        return "Non-smoker"
    if number <= 4:
        return "Light smoker"
    return "Heavy smoker"


def map_alcohol_yes_no(value) -> str:
    text = normalize_string(value)
    if text is None:
        return UNKNOWN
    lowered = text.lower()
    if lowered in {"no", "n", "false", "0"}:
        return "None"
    if lowered in {"yes", "y", "true", "1"}:
        return "Moderate"
    return UNKNOWN


def map_alcohol_scale_monthly(value) -> str:
    number = to_number(value)
    if number is None:
        return UNKNOWN
    if number <= 0:
        return "None"
    if number <= 4:
        return "Low"
    if number <= 14:
        return "Moderate"
    return "High"


def map_alcohol_scale_0_to_10(value) -> str:
    number = to_number(value)
    if number is None:
        return UNKNOWN
    if number <= 0:
        return "None"
    if number <= 3:
        return "Low"
    if number <= 6:
        return "Moderate"
    return "High"


def map_sleep_category(hours) -> str:
    value = to_number(hours)
    if value is None:
        return UNKNOWN
    if value < 6:
        return "Poor"
    if value <= 9:
        return "Normal"
    return "Excess"


def map_bmi_category(value) -> str:
    if isinstance(value, str):
        text = normalize_string(value)
        if text is None:
            return UNKNOWN
        lowered = text.lower()
        text_map = {
            "underweight": "Underweight",
            "normal": "Normal",
            "normal weight": "Normal",
            "overweight": "Overweight",
            "obese": "Obese",
            "obesity": "Obese",
        }
        if lowered in text_map:
            return text_map[lowered]

    bmi = to_number(value)
    if bmi is None:
        return UNKNOWN
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def map_activity_from_steps(value) -> str:
    steps = to_number(value)
    if steps is None:
        return UNKNOWN
    if steps < 5000:
        return "Low"
    if steps < 9000:
        return "Medium"
    return "High"


def map_activity_numeric_0_to_100(value) -> str:
    number = to_number(value)
    if number is None:
        return UNKNOWN
    if number < 40:
        return "Low"
    if number < 70:
        return "Medium"
    return "High"


def map_activity_numeric_0_to_10(value) -> str:
    number = to_number(value)
    if number is None:
        return UNKNOWN
    if number <= 3:
        return "Low"
    if number <= 6:
        return "Medium"
    return "High"


def map_activity_yes_no(value) -> str:
    text = normalize_string(value)
    if text is None:
        return UNKNOWN
    lowered = text.lower()
    if lowered in {"no", "n", "false", "0"}:
        return "Low"
    if lowered in {"yes", "y", "true", "1"}:
        return "Medium"
    return UNKNOWN


def map_bp_from_string(value) -> str:
    text = normalize_string(value)
    if text is None or "/" not in text:
        return UNKNOWN
    try:
        systolic_text, diastolic_text = text.split("/", 1)
        systolic = float(systolic_text)
        diastolic = float(diastolic_text)
    except ValueError:
        return UNKNOWN
    return map_bp_from_pair(systolic, diastolic)


def map_bp_from_pair(systolic, diastolic=None) -> str:
    systolic_value = to_number(systolic)
    diastolic_value = to_number(diastolic)
    if systolic_value is None or systolic_value <= 0:
        return UNKNOWN
    if diastolic_value is not None and diastolic_value > 0:
        if systolic_value < 120 and diastolic_value < 80:
            return "Normal"
        if 120 <= systolic_value < 130 and diastolic_value < 80:
            return "Elevated"
        return "High"
    if systolic_value < 120:
        return "Normal"
    if systolic_value < 130:
        return "Elevated"
    return "High"


def map_bp_from_hypertension(value) -> str:
    text = normalize_string(value)
    if text is None:
        return UNKNOWN
    lowered = text.lower()
    if lowered in {"0", "no", "false", "n"}:
        return "Normal"
    if lowered in {"1", "yes", "true", "y"}:
        return "High"
    return UNKNOWN


def map_glucose_numeric(value) -> str:
    number = to_number(value)
    if number is None or number <= 0:
        return UNKNOWN
    if number < 100:
        return "Normal"
    if number < 126:
        return "Prediabetic/Elevated"
    return "High"


def map_glucose_binary_fasting(value) -> str:
    number = to_number(value)
    if number is None:
        return UNKNOWN
    if number <= 0:
        return "Normal"
    return "High"


def map_cholesterol_numeric(value) -> str:
    number = to_number(value)
    if number is None or number <= 0:
        return UNKNOWN
    if number < 200:
        return "Normal"
    if number < 240:
        return "Elevated"
    return "High"


def map_disease_risk_binary(value) -> str:
    number = to_number(value)
    if number is None:
        return UNKNOWN
    if number <= 0:
        return "None/Low"
    return "Diagnosed/High"


def map_disease_risk_yes_no(value) -> str:
    text = normalize_string(value)
    if text is None:
        return UNKNOWN
    lowered = text.lower()
    if lowered in {"no", "n", "false", "0"}:
        return "None/Low"
    if lowered in {"yes", "y", "true", "1"}:
        return "Diagnosed/High"
    return UNKNOWN


def map_disease_risk_sleep_disorder(value) -> str:
    text = normalize_string(value)
    if text is None:
        return UNKNOWN
    lowered = text.lower()
    if lowered == "none":
        return "None/Low"
    if lowered in {"insomnia", "sleep apnea"}:
        return "Diagnosed/High"
    return UNKNOWN


def map_disease_risk_from_risk_level(value) -> str:
    text = normalize_string(value)
    if text is None:
        return UNKNOWN
    lowered = text.lower()
    if lowered == "low":
        return "None/Low"
    if lowered == "medium":
        return "At risk"
    if lowered == "high":
        return "Diagnosed/High"
    return UNKNOWN


def apply_standard_columns(df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
    standardized = df.copy()
    for column in STANDARD_COLUMNS:
        if column not in standardized.columns:
            standardized[column] = UNKNOWN if column != "source_dataset" else dataset_name
    standardized["source_dataset"] = dataset_name
    return standardized


def populated_columns(df: pd.DataFrame) -> list[str]:
    columns = []
    for column in STANDARD_COLUMNS:
        if column == "source_dataset":
            columns.append(column)
            continue
        if column not in df.columns:
            continue
        non_unknown = df[column].fillna(UNKNOWN).astype(str).ne(UNKNOWN).any()
        if non_unknown:
            columns.append(column)
    return columns


def process_sleep_dataset() -> DatasetResult:
    path = DATA_DIR / "sleep" / "sleep_health_and_lifestyle_dataset.csv"
    df = pd.read_csv(path, keep_default_na=False)
    df = apply_standard_columns(df, "sleep")

    df["age_group"] = df["Age"].apply(map_age_group_from_numeric)
    df["gender"] = df["Gender"].apply(map_gender)
    df["sleep_category"] = df["Sleep Duration"].apply(map_sleep_category)
    df["bmi_category"] = df["BMI Category"].apply(map_bmi_category)
    df["activity_level"] = df["Daily Steps"].apply(map_activity_from_steps)
    df["blood_pressure_category"] = df["Blood Pressure"].apply(map_bp_from_string)
    df["disease_risk"] = df["Sleep Disorder"].apply(map_disease_risk_sleep_disorder)

    output_name = "sleep_standardized.csv"
    df.to_csv(OUTPUT_DIR / output_name, index=False)

    return DatasetResult(
        dataset_name="sleep",
        output_name=output_name,
        row_count=len(df),
        populated_standardized_columns=populated_columns(df),
        original_columns_used=[
            "Age",
            "Gender",
            "Sleep Duration",
            "BMI Category",
            "Daily Steps",
            "Blood Pressure",
            "Sleep Disorder",
        ],
        mapping_notes=[
            "`Age` -> `age_group` using the shared 18-24 to 65+ buckets.",
            "`Gender` -> `gender` with text normalization (`Male`, `Female`).",
            "`Sleep Duration` -> `sleep_category` using Poor (<6), Normal (6-9), Excess (>9).",
            "`BMI Category` -> `bmi_category` by normalizing the source text labels to `Underweight`, `Normal`, `Overweight`, `Obese`.",
            "`Daily Steps` -> `activity_level` with thresholds: Low <5000, Medium 5000-8999, High >=9000.",
            "`Blood Pressure` -> `blood_pressure_category` by splitting systolic/diastolic values and applying: Normal <120/<80, Elevated 120-129 and <80, otherwise High.",
            "`Sleep Disorder` -> `disease_risk` where `None` becomes `None/Low` and diagnosed disorders become `Diagnosed/High`.",
        ],
        assumptions=[
            "Used `Daily Steps` instead of `Physical Activity Level` because step count is easier to explain and bucket consistently.",
            "Standardized fields with no matching source column were left as `Unknown` to preserve a shared schema.",
            "Literal `None` values in `Sleep Disorder` were preserved during CSV import so they can be mapped to `None/Low` instead of being treated as missing.",
        ],
        unmapped_columns=[
            "Person ID",
            "Occupation",
            "Quality of Sleep",
            "Physical Activity Level",
            "Stress Level",
            "Heart Rate",
        ],
    )


def process_body_dataset() -> DatasetResult:
    path = DATA_DIR / "body" / "CVD_cleaned.csv"
    df = pd.read_csv(path)
    df = apply_standard_columns(df, "cardiovascular_body")

    df["age_group"] = df["Age_Category"].apply(map_age_group_from_text)
    df["gender"] = df["Sex"].apply(map_gender)
    df["smoking_status"] = df["Smoking_History"].apply(map_smoking_yes_no)
    df["alcohol_level"] = df["Alcohol_Consumption"].apply(map_alcohol_scale_monthly)
    df["bmi_category"] = df["BMI"].apply(map_bmi_category)
    df["activity_level"] = df["Exercise"].apply(map_activity_yes_no)
    df["disease_risk"] = df["Heart_Disease"].apply(map_disease_risk_yes_no)

    output_name = "cardiovascular_body_standardized.csv"
    df.to_csv(OUTPUT_DIR / output_name, index=False)

    return DatasetResult(
        dataset_name="cardiovascular_body",
        output_name=output_name,
        row_count=len(df),
        populated_standardized_columns=populated_columns(df),
        original_columns_used=[
            "Age_Category",
            "Sex",
            "Smoking_History",
            "Alcohol_Consumption",
            "BMI",
            "Exercise",
            "Heart_Disease",
        ],
        mapping_notes=[
            "`Age_Category` -> `age_group` by collapsing source ranges like `25-29` and `30-34` into the shared `25-34` bucket, and `80+` into `65+`.",
            "`Sex` -> `gender` with text normalization.",
            "`Smoking_History` -> `smoking_status` where `No` becomes `Non-smoker` and `Yes` becomes `Light smoker` because only yes/no detail is available.",
            "`Alcohol_Consumption` -> `alcohol_level` using thresholds: 0 None, 1-4 Low, 5-14 Moderate, 15+ High.",
            "`BMI` -> `bmi_category` using standard BMI cutoffs.",
            "`Exercise` -> `activity_level` where `No` becomes `Low` and `Yes` becomes `Medium` because the dataset does not provide activity intensity or duration.",
            "`Heart_Disease` -> `disease_risk` where `No` becomes `None/Low` and `Yes` becomes `Diagnosed/High`.",
        ],
        assumptions=[
            "The exact unit of `Alcohol_Consumption` is not encoded in the CSV header, so thresholds were chosen as sensible ordinal buckets and documented for transparency.",
            "Because `Exercise` is only yes/no, rows cannot be distinguished into `Medium` versus `High` activity with confidence.",
            "Columns for blood pressure, glucose, cholesterol, and sleep do not exist in this dataset, so those shared variables remain `Unknown`.",
        ],
        unmapped_columns=[
            "General_Health",
            "Checkup",
            "Skin_Cancer",
            "Other_Cancer",
            "Depression",
            "Diabetes",
            "Arthritis",
            "Height_(cm)",
            "Weight_(kg)",
            "Fruit_Consumption",
            "Green_Vegetables_Consumption",
            "FriedPotato_Consumption",
        ],
    )


def process_heart_dataset() -> DatasetResult:
    path = DATA_DIR / "disease" / "heart.csv"
    df = pd.read_csv(path)
    df = apply_standard_columns(df, "heart_disease")

    df["age_group"] = df["Age"].apply(map_age_group_from_numeric)
    df["gender"] = df["Sex"].apply(map_gender)
    df["blood_pressure_category"] = df["RestingBP"].apply(map_bp_from_pair)
    df["glucose_category"] = df["FastingBS"].apply(map_glucose_binary_fasting)
    df["cholesterol_category"] = df["Cholesterol"].apply(map_cholesterol_numeric)
    df["disease_risk"] = df["HeartDisease"].apply(map_disease_risk_binary)

    output_name = "heart_disease_standardized.csv"
    df.to_csv(OUTPUT_DIR / output_name, index=False)

    return DatasetResult(
        dataset_name="heart_disease",
        output_name=output_name,
        row_count=len(df),
        populated_standardized_columns=populated_columns(df),
        original_columns_used=[
            "Age",
            "Sex",
            "RestingBP",
            "Cholesterol",
            "FastingBS",
            "MaxHR",
            "HeartDisease",
        ],
        mapping_notes=[
            "`Age` -> `age_group` using the shared age buckets.",
            "`Sex` -> `gender` by normalizing `M` and `F` to `Male` and `Female`.",
            "`RestingBP` -> `blood_pressure_category` using systolic-only thresholds: Normal <120, Elevated 120-129, High >=130. Zero values were treated as missing.",
            "`Cholesterol` -> `cholesterol_category` using mg/dL-style thresholds: Normal <200, Elevated 200-239, High >=240. Zero values were treated as missing.",
            "`FastingBS` -> `glucose_category` where 0 becomes `Normal` and 1 becomes `High` because the source is a binary elevated fasting blood sugar flag.",
            "`HeartDisease` -> `disease_risk` where 0 becomes `None/Low` and 1 becomes `Diagnosed/High`.",
        ],
        assumptions=[
            "This dataset does not contain direct lifestyle variables for smoking, alcohol, sleep, BMI, or physical activity behavior, so those remain `Unknown` rather than being inferred from weak physiological proxies.",
        ],
        unmapped_columns=[
            "ChestPainType",
            "RestingECG",
            "MaxHR",
            "ExerciseAngina",
            "Oldpeak",
            "ST_Slope",
        ],
    )


def process_stroke_dataset() -> DatasetResult:
    path = DATA_DIR / "disease" / "healthcare-dataset-stroke-data.csv"
    df = pd.read_csv(path)
    df = apply_standard_columns(df, "stroke")

    df["age_group"] = df["age"].apply(map_age_group_from_numeric)
    df["gender"] = df["gender"].apply(map_gender)
    df["smoking_status"] = df["smoking_status"].apply(map_smoking_text)
    df["bmi_category"] = df["bmi"].apply(map_bmi_category)
    df["blood_pressure_category"] = df["hypertension"].apply(map_bp_from_hypertension)
    df["glucose_category"] = df["avg_glucose_level"].apply(map_glucose_numeric)
    df["disease_risk"] = df["stroke"].apply(map_disease_risk_binary)

    output_name = "stroke_standardized.csv"
    df.to_csv(OUTPUT_DIR / output_name, index=False)

    return DatasetResult(
        dataset_name="stroke",
        output_name=output_name,
        row_count=len(df),
        populated_standardized_columns=populated_columns(df),
        original_columns_used=[
            "age",
            "gender",
            "smoking_status",
            "bmi",
            "hypertension",
            "avg_glucose_level",
            "stroke",
        ],
        mapping_notes=[
            "`age` -> `age_group` using the shared age buckets. Source rows below 18 were mapped to `Unknown` because the target schema starts at 18.",
            "`gender` -> `gender` with text normalization; source `Other` becomes `Other/Unknown`.",
            "`smoking_status` -> `smoking_status` by normalizing values like `never smoked`, `formerly smoked`, and `smokes`.",
            "`bmi` -> `bmi_category` using standard BMI cutoffs.",
            "`hypertension` -> `blood_pressure_category` where 0 becomes `Normal` and 1 becomes `High` because only a binary hypertension flag is available.",
            "`avg_glucose_level` -> `glucose_category` using thresholds: Normal <100, Prediabetic/Elevated 100-125.9, High >=126.",
            "`stroke` -> `disease_risk` where 0 becomes `None/Low` and 1 becomes `Diagnosed/High`.",
        ],
        assumptions=[
            "The source dataset contains some children, but the project's shared age schema starts at 18, so those rows were marked `Unknown` for `age_group`.",
            "No alcohol, sleep duration, cholesterol, or direct activity measure is present, so those standardized variables remain `Unknown`.",
            "Missing BMI values (including source `N/A`) were carried through safely and standardized to `Unknown`.",
        ],
        unmapped_columns=[
            "id",
            "heart_disease",
            "ever_married",
            "work_type",
            "Residence_type",
        ],
    )


def process_cancer_dataset() -> DatasetResult:
    path = DATA_DIR / "disease" / "cancer-risk-factors.csv"
    df = pd.read_csv(path)
    df = apply_standard_columns(df, "cancer_risk")

    df["age_group"] = df["Age"].apply(map_age_group_from_numeric)
    df["gender"] = df["Gender"].apply(map_gender_numeric_ambiguous)
    df["smoking_status"] = df["Smoking"].apply(map_smoking_scale_0_to_10)
    df["alcohol_level"] = df["Alcohol_Use"].apply(map_alcohol_scale_0_to_10)
    df["bmi_category"] = df["BMI"].apply(map_bmi_category)
    df["activity_level"] = df["Physical_Activity_Level"].apply(map_activity_numeric_0_to_10)
    df["disease_risk"] = df["Risk_Level"].apply(map_disease_risk_from_risk_level)

    output_name = "cancer_risk_standardized.csv"
    df.to_csv(OUTPUT_DIR / output_name, index=False)

    return DatasetResult(
        dataset_name="cancer_risk",
        output_name=output_name,
        row_count=len(df),
        populated_standardized_columns=populated_columns(df),
        original_columns_used=[
            "Age",
            "Gender",
            "Smoking",
            "Alcohol_Use",
            "BMI",
            "Physical_Activity_Level",
            "Risk_Level",
        ],
        mapping_notes=[
            "`Age` -> `age_group` using the shared age buckets.",
            "`Smoking` -> `smoking_status` using a documented ordinal mapping on the source 0-10 scale: 0 `Non-smoker`, 1-4 `Light smoker`, 5-10 `Heavy smoker`.",
            "`Alcohol_Use` -> `alcohol_level` using a documented ordinal mapping on the source 0-10 scale: 0 `None`, 1-3 `Low`, 4-6 `Moderate`, 7-10 `High`.",
            "`BMI` -> `bmi_category` using standard BMI cutoffs.",
            "`Physical_Activity_Level` -> `activity_level` using 0-3 `Low`, 4-6 `Medium`, 7-10 `High`.",
            "`Risk_Level` -> `disease_risk` where `Low` becomes `None/Low`, `Medium` becomes `At risk`, and `High` becomes `Diagnosed/High`.",
        ],
        assumptions=[
            "The `Gender` column is encoded as 0/1, but the CSV does not define which number corresponds to which sex. To avoid guessing blindly, all cancer-dataset values were standardized to `Other/Unknown`.",
            "The smoking, alcohol, and activity fields appear to be ordinal 0-10 scores rather than real-world units, so bucket thresholds were chosen for consistency and documented rather than treated as literal cigarettes/day or drinks/week.",
            "No direct sleep, blood pressure, glucose, or cholesterol columns exist in this dataset, so those shared variables remain `Unknown`.",
        ],
        unmapped_columns=[
            "Patient_ID",
            "Cancer_Type",
            "Obesity",
            "Family_History",
            "Diet_Red_Meat",
            "Diet_Salted_Processed",
            "Fruit_Veg_Intake",
            "Physical_Activity",
            "Air_Pollution",
            "Occupational_Hazards",
            "BRCA_Mutation",
            "H_Pylori_Infection",
            "Calcium_Intake",
            "Overall_Risk_Score",
        ],
    )


def write_notes(results: list[DatasetResult]) -> None:
    lines = [
        "# Standardization Notes",
        "",
        "This file documents how each health dataset was standardized into a shared schema for the interactive visualization prototype.",
        "",
        "## Shared standardized variables",
        "",
        ", ".join(f"`{column}`" for column in STANDARD_COLUMNS),
        "",
        "## Dataset-by-dataset mappings",
        "",
    ]

    for result in results:
        lines.extend(
            [
                f"### {result.dataset_name}",
                "",
                f"- Source file output: `data/standardized/{result.output_name}`",
                f"- Rows: {result.row_count}",
                f"- Original columns used: {', '.join(f'`{column}`' for column in result.original_columns_used)}",
                f"- Standardized columns populated: {', '.join(f'`{column}`' for column in result.populated_standardized_columns)}",
                "",
                "#### Mapping details",
                "",
            ]
        )
        lines.extend([f"- {note}" for note in result.mapping_notes])
        lines.extend(["", "#### Assumptions and missing values", ""])
        lines.extend([f"- {note}" for note in result.assumptions])
        lines.extend(["", "#### Columns not mapped into shared variables", ""])
        lines.extend([f"- `{column}`" for column in result.unmapped_columns])
        lines.append("")

    NOTES_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    processors: list[Callable[[], DatasetResult]] = [
        process_sleep_dataset,
        process_body_dataset,
        process_heart_dataset,
        process_stroke_dataset,
        process_cancer_dataset,
    ]

    results = [processor() for processor in processors]
    write_notes(results)

    print("Standardization summary")
    for result in results:
        print(
            f"- {result.output_name}: {result.row_count} rows | "
            f"standardized columns populated: {', '.join(result.populated_standardized_columns)}"
        )
    print(f"- standardization_notes.md written to: {NOTES_PATH}")


if __name__ == "__main__":
    main()
