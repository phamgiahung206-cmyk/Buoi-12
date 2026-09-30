import pandas as pd

def detect_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Multi-field duplicate detection logic.
    For V1: Exact email match OR (Exact phone match).
    Fuzzy name matching can be added here in V2.
    """
    df['is_duplicate'] = False
    
    # 1. Email duplicates (ignore empty)
    email_dups = df[df['email'] != ""].duplicated(subset=['email'], keep='first')
    df.loc[df['email'] != "", 'is_duplicate'] = df.loc[df['email'] != "", 'is_duplicate'] | email_dups
    
    # 2. Phone duplicates (ignore empty)
    phone_dups = df[df['phone'] != ""].duplicated(subset=['phone'], keep='first')
    df.loc[df['phone'] != "", 'is_duplicate'] = df.loc[df['phone'] != "", 'is_duplicate'] | phone_dups

    return df