# Health Lifestyle Dashboard

Interactive Dash/Plotly dashboard for exploring how lifestyle-related factors appear together with body attributes and disease-risk indicators.

The project was created for the University of Helsinki Interactive Data Visualization course. The target users are students who want an approachable way to explore lifestyle habits such as sleep, smoking, alcohol, activity, BMI, and broader health-risk profiles.

Deployed Render application:
https://lifestyle-habit-interactive-visualisation.onrender.com/

## Project Idea

The dashboard follows the structure:

```text
Lifestyle habits -> body attributes -> disease risk
```

It does not predict personal medical outcomes. Instead, it supports exploratory analysis by showing patterns in standardized health datasets.

## Main Tasks

- **T1: Identify risk factors for diseases**  
  Select a disease and inspect which available risk factors are most common among disease-risk records.

- **T2: Compare different lifestyles**  
  Compare average alcohol, fried potato, and green vegetable consumption between smoking-history groups.

- **T3: Explore relationships between lifestyle variables**  
  Explore how sleep quality is distributed across stress levels.

- **T4: Simulate lifestyle scenarios**  
  Use global filters to inspect how patterns change for selected subgroups.

## Dashboard Features

- Disease risk-factor profile cards for Cancer Risk, Heart Disease, and Stroke.
- Lifestyle grouped bar chart comparing smoking-history groups.
- Sleep heatmap showing the relationship between stress level and sleep quality.
- Global filters for age group, gender, BMI category, and activity level.
- Clear filters button for quickly returning to the full dataset.
- Record counts after filtering, so users can see how much data each view is based on.
- Standardized shared schema across multiple health datasets.

## Data Sources

The project uses public Kaggle datasets:

- Sleep Health and Lifestyle Dataset  
  https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset

- Cardiovascular Diseases Risk Prediction Dataset  
  https://www.kaggle.com/datasets/alphiree/cardiovascular-diseases-risk-prediction-dataset

- Heart Failure Prediction Dataset  
  https://www.kaggle.com/datasets/fedesoriano/heart-failure-prediction

- Stroke Prediction Dataset  
  https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset

- Cancer Risk Factors Dataset  
  https://www.kaggle.com/datasets/tarekmasryo/cancer-risk-factors-dataset

The raw datasets are not included in this repository. The app uses standardized CSV files under:

```text
data/standardized/
```

## Standardized Variables

The datasets are connected through shared standardized columns, including:

```text
age_group
gender
smoking_status
alcohol_level
sleep_category
bmi_category
activity_level
blood_pressure_category
glucose_category
cholesterol_category
disease_risk
source_dataset
```

Not every dataset contains usable values for every standardized variable. For example, some disease datasets do not contain direct lifestyle variables. The dashboard keeps the shared schema but only applies filters when the selected dataset supports them.

## Repository Structure

```text
app.py                         Main Dash layout and callbacks
visuals/disease.py             Disease risk-factor profile chart
visuals/lifestyle.py           Lifestyle grouped bar chart
visuals/sleep.py               Sleep heatmap
preprocess_standardize.py      Dataset standardization script
shared_variable_check.py       Helper for checking shared standardized variables
standardization_notes.md       Notes on dataset mappings and assumptions
data/standardized/             Standardized CSV files used by the app
```

## Design Notes

The final prototype was refined based on a qualitative user study. The original disease Sankey idea was replaced with simpler disease risk-factor profile cards because users found the Sankey hardest to understand. Later polish focused on clearer labels, visible record counts, improved global filters, and a clear filters button.
