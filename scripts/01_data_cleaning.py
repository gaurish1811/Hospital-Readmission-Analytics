import os
import pandas as pd
import numpy as np

RAW_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw", "diabetic_data.csv")
CLEAN_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cleaned_diabetic_data.csv")
CLEAN_DEDUP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cleaned_patient_first_visits.csv")
AUDIT_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cleaning_audit_log.txt")

EXPIRED_HOSPICE_DISCHARGE_IDS = [11, 13, 14, 19, 20, 21]

def clean_data():
    print("[INFO] Starting Data Cleaning and Auditing Pipeline...")
    
    # 1. Load raw dataset
    df_raw = pd.read_csv(RAW_DATA_PATH)
    initial_rows = len(df_raw)
    print(f"[AUDIT] Initial Raw Encounters: {initial_rows:,}")
    
    audit_lines = [
        "=== HOSPITAL READMISSION DATA CLEANING AUDIT TRAIL ===",
        f"1. Initial Raw Records: {initial_rows:,}"
    ]
    
    # 2. Replace '?' with NaN
    df = df_raw.replace('?', np.nan)
    
    # Missing value analysis
    missing_summary = df.isnull().sum()
    missing_cols = missing_summary[missing_summary > 0]
    print("\n[INFO] Columns with Missing Values ('?'):")
    for col, count in missing_cols.items():
        pct = (count / initial_rows) * 100
        print(f"  - {col}: {count:,} ({pct:.2f}%)")
        audit_lines.append(f"   Missing in '{col}': {count:,} ({pct:.2f}%)")
        
    # 3. Drop high-missing / uninformative columns
    cols_to_drop = ['weight', 'payer_code', 'medical_specialty']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
    audit_lines.append(f"2. Dropped High-Missing Columns: {cols_to_drop}")
    
    # 4. Exclude Expired and Hospice care encounters (Readmission not possible)
    expired_mask = df['discharge_disposition_id'].isin(EXPIRED_HOSPICE_DISCHARGE_IDS)
    expired_count = expired_mask.sum()
    df_valid = df[~expired_mask].copy()
    valid_rows = len(df_valid)
    
    print(f"\n[AUDIT] Removed {expired_count:,} encounters where patient expired or entered hospice care.")
    audit_lines.append(f"3. Removed Deceased/Hospice Encounters: {expired_count:,} rows")
    audit_lines.append(f"   Valid Post-Discharge Encounters: {valid_rows:,}")
    
    # 5. Handle Target Variable (readmitted)
    # Target: 30-day readmission -> readmitted == '<30'
    df_valid['readmitted_30day'] = np.where(df_valid['readmitted'] == '<30', 1, 0)
    df_valid['readmitted_any'] = np.where(df_valid['readmitted'] != 'NO', 1, 0)
    
    # 6. Feature Engineering for Dashboard & SQL Analysis
    # Standardize Age Groups
    age_map = {
        '[0-10)': '0-10', '[10-20)': '10-20', '[20-30)': '20-30',
        '[30-40)': '30-40', '[40-50)': '40-50', '[50-60)': '50-60',
        '[60-70)': '60-70', '[70-80)': '70-80', '[80-90)': '80-90',
        '[90-100)': '90-100'
    }
    df_valid['age_clean'] = df_valid['age'].map(age_map).fillna(df_valid['age'])
    
    # Prior Inpatient Bucket
    def bucket_inpatient(val):
        if val == 0: return '0 Visits'
        elif val == 1: return '1 Visit'
        elif val == 2: return '2 Visits'
        else: return '3+ Visits'
        
    df_valid['prior_inpatient_bucket'] = df_valid['number_inpatient'].apply(bucket_inpatient)
    
    # Length of stay bucket
    def bucket_los(days):
        if days <= 2: return '1-2 Days'
        elif days <= 4: return '3-4 Days'
        elif days <= 7: return '5-7 Days'
        else: return '8+ Days'
        
    df_valid['los_bucket'] = df_valid['time_in_hospital'].apply(bucket_los)
    
    # Discharge disposition category
    def category_discharge(d_id):
        if d_id == 1: return 'Home'
        elif d_id in [3, 4, 23, 24]: return 'SNF / ICF / LTC'
        elif d_id in [2, 5, 22, 27, 28, 29]: return 'Rehab / Hospital Transfer'
        elif d_id in [6, 8]: return 'Home Health Services'
        elif d_id == 7: return 'Left AMA'
        else: return 'Other / Outpatient'
        
    df_valid['discharge_category'] = df_valid['discharge_disposition_id'].apply(category_discharge)
    
    # 7. Deduplicate Multi-visit Patients (First Encounter per Patient)
    # Sort by encounter_id to get earliest encounter
    df_valid_sorted = df_valid.sort_values(['patient_nbr', 'encounter_id'])
    df_first_visit = df_valid_sorted.drop_duplicates(subset=['patient_nbr'], keep='first').copy()
    dedup_rows = len(df_first_visit)
    dups_removed = valid_rows - dedup_rows
    
    print(f"[AUDIT] Removed {dups_removed:,} secondary encounters for multi-visit patients.")
    print(f"[AUDIT] Final Cleaned Patient Dataset (Unique Patients): {dedup_rows:,} records.")
    
    audit_lines.append(f"4. Deduplicated Multi-visit Patients: {dups_removed:,} duplicate encounters removed")
    audit_lines.append(f"5. Final Clean Unique Patients Dataset: {dedup_rows:,} records")
    audit_lines.append(f"   Overall 30-Day Readmission Rate (Encounters): {df_valid['readmitted_30day'].mean()*100:.2f}%")
    audit_lines.append(f"   Overall 30-Day Readmission Rate (Unique Patients): {df_first_visit['readmitted_30day'].mean()*100:.2f}%")
    
    # 8. Export Cleaned Datasets
    os.makedirs(os.path.dirname(CLEAN_DATA_PATH), exist_ok=True)
    df_valid.to_csv(CLEAN_DATA_PATH, index=False)
    df_first_visit.to_csv(CLEAN_DEDUP_PATH, index=False)
    
    with open(AUDIT_LOG_PATH, 'w') as f:
        f.write('\n'.join(audit_lines))
        
    print(f"\n[SUCCESS] Exported cleaned encounter data to: {CLEAN_DATA_PATH}")
    print(f"[SUCCESS] Exported cleaned unique patient data to: {CLEAN_DEDUP_PATH}")
    print(f"[SUCCESS] Audit log written to: {AUDIT_LOG_PATH}")

if __name__ == "__main__":
    clean_data()
