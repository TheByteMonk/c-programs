"""
COMPLEX ADMINISTRATION SYSTEM
Version 1.0
Features:
- User authentication with roles (admin, manager, staff)
- Department management
- Employee records
- Task assignment and tracking
- Reporting system
- Data persistence using JSON files
"""

import json
import os
from datetime import datetime
from getpass import getpass
import hashlib
import sys
from typing import Dict, List, Optional, Union

# Constants
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
DEPARTMENTS_FILE = os.path.join(DATA_DIR, "departments.json")
EMPLOYEES_FILE = os.path.join(DATA_DIR, "employees.json")
TASKS_FILE = os.path.join(DATA_DIR, "tasks.json")
LOGS_FILE = os.path.join(DATA_DIR, "activity_logs.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize empty data structures if files don't exist
for file in [USERS_FILE, DEPARTMENTS_FILE, EMPLOYEES_FILE, TASKS_FILE, LOGS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump([], f)

class User:
    def __init__(self, username: str, password_hash: str, role: str, full_name: str, email: str):
        self.username = username
        self.password_hash = password_hash
        self.role = role  # 'admin', 'manager', 'staff'
        self.full_name = full_name
        self.email = email
        self.last_login = None
        self.is_active = True

    def to_dict(self) -> Dict:
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role,
            'full_name': self.full_name,
            'email': self.email,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        user = cls(
            username=data['username'],
            password_hash=data['password_hash'],
            role=data['role'],
            full_name=data['full_name'],
            email=data['email']
        )
        user.last_login = datetime.fromisoformat(data['last_login']) if data['last_login'] else None
        user.is_active = data['is_active']
        return user

    def verify_password(self, password: str) -> bool:
        return self.password_hash == self.hash_password(password)

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

class Department:
    def __init__(self, dept_id: str, name: str, manager: str, description: str = ""):
        self.dept_id = dept_id
        self.name = name
        self.manager = manager  # username of the manager
        self.description = description
        self.employees = []
        self.budget = 0.0
        self.created_at = datetime.now()

    def to_dict(self) -> Dict:
        return {
            'dept_id': self.dept_id,
            'name': self.name,
            'manager': self.manager,
            'description': self.description,
            'employees': self.employees,
            'budget': self.budget,
            'created_at': self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Department':
        dept = cls(
            dept_id=data['dept_id'],
            name=data['name'],
            manager=data['manager'],
            description=data.get('description', "")
        )
        dept.employees = data.get('employees', [])
        dept.budget = data.get('budget', 0.0)
        dept.created_at = datetime.fromisoformat(data['created_at'])
        return dept

    def add_employee(self, employee_id: str) -> bool:
        if employee_id not in self.employees:
            self.employees.append(employee_id)
            return True
        return False

    def remove_employee(self, employee_id: str) -> bool:
        if employee_id in self.employees:
            self.employees.remove(employee_id)
            return True
        return False

class Employee:
    def __init__(self, emp_id: str, full_name: str, position: str, department: str, 
                 hire_date: str, salary: float, email: str, phone: str):
        self.emp_id = emp_id
        self.full_name = full_name
        self.position = position
        self.department = department  # department ID
        self.hire_date = hire_date  # YYYY-MM-DD
        self.salary = salary
        self.email = email
        self.phone = phone
        self.is_active = True
        self.emergency_contact = None
        self.notes = ""

    def to_dict(self) -> Dict:
        return {
            'emp_id': self.emp_id,
            'full_name': self.full_name,
            'position': self.position,
            'department': self.department,
            'hire_date': self.hire_date,
            'salary': self.salary,
            'email': self.email,
            'phone': self.phone,
            'is_active': self.is_active,
            'emergency_contact': self.emergency_contact,
            'notes': self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Employee':
        emp = cls(
            emp_id=data['emp_id'],
            full_name=data['full_name'],
            position=data['position'],
            department=data['department'],
            hire_date=data['hire_date'],
            salary=data['salary'],
            email=data['email'],
            phone=data['phone']
        )
        emp.is_active = data.get('is_active', True)
        emp.emergency_contact = data.get('emergency_contact')
        emp.notes = data.get('notes', "")
        return emp

class Task:
    def __init__(self, task_id: str, title: str, description: str, assigned_to: str, 
                 assigned_by: str, due_date: str, priority: str = "medium"):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.assigned_to = assigned_to  # employee ID
        self.assigned_by = assigned_by  # username
        self.due_date = due_date  # YYYY-MM-DD
        self.priority = priority  # low, medium, high
        self.status = "pending"  # pending, in_progress, completed, cancelled
        self.created_at = datetime.now()
        self.completed_at = None
        self.comments = []

    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'assigned_to': self.assigned_to,
            'assigned_by': self.assigned_by,
            'due_date': self.due_date,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'comments': self.comments
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        task = cls(
            task_id=data['task_id'],
            title=data['title'],
            description=data['description'],
            assigned_to=data['assigned_to'],
            assigned_by=data['assigned_by'],
            due_date=data['due_date'],
            priority=data.get('priority', 'medium')
        )
        task.status = data.get('status', 'pending')
        task.created_at = datetime.fromisoformat(data['created_at'])
        task.completed_at = datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None
        task.comments = data.get('comments', [])
        return task

    def add_comment(self, comment: str, author: str) -> None:
        timestamp = datetime.now().isoformat()
        self.comments.append({
            'text': comment,
            'author': author,
            'timestamp': timestamp
        })

    def update_status(self, new_status: str) -> None:
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if new_status in valid_statuses:
            self.status = new_status
            if new_status == 'completed':
                self.completed_at = datetime.now()

class AdminSystem:
    def __init__(self):
        self.current_user = None
        self.users = self._load_data(USERS_FILE, User)
        self.departments = self._load_data(DEPARTMENTS_FILE, Department)
        self.employees = self._load_data(EMPLOYEES_FILE, Employee)
        self.tasks = self._load_data(TASKS_FILE, Task)
        self.logs = self._load_logs()

    def _load_data(self, filename: str, cls) -> Dict:
        with open(filename, 'r') as f:
            data = json.load(f)
        return {item['username'] if 'username' in item else item['dept_id'] if 'dept_id' in item else item['emp_id'] if 'emp_id' in item else item['task_id']: cls.from_dict(item) for item in data}

    def _load_logs(self) -> List[Dict]:
        with open(LOGS_FILE, 'r') as f:
            return json.load(f)

    def _save_data(self, filename: str, data: Union[Dict, List]) -> None:
        if isinstance(data, dict):
            data = [v.to_dict() for v in data.values()]
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

    def _log_activity(self, action: str, details: str = "") -> None:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user': self.current_user.username if self.current_user else 'system',
            'action': action,
            'details': details
        }
        self.logs.append(log_entry)
        self._save_data(LOGS_FILE, self.logs)

    def login(self) -> bool:
        print("\n=== Login ===")
        username = input("Username: ")
        password = getpass("Password: ")

        user = self.users.get(username)
        if user and user.verify_password(password) and user.is_active:
            self.current_user = user
            user.last_login = datetime.now()
            self._save_data(USERS_FILE, self.users)
            self._log_activity("login", f"User {username} logged in")
            return True
        print("Invalid username or password")
        return False

    def logout(self) -> None:
        if self.current_user:
            self._log_activity("logout", f"User {self.current_user.username} logged out")
            self.current_user = None
        print("Logged out successfully")

    def change_password(self) -> None:
        if not self.current_user:
            print("You must be logged in to change password")
            return

        print("\n=== Change Password ===")
        current = getpass("Current password: ")
        if not self.current_user.verify_password(current):
            print("Incorrect current password")
            return

        new_pass = getpass("New password: ")
        confirm = getpass("Confirm new password: ")
        if new_pass != confirm:
            print("Passwords don't match")
            return

        self.current_user.password_hash = User.hash_password(new_pass)
        self._save_data(USERS_FILE, self.users)
        self._log_activity("password_change", "User changed their password")
        print("Password changed successfully")

    # User Management
    def create_user(self) -> None:
        if not self.current_user or self.current_user.role != 'admin':
            print("Only admins can create users")
            return

        print("\n=== Create New User ===")
        username = input("Username: ")
        if username in self.users:
            print("Username already exists")
            return

        password = getpass("Password: ")
        confirm = getpass("Confirm password: ")
        if password != confirm:
            print("Passwords don't match")
            return

        role = input("Role (admin/manager/staff): ").lower()
        if role not in ['admin', 'manager', 'staff']:
            print("Invalid role")
            return

        full_name = input("Full name: ")
        email = input("Email: ")

        new_user = User(
            username=username,
            password_hash=User.hash_password(password),
            role=role,
            full_name=full_name,
            email=email
        )
        self.users[username] = new_user
        self._save_data(USERS_FILE, self.users)
        self._log_activity("user_create", f"Created user {username} with role {role}")
        print(f"User {username} created successfully")

    def list_users(self) -> None:
        if not self.current_user or self.current_user.role not in ['admin', 'manager']:
            print("Permission denied")
            return

        print("\n=== User List ===")
        print(f"{'Username':<15} {'Full Name':<20} {'Role':<10} {'Email':<25} {'Last Login':<20}")
        for user in sorted(self.users.values(), key=lambda u: u.username):
            last_login = user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"
            print(f"{user.username:<15} {user.full_name:<20} {user.role:<10} {user.email:<25} {last_login:<20}")

    # Department Management
    def create_department(self) -> None:
        if not self.current_user or self.current_user.role != 'admin':
            print("Only admins can create departments")
            return

        print("\n=== Create New Department ===")
        dept_id = input("Department ID: ")
        if dept_id in self.departments:
            print("Department ID already exists")
            return

        name = input("Department Name: ")
        manager = input("Manager username: ")
        if manager not in self.users or self.users[manager].role != 'manager':
            print("Invalid manager username or user is not a manager")
            return

        description = input("Description (optional): ")
        budget = float(input("Annual budget: "))

        new_dept = Department(
            dept_id=dept_id,
            name=name,
            manager=manager,
            description=description
        )
        new_dept.budget = budget
        self.departments[dept_id] = new_dept
        self._save_data(DEPARTMENTS_FILE, self.departments)
        self._log_activity("dept_create", f"Created department {dept_id}")
        print(f"Department {name} created successfully")

    def list_departments(self) -> None:
        print("\n=== Department List ===")
        print(f"{'ID':<8} {'Name':<20} {'Manager':<15} {'Employees':<5} {'Budget':<15}")
        for dept in sorted(self.departments.values(), key=lambda d: d.dept_id):
            manager_name = self.users[dept.manager].full_name if dept.manager in self.users else "Unknown"
            print(f"{dept.dept_id:<8} {dept.name:<20} {manager_name:<15} {len(dept.employees):<5} ${dept.budget:,.2f}")

    # Employee Management
    def add_employee(self) -> None:
        if not self.current_user or self.current_user.role not in ['admin', 'manager']:
            print("Permission denied")
            return

        print("\n=== Add New Employee ===")
        emp_id = input("Employee ID: ")
        if emp_id in self.employees:
            print("Employee ID already exists")
            return

        full_name = input("Full Name: ")
        position = input("Position: ")
        
        # Show available departments
        self.list_departments()
        department = input("Department ID: ")
        if department not in self.departments:
            print("Invalid department ID")
            return

        hire_date = input("Hire Date (YYYY-MM-DD): ")
        try:
            datetime.strptime(hire_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format")
            return

        salary = float(input("Salary: "))
        email = input("Email: ")
        phone = input("Phone: ")

        new_emp = Employee(
            emp_id=emp_id,
            full_name=full_name,
            position=position,
            department=department,
            hire_date=hire_date,
            salary=salary,
            email=email,
            phone=phone
        )
        self.employees[emp_id] = new_emp
        self.departments[department].add_employee(emp_id)
        
        self._save_data(EMPLOYEES_FILE, self.employees)
        self._save_data(DEPARTMENTS_FILE, self.departments)
        self._log_activity("employee_add", f"Added employee {emp_id}")
        print(f"Employee {full_name} added successfully")

    def list_employees(self, department_id: str = None) -> None:
        print("\n=== Employee List ===")
        if department_id:
            if department_id not in self.departments:
                print("Invalid department ID")
                return
            employees = [self.employees[eid] for eid in self.departments[department_id].employees if eid in self.employees]
            print(f"Employees in {self.departments[department_id].name} department:")
        else:
            employees = list(self.employees.values())

        print(f"{'ID':<8} {'Name':<20} {'Position':<20} {'Department':<15} {'Hire Date':<12} {'Salary':<10}")
        for emp in sorted(employees, key=lambda e: e.emp_id):
            dept_name = self.departments[emp.department].name if emp.department in self.departments else "Unknown"
            print(f"{emp.emp_id:<8} {emp.full_name:<20} {emp.position:<20} {dept_name:<15} {emp.hire_date:<12} ${emp.salary:,.2f}")

    # Task Management
    def create_task(self) -> None:
        if not self.current_user:
            print("You must be logged in to create tasks")
            return

        print("\n=== Create New Task ===")
        task_id = input("Task ID: ")
        if task_id in self.tasks:
            print("Task ID already exists")
            return

        title = input("Title: ")
        description = input("Description: ")
        
        # Show employees
        self.list_employees()
        assigned_to = input("Assign to Employee ID: ")
        if assigned_to not in self.employees:
            print("Invalid employee ID")
            return

        due_date = input("Due Date (YYYY-MM-DD): ")
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format")
            return

        priority = input("Priority (low/medium/high): ").lower()
        if priority not in ['low', 'medium', 'high']:
            priority = 'medium'

        new_task = Task(
            task_id=task_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            assigned_by=self.current_user.username,
            due_date=due_date,
            priority=priority
        )
        self.tasks[task_id] = new_task
        self._save_data(TASKS_FILE, self.tasks)
        self._log_activity("task_create", f"Created task {task_id} assigned to {assigned_to}")
        print(f"Task '{title}' created successfully")

    def list_tasks(self, assigned_to: str = None) -> None:
        print("\n=== Task List ===")
        if assigned_to:
            tasks = [t for t in self.tasks.values() if t.assigned_to == assigned_to]
            emp_name = self.employees[assigned_to].full_name if assigned_to in self.employees else assigned_to
            print(f"Tasks assigned to {emp_name}:")
        else:
            tasks = list(self.tasks.values())

        print(f"{'ID':<8} {'Title':<20} {'Assigned To':<20} {'Due Date':<12} {'Priority':<8} {'Status':<12}")
        for task in sorted(tasks, key=lambda t: t.due_date):
            emp_name = self.employees[task.assigned_to].full_name if task.assigned_to in self.employees else task.assigned_to
            print(f"{task.task_id:<8} {task.title:<20} {emp_name:<20} {task.due_date:<12} {task.priority:<8} {task.status:<12}")

    def update_task_status(self) -> None:
        if not self.current_user:
            print("You must be logged in to update tasks")
            return

        print("\n=== Update Task Status ===")
        task_id = input("Task ID: ")
        if task_id not in self.tasks:
            print("Task not found")
            return

        task = self.tasks[task_id]
        print(f"Current status: {task.status}")
        print("Available statuses: pending, in_progress, completed, cancelled")
        new_status = input("New status: ").lower()

        if new_status not in ['pending', 'in_progress', 'completed', 'cancelled']:
            print("Invalid status")
            return

        task.update_status(new_status)
        if new_status == 'completed':
            task.completed_at = datetime.now()

        comment = input("Add comment (optional): ")
        if comment:
            task.add_comment(comment, self.current_user.username)

        self._save_data(TASKS_FILE, self.tasks)
        self._log_activity("task_update", f"Updated task {task_id} to status {new_status}")
        print("Task updated successfully")

    # Reporting
    def generate_department_report(self) -> None:
        if not self.current_user or self.current_user.role not in ['admin', 'manager']:
            print("Permission denied")
            return

        print("\n=== Department Report ===")
        self.list_departments()
        dept_id = input("Select department ID: ")
        if dept_id not in self.departments:
            print("Invalid department ID")
            return

        dept = self.departments[dept_id]
        print(f"\nDepartment: {dept.name}")
        print(f"Manager: {self.users[dept.manager].full_name}")
        print(f"Budget: ${dept.budget:,.2f}")
        print(f"Employee Count: {len(dept.employees)}")
        print("\nEmployees:")
        self.list_employees(dept_id)

        print("\nTasks:")
        dept_employees = dept.employees
        dept_tasks = [t for t in self.tasks.values() if t.assigned_to in dept_employees]
        for task in sorted(dept_tasks, key=lambda t: t.due_date):
            status = task.status.upper() if task.status == 'pending' else task.status
            print(f"- {task.title} (Due: {task.due_date}, Status: {status})")

    def generate_employee_report(self) -> None:
        if not self.current_user:
            print("You must be logged in")
            return

        print("\n=== Employee Report ===")
        self.list_employees()
        emp_id = input("Select employee ID: ")
        if emp_id not in self.employees:
            print("Invalid employee ID")
            return

        emp = self.employees[emp_id]
        dept = self.departments.get(emp.department, None)
        print(f"\nEmployee: {emp.full_name}")
        print(f"Position: {emp.position}")
        print(f"Department: {dept.name if dept else 'Unknown'}")
        print(f"Hire Date: {emp.hire_date}")
        print(f"Salary: ${emp.salary:,.2f}")
        print(f"Email: {emp.email}")
        print(f"Phone: {emp.phone}")

        print("\nTasks Assigned:")
        emp_tasks = [t for t in self.tasks.values() if t.assigned_to == emp_id]
        if not emp_tasks:
            print("No tasks assigned")
        else:
            for task in sorted(emp_tasks, key=lambda t: t.due_date):
                status = task.status.upper() if task.status == 'pending' else task.status
                print(f"- {task.title} (Due: {task.due_date}, Status: {status})")

    def view_activity_logs(self) -> None:
        if not self.current_user or self.current_user.role != 'admin':
            print("Only admins can view activity logs")
            return

        print("\n=== Activity Logs ===")
        print(f"{'Timestamp':<25} {'User':<15} {'Action':<20} {'Details':<30}")
        for log in sorted(self.logs, key=lambda l: l['timestamp'], reverse=True)[:50]:  # Show last 50 entries
            timestamp = datetime.fromisoformat(log['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp:<25} {log['user']:<15} {log['action']:<20} {log.get('details', '')[:30]:<30}")

    # Main Menu
    def main_menu(self) -> None:
        while True:
            print("\n=== ADMINISTRATION SYSTEM ===")
            if self.current_user:
                print(f"Logged in as: {self.current_user.full_name} ({self.current_user.role})")
                print("1. User Management")
                print("2. Department Management")
                print("3. Employee Management")
                print("4. Task Management")
                print("5. Reports")
                print("6. Change Password")
                print("7. Logout")
                if self.current_user.role == 'admin':
                    print("8. View Activity Logs")
                print("0. Exit")
            else:
                print("1. Login")
                print("0. Exit")

            choice = input("Enter choice: ")

            if self.current_user:
                if choice == '1':  # User Management
                    if self.current_user.role == 'admin':
                        print("\nUser Management")
                        print("1. Create User")
                        print("2. List Users")
                        sub = input("Enter choice: ")
                        if sub == '1':
                            self.create_user()
                        elif sub == '2':
                            self.list_users()
                    else:
                        print("Permission denied")

                elif choice == '2':  # Department Management
                    if self.current_user.role == 'admin':
                        print("\nDepartment Management")
                        print("1. Create Department")
                        print("2. List Departments")
                        sub = input("Enter choice: ")
                        if sub == '1':
                            self.create_department()
                        elif sub == '2':
                            self.list_departments()
                    else:
                        print("Permission denied")

                elif choice == '3':  # Employee Management
                    print("\nEmployee Management")
                    print("1. Add Employee")
                    print("2. List Employees")
                    print("3. List Department Employees")
                    sub = input("Enter choice: ")
                    if sub == '1':
                        self.add_employee()
                    elif sub == '2':
                        self.list_employees()
                    elif sub == '3':
                        dept = input("Enter department ID: ")
                        self.list_employees(dept)

                elif choice == '4':  # Task Management
                    print("\nTask Management")
                    print("1. Create Task")
                    print("2. List All Tasks")
                    print("3. List My Tasks")
                    print("4. Update Task Status")
                    sub = input("Enter choice: ")
                    if sub == '1':
                        self.create_task()
                    elif sub == '2':
                        self.list_tasks()
                    elif sub == '3':
                        emp_id = input("Enter employee ID (leave blank for current user): ")
                        if not emp_id and self.current_user:
                            # Find employee record matching current user's email
                            emp_id = next((e.emp_id for e in self.employees.values() if e.email == self.current_user.email), None)
                        if emp_id:
                            self.list_tasks(emp_id)
                        else:
                            print("No employee record found for current user")
                    elif sub == '4':
                        self.update_task_status()

                elif choice == '5':  # Reports
                    print("\nReports")
                    print("1. Department Report")
                    print("2. Employee Report")
                    sub = input("Enter choice: ")
                    if sub == '1':
                        self.generate_department_report()
                    elif sub == '2':
                        self.generate_employee_report()

                elif choice == '6':
                    self.change_password()

                elif choice == '7':
                    self.logout()

                elif choice == '8' and self.current_user.role == 'admin':
                    self.view_activity_logs()

                elif choice == '0':
                    if self.current_user:
                        self.logout()
                    print("Exiting system...")
                    sys.exit(0)

            else:  # Not logged in
                if choice == '1':
                    if self.login():
                        continue
                elif choice == '0':
                    print("Exiting system...")
                    sys.exit(0)

if __name__ == "__main__":
    system = AdminSystem()
    
    # Create default admin if no users exist
    if not system.users:
        print("No users found. Creating default admin account...")
        admin = User(
            username="admin",
            password_hash=User.hash_password("admin123"),
            role="admin",
            full_name="System Administrator",
            email="admin@company.com"
        )
        system.users["admin"] = admin
        system._save_data(USERS_FILE, system.users)
        print("Default admin created - username: admin, password: admin123")
        print("Please change the password immediately after login!")

    system.main_menu()