import os
import sqlite3
import pandas as pd

CLEAN_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "cleaned_diabetic_data.csv")
SQL_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql", "02_readmission_analysis.sql")

def run_sql_analysis():
    print("[INFO] Loading cleaned data into SQLite in-memory database...")
    df = pd.read_csv(CLEAN_DATA_PATH)
    
    conn = sqlite3.connect(":memory:")
    df.to_sql("cleaned_patient_encounters", conn, index=False, if_exists="replace")
    
    print("[SUCCESS] Table 'cleaned_patient_encounters' loaded with", len(df), "records.")
    print("=" * 70)
    
    # Read SQL file queries
    with open(SQL_FILE_PATH, 'r') as f:
        sql_content = f.read()
        
    # Split queries by semicolon
    raw_queries = [q.strip() for q in sql_content.split(';') if q.strip() and not q.strip().startswith('--')]
    
    query_names = [
        "1. Overall 30-Day Readmission Rate KPI",
        "2. Readmission Rate by Age Group",
        "3. Readmission Rate by Prior Inpatient Visits",
        "4. Readmission Rate by Length of Stay",
        "5. Readmission Rate by HbA1c Test Result",
        "6. Readmission Rate by Discharge Disposition Category",
        "7. WINDOW FUNCTION: Patient Visit Sequence & Running Metrics",
        "8. CTE: High-Risk Cohort Risk Multiplier Analysis"
    ]
    
    query_idx = 0
    for block in sql_content.split(';'):
        cleaned_block = '\n'.join([line for line in block.split('\n') if not line.strip().startswith('--')]).strip()
        if not cleaned_block:
            continue
            
        title = query_names[query_idx] if query_idx < len(query_names) else f"Query {query_idx+1}"
        print(f"\n--- EXECUTING: {title} ---")
        try:
            res_df = pd.read_sql_query(cleaned_block, conn)
            print(res_df.to_string(index=False))
        except Exception as e:
            print(f"[ERROR executing query]: {e}")
        query_idx += 1

    conn.close()

if __name__ == "__main__":
    run_sql_analysis()
