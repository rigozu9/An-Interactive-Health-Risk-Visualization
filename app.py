from dash import Dash, Input, Output, dcc, html

from visuals.sleep import load_sleep_data, make_sleep_heatmap
from visuals.lifestyle import (
    load_lifestyle_data,
    make_smoking_lifestyle_bar_chart,
)
from visuals.disease import DISEASE_FILES, load_disease_data, make_disease_profile

app = Dash(__name__)
server = app.server

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
disease_options = [
    {"label": disease_name, "value": disease_name}
    for disease_name in DISEASE_FILES
]

APP_STYLE = {
    "minHeight": "100vh",
    "display": "grid",
    "gridTemplateRows": "auto auto auto",
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
    "alignItems": "flexStart",
    "justifyContent": "spaceBetween",
    "gap": "16px",
    "flexWrap": "wrap",
}

FILTER_BAR_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "gap": "8px",
    "flexWrap": "wrap",
}

FILTER_LABEL_STYLE = {
    "fontSize": "14px",
    "fontWeight": "600",
    "color": "#253858",
}

FILTER_DROPDOWN_STYLE = {
    "width": "180px",
    "minWidth": "160px",
}

FILTER_NOTE_STYLE = {
    "margin": "4px 0 0 0",
    "fontSize": "12px",
    "color": "#6b7280",
}

GRID_ROW_STYLE = {
    "display": "grid",
    "gridTemplateColumns": "repeat(auto-fit, minmax(420px, 1fr))",
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
    "minHeight": "320px",
}

CARD_TITLE_STYLE = {
    "margin": "0 0 4px 0",
    "fontSize": "18px",
    "color": "#253858",
}

CARD_DESCRIPTION_STYLE = {
    "margin": "0 0 6px 0",
    "fontSize": "13px",
    "lineHeight": "1.35",
    "color": "#4b5563",
}

CARD_HEADER_STYLE = {
    "display": "flex",
    "alignItems": "center",
    "justifyContent": "spaceBetween",
    "gap": "12px",
    "marginBottom": "4px",
}

DISEASE_DROPDOWN_STYLE = {
    "width": "220px",
    "minWidth": "180px",
}

GRAPH_STYLE = {
    "height": "100%",
    "minHeight": "260px",
}

GRAPH_CONFIG = {
    "displayModeBar": False,
    "scrollZoom": False,
    "responsive": True,
}

app.layout = html.Div(
    style=APP_STYLE,
    children=[
        html.Div(
            style=HEADER_ROW_STYLE,
            children=[
                html.H1("Health Lifestyle Dashboard", style=HEADER_STYLE),
                html.Div(
                    children=[
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
                        html.P(
                            "Filters update charts when the selected dataset contains that variable.",
                            style=FILTER_NOTE_STYLE,
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
                        html.Div(
                            style=CARD_HEADER_STYLE,
                            children=[
                                html.H2("Disease", style=CARD_TITLE_STYLE),
                                dcc.Dropdown(
                                    id="disease-selector",
                                    options=disease_options,
                                    value="Cancer Risk",
                                    clearable=False,
                                    style=DISEASE_DROPDOWN_STYLE,
                                ),
                            ],
                        ),
                        html.P(
                            "Choose a disease to see which available risk factors are common among disease-risk records.",
                            style=CARD_DESCRIPTION_STYLE,
                        ),
                        dcc.Graph(
                            id="disease-chart",
                            figure=make_disease_profile(disease_df),
                            style=GRAPH_STYLE,
                            config=GRAPH_CONFIG,
                        ),
                    ],
                ),
                html.Div(
                    style=CARD_STYLE,
                    children=[
                        html.H2("Lifestyle", style=CARD_TITLE_STYLE),
                        html.P(
                            "Compare average alcohol, fried potato, and green vegetable consumption between smoking groups.",
                            style=CARD_DESCRIPTION_STYLE,
                        ),
                        dcc.Graph(
                            id="lifestyle-chart",
                            figure=make_smoking_lifestyle_bar_chart(lifestyle_df),
                            style=GRAPH_STYLE,
                            config=GRAPH_CONFIG,
                        ),
                    ],
                ),
            ],
        ),
        html.Div(
            style=CARD_STYLE,
            children=[
                html.H2("Sleep", style=CARD_TITLE_STYLE),
                html.P(
                    "Explore how stress level and sleep quality are distributed in the selected group.",
                    style=CARD_DESCRIPTION_STYLE,
                ),
                dcc.Graph(
                    id="sleep-chart",
                    figure=make_sleep_heatmap(sleep_df),
                    style=GRAPH_STYLE,
                    config=GRAPH_CONFIG,
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
    Input("disease-selector", "value"),
)
def update_dashboard(age_group, bmi_category, activity_level, disease_dataset):
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
    disease_fig = make_disease_profile(
        disease_df,
        disease_dataset=disease_dataset,
        age_group=age_group,
        bmi_category=bmi_category,
        activity_level=activity_level,
    )

    return sleep_fig, lifestyle_fig, disease_fig


if __name__ == "__main__":
    app.run(debug=True)
