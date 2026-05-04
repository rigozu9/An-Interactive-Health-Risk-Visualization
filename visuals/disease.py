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

DISEASE_FACTOR_CONFIG = {
    "Cancer Risk": [
        {
            "label": "Heavy smoking",
            "column": "smoking_status",
            "matches": {"Heavy smoker"},
            "description": "standardized smoking score in the heavy range",
        },
        {
            "label": "High alcohol",
            "column": "alcohol_level",
            "matches": {"High"},
            "description": "standardized alcohol score in the high range",
        },
        {
            "label": "BMI above normal",
            "column": "bmi_category",
            "matches": {"Overweight", "Obese"},
            "description": "BMI category is overweight or obese",
        },
        {
            "label": "Low activity",
            "column": "activity_level",
            "matches": {"Low"},
            "description": "standardized physical activity level is low",
        },
        {
            "label": "Family history",
            "column": "Family_History",
            "matches": {1, "1"},
            "description": "family history is marked yes",
        },
    ],
    "Heart Disease": [
        {
            "label": "High blood pressure",
            "column": "blood_pressure_category",
            "matches": {"High"},
            "description": "resting blood pressure is in the high category",
        },
        {
            "label": "High cholesterol",
            "column": "cholesterol_category",
            "matches": {"High"},
            "description": "cholesterol is in the high category",
        },
        {
            "label": "High glucose",
            "column": "glucose_category",
            "matches": {"High"},
            "description": "fasting blood sugar flag is high",
        },
        {
            "label": "Exercise angina",
            "column": "ExerciseAngina",
            "matches": {"Y"},
            "description": "exercise-induced angina is marked yes",
        },
        {
            "label": "Flat/down ST slope",
            "column": "ST_Slope",
            "matches": {"Flat", "Down"},
            "description": "ST slope is flat or down",
        },
    ],
    "Stroke": [
        {
            "label": "High glucose",
            "column": "glucose_category",
            "matches": {"Prediabetic/Elevated", "High"},
            "description": "average glucose is elevated or high",
        },
        {
            "label": "High blood pressure",
            "column": "blood_pressure_category",
            "matches": {"High"},
            "description": "hypertension flag is marked yes",
        },
        {
            "label": "BMI above normal",
            "column": "bmi_category",
            "matches": {"Overweight", "Obese"},
            "description": "BMI category is overweight or obese",
        },
        {
            "label": "Smoked",
            "column": "smoking_status",
            "matches": {"Former smoker", "Light smoker"},
            "description": "smoking status is current or former smoking",
        },
        {
            "label": "Heart disease history",
            "column": "heart_disease",
            "matches": {1, "1"},
            "description": "previous heart disease is marked yes",
        },
    ],
}


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

def apply_supported_filters(df, age_group="All", bmi_category="All", activity_level="All"):
    """Apply global filters only when the selected disease dataset supports them."""

    skipped_filters = []

    if age_group != "All" and age_group is not None:
        df = filter_by_age_group(df, age_group)

    if bmi_category != "All" and bmi_category is not None:
        if "bmi_category" in df and bmi_category in set(df["bmi_category"].dropna()):
            df = filter_by_bmi_category(df, bmi_category)
        else:
            skipped_filters.append("BMI")

    if activity_level != "All" and activity_level is not None:
        if "activity_level" in df and activity_level in set(df["activity_level"].dropna()):
            df = filter_by_activity_level(df, activity_level)
        else:
            skipped_filters.append("activity")

    return df, skipped_filters

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

def make_empty_disease_profile(message):
    """Create an empty-state figure for filter combinations with no disease cases."""

    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5,
        y=0.5,
        xref="paper",
        yref="paper",
        showarrow=False,
        font=dict(size=16, color="#4b5563"),
        align="center",
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig

def calculate_factor_stats(df, factor_config):
    """Calculate the share of disease-risk cases that match each factor."""

    risk_cases = df[df["disease_risk"].isin(INCLUDED_DISEASE_RISKS)]
    total = len(risk_cases)
    stats = []

    for factor in factor_config:
        column = factor["column"]
        if column not in risk_cases.columns:
            continue

        values = risk_cases[column]
        usable_values = values[values.map(is_usable_value)]
        if usable_values.empty:
            continue

        matched = values.isin(factor["matches"])
        count = int(matched.sum())
        percentage = count / total * 100 if total else 0

        stats.append(
            {
                "label": factor["label"],
                "description": factor["description"],
                "count": count,
                "percentage": percentage,
            }
        )

    return stats, total

def make_disease_profile(
    df,
    disease_dataset="Cancer Risk",
    age_group="All",
    bmi_category="All",
    activity_level="All",
):
    """
    Create a disease-specific risk factor profile.

    The selected disease controls which columns are used so the chart does not
    imply that every disease dataset contains the same variables.
    """

    df = df[df["disease_dataset"] == disease_dataset]
    df, skipped_filters = apply_supported_filters(
        df,
        age_group=age_group,
        bmi_category=bmi_category,
        activity_level=activity_level,
    )

    factor_config = DISEASE_FACTOR_CONFIG[disease_dataset]
    stats, total = calculate_factor_stats(df, factor_config)

    if total == 0 or not stats:
        return make_empty_disease_profile(
            f"No disease-risk cases found for {disease_dataset}<br>"
            "with the selected filters."
        )

    x_values = list(range(len(stats)))
    percentages = [stat["percentage"] for stat in stats]
    labels = [stat["label"].replace(" ", "<br>") for stat in stats]
    text = [f"{stat['percentage']:.0f}%" for stat in stats]
    hover_data = [
        (
            stat["label"],
            stat["description"],
            stat["count"],
            total,
            stat["percentage"],
        )
        for stat in stats
    ]

    fig = go.Figure(
        data=go.Scatter(
            x=x_values,
            y=[0] * len(stats),
            mode="markers+text",
            marker=dict(
                symbol="square",
                size=96,
                color=percentages,
                colorscale="YlOrRd",
                cmin=0,
                cmax=100,
                line=dict(color="white", width=2),
                colorbar=dict(
                title="Share",
                thickness=20,
                len=1.3,
            )
            ),
            text=text,
            textfont=dict(size=18, color="#111827"),
            customdata=hover_data,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "Disease-risk records with factor: %{customdata[2]} / %{customdata[3]}<br>"
                "Share: %{customdata[4]:.1f}%<extra></extra>"
            ),
        )
    )

    skipped_note = ""
    if skipped_filters:
        skipped_note = "<br><sup>Skipped unsupported filter(s): " + ", ".join(skipped_filters) + "</sup>"

    fig.update_layout(
        title=(
            f"{disease_dataset} Risk Factor Profile"
            f"<br><sup>Among {total} disease-risk records after supported filters</sup>"
            f"{skipped_note}"
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=x_values,
            ticktext=labels,
            range=[-0.6, len(stats) - 0.4],
            showgrid=False,
            zeroline=False,
            title="",
            tickfont=dict(size=13),
        ),
        yaxis=dict(
            range=[-0.8, 0.8],
            showgrid=False,
            zeroline=False,
            visible=False,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=30, r=30, t=95, b=80),
        font=dict(size=13),
    )

    return fig


if __name__ == "__main__":
    df = load_disease_data()
    fig = make_disease_profile(df, disease_dataset="Cancer Risk", age_group="All")
    fig.show()
