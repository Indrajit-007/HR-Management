"""
Interactive testing of Database server
"""

from mcp_servers.database_server import DatabaseServer

def interactive_test():
    print("\n💾 Database Server - Interactive Testing")
    print("="*60)
    
    # Initialize
    server = DatabaseServer()
    
    print("\n💬 Commands:")
    print("  - info <EMP_ID>     : Get employee info")
    print("  - leave <EMP_ID>    : Get leave balance")
    print("  - dept              : Department summary")
    print("  - search <dept>     : Search by department")
    print("  - exit              : Quit")
    print("="*60 + "\n")
    
    while True:
        cmd = input("Command: ").strip().lower()
        
        if cmd == 'exit':
            print("\n👋 Goodbye!")
            break
        
        parts = cmd.split()
        if not parts:
            continue
        
        action = parts[0]
        
        if action == 'info' and len(parts) > 1:
            emp_id = parts[1].upper()
            result = server.get_employee_info(emp_id)
            
            if result['found']:
                print(f"\n👤 {result['name']}")
                print(f"   ID: {result['employee_id']}")
                print(f"   Dept: {result['department']}")
                print(f"   Position: {result['position']}")
                print(f"   Manager: {result['manager']}")
                print(f"   Email: {result['email']}")
            else:
                print(f"\n❌ {result['message']}")
        
        elif action == 'leave' and len(parts) > 1:
            emp_id = parts[1].upper()
            result = server.get_leave_balance(emp_id)
            
            if result['found']:
                print(f"\n📊 Leave Balance for {result['name']}:")
                print(f"   Casual: {result['casual_leave']} days")
                print(f"   Earned: {result['earned_leave']} days")
                print(f"   Sick: {result['sick_leave']} days")
                print(f"   Total: {result['total_leaves']} days")
            else:
                print(f"\n❌ {result['message']}")
        
        elif action == 'dept':
            result = server.get_department_summary()
            print(f"\n📈 Department Summary:")
            for dept, count in result['departments'].items():
                print(f"   {dept}: {count} employees")
        
        elif action == 'search' and len(parts) > 1:
            dept = ' '.join(parts[1:]).title()
            result = server.search_employees(department=dept)
            
            print(f"\n🔍 Found {result['count']} employees:")
            for emp in result['employees']:
                print(f"   {emp['employee_id']}: {emp['name']} ({emp['position']})")
        
        else:
            print("❌ Invalid command. Try: info EMP001, leave EMP001, dept, search Engineering")
        
        print()

if __name__ == "__main__":
    interactive_test()