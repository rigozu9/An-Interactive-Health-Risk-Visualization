import pandas as pd
import plotly.graph_objects as go


DISEASE_FILES = {
    "Cancer Risk": "data/standardized/disease/cancer_risk_standardized.csv",
    "Heart Disease": "data/standardized/disease/heart_disease_standardized.csv",
    "Stroke": "data/standardized/disease/stroke_standardized.csv",
}

RISK_FACTOR_COLUMNS = {
    "bmi_category": "BMI",
    "blood_pressure_category": "Blood Pressure",
    "glucose_category": "Glucose",
}

UNKNOWN_VALUES = {"Unknown", "Other/Unknown", "", "nan", "None"}
INCLUDED_DISEASE_RISKS = {"At risk", "Diagnosed/High"}


def load_disease_data():
    """Load and combine the standardized disease datasets."""
    frames = []

    for disease_name, path in DISEASE_FILES.items():
        df = pd.read_csv(path)
        df["disease_dataset"] = disease_name
        frames.append(df)

    return pd.concat(frames, ignore_index=True)

def filter_by_age_group(df, age_group="All"):
    """Filter the dataframe by age group."""

    if age_group == "All" or age_group is None:
        return df

    return df[df["age_group"] == age_group]

def filter_by_bmi_category(df, bmi_category="All"):
    """Filter the dataframe by BMI category."""

    if bmi_category == "All" or bmi_category is None:
        return df

    return df[df["bmi_category"] == bmi_category]

def filter_by_activity_level(df, activity_level="All"):
    """Filter the dataframe by activity level."""

    if activity_level == "All" or activity_level is None:
        return df

    return df[df["activity_level"] == activity_level]

def is_usable_value(value):
    """Check whether a standardized value should be included in the Sankey."""

    if pd.isna(value):
        return False

    return str(value).strip() not in UNKNOWN_VALUES

def map_physiological_risk_factor(column, value):
    """Map detailed standardized values into broader physiological risk factors."""

    if not is_usable_value(value):
        return None

    value = str(value).strip()

    if column == "bmi_category" and value in {"Overweight", "Obese"}:
        return "BMI: Above Normal"

    if column == "blood_pressure_category" and value == "High":
        return "Blood Pressure: High"

    if column == "glucose_category" and value in {"Prediabetic/Elevated", "High"}:
        return "Glucose: Elevated/High"

    return None

def build_sankey_links(df):
    """Build Sankey links from risk factors to disease datasets."""
    first_layer_links = []

    df = df[df["disease_risk"].isin(INCLUDED_DISEASE_RISKS)]
    disease_case_totals = df.groupby("disease_dataset").size().to_dict()

    for column in RISK_FACTOR_COLUMNS:
        usable_df = df.copy()
        usable_df["risk_factor_label"] = usable_df[column].map(
            lambda value: map_physiological_risk_factor(column, value)
        )
        usable_df = usable_df[usable_df["risk_factor_label"].notna()]

        grouped_factors = (
            usable_df.groupby(["risk_factor_label", "disease_dataset"], as_index=False)
            .size()
            .rename(columns={"size": "count"})
        )

        for _, row in grouped_factors.iterrows():
            disease_total = disease_case_totals[row["disease_dataset"]]
            percentage = row["count"] / disease_total * 100
            first_layer_links.append(
                {
                    "source": row["risk_factor_label"],
                    "target": row["disease_dataset"],
                    "value": percentage,
                    "count": row["count"],
                }
            )

    return first_layer_links

def make_disease_sankey(
    df,
    age_group="All",
    bmi_category="All",
    activity_level="All",
):
    """
    Create a Sankey diagram showing disease risk-factor distributions.

    Filter:
    - age_group
    - bmi_category
    - activity_level

    Flow:
    - Risk Factor Category -> Disease Dataset
    """

    df = filter_by_age_group(df, age_group)
    df = filter_by_bmi_category(df, bmi_category)
    df = filter_by_activity_level(df, activity_level)
    links = build_sankey_links(df)

    labels = []
    for link in links:
        if link["source"] not in labels:
            labels.append(link["source"])
        if link["target"] not in labels:
            labels.append(link["target"])

    label_to_index = {label: index for index, label in enumerate(labels)}

    fig = go.Figure(
        data=go.Sankey(
            node=dict(
                pad=18,
                thickness=18,
                line=dict(color="#ffffff", width=0.5),
                label=labels,
            ),
            link=dict(
                source=[label_to_index[link["source"]] for link in links],
                target=[label_to_index[link["target"]] for link in links],
                value=[link["value"] for link in links],
                customdata=[link["count"] for link in links],
                hovertemplate=(
                    "%{source.label} -> %{target.label}<br>"
                    "Share of disease-risk cases: %{value:.1f}%<br>"
                    "Records: %{customdata}<extra></extra>"
                ),
            ),
        )
    )

    fig.update_layout(
        title=f"Risk Factor Categories in Disease-Risk Cases, Normalized by Dataset ({age_group})",
        font=dict(size=12),
    )

    return fig


if __name__ == "__main__":
    df = load_disease_data()
    fig = make_disease_sankey(df, age_group="All")
    fig.show()
