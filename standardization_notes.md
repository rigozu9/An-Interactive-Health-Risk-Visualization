# Standardization Notes

This file documents how each health dataset was standardized into a shared schema for the interactive visualization prototype.

## Shared standardized variables

`age_group`, `gender`, `smoking_status`, `alcohol_level`, `sleep_category`, `bmi_category`, `activity_level`, `blood_pressure_category`, `glucose_category`, `cholesterol_category`, `disease_risk`, `source_dataset`

## Dataset-by-dataset mappings

### sleep

- Source file output: `data/standardized/sleep_standardized.csv`
- Rows: 374
- Original columns used: `Age`, `Gender`, `Sleep Duration`, `BMI Category`, `Daily Steps`, `Blood Pressure`, `Sleep Disorder`
- Standardized columns populated: `age_group`, `gender`, `sleep_category`, `bmi_category`, `activity_level`, `blood_pressure_category`, `disease_risk`, `source_dataset`

#### Mapping details

- `Age` -> `age_group` using the shared 18-24 to 65+ buckets.
- `Gender` -> `gender` with text normalization (`Male`, `Female`).
- `Sleep Duration` -> `sleep_category` using Poor (<6), Normal (6-9), Excess (>9).
- `BMI Category` -> `bmi_category` by normalizing the source text labels to `Underweight`, `Normal`, `Overweight`, `Obese`.
- `Daily Steps` -> `activity_level` with thresholds: Low <5000, Medium 5000-8999, High >=9000.
- `Blood Pressure` -> `blood_pressure_category` by splitting systolic/diastolic values and applying: Normal <120/<80, Elevated 120-129 and <80, otherwise High.
- `Sleep Disorder` -> `disease_risk` where `None` becomes `None/Low` and diagnosed disorders become `Diagnosed/High`.

#### Assumptions and missing values

- Used `Daily Steps` instead of `Physical Activity Level` because step count is easier to explain and bucket consistently.
- Standardized fields with no matching source column were left as `Unknown` to preserve a shared schema.
- Literal `None` values in `Sleep Disorder` were preserved during CSV import so they can be mapped to `None/Low` instead of being treated as missing.

#### Columns not mapped into shared variables

- `Person ID`
- `Occupation`
- `Quality of Sleep`
- `Physical Activity Level`
- `Stress Level`
- `Heart Rate`

### cardiovascular_body

- Source file output: `data/standardized/cardiovascular_body_standardized.csv`
- Rows: 308854
- Original columns used: `Age_Category`, `Sex`, `Smoking_History`, `Alcohol_Consumption`, `BMI`, `Exercise`, `Heart_Disease`
- Standardized columns populated: `age_group`, `gender`, `smoking_status`, `alcohol_level`, `bmi_category`, `activity_level`, `disease_risk`, `source_dataset`

#### Mapping details

- `Age_Category` -> `age_group` by collapsing source ranges like `25-29` and `30-34` into the shared `25-34` bucket, and `80+` into `65+`.
- `Sex` -> `gender` with text normalization.
- `Smoking_History` -> `smoking_status` where `No` becomes `Non-smoker` and `Yes` becomes `Light smoker` because only yes/no detail is available.
- `Alcohol_Consumption` -> `alcohol_level` using thresholds: 0 None, 1-4 Low, 5-14 Moderate, 15+ High.
- `BMI` -> `bmi_category` using standard BMI cutoffs.
- `Exercise` -> `activity_level` where `No` becomes `Low` and `Yes` becomes `Medium` because the dataset does not provide activity intensity or duration.
- `Heart_Disease` -> `disease_risk` where `No` becomes `None/Low` and `Yes` becomes `Diagnosed/High`.

#### Assumptions and missing values

- The exact unit of `Alcohol_Consumption` is not encoded in the CSV header, so thresholds were chosen as sensible ordinal buckets and documented for transparency.
- Because `Exercise` is only yes/no, rows cannot be distinguished into `Medium` versus `High` activity with confidence.
- Columns for blood pressure, glucose, cholesterol, and sleep do not exist in this dataset, so those shared variables remain `Unknown`.

#### Columns not mapped into shared variables

- `General_Health`
- `Checkup`
- `Skin_Cancer`
- `Other_Cancer`
- `Depression`
- `Diabetes`
- `Arthritis`
- `Height_(cm)`
- `Weight_(kg)`
- `Fruit_Consumption`
- `Green_Vegetables_Consumption`
- `FriedPotato_Consumption`

### heart_disease

- Source file output: `data/standardized/heart_disease_standardized.csv`
- Rows: 918
- Original columns used: `Age`, `Sex`, `RestingBP`, `Cholesterol`, `FastingBS`, `MaxHR`, `HeartDisease`
- Standardized columns populated: `age_group`, `gender`, `blood_pressure_category`, `glucose_category`, `cholesterol_category`, `disease_risk`, `source_dataset`

#### Mapping details

