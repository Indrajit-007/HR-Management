"""
View all data in the employee database with nice formatting
"""

import sqlite3
from datetime import datetime

def view_database():
    conn = sqlite3.connect("data/employees.db")
    cursor = conn.cursor()
    
    print("\n" + "="*80)
    print("📊 EMPLOYEE DATABASE - COMPLETE VIEW")
    print("="*80)
    
    # TABLE 1: EMPLOYEES
    print("\n" + "="*80)
    print("👥 TABLE 1: EMPLOYEES")
    print("="*80)
    
    cursor.execute("SELECT * FROM employees ORDER BY emp_id")
    employees = cursor.fetchall()
    
    print(f"\n{'ID':<8} {'Name':<18} {'Department':<12} {'Position':<20} {'Join Date':<12} {'Manager':<8}")
    print("-" * 80)
    
    for emp in employees:
        emp_id = emp[0]
        name = emp[1][:17]  # Truncate if too long
        dept = emp[2][:11]
        position = emp[3][:19]
        join_date = emp[4]
        manager = emp[5] if emp[5] else "None"
        
        print(f"{emp_id:<8} {name:<18} {dept:<12} {position:<20} {join_date:<12} {manager:<8}")
    
    print(f"\n📊 Total Employees: {len(employees)}")
    
    # TABLE 2: LEAVE BALANCE
    print("\n" + "="*80)
    print("📅 TABLE 2: LEAVE BALANCE")
    print("="*80)
    
    cursor.execute("""
    SELECT l.emp_id, e.name, l.casual_leave, l.earned_leave, l.sick_leave, l.last_updated
    FROM leave_balance l
    JOIN employees e ON l.emp_id = e.emp_id
    ORDER BY l.emp_id
    """)
    balances = cursor.fetchall()
    
    print(f"\n{'ID':<8} {'Name':<18} {'Casual':<8} {'Earned':<8} {'Sick':<8} {'Last Updated':<12}")
    print("-" * 80)
    
    total_cl = 0
    total_el = 0
    total_sl = 0
    
    for balance in balances:
        emp_id = balance[0]
        name = balance[1][:17]
        casual = balance[2]
        earned = balance[3]
        sick = balance[4]
        updated = balance[5]
        
        total_cl += casual
        total_el += earned
        total_sl += sick
        
        print(f"{emp_id:<8} {name:<18} {casual:<8} {earned:<8} {sick:<8} {updated:<12}")
    
    print("-" * 80)
    print(f"{'TOTALS':<27} {total_cl:<8} {total_el:<8} {total_sl:<8}")
    
    # COMBINED VIEW
    print("\n" + "="*80)
    print("🔗 COMBINED VIEW: EMPLOYEES + LEAVE BALANCE")
    print("="*80)
    
    cursor.execute("""
    SELECT e.emp_id, e.name, e.department, e.position,
           l.casual_leave, l.earned_leave, l.sick_leave,
           (l.casual_leave + l.earned_leave + l.sick_leave) as total_leaves
    FROM employees e
    JOIN leave_balance l ON e.emp_id = l.emp_id
    ORDER BY total_leaves DESC
    """)
    
    combined = cursor.fetchall()
    
    print(f"\n{'ID':<8} {'Name':<18} {'Department':<12} {'CL':<5} {'EL':<5} {'SL':<5} {'Total':<6}")
    print("-" * 80)
    
    for row in combined:
        print(f"{row[0]:<8} {row[1][:17]:<18} {row[2][:11]:<12} {row[4]:<5} {row[5]:<5} {row[6]:<5} {row[7]:<6}")
    
    # STATISTICS
    print("\n" + "="*80)
    print("📈 DATABASE STATISTICS")
    print("="*80)
    
    # Department breakdown
    cursor.execute("""
    SELECT department, COUNT(*) as count
    FROM employees
    GROUP BY department
    ORDER BY count DESC
    """)
    
    print("\n👔 Employees by Department:")
    for dept in cursor.fetchall():
        print(f"   {dept[0]:<15} : {dept[1]} employees")
    
    # Average leaves
    cursor.execute("""
    SELECT 
        AVG(casual_leave) as avg_cl,
        AVG(earned_leave) as avg_el,
        AVG(sick_leave) as avg_sl
    FROM leave_balance
    """)
    
    avg = cursor.fetchone()
    print(f"\n📊 Average Leave Balance:")
    print(f"   Casual Leave  : {avg[0]:.1f} days")
    print(f"   Earned Leave  : {avg[1]:.1f} days")
    print(f"   Sick Leave    : {avg[2]:.1f} days")
    
    # Who has most/least leaves
    cursor.execute("""
    SELECT e.name, (l.casual_leave + l.earned_leave + l.sick_leave) as total
    FROM employees e
    JOIN leave_balance l ON e.emp_id = l.emp_id
    ORDER BY total DESC
    LIMIT 1
    """)
    most = cursor.fetchone()
    
    cursor.execute("""
    SELECT e.name, (l.casual_leave + l.earned_leave + l.sick_leave) as total
    FROM employees e
    JOIN leave_balance l ON e.emp_id = l.emp_id
    ORDER BY total ASC
    LIMIT 1
    """)
    least = cursor.fetchone()
    
    print(f"\n🏆 Most Leaves  : {most[0]} ({most[1]} days)")
    print(f"⚠️  Least Leaves : {least[0]} ({least[1]} days)")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ Database view complete!")
    print("="*80 + "\n")

if __name__ == "__main__":
    view_database()