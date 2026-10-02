import os
import sys
import zipfile
import urllib.request

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
ZIP_PATH = os.path.join(DATA_DIR, "dataset_diabetes.zip")
CSV_PATH = os.path.join(DATA_DIR, "diabetic_data.csv")
UCI_ZIP_URL = "https://archive.ics.uci.edu/static/public/296/diabetes+130-us+hospitals+for+years+1999-2008.zip"

def download_and_extract():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(CSV_PATH):
        print(f"[INFO] Raw dataset already exists at: {CSV_PATH}")
        return CSV_PATH
    
    print(f"[INFO] Downloading UCI Diabetes dataset from {UCI_ZIP_URL}...")
    try:
        req = urllib.request.Request(UCI_ZIP_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(ZIP_PATH, 'wb') as out_file:
            out_file.write(response.read())
        print("[INFO] Download completed. Extracting ZIP contents...")
        
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)
        
        # Check nested dataset zip if present
        nested_zip = os.path.join(DATA_DIR, "dataset_diabetes.zip")
        if os.path.exists(nested_zip) and nested_zip != ZIP_PATH:
            with zipfile.ZipFile(nested_zip, 'r') as nzip:
                nzip.extractall(DATA_DIR)
                
        print(f"[SUCCESS] Dataset successfully extracted to {DATA_DIR}")
        return CSV_PATH
    except Exception as e:
        print(f"[WARNING] Direct ZIP download failed: {e}. Trying ucimlrepo...")
        try:
            from ucimlrepo import fetch_ucirepo
            dataset = fetch_ucirepo(id=296)
            df = dataset.data.original
            df.to_csv(CSV_PATH, index=False)
            print(f"[SUCCESS] Dataset fetched via ucimlrepo and saved to {CSV_PATH}")
            return CSV_PATH
        except Exception as e2:
            print(f"[ERROR] Failed to fetch dataset: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    download_and_extract()
