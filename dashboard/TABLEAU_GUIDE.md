# Tableau Public Dashboard Guide: Hospital Readmission Analytics

This guide provides instructions for connecting the cleaned dataset to **Tableau Public** and building a published 30-day readmission dashboard.

---

## 1. Dataset Connection & Source Setup
1. Download or locate `data/cleaned_diabetic_data.csv`.
2. Open **Tableau Public** (Desktop or Web).
3. Select **To a File -> Text File** and connect to `cleaned_diabetic_data.csv`.
4. Ensure data types are set as follows:
   - `readmitted_30day`: **Measure (Integer)**
   - `age_clean`: **Dimension (String)**
   - `prior_inpatient_bucket`: **Dimension (String)**
   - `A1Cresult`: **Dimension (String)**
   - `discharge_category`: **Dimension (String)**
   - `time_in_hospital`: **Measure (Integer)**

---

## 2. Calculated Fields & Measures

Create the following calculated fields in Tableau:

### 1. **Readmission Rate (%)**
```sql
AVG([readmitted_30day]) * 100
```
*Format: Number (Custom), 2 Decimal Places, Suffix `%`*

### 2. **High-Risk Cohort Flag**
```sql
IF [number_inpatient] >= 2 THEN "High-Risk (2+ Visits)"
ELSE "Standard Baseline"
END
```

### 3. **Glycemic Test Group**
```sql
IF ISNULL([A1Cresult]) OR [A1Cresult] = "None" THEN "Not Tested"
ELSE [A1Cresult]
END
```

---

## 3. Worksheet Build Specs

| Worksheet Name | Chart Type | Dimensions (Rows/Columns) | Measures | Styling / Colors |
| :--- | :--- | :--- | :--- | :--- |
| **KPI Rate** | Text Card | None | `Readmission Rate (%)` | 36pt Bold, Crimson (`#F43F5E`) |
| **KPI Total** | Text Card | None | `COUNT([encounter_id])` | 36pt Bold, White (`#FFFFFF`) |
| **KPI High Risk** | Text Card | None | `Readmission Rate (%)` filtered to `High-Risk` | 36pt Bold, Amber (`#FBBF24`) |
| **Readmission by Age** | Column Chart | Columns: `age_clean`<br>Rows: `Readmission Rate (%)` | `Readmission Rate (%)` | Indigo to Crimson Gradient |
| **Prior Inpatient Trend** | Line Chart | Columns: `prior_inpatient_bucket`<br>Rows: `Readmission Rate (%)` | `Readmission Rate (%)` | Gold Line (`#FBBF24`) with Points |
| **HbA1c Impact** | Bar Chart | Columns: `Glycemic Test Group`<br>Rows: `Readmission Rate (%)` | `Readmission Rate (%)` | Emerald (`#10B981`) & Blue (`#38BDF8`) |
| **Discharge Risk** | Horizontal Bar | Columns: `Readmission Rate (%)`<br>Rows: `discharge_category` | `Readmission Rate (%)` | Red Accent on High Risk |

---

## 4. Dashboard Assembly & Filters

1. **Dashboard Canvas Size**: Automatic or Fixed (1400 x 900 px).
2. **Layout Containers**:
   - Header Banner (Title + Subtitle + Innovaccer Provider Badge).
   - Filter Bar (Global Filters for `age_clean`, `Glycemic Test Group`, `discharge_category`).
   - KPI Row (4 Cards Side-by-Side).
   - 2x2 Grid of Worksheets.
   - Executive Insights Panel at Bottom.
3. **Publishing to Tableau Public**:
   - File -> Save to Tableau Public As...
   - Name: `Hospital Readmission Analytics - Innovaccer Case Study`
   - Copy Public URL for resume / portfolio repository.
