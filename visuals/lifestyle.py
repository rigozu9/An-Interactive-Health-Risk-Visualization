import pandas as pd
import plotly.graph_objects as go


def load_lifestyle_data():
    """Load the standardized cardiovascular/body dataset."""
    return pd.read_csv("data/standardized/body/cardiovascular_body_standardized.csv")

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

def make_smoking_lifestyle_bar_chart(
    df,
    age_group="All",
    bmi_category="All",
    activity_level="All",
):
    """
    Create a grouped bar chart comparing average consumption values
    between smokers and non-smokers.

    Filter:
    - age_group
    - bmi_category
    - activity_level

    Visual variable:
    - Smoking_History

    Bar values:
    - Average Alcohol_Consumption
    - Average Green_Vegetables_Consumption
    - Average FriedPotato_Consumption
    """

    df = filter_by_age_group(df, age_group)
    df = filter_by_bmi_category(df, bmi_category)
    df = filter_by_activity_level(df, activity_level)

    consumption_columns = [
        ("Alcohol_Consumption", "Alcohol", "Alcohol"),
        ("FriedPotato_Consumption", "Fried<br>potatoes", "Fried Potatoes"),
        (
            "Green_Vegetables_Consumption",
            "Green<br>vegetables",
            "Green Vegetables",
        ),
    ]
    colors = {
        "Alcohol": "#5b7fb5",
        "Green Vegetables": "#6fbe59",
        "Fried Potatoes": "#f0a202",
    }

    chart_data = (
        df.groupby("Smoking_History", as_index=False)[
            [column for column, _, _ in consumption_columns]
        ]
        .mean()
        .sort_values("Smoking_History")
    )

    x_positions = []
    smoking_history = []
    tick_labels = []
    hover_labels = []
    averages = []
    bar_colors = []

    for group_index, (_, row) in enumerate(chart_data.iterrows()):
        for measure_index, (column, tick_label, hover_label) in enumerate(
            consumption_columns
        ):
            x_positions.append(group_index * 3 + measure_index)
            smoking_history.append(row["Smoking_History"])
            tick_labels.append(tick_label)
            hover_labels.append(hover_label)
            averages.append(row[column])
            bar_colors.append(colors[hover_label])

    fig = go.Figure(
        data=go.Bar(
            x=x_positions,
            y=averages,
            marker_color=bar_colors,
            text=[round(value, 2) for value in averages],
            textposition="outside",
            width=0.96,
            customdata=list(zip(smoking_history, hover_labels)),
            hovertemplate=(
                "Smoking History: %{customdata[0]}<br>"
                "Measure: %{customdata[1]}<br>"
                "Average: %{y:.2f}<extra></extra>"
            ),
            cliponaxis=False,
        )
    )

    fig.update_layout(
        title=f"Lifestyle ({age_group})",
        yaxis_title="Average Consumption",
        bargap=0,
        showlegend=False,
        plot_bgcolor="white",
        margin=dict(t=110),
        xaxis=dict(
            tickmode="array",
            tickvals=x_positions,
            ticktext=tick_labels,
            title="",
            showline=True,
            linecolor="#cccccc",
        ),
        yaxis=dict(gridcolor="#e8e8e8", rangemode="tozero"),
        shapes=[
            dict(
                type="line",
                x0=2.5,
                x1=2.5,
                y0=0,
                y1=1.06,
                xref="x",
                yref="paper",
                line=dict(color="#cccccc", width=1),
            ),
            dict(
                type="line",
                x0=-0.5,
                x1=5.5,
                y0=1.02,
                y1=1.02,
                xref="x",
                yref="paper",
                line=dict(color="#cccccc", width=1),
            ),
        ],
        annotations=[
            dict(
                x=2.5,
                y=1.55,
                xref="x",
                yref="paper",
                text="<b>Smoking History</b>",
                showarrow=False,
            ),
            dict(x=1, y=1.35, xref="x", yref="paper", text="No", showarrow=False),
            dict(x=4, y=1.35, xref="x", yref="paper", text="Yes", showarrow=False),
        ],
    )

    return fig


if __name__ == "__main__":
    df = load_lifestyle_data()
    fig = make_smoking_lifestyle_bar_chart(df, age_group="All")
    fig.show()
