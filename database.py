import sqlite3
import json
import pandas as pd
from config import DB_PATH, logger

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id TEXT PRIMARY KEY,
            original_data TEXT,
            status TEXT,
            issues TEXT,
            suggested_corrections TEXT,
            final_data TEXT,
            action_taken TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def save_batch(df: pd.DataFrame):
    """Save initial processed batch to DB"""
    conn = sqlite3.connect(DB_PATH)
    for _, row in df.iterrows():
        try:
            conn.execute('''
                INSERT OR REPLACE INTO records 
                (id, original_data, status, issues, suggested_corrections, final_data, action_taken)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(row['customer_id']),
                json.dumps(row['original_data']),
                row['status'],
                json.dumps(row['issues']),
                json.dumps(row.get('suggested_corrections', {})),
                json.dumps(row['original_data']), # Initially same as original
                "SYSTEM_CLASSIFIED"
            ))
        except Exception as e:
            logger.error(f"DB Save Error for ID {row.get('customer_id')}: {e}")
    conn.commit()
    conn.close()

def load_records_by_status(status: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM records WHERE status = '{status}'", conn)
    conn.close()
    return df

def update_record_decision(record_id: str, final_data: dict, action: str, new_status: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        UPDATE records 
        SET final_data = ?, action_taken = ?, status = ?
        WHERE id = ?
    ''', (json.dumps(final_data), action, new_status, str(record_id)))
    conn.commit()
    conn.close()
    logger.info(f"Record {record_id} updated via HITL. Action: {action}")