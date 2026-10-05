"""
MCP Server #2: Employee Database Access
Provides tools to query employee information and leave balances
"""

import os
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()








class DatabaseMCPServer:
    """
    Employee Database as MCP-style server
    
    Tools provided:
    1. get_employee_info - Get employee details by ID
    2. get_leave_balance - Get leave balance for employee
    3. get_department_summary - Get employee count by department
    """
    



    def __init__(self):
        """Initialize database connection"""
        
        print("🔄 Initializing Database Server...")
        
        self.db_path = os.getenv("EMPLOYEE_DB_PATH", "data/employees.db")
        
        # Verify database exists
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(
                f"❌ Database not found: {self.db_path}\n"
                f"   Please run: python setup_database.py"
            )
        
        # Test connection
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM employees")
            emp_count = cursor.fetchone()[0]
            conn.close()
            print(f"✅ Connected to database ({emp_count} employees)")
        except Exception as e:
            raise ConnectionError(f"❌ Database connection failed: {e}")
        
        print("✅ Database Server initialized successfully!")
    



    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    


    def get_employee_info(self, employee_id: str) -> Dict:
        """
        Tool 1: Get employee information by ID
        
        Args:
            employee_id: Employee ID (e.g., EMP001)
        
        Returns:
            Dict with employee details
        """
        
        print(f"  👤 Getting info for employee: {employee_id}")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT emp_id, name, department, position, join_date, manager, email
            FROM employees
            WHERE emp_id = ?
            """, (employee_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "employee_id": result[0],
                    "name": result[1],
                    "department": result[2],
                    "position": result[3],
                    "join_date": result[4],
                    "manager": result[5],
                    "email": result[6],
                    "tool": "get_employee_info",
                    "found": True
                }
            else:
                return {
                    "employee_id": employee_id,
                    "found": False,
                    "message": f"Employee {employee_id} not found",
                    "tool": "get_employee_info"
                }
                
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "tool": "get_employee_info"
            }
    


    def get_leave_balance(self, employee_id: str) -> Dict:
        """
        Tool 2: Get leave balance for employee
        
        Args:
            employee_id: Employee ID (e.g., EMP001)
        
        Returns:
            Dict with leave balance details
        """
        
        print(f"  📊 Getting leave balance for: {employee_id}")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get employee name + leave balance
            cursor.execute("""
            SELECT e.name, l.casual_leave, l.earned_leave, l.sick_leave, l.last_updated
            FROM employees e
            JOIN leave_balance l ON e.emp_id = l.emp_id
            WHERE e.emp_id = ?
            """, (employee_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                total_leaves = result[1] + result[2] + result[3]
                
                return {
                    "employee_id": employee_id,
                    "name": result[0],
                    "casual_leave": result[1],
                    "earned_leave": result[2],
                    "sick_leave": result[3],
                    "total_leaves": total_leaves,
                    "last_updated": result[4],
                    "tool": "get_leave_balance",
                    "found": True
                }
            else:
                return {
                    "employee_id": employee_id,
                    "found": False,
                    "message": f"Leave balance not found for {employee_id}",
                    "tool": "get_leave_balance"
                }
                
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "tool": "get_leave_balance"
            }
    


    def get_department_summary(self) -> Dict:
        """
        Tool 3: Get employee count by department
        
        Returns:
            Dict with department-wise employee count
        """
        
        print("  📈 Getting department summary...")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT department, COUNT(*) as count
            FROM employees
            GROUP BY department
            ORDER BY count DESC
            """)
            
            results = cursor.fetchall()
            conn.close()
            
            departments = {}
            total_employees = 0
            
            for dept, count in results:
                departments[dept] = count
                total_employees += count
            
            return {
                "departments": departments,
                "total_employees": total_employees,
                "department_count": len(departments),
                "tool": "get_department_summary"
            }
            
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "tool": "get_department_summary"
            }
    


    def search_employees(self, 
                        department: Optional[str] = None,
                        name_contains: Optional[str] = None) -> Dict:
        """
        Tool 4 (Bonus): Search employees by criteria
        
        Args:
            department: Filter by department
            name_contains: Filter by name (partial match)
        
        Returns:
            Dict with matching employees
        """
        
        print(f"  🔍 Searching employees (dept={department}, name={name_contains})")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT emp_id, name, department, position FROM employees WHERE 1=1"
            params = []
            
            if department:
                query += " AND department = ?"
                params.append(department)
            
            if name_contains:
                query += " AND name LIKE ?"
                params.append(f"%{name_contains}%")
            
            query += " ORDER BY name"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            employees = []
            for row in results:
                employees.append({
                    "employee_id": row[0],
                    "name": row[1],
                    "department": row[2],
                    "position": row[3]
                })
            
            return {
                "employees": employees,
                "count": len(employees),
                "tool": "search_employees"
            }
            
        except Exception as e:
            return {
                "error": True,
                "message": str(e),
                "tool": "search_employees"
            }
    


    def get_tool_descriptions(self) -> List[Dict]:
        """
        Get descriptions of available tools (for LLM to understand)
        """
        return [
            {
                "name": "get_employee_info",
                "description": "Get employee details like name, department, position, manager, email. Use when user asks about employee information.",
                "parameters": {
                    "employee_id": "Employee ID (e.g., EMP001, EMP002)"
                },
                "examples": [
                    "What is employee EMP001's department?",
                    "Who is the manager of EMP005?",
                    "Give me details for employee EMP003"
                ]
            },
            {
                "name": "get_leave_balance",
                "description": "Get employee's leave balance (casual, earned, sick leaves). Use when user asks about leave availability.",
                "parameters": {
                    "employee_id": "Employee ID (e.g., EMP001, EMP002)"
                },
                "examples": [
                    "How many leaves does EMP001 have?",
                    "What's my leave balance? (EMP002)",
                    "Check casual leave for EMP005"
                ]
            },
            {
                "name": "get_department_summary",
                "description": "Get employee count by department. Use when user asks about team size or department statistics.",
                "parameters": {},
                "examples": [
                    "How many people in each department?",
                    "Show me department-wise employee count",
                    "Which department has most employees?"
                ]
            },
            {
                "name": "search_employees",
                "description": "Search employees by department or name. Use when user wants to find employees matching criteria.",
                "parameters": {
                    "department": "Department name (optional)",
                    "name_contains": "Name search term (optional)"
                },
                "examples": [
                    "Show all employees in Engineering",
                    "Find employees with 'Kumar' in their name",
                    "List all HR department employees"
                ]
            }
        ]
    


    def call_tool(self, tool_name: str, **kwargs) -> Dict:
        """
        Generic tool calling interface
        
        Args:
            tool_name: Name of the tool to call
            **kwargs: Tool-specific arguments
        
        Returns:
            Tool response
        """
        
        if tool_name == "get_employee_info":
            employee_id = kwargs.get("employee_id", "")
            if not employee_id:
                return {"error": True, "message": "employee_id parameter required"}
            return self.get_employee_info(employee_id)
        
        elif tool_name == "get_leave_balance":
            employee_id = kwargs.get("employee_id", "")
            if not employee_id:
                return {"error": True, "message": "employee_id parameter required"}
            return self.get_leave_balance(employee_id)
        
        elif tool_name == "get_department_summary":
            return self.get_department_summary()
        
        elif tool_name == "search_employees":
            department = kwargs.get("department")
            name_contains = kwargs.get("name_contains")
            return self.search_employees(department, name_contains)
        
        else:
            return {
                "error": True,
                "message": f"Unknown tool: {tool_name}"
            }




