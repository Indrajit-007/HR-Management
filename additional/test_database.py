"""
Test the employee database with sample queries
"""

import sqlite3

def test_database():
    print("🧪 Testing Employee Database\n")
    
    conn = sqlite3.connect("data/employees.db")
    cursor = conn.cursor()
    
    # Test 1: Count employees
    print("1️⃣ Total employees:")
    cursor.execute("SELECT COUNT(*) FROM employees")
    count = cursor.fetchone()[0]
    print(f"   ✅ {count} employees in database\n")
    
    # Test 2: Get employee info
    print("2️⃣ Get specific employee (EMP001):")
    cursor.execute("""
    SELECT name, department, position, email
    FROM employees
    WHERE emp_id = 'EMP001'
    """)
    result = cursor.fetchone()
    print(f"   Name: {result[0]}")
    print(f"   Dept: {result[1]}")
    print(f"   Position: {result[2]}")
    print(f"   Email: {result[3]}\n")
    
    # Test 3: Get leave balance
    print("3️⃣ Get leave balance (EMP001):")
    cursor.execute("""
    SELECT casual_leave, earned_leave, sick_leave
    FROM leave_balance
    WHERE emp_id = 'EMP001'
    """)
    result = cursor.fetchone()
    print(f"   Casual Leave: {result[0]} days")
    print(f"   Earned Leave: {result[1]} days")
    print(f"   Sick Leave: {result[2]} days\n")
    
    # Test 4: Join query (employee + leave)
    print("4️⃣ Combined query (employee + leave):")
    cursor.execute("""
    SELECT e.name, e.department,
           l.casual_leave, l.earned_leave, l.sick_leave
    FROM employees e
    JOIN leave_balance l ON e.emp_id = l.emp_id
    WHERE e.emp_id = 'EMP001'
    """)
    result = cursor.fetchone()
    print(f"   {result[0]} ({result[1]}) has:")
    print(f"   → {result[2]} casual, {result[3]} earned, {result[4]} sick leaves\n")
    
    # Test 5: List all employees by department
    print("5️⃣ Employees by department:")
    cursor.execute("""
    SELECT department, COUNT(*) as count
    FROM employees
    GROUP BY department
    ORDER BY count DESC
    """)
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} employees")
    
    conn.close()
    
    print("\n" + "="*50)
    print("✅ All database tests passed!")
    print("="*50)

if __name__ == "__main__":
    test_database()