from dash import Dash, Input, Output, dcc, html

from visuals.sleep import load_sleep_data, make_sleep_heatmap
from visuals.lifestyle import (
    load_lifestyle_data,
    make_smoking_lifestyle_bar_chart,
)
from visuals.disease import load_disease_data, make_disease_sankey

app = Dash(__name__)

sleep_df = load_sleep_data()
lifestyle_df = load_lifestyle_data()
disease_df = load_disease_data()
age_group_options = [
    {"label": "All", "value": "All"},
    *[
        {"label": age_group, "value": age_group}
        for age_group in sorted(sleep_df["age_group"].dropna().unique())
        if age_group != "Unknown"
    ],
]
bmi_category_options = [
    {"label": "All", "value": "All"},
    *[
        {"label": bmi_category, "value": bmi_category}
        for bmi_category in ["Normal", "Overweight", "Obese"]
        if bmi_category in set(sleep_df["bmi_category"].dropna().unique())
    ],
]
activity_level_options = [
    {"label": "All", "value": "All"},
    *[
        {"label": activity_level, "value": activity_level}
        for activity_level in ["Low", "Medium", "High"]
        if activity_level in set(sleep_df["activity_level"].dropna().unique())
    ],
]

APP_STYLE = {
    "height": "100vh",
    "display": "grid",
    "gridTemplateRows": "auto 1fr 1fr",
    "gap": "12px",
    "padding": "16px",
    "boxSizing": "border-box",
    "fontFamily": "Arial, sans-serif",
    "backgroundColor": "#f7f8fa",
}

HEADER_STYLE = {
    "margin": "0",
    "fontSize": "28px",
    "color": "#253858",
}

HEADER_ROW_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "spaceBetween",
    "gap": "16px",
}

FILTER_BAR_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "gap": "8px",
}

FILTER_LABEL_STYLE = {
    "fontSize": "14px",
    "fontWeight": "600",
    "color": "#253858",
}

FILTER_DROPDOWN_STYLE = {
    "width": "180px",
}

GRID_ROW_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "1fr 1fr",
    "gap": "12px",
    "minHeight": "0",
}

CARD_STYLE = {
    "backgroundColor": "white",
    "border": "1px solid #e5e7eb",
    "borderRadius": "8px",
    "padding": "10px",
    "display": "flex",
    "flexDirection": "column",
    "minHeight": "0",
}

CARD_TITLE_STYLE = {
    "margin": "0 0 4px 0",
    "fontSize": "18px",
    "color": "#253858",
}

GRAPH_STYLE = {
    "height": "100%",
    "minHeight": "0",
}

app.layout = html.Div(
    style=APP_STYLE,
    children=[
        html.Div(
            style=HEADER_ROW_STYLE,
            children=[
                html.H1("Health Lifestyle Dashboard", style=HEADER_STYLE),
                html.Div(
                    style=FILTER_BAR_STYLE,
                    children=[
                        html.Label("Age Group", style=FILTER_LABEL_STYLE),
                        dcc.Dropdown(
                            id="age-group-filter",
                            options=age_group_options,
                            value="All",
                            clearable=False,
                            style=FILTER_DROPDOWN_STYLE,
                        ),
                        html.Label("BMI Category", style=FILTER_LABEL_STYLE),
                        dcc.Dropdown(
                            id="bmi-category-filter",
                            options=bmi_category_options,
                            value="All",
                            clearable=False,
                            style=FILTER_DROPDOWN_STYLE,
                        ),
                        html.Label("Activity Level", style=FILTER_LABEL_STYLE),
                        dcc.Dropdown(
                            id="activity-level-filter",
                            options=activity_level_options,
                            value="All",
                            clearable=False,
                            style=FILTER_DROPDOWN_STYLE,
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            style=GRID_ROW_STYLE,
            children=[
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.H2("Sleep", style=CARD_TITLE_STYLE),
                        dcc.Graph(
                            id="sleep-chart",
                            figure=make_sleep_heatmap(sleep_df),
                            style=GRAPH_STYLE,
                        ),
                    ],
                ),
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.H2("Lifestyle", style=CARD_TITLE_STYLE),
                        dcc.Graph(
                            id="lifestyle-chart",
                            figure=make_smoking_lifestyle_bar_chart(lifestyle_df),
                            style=GRAPH_STYLE,
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            style=CARD_STYLE,
            children=[
                html.H2("Disease", style=CARD_TITLE_STYLE),
                dcc.Graph(
                    id="disease-chart",
                    figure=make_disease_sankey(disease_df),
                    style=GRAPH_STYLE,
                ),
            ],
        ),
    ]
)

@app.callback(
    Output("sleep-chart", "figure"),
    Output("lifestyle-chart", "figure"),
    Output("disease-chart", "figure"),
    Input("age-group-filter", "value"),
    Input("bmi-category-filter", "value"),
    Input("activity-level-filter", "value"),
)
def update_dashboard(age_group, bmi_category, activity_level):
    sleep_fig = make_sleep_heatmap(
        sleep_df,
        age_group=age_group,
        bmi_category=bmi_category,
        activity_level=activity_level,
    )
    lifestyle_fig = make_smoking_lifestyle_bar_chart(
        lifestyle_df,
        age_group=age_group,
        bmi_category=bmi_category,
        activity_level=activity_level,
    )
    disease_fig = make_disease_sankey(
        disease_df,
        age_group=age_group,
        bmi_category=bmi_category,
        activity_level=activity_level,
    )

    return sleep_fig, lifestyle_fig, disease_fig


if __name__ == "__main__":
    app.run(debug=True)