# Test function
def test_database_server():
    """Test the database server with sample queries"""
    
    print("\n" + "="*60)
    print("🧪 TESTING DATABASE SERVER")
    print("="*60 + "\n")
    
    # Initialize server
    server = DatabaseMCPServer()
    
    print("\n" + "-"*60)
    print("Test 1: Get Employee Info")
    print("-"*60)
    
    result = server.get_employee_info("EMP001")
    
    if result['found']:
        print(f"\n👤 Employee: {result['name']}")
        print(f"   Department: {result['department']}")
        print(f"   Position: {result['position']}")
        print(f"   Email: {result['email']}")
        print(f"   Manager: {result['manager']}")
    
    print("\n" + "-"*60)
    print("Test 2: Get Leave Balance")
    print("-"*60)
    
    result = server.get_leave_balance("EMP001")
    
    if result['found']:
        print(f"\n📊 Leave Balance for {result['name']}:")
        print(f"   Casual Leave: {result['casual_leave']} days")
        print(f"   Earned Leave: {result['earned_leave']} days")
        print(f"   Sick Leave: {result['sick_leave']} days")
        print(f"   Total: {result['total_leaves']} days")
    
    print("\n" + "-"*60)
    print("Test 3: Department Summary")
    print("-"*60)
    
    result = server.get_department_summary()
    
    print(f"\n📈 Department Summary:")
    print(f"   Total Employees: {result['total_employees']}")
    print(f"   Departments: {result['department_count']}")
    print(f"\n   Breakdown:")
    for dept, count in result['departments'].items():
        print(f"   - {dept}: {count} employees")
    
    print("\n" + "-"*60)
    print("Test 4: Search Employees")
    print("-"*60)
    
    result = server.search_employees(department="Engineering")
    
    print(f"\n🔍 Engineering Department ({result['count']} employees):")
    for emp in result['employees']:
        print(f"   - {emp['employee_id']}: {emp['name']} ({emp['position']})")
    
    print("\n" + "-"*60)
    print("Test 5: Tool Descriptions")
    print("-"*60)
    
    tools = server.get_tool_descriptions()
    print(f"\nAvailable Tools: {len(tools)}")
    for tool in tools:
        print(f"\n📌 {tool['name']}")
        print(f"   {tool['description'][:70]}...")
    
    print("\n" + "="*60)
    print("✅ Database Server tests complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_database_server()