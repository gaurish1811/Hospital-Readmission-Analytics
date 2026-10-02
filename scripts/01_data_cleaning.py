import os
import pandas as pd
import numpy as np

RAW_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw", "diabetic_data.csv")
CLEAN_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cleaned_diabetic_data.csv")
CLEAN_DEDUP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cleaned_patient_first_visits.csv")
AUDIT_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cleaning_audit_log.txt")

# Discharge disposition IDs corresponding to Expired or Hospice care
# Patients who died or entered hospice care cannot be readmitted within 30 days.
EXPIRED_HOSPICE_DISCHARGE_IDS = [11, 13, 14, 19, 20, 21]

def clean_data():
    print("Starting data cleaning pipeline...")
    
    # Load raw dataset
    df_raw = pd.read_csv(RAW_DATA_PATH)
    initial_rows = len(df_raw)
    print(f"Raw encounters loaded: {initial_rows:,}")
    
    audit_lines = [
        "Data Cleaning Audit Summary",
        f"Initial raw records: {initial_rows:,}"
    ]
    
    # Replace '?' with NaN
    df = df_raw.replace('?', np.nan)
    
    # Inspect missing values
    missing_summary = df.isnull().sum()
    missing_cols = missing_summary[missing_summary > 0]
    for col, count in missing_cols.items():
        pct = (count / initial_rows) * 100
        audit_lines.append(f"Missing in {col}: {count:,} ({pct:.2f}%)")
        
    # Drop columns with high missingness
    # weight is ~97% missing, payer_code ~40%, medical_specialty ~49%
    cols_to_drop = ['weight', 'payer_code', 'medical_specialty']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    audit_lines.append(f"Dropped high-missing columns: {cols_to_drop}")
    
    # Filter out deceased and hospice encounters
    expired_mask = df['discharge_disposition_id'].isin(EXPIRED_HOSPICE_DISCHARGE_IDS)
    expired_count = expired_mask.sum()
    df_valid = df[~expired_mask].copy()
    valid_rows = len(df_valid)
    
    audit_lines.append(f"Removed deceased/hospice encounters: {expired_count:,}")
    audit_lines.append(f"Valid post-discharge encounters: {valid_rows:,}")
    
    # Target variable: binary 30-day readmission flag
    df_valid['readmitted_30day'] = np.where(df_valid['readmitted'] == '<30', 1, 0)
    df_valid['readmitted_any'] = np.where(df_valid['readmitted'] != 'NO', 1, 0)
    
    # Feature buckets
    age_map = {
        '[0-10)': '0-10', '[10-20)': '10-20', '[20-30)': '20-30',
        '[30-40)': '30-40', '[40-50)': '40-50', '[50-60)': '50-60',
        '[60-70)': '60-70', '[70-80)': '70-80', '[80-90)': '80-90',
        '[90-100)': '90-100'
    }
    df_valid['age_clean'] = df_valid['age'].map(age_map).fillna(df_valid['age'])
    
    def bucket_inpatient(val):
        if val == 0: return '0 Visits'
        elif val == 1: return '1 Visit'
        elif val == 2: return '2 Visits'
        else: return '3+ Visits'
        
    df_valid['prior_inpatient_bucket'] = df_valid['number_inpatient'].apply(bucket_inpatient)
    
    def bucket_los(days):
        if days <= 2: return '1-2 Days'
        elif days <= 4: return '3-4 Days'
        elif days <= 7: return '5-7 Days'
        else: return '8+ Days'
        
    df_valid['los_bucket'] = df_valid['time_in_hospital'].apply(bucket_los)
    
    def category_discharge(d_id):
        if d_id == 1: return 'Home'
        elif d_id in [3, 4, 23, 24]: return 'SNF / ICF / LTC'
        elif d_id in [2, 5, 22, 27, 28, 29]: return 'Rehab / Hospital Transfer'
        elif d_id in [6, 8]: return 'Home Health Services'
        elif d_id == 7: return 'Left AMA'
        else: return 'Other / Outpatient'
        
    df_valid['discharge_category'] = df_valid['discharge_disposition_id'].apply(category_discharge)
    
    # Patient-level index visit cohort (deduplicated by patient_nbr)
    # We maintain both the full 99,343 encounter dataset and this 69,990 patient cohort
    # to account for repeat-patient bias in encounter-level rates.
    df_valid_sorted = df_valid.sort_values(['patient_nbr', 'encounter_id'])
    df_first_visit = df_valid_sorted.drop_duplicates(subset=['patient_nbr'], keep='first').copy()
    dedup_rows = len(df_first_visit)
    dups_removed = valid_rows - dedup_rows
    
    audit_lines.append(f"Deduplicated secondary visits: {dups_removed:,}")
    audit_lines.append(f"Final first-visit patient cohort: {dedup_rows:,}")
    
    # Export cleaned CSV files
    os.makedirs(os.path.dirname(CLEAN_DATA_PATH), exist_ok=True)
    df_valid.to_csv(CLEAN_DATA_PATH, index=False)
    df_first_visit.to_csv(CLEAN_DEDUP_PATH, index=False)
    
    with open(AUDIT_LOG_PATH, 'w') as f:
        f.write('\n'.join(audit_lines))
        
    print(f"Cleaned encounters exported to: {CLEAN_DATA_PATH}")
    print(f"First-visit patient cohort exported to: {CLEAN_DEDUP_PATH}")

if __name__ == "__main__":
    clean_data()
