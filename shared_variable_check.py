from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
NOTES_PATH = BASE_DIR / "standardization_notes.md"
STANDARDIZED_DIR = BASE_DIR / "data" / "standardized"

DEFAULT_SHARED_VARS = [
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

# Comment out any variables here that you do not want to inspect.
INSPECT_VARIABLES = [
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
    # "source_dataset",
]

UNKNOWN_VALUES = {
    "",
    "unknown",
    "other/unknown",
    "nan",
    "none",
    "null",
    "n/a",
    "na",
}


def load_shared_variables() -> list[str]:
    if not NOTES_PATH.exists():
        return DEFAULT_SHARED_VARS

    content = NOTES_PATH.read_text(encoding="utf-8")
    section_match = re.search(
        r"## Shared standardized variables\s+(.+?)(?:\n## |\Z)",
        content,
        flags=re.DOTALL,
    )
    if not section_match:
        return DEFAULT_SHARED_VARS

    shared_vars = re.findall(r"`([^`]+)`", section_match.group(1))
    return shared_vars or DEFAULT_SHARED_VARS


def discover_standardized_files() -> dict[str, Path]:
    files = sorted(STANDARDIZED_DIR.glob("**/*_standardized.csv"))
    return {path.stem.replace("_standardized", ""): path for path in files}


def normalize_value(value: object) -> str | None:
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    if text.lower() in UNKNOWN_VALUES:
        return None

    return text


def collect_usable_values(
    files: dict[str, Path],
    variables: list[str],
) -> dict[str, dict[str, set[str]]]:
    value_map: dict[str, dict[str, set[str]]] = {var: {} for var in variables}

    for dataset_name, path in files.items():
        df = pd.read_csv(path)
        for var in variables:
            if var not in df.columns:
                value_map[var][dataset_name] = set()
                continue

            usable_values = {
                value for value in df[var].map(normalize_value).dropna().tolist() if value is not None
            }
            value_map[var][dataset_name] = usable_values

    return value_map


def print_shared_variable_summary(
    files: dict[str, Path],
    variables: list[str],
) -> None:
    value_map = collect_usable_values(files, variables)
    dataset_names = sorted(files)
    dataset_count = len(dataset_names)

    print("\n=== SHARED VARIABLES ACROSS DATASETS ===\n")
    print("Datasets:")
    for dataset_name in dataset_names:
        print(f"- {dataset_name}: {files[dataset_name].relative_to(BASE_DIR)}")

    print("\nVariables inspected:")
    for variable in variables:
        print(f"- {variable}")

    print("\n=== RESULTS ===")
    for variable in variables:
        dataset_values = value_map[variable]
        datasets_with_data = sorted(
            dataset_name for dataset_name, values in dataset_values.items() if values
        )
        datasets_without_data = sorted(
            dataset_name for dataset_name, values in dataset_values.items() if not values
        )
        common_values = (
            sorted(set.intersection(*(dataset_values[name] for name in dataset_names)))
            if dataset_names and all(dataset_values[name] for name in dataset_names)
            else []
        )

        print(f"\n{variable}")
        print(f"  datasets with usable data: {len(datasets_with_data)}/{dataset_count}")
        print(f"  dataset list: {', '.join(datasets_with_data) if datasets_with_data else 'none'}")
        print(
            "  datasets missing usable data: "
            + (", ".join(datasets_without_data) if datasets_without_data else "none")
        )

        if len(datasets_with_data) == dataset_count:
            print("  shared across all datasets: YES")
            print(
                "  common values: "
                + (", ".join(common_values) if common_values else "none")
            )
        else:
            print("  shared across all datasets: NO")


def main() -> None:
    available_shared_vars = set(load_shared_variables())
    files = discover_standardized_files()

    if not files:
        print(f"No standardized CSV files found under {STANDARDIZED_DIR}")
        return

    variables_to_check = [var for var in INSPECT_VARIABLES if var in available_shared_vars]

    if not variables_to_check:
        print("No variables selected for inspection.")
        return

    print_shared_variable_summary(files, variables_to_check)


if __name__ == "__main__":
    main()
