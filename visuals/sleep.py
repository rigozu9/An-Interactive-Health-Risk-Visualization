import pandas as pd
import plotly.graph_objects as go


def load_sleep_data():
    """Load the standardized sleep dataset."""
    return pd.read_csv("data/standardized/sleep/sleep_standardized.csv")

def add_sleep_bins(df):
    """Add grouped categories for stress level and quality of sleep."""

    df = df.copy()

    df["stress_group"] = pd.cut(
        df["Stress Level"],
        bins=[2, 4, 6, 8],
        labels=["Low", "Medium", "High"],
        include_lowest=True,
    )

    df["sleep_quality_group"] = pd.cut(
        df["Quality of Sleep"],
        bins=[3, 5, 7, 9],
        labels=["Poor", "Normal", "Good"],
        include_lowest=True,
    )

    return df

def filter_by_age_group(df, age_group="All"):
    """Filter the dataframe by age group."""

    if age_group == "All" or age_group is None:
        return df

    return df[df["age_group"] == age_group]

def make_sleep_heatmap(df, age_group="All"):
    """
    Create a heatmap showing the relationship between grouped stress level
    and grouped quality of sleep.

    Filter:
    - age_group

    Visual variables:
    - stress_group
    - sleep_quality_group

    Cell color:
    - Number of people

    Cell label:
    - Percentage of total people
    """

    df = filter_by_age_group(df, age_group)
    df = add_sleep_bins(df)

    heatmap_data = (
        df.groupby(["stress_group", "sleep_quality_group"], observed=False)
        .size()
        .reset_index(name="count")
    )
    total_count = heatmap_data["count"].sum()
    heatmap_data["percentage"] = (
        heatmap_data["count"] / total_count * 100
    ).round().astype(int)
    heatmap_data["percentage_label"] = heatmap_data["percentage"].astype(str) + "%"

    stress_order = ["Low", "Medium", "High"]
    sleep_quality_order = ["Poor", "Normal", "Good"]

    count_grid = heatmap_data.pivot(
        index="sleep_quality_group",
        columns="stress_group",
        values="count",
    ).reindex(index=sleep_quality_order, columns=stress_order)

    percentage_grid = heatmap_data.pivot(
        index="sleep_quality_group",
        columns="stress_group",
        values="percentage_label",
    ).reindex(index=sleep_quality_order, columns=stress_order)

    fig = go.Figure(
        data=go.Heatmap(
            x=stress_order,
            y=sleep_quality_order,
            z=count_grid.values,
            text=percentage_grid.values,
            texttemplate="%{text}",
            textfont=dict(size=16, color="black"),
            colorscale="Blues",
            colorbar=dict(title="People"),
            hovertemplate=(
                "Stress Level: %{x}<br>"
                "Quality of Sleep: %{y}<br>"
                "People: %{z}<br>"
                "Share: %{text}<extra></extra>"
            ),
        ),
    )

    fig.update_layout(
        title=f"Sleep Quality by Stress Level ({age_group})",
        xaxis=dict(
            title="Stress Level",
            categoryorder="array",
            categoryarray=stress_order,
        ),
        yaxis=dict(
            title="Quality of Sleep",
            categoryorder="array",
            categoryarray=sleep_quality_order,
        ),
    )

    return fig

if __name__ == "__main__":
    df = load_sleep_data()
    fig = make_sleep_heatmap(df, age_group="25-34")
    fig.show()
