import sqlite3
import os
from datetime import datetime, timedelta
import random




def create_database():
    
    db_path = "data/employees.db"
    
    # Remove old database if exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed old database")
    
    # Create new database
    conn = sqlite3.connect(db_path)
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