"""MCP tools for querying the employee and leave databases."""


import os
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP


SCRIPT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(SCRIPT_ROOT / ".env")
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", str(SCRIPT_ROOT))).expanduser()

mcp = FastMCP("DatabaseMCPServer")


class DatabaseMCPServer:
    """Synchronous database access shared by MCP tools and local callers."""

    def __init__(self, db_path: str | os.PathLike[str] | None = None):
        configured_path = db_path or os.getenv("EMPLOYEE_DB_PATH", "data/employees.db")
        path = Path(configured_path).expanduser()
        self.db_path = path if path.is_absolute() else PROJECT_ROOT / path
        if not self.db_path.is_file():
            raise FileNotFoundError(
                f"Database not found: {self.db_path}. Run setup_database.py first."
            )

        try:
            with closing(self._get_connection()) as conn:
                conn.execute("SELECT COUNT(*) FROM employees").fetchone()
        except sqlite3.Error as exc:
            raise ConnectionError(f"Database connection failed: {exc}") from exc

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def get_employee_info(self, employee_id: str) -> dict[str, Any]:
        with closing(self._get_connection()) as conn:
            row = conn.execute(
                """SELECT emp_id, name, department, position, join_date, manager, email
                   FROM employees WHERE emp_id = ?""",
                (employee_id,),
            ).fetchone()

        if row is None:
            return {
                "employee_id": employee_id,
                "found": False,
                "message": f"Employee {employee_id} not found",
            }
        return {
            "employee_id": row[0],
            "name": row[1],
            "department": row[2],
            "position": row[3],
            "join_date": row[4],
            "manager": row[5],
            "email": row[6],
            "found": True,
        }

    def get_leave_balance(self, employee_id: str) -> dict[str, Any]:
        with closing(self._get_connection()) as conn:
            row = conn.execute(
                """SELECT e.name, l.casual_leave, l.earned_leave, l.sick_leave, l.last_updated
                   FROM employees AS e JOIN leave_balance AS l ON e.emp_id = l.emp_id
                   WHERE e.emp_id = ?""",
                (employee_id,),
            ).fetchone()

        if row is None:
            return {
                "employee_id": employee_id,
                "found": False,
                "message": f"Leave balance not found for {employee_id}",
            }
        return {
            "employee_id": employee_id,
            "name": row[0],
            "casual_leave": row[1],
            "earned_leave": row[2],
            "sick_leave": row[3],
            "total_leaves": row[1] + row[2] + row[3],
            "last_updated": row[4],
            "found": True,
        }

    def get_department_summary(self) -> dict[str, Any]:
        with closing(self._get_connection()) as conn:
            rows = conn.execute(
                """SELECT department, COUNT(*) AS employee_count
                   FROM employees GROUP BY department ORDER BY employee_count DESC"""
            ).fetchall()
        departments = {department: count for department, count in rows}
        return {
            "departments": departments,
            "total_employees": sum(departments.values()),
            "department_count": len(departments),
        }

    def search_employees(
        self, department: str | None = None, name_contains: str | None = None
    ) -> dict[str, Any]:
        query = "SELECT emp_id, name, department, position FROM employees WHERE 1=1"
        params: list[str] = []
        if department:
            query += " AND department = ?"
            params.append(department)
        if name_contains:
            query += " AND name LIKE ? COLLATE NOCASE"
            params.append(f"%{name_contains}%")
        query += " ORDER BY name"

        with closing(self._get_connection()) as conn:
            rows = conn.execute(query, params).fetchall()
        employees = [
            {"employee_id": row[0], "name": row[1], "department": row[2], "position": row[3]}
            for row in rows
        ]
        return {"employees": employees, "count": len(employees)}


def _database() -> DatabaseMCPServer:
    """Create the database accessor on first use, not while importing this module."""
    global _database_instance
    if _database_instance is None:
        _database_instance = DatabaseMCPServer()
    return _database_instance


_database_instance: DatabaseMCPServer | None = None


@mcp.tool()
def get_employee_info(employee_id: str) -> dict[str, Any]:
    """Get an employee's details by ID, such as EMP001."""
    return _database().get_employee_info(employee_id)


@mcp.tool()
def get_leave_balance(employee_id: str) -> dict[str, Any]:
    """Get an employee's casual, earned, and sick leave balances by ID."""
    return _database().get_leave_balance(employee_id)


@mcp.tool()
def get_department_summary() -> dict[str, Any]:
    """Get employee counts grouped by department."""
    return _database().get_department_summary()


@mcp.tool()
def search_employees(
    department: str | None = None, name_contains: str | None = None
) -> dict[str, Any]:
    """Search employees by exact department and/or a partial name."""
    return _database().search_employees(department, name_contains)


if __name__ == "__main__":
    mcp.run(transport="stdio")
