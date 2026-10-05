"""
Create demo employee database with sample data
This simulates a real HR database with employees and leave balances
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random




def create_database():
    """Create SQLite database with tables and sample data"""
    
    db_path = "data/employees.db"
    
    # Remove old database if exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️  Removed old database")
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📦 Creating database tables...")
    
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
    
    print("✅ Tables created successfully!")
    
    # Insert sample employees
    print("\n👥 Adding sample employees...")
    
    employees = [
        # (emp_id, name, department, position, join_date, manager, email)
        ("EMP001", "Rajesh Kumar", "Engineering", "Senior Developer", "2020-03-15", "EMP010", "rajesh.kumar@company.com"),
        ("EMP002", "Priya Sharma", "HR", "HR Manager", "2019-01-10", "EMP010", "priya.sharma@company.com"),
        ("EMP003", "Amit Patel", "Engineering", "DevOps Engineer", "2021-06-20", "EMP010", "amit.patel@company.com"),
        ("EMP004", "Sneha Reddy", "Marketing", "Marketing Executive", "2022-02-14", "EMP009", "sneha.reddy@company.com"),
        ("EMP005", "Vikram Singh", "Sales", "Sales Manager", "2018-11-05", "EMP010", "vikram.singh@company.com"),
        ("EMP006", "Ananya Iyer", "Engineering", "Junior Developer", "2023-01-10", "EMP001", "ananya.iyer@company.com"),
        ("EMP007", "Rahul Gupta", "Finance", "Accountant", "2020-08-22", "EMP008", "rahul.gupta@company.com"),
        ("EMP008", "Meera Nair", "Finance", "Finance Manager", "2017-05-15", "EMP010", "meera.nair@company.com"),
        ("EMP009", "Karthik Rao", "Marketing", "Marketing Head", "2019-07-30", "EMP010", "karthik.rao@company.com"),
        ("EMP010", "Sunita Desai", "Executive", "CEO", "2015-01-01", None, "sunita.desai@company.com"),
    ]
    
    cursor.executemany("""
    INSERT INTO employees (emp_id, name, department, position, join_date, manager, email)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, employees)
    
    print(f"✅ Added {len(employees)} employees")
    
    # Insert leave balances
    print("\n📊 Adding leave balances...")
    
    # Generate realistic leave balances
    leave_balances = []
    for emp in employees:
        emp_id = emp[0]
        join_date = datetime.strptime(emp[4], "%Y-%m-%d")
        months_employed = (datetime.now() - join_date).days // 30
        
        # Calculate leave based on tenure (realistic)
        if months_employed >= 12:
            # Full year employees
            casual = random.randint(3, 12)  # Out of 12 per year
            earned = random.randint(8, 18)  # Out of 18 per year
            sick = random.randint(2, 7)     # Out of 7 per year
        else:
            # Pro-rata for new employees
            casual = random.randint(1, 6)
            earned = random.randint(3, 10)
            sick = random.randint(1, 4)
        
        leave_balances.append((
            emp_id,
            casual,
            earned,
            sick,
            datetime.now().strftime("%Y-%m-%d")
        ))
    
    cursor.executemany("""
    INSERT INTO leave_balance (emp_id, casual_leave, earned_leave, sick_leave, last_updated)
    VALUES (?, ?, ?, ?, ?)
    """, leave_balances)
    
    print(f"✅ Added leave balances for {len(leave_balances)} employees")
    
    # Commit and close
    conn.commit()
    
    # Display sample data
    print("\n" + "="*60)
    print("📋 SAMPLE DATA PREVIEW")
    print("="*60)
    
    # Show 3 employees
    cursor.execute("""
    SELECT e.emp_id, e.name, e.department, e.position,
           l.casual_leave, l.earned_leave, l.sick_leave
    FROM employees e
    JOIN leave_balance l ON e.emp_id = l.emp_id
    LIMIT 3
    """)
    
    print("\n👤 Sample Employees with Leave Balance:")
    print("-" * 60)
    for row in cursor.fetchall():
        print(f"ID: {row[0]}")
        print(f"Name: {row[1]}")
        print(f"Dept: {row[2]} | Position: {row[3]}")
        print(f"Leaves → CL: {row[4]} | EL: {row[5]} | SL: {row[6]}")
        print("-" * 60)
    
    conn.close()
    
    print("\n✅ Database created successfully!")
    print(f"📍 Location: {db_path}")





if __name__ == "__main__":
    create_database()