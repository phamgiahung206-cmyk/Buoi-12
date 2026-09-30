import pandas as pd
from config import EXPECTED_COLUMNS, logger

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Starting Data Preprocessing...")
    # Normalize headers
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    
    # Check required headers
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    for col in missing_cols:
        df[col] = "" # Fill missing columns with empty string to prevent KeyError
        
    # Standardize data types (convert all to string and strip)
    for col in EXPECTED_COLUMNS:
        df[col] = df[col].astype(str).str.strip()
        # Replace string "nan" or "None" with empty string
        df[col] = df[col].replace(["nan", "None", "<NA>"], "")
        
    return df[EXPECTED_COLUMNS]