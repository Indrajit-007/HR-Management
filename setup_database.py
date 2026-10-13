import sqlite3
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

from dotenv import load_dotenv

SCRIPT_ROOT = Path(__file__).resolve().parent
load_dotenv(SCRIPT_ROOT / ".env")
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", str(SCRIPT_ROOT))).expanduser()


def create_database():
    configured_path = Path(os.getenv("EMPLOYEE_DB_PATH", "data/employees.db")).expanduser()
    db_path = configured_path if configured_path.is_absolute() else PROJECT_ROOT / configured_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove old database if exists
    if db_path.exists():
        db_path.unlink()
        print("Removed old database")
    
    # Create new database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("Creating database tables...")
    
    # Table 1: Employees
    cursor.execute("""
    CREATE TABLE employees (
        emp_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        position TEXT NOT NULL,
        join_date TEXT NOT NULL,
        manager TEXT,
        email TEXT NOT NULL
    )
    """)
    
    # Table 2: Leave Balance
    cursor.execute("""
    CREATE TABLE leave_balance (
        emp_id TEXT PRIMARY KEY,
        casual_leave INTEGER DEFAULT 0,
        earned_leave INTEGER DEFAULT 0,
        sick_leave INTEGER DEFAULT 0,
        last_updated TEXT NOT NULL,
        FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
    )
    """)
    
    print("Tables created successfully!")
    
    conn.close()
    
    print("\n Database created successfully!")
    print(f" Location: {db_path}")





if __name__ == "__main__":
    create_database()