- `Age` -> `age_group` using the shared age buckets.
- `Sex` -> `gender` by normalizing `M` and `F` to `Male` and `Female`.
- `RestingBP` -> `blood_pressure_category` using systolic-only thresholds: Normal <120, Elevated 120-129, High >=130. Zero values were treated as missing.
- `Cholesterol` -> `cholesterol_category` using mg/dL-style thresholds: Normal <200, Elevated 200-239, High >=240. Zero values were treated as missing.
- `FastingBS` -> `glucose_category` where 0 becomes `Normal` and 1 becomes `High` because the source is a binary elevated fasting blood sugar flag.
- `HeartDisease` -> `disease_risk` where 0 becomes `None/Low` and 1 becomes `Diagnosed/High`.

#### Assumptions and missing values

- This dataset does not contain direct lifestyle variables for smoking, alcohol, sleep, BMI, or physical activity behavior, so those remain `Unknown` rather than being inferred from weak physiological proxies.

#### Columns not mapped into shared variables

- `ChestPainType`
- `RestingECG`
- `MaxHR`
- `ExerciseAngina`
- `Oldpeak`
- `ST_Slope`

### stroke

- Source file output: `data/standardized/stroke_standardized.csv`
- Rows: 5110
- Original columns used: `age`, `gender`, `smoking_status`, `bmi`, `hypertension`, `avg_glucose_level`, `stroke`
- Standardized columns populated: `age_group`, `gender`, `smoking_status`, `bmi_category`, `blood_pressure_category`, `glucose_category`, `disease_risk`, `source_dataset`

#### Mapping details

- `age` -> `age_group` using the shared age buckets. Source rows below 18 were mapped to `Unknown` because the target schema starts at 18.
- `gender` -> `gender` with text normalization; source `Other` becomes `Other/Unknown`.
- `smoking_status` -> `smoking_status` by normalizing values like `never smoked`, `formerly smoked`, and `smokes`.
- `bmi` -> `bmi_category` using standard BMI cutoffs.
- `hypertension` -> `blood_pressure_category` where 0 becomes `Normal` and 1 becomes `High` because only a binary hypertension flag is available.
- `avg_glucose_level` -> `glucose_category` using thresholds: Normal <100, Prediabetic/Elevated 100-125.9, High >=126.
- `stroke` -> `disease_risk` where 0 becomes `None/Low` and 1 becomes `Diagnosed/High`.

#### Assumptions and missing values

- The source dataset contains some children, but the project's shared age schema starts at 18, so those rows were marked `Unknown` for `age_group`.
- No alcohol, sleep duration, cholesterol, or direct activity measure is present, so those standardized variables remain `Unknown`.
- Missing BMI values (including source `N/A`) were carried through safely and standardized to `Unknown`.

#### Columns not mapped into shared variables

- `id`
- `heart_disease`
- `ever_married`
- `work_type`
- `Residence_type`

### cancer_risk

- Source file output: `data/standardized/cancer_risk_standardized.csv`
- Rows: 2000
- Original columns used: `Age`, `Gender`, `Smoking`, `Alcohol_Use`, `BMI`, `Physical_Activity_Level`, `Risk_Level`
- Standardized columns populated: `age_group`, `gender`, `smoking_status`, `alcohol_level`, `bmi_category`, `activity_level`, `disease_risk`, `source_dataset`

#### Mapping details

- `Age` -> `age_group` using the shared age buckets.
- `Smoking` -> `smoking_status` using a documented ordinal mapping on the source 0-10 scale: 0 `Non-smoker`, 1-4 `Light smoker`, 5-10 `Heavy smoker`.
- `Alcohol_Use` -> `alcohol_level` using a documented ordinal mapping on the source 0-10 scale: 0 `None`, 1-3 `Low`, 4-6 `Moderate`, 7-10 `High`.
- `BMI` -> `bmi_category` using standard BMI cutoffs.
- `Physical_Activity_Level` -> `activity_level` using 0-3 `Low`, 4-6 `Medium`, 7-10 `High`.
- `Risk_Level` -> `disease_risk` where `Low` becomes `None/Low`, `Medium` becomes `At risk`, and `High` becomes `Diagnosed/High`.

#### Assumptions and missing values

- The `Gender` column is encoded as 0/1, but the CSV does not define which number corresponds to which sex. To avoid guessing blindly, all cancer-dataset values were standardized to `Other/Unknown`.
- The smoking, alcohol, and activity fields appear to be ordinal 0-10 scores rather than real-world units, so bucket thresholds were chosen for consistency and documented rather than treated as literal cigarettes/day or drinks/week.
- No direct sleep, blood pressure, glucose, or cholesterol columns exist in this dataset, so those shared variables remain `Unknown`.

#### Columns not mapped into shared variables

- `Patient_ID`
- `Cancer_Type`
- `Obesity`
- `Family_History`
- `Diet_Red_Meat`
- `Diet_Salted_Processed`
- `Fruit_Veg_Intake`
- `Physical_Activity`
- `Air_Pollution`
- `Occupational_Hazards`
- `BRCA_Mutation`
- `H_Pylori_Infection`
- `Calcium_Intake`
- `Overall_Risk_Score`
