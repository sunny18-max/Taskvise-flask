from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
import csv, os, uuid
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
EMP_CSV = os.path.join(DATA_DIR, "employees.csv")
TASKS_CSV = os.path.join(DATA_DIR, "tasks.csv")
PROJECTS_CSV = os.path.join(DATA_DIR, "projects.csv")
PROJECT_MEMBERS_CSV = os.path.join(DATA_DIR, "project_members.csv")
LEAVE_CSV = os.path.join(DATA_DIR, "leave.csv")
NOTES_CSV = os.path.join(DATA_DIR, "team_notes.csv")
WORK_CSV = os.path.join(DATA_DIR, "work.csv")

def ensure_csv(path, headers):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()

def ensure_notes_csv():
    # Use ensure_csv so we don't rely on write_csv before it's defined
    ensure_csv(NOTES_CSV, ['id','title','content','author','author_id','priority','is_pinned','created_at','updated_at','visible_to'])

ensure_csv(USERS_CSV, ["id","username","password_hash","full_name","role","created_at","is_active"])
ensure_csv(EMP_CSV, ["id","name","email","position","department","join_date","phone","skills","location","last_login","password_last_changed"])
ensure_csv(TASKS_CSV, ["id","title","description","project_id","assignee_id","status","priority","created_at","due_date"])
ensure_csv(PROJECTS_CSV, ["id","name","description","owner_id","start_date","end_date","status"])
ensure_csv(PROJECT_MEMBERS_CSV, ["id","project_id","employee_id"])
ensure_csv(LEAVE_CSV, ["id","employee_id","start_date","end_date","reason","status","applied_at"])
ensure_csv(WORK_CSV, ["id","employee_id","task_id","start_time","end_time","duration_minutes","notes"])
ensure_notes_csv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")

def create_sample_users():
    """Create sample users for testing"""
    sample_users = [
        {
            "username": "admin@gmail.com",
            "password": "admin123", 
            "role": "admin",
            "full_name": "System Administrator"
        },
        {
            "username": "manager@gmail.com",
            "password": "manager123",
            "role": "manager", 
            "full_name": "Project Manager"
        },
        {
            "username": "employee1@gmail.com",
            "password": "emp123",
            "role": "employee",
            "full_name": "John Doe"
        },
        {
            "username": "employee2@gmail.com", 
            "password": "empl123",
            "role": "employee",
            "full_name": "Jane Smith"
        },
        {
            "username": "hr@gmail.com",
            "password": "hr123",
            "role": "hr",
            "full_name": "HR Manager"
        },
        {
            "username": "teamlead@gmail.com",
            "password": "lead123", 
            "role": "teamlead",
            "full_name": "Team Lead"
        }
    ]
    
    # Check if we need to create sample users
    existing_users = read_csv(USERS_CSV)
    existing_usernames = [user['username'] for user in existing_users]
    
    for sample in sample_users:
        if sample['username'] not in existing_usernames:
            user_id = str(uuid.uuid4())
            user_row = {
                'id': user_id,
                'username': sample['username'],
                'password_hash': generate_password_hash(sample['password']),
                'full_name': sample['full_name'],
                'role': sample['role'],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': 'true'
            }
            
            # Create corresponding employee record
            employee_row = {
                'id': user_id,
                'name': sample['full_name'],
                'email': sample['username'],
                'position': sample['role'].title(),
                'department': 'IT',
                'join_date': datetime.now().strftime('%Y-%m-%d'),
                'phone': '555-0100',
                'skills': 'Sample Skills',
                'location': 'Office',
                'last_login': '',
                'password_last_changed': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            append_csv(USERS_CSV, user_row, ['id','username','password_hash','full_name','role','created_at','is_active'])
            append_csv(EMP_CSV, employee_row, ['id','name','email','position','department','join_date','phone','skills','location','last_login','password_last_changed'])
            print(f"Created sample user: {sample['username']}")

def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_csv(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def append_csv(path, row, fieldnames):
    exists = os.path.exists(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists or os.path.getsize(path) == 0:
            writer.writeheader()
        writer.writerow(row)

def find_by_id(path, id):
    rows = read_csv(path)
    for r in rows:
        if r.get("id") == id:
            return r
    return None

def update_by_id(path, id, updates, fieldnames):
    rows = read_csv(path)
    updated = False
    for r in rows:
        if r.get("id") == id:
            r.update(updates)
            updated = True
    if updated:
        write_csv(path, rows, fieldnames)
    return updated

def delete_by_id(path, id, fieldnames):
    rows = read_csv(path)
    new = [r for r in rows if r.get("id") != id]
    if len(new) != len(rows):
        write_csv(path, new, fieldnames)
        return True
    return False

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated

# Helper functions for role-based display
def get_role_title(role):
    role_titles = {
        'admin': 'Admin Credentials Generated!',
        'manager': 'Manager Credentials Generated!',
        'hr': 'HR Credentials Generated!',
        'teamlead': 'Team Lead Credentials Generated!',
        'employee': 'Employee Credentials Generated!'
    }
    return role_titles.get(role, 'Employee Credentials Generated!')

def get_role_description(role):
    role_descriptions = {
        'admin': 'Administrator account with full system access',
        'manager': 'Manager account with team management access',
        'hr': 'HR account with employee management access',
        'teamlead': 'Team Lead account with project team access',
        'employee': 'Employee account created successfully'
    }
    return role_descriptions.get(role, 'Employee account created successfully')

def get_role_access_description(role):
    access_descriptions = {
        'admin': 'Admin access includes all system privileges',
        'manager': 'Manager access includes team management features',
        'hr': 'HR access includes employee management and HR features',
        'teamlead': 'Team Lead access includes project team management',
        'employee': 'Employee can access personal dashboard and tasks'
    }
    return access_descriptions.get(role, 'Employee can access personal dashboard and tasks')

def get_employee_data(user_id):
    """Get comprehensive employee data for dashboard display"""
    
    # Resolve the employee profile row by id/email/name to handle users.id vs employees.id
    employees = read_csv(EMP_CSV)
    employee = next((e for e in employees if e.get('id') == user_id), None)
    if not employee:
        username = session.get('username')
        if username:
            employee = next((e for e in employees if (e.get('email') or '').strip().lower() == str(username).strip().lower()), None)
    if not employee:
        full_name = session.get('full_name')
        if full_name:
            employee = next((e for e in employees if (e.get('name') or '').strip().lower() == str(full_name).strip().lower()), None)
    # Build candidate ids set for matching tasks/memberships
    candidate_ids = set()
    if employee and employee.get('id'):
        candidate_ids.add(employee.get('id'))
    if user_id:
        candidate_ids.add(user_id)
    if not employee:
        # Return default structure if employee not found
        return {
            'profile': {
                'id': user_id,
                'name': session.get('full_name', 'Unknown'),
                'email': session.get('username', ''),
                'position': 'Unknown',
                'department': 'Unknown',
                'join_date': '',
                'phone': '',
                'skills': '',
                'location': '',
                'designation': session.get('role', '').title(),
                'role': session.get('role', 'employee')
            },
            'stats': {
                'totalTasks': 0,
                'completedTasks': 0,
                'inProgressTasks': 0,
                'overdueTasks': 0,
                'activeProjects': 0,
                'workload': 'light'
            },
            'tasks': [],
            'projects': []
        }
    
    # Get all tasks assigned to this employee (by any candidate id)
    all_tasks = read_csv(TASKS_CSV)
    employee_tasks = [task for task in all_tasks if task.get('assignee_id') in candidate_ids]
    
    # Calculate task statistics
    total_tasks = len(employee_tasks)
    completed_tasks = len([task for task in employee_tasks if task.get('status') == 'completed'])
    in_progress_tasks = len([task for task in employee_tasks if task.get('status') == 'in-progress'])
    
    # Calculate overdue tasks
    today = datetime.now().date()
    overdue_tasks = 0
    for task in employee_tasks:
        if task.get('status') not in ['completed', 'cancelled'] and task.get('due_date'):
            try:
                due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if due_date < today:
                    overdue_tasks += 1
            except ValueError:
                continue
    
    # Get projects owned by or assigned to this employee (via project_members.csv)
    all_projects = read_csv(PROJECTS_CSV)
    member_rows = read_csv(PROJECT_MEMBERS_CSV)
    member_project_ids = {m.get('project_id') for m in member_rows if m.get('employee_id') in candidate_ids}
    employee_projects = [p for p in all_projects if p.get('owner_id') in candidate_ids or p.get('id') in member_project_ids]
    active_projects = len([p for p in employee_projects if p.get('status') in ['active', 'planning']])
    
    # Determine workload level
    if total_tasks == 0:
        workload = 'light'
    elif total_tasks <= 3:
        workload = 'balanced'
    else:
        workload = 'heavy'
    
    # Get user role from users CSV
    user = find_by_id(USERS_CSV, user_id)
    user_role = user.get('role', 'employee') if user else 'employee'
    
    # Prepare profile data
    profile_data = {
        'id': employee.get('id', user_id),
        'name': employee.get('name', 'Unknown'),
        'fullName': employee.get('name', 'Unknown'),
        'email': employee.get('email', ''),
        'position': employee.get('position', 'Unknown'),
        'department': employee.get('department', 'Unknown'),
        'join_date': employee.get('join_date', ''),
        'phone': employee.get('phone', ''),
        'skills': employee.get('skills', ''),
        'location': employee.get('location', ''),
        'designation': employee.get('position', ''),
        'role': user_role
    }
    
    # Prepare stats data
    stats_data = {
        'totalTasks': total_tasks,
        'completedTasks': completed_tasks,
        'inProgressTasks': in_progress_tasks,
        'overdueTasks': overdue_tasks,
        'activeProjects': active_projects,
        'workload': workload
    }
    
    return {
        'profile': profile_data,
        'stats': stats_data,
        'tasks': employee_tasks,
        'projects': employee_projects
    }

# Manager-specific functions
def get_manager_data(user_id):
    """Get comprehensive data for manager dashboard"""
    
    # Get all employees (filter out admins, managers, HR)
    all_employees = read_csv(EMP_CSV)
    all_users = read_csv(USERS_CSV)
    
    # Filter employees to show only regular employees
    filtered_employees = []
    seen_emp_ids = set()
    for emp in all_employees:
        emp_id = emp.get('id')
        if emp_id in seen_emp_ids:
            continue
        user = next((u for u in all_users if u['id'] == emp_id), None)
        if user and user.get('role') not in ['admin', 'manager', 'hr']:
            emp_with_role = emp.copy()
            emp_with_role['role'] = user.get('role', 'employee')
            emp_with_role['fullName'] = emp.get('name', 'Unknown')
            filtered_employees.append(emp_with_role)
            seen_emp_ids.add(emp_id)
    
    # Get all tasks
    all_tasks = read_csv(TASKS_CSV)
    
    # Get all projects
    all_projects = read_csv(PROJECTS_CSV)
    
    # Calculate manager stats
    stats = {
        'totalEmployees': len(filtered_employees),
        'activeEmployees': len([e for e in filtered_employees if e.get('last_login')]),
        'totalProjects': len(all_projects),
        'activeProjects': len([p for p in all_projects if p.get('status') in ['active', 'planning']]),
        'totalTasks': len(all_tasks),
        'completedTasks': len([t for t in all_tasks if t.get('status') == 'completed']),
        'overdueTasks': calculate_overdue_tasks(all_tasks),
        'totalHours': calculate_total_hours(all_tasks),
        'productivity': calculate_team_productivity(filtered_employees, all_tasks),
        'unreadNotifications': 0  # You can implement notification system later
    }
    
    return {
        'employees': filtered_employees,
        'tasks': all_tasks,
        'projects': all_projects,
        'stats': stats,
        'notifications': []  # Placeholder for notifications
    }

@app.route('/api/manager/stats')
@login_required
def api_manager_stats():
    if session.get('role') != 'manager':
        return jsonify({})
    user_id = session.get('user_id')
    data = get_manager_data(user_id)
    return jsonify(data.get('stats', {}))

def calculate_overdue_tasks(tasks):
    """Calculate number of overdue tasks"""
    today = datetime.now().date()
    overdue = 0
    for task in tasks:
        if task.get('status') not in ['completed', 'cancelled'] and task.get('due_date'):
            try:
                due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if due_date < today:
                    overdue += 1
            except ValueError:
                continue
    return overdue

def calculate_total_hours(tasks):
    """Calculate total hours from tasks (placeholder implementation)"""
    return len(tasks) * 8  # Assuming 8 hours per task on average

def calculate_team_productivity(employees, tasks):
    """Calculate team productivity percentage"""
    if not employees:
        return 0
    
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
    
    if total_tasks == 0:
        return 0
    
    return int((completed_tasks / total_tasks) * 100)

def _parse_date_any(s: str):
    s = (s or '').strip()
    if not s:
        return None
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None

def build_recent_activity(employees, projects, tasks, limit=10):
    """Build recent activity feed items from CSV rows.
    Returns list of {message, time, icon} sorted by time desc.
    """
    items = []
    # Employees joined
    for e in employees or []:
        dt = _parse_date_any(e.get('join_date',''))
        if dt:
            items.append({
                'message': f"Employee '{e.get('name','Unknown')}' joined",
                'time': dt.strftime('%Y-%m-%d %H:%M') if dt.time() != datetime.min.time() else dt.strftime('%Y-%m-%d'),
                'icon': 'fas fa-user-plus'
            })
    # Projects started
    for p in projects or []:
        dt = _parse_date_any(p.get('start_date',''))
        if dt:
            items.append({
                'message': f"Project '{p.get('name','Unnamed')}' started",
                'time': dt.strftime('%Y-%m-%d'),
                'icon': 'fas fa-project-diagram'
            })
    # Tasks created
    for t in tasks or []:
        dt = _parse_date_any(t.get('created_at',''))
        if dt:
            items.append({
                'message': f"Task '{t.get('title','Untitled')}' created",
                'time': dt.strftime('%Y-%m-%d %H:%M') if dt.time() != datetime.min.time() else dt.strftime('%Y-%m-%d'),
                'icon': 'fas fa-tasks'
            })
    # Sort and limit
    def _dt_of(item):
        # Parse back for sort; fall back recent
        return _parse_date_any(item['time']) or datetime.now()
    items.sort(key=_dt_of, reverse=True)
    return items[:limit]

def load_employees():
    """Load employees from CSV"""
    return read_csv(EMP_CSV)

def load_tasks():
    """Load tasks from CSV"""
    return read_csv(TASKS_CSV)

def load_projects():
    """Load projects from CSV"""
    return read_csv(PROJECTS_CSV)

def ensure_projects_team_members():
    """Ensure projects.csv has a 'team_members' column and backfill from project_members.csv.
    team_members stored as comma-separated employee_ids.
    """
    try:
        rows = read_csv(PROJECTS_CSV)
        if not rows:
            return
        # if any row has team_members, assume column exists
        has_col = any('team_members' in r for r in rows)
        if has_col:
            return
        members = read_csv(PROJECT_MEMBERS_CSV)
        team_map = {}
        for m in members:
            pid = m.get('project_id')
            eid = m.get('employee_id')
            if not pid:
                continue
            team_map.setdefault(pid, []).append(eid)
        # Add team_members to each project row
        for r in rows:
            pid = r.get('id')
            r['team_members'] = ','.join([e for e in team_map.get(pid, []) if e])
        # Write back with added column
        fieldnames = set()
        for r in rows:
            fieldnames.update(r.keys())
        write_csv(PROJECTS_CSV, rows, list(fieldnames))
    except Exception:
        # Non-blocking; do not crash app if migration fails
        pass

def ensure_leave_type_column():
    """Ensure leave.csv has a 'type' column (vacation/sick/etc)."""
    try:
        rows = read_csv(LEAVE_CSV)
        if not rows:
            return
        missing = any('type' not in r for r in rows)
        if not missing:
            return
        for r in rows:
            if 'type' not in r:
                r['type'] = r.get('leave_type','') or ''
        fieldnames = set()
        for r in rows:
            fieldnames.update(r.keys())
        write_csv(LEAVE_CSV, rows, list(fieldnames))
    except Exception:
        pass

def calculate_completion_rate(tasks):
    """Calculate task completion rate"""
    if not tasks:
        return "0%"
    completed = len([t for t in tasks if t.get('status') == 'completed'])
    return f"{(completed / len(tasks)) * 100:.0f}%"

def is_task_overdue(task):
    """Check if a task is overdue"""
    if not task.get('due_date'):
        return False
    try:
        due_date = datetime.strptime(task['due_date'], '%Y-%m-%d')
        return due_date < datetime.now() and task.get('status') != 'completed'
    except:
        return False

@app.route('/static/<path:p>')
def static_proxy(p):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), p)

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        users = read_csv(USERS_CSV)
        
        print(f"Login attempt - Username: {username}")
        print(f"Total users in system: {len(users)}")
        
        for u in users:
            print(f"Checking user: {u['username']}")
            
            # Check if username matches and user is active
            if u['username'] == username and u.get('is_active', 'true').lower() == 'true':
                print(f"Username matched: {u['username']}")
                print(f"User active: {u.get('is_active', 'true')}")
                
                # Verify password
                try:
                    if check_password_hash(u['password_hash'], password):
                        print("Password verified successfully!")
                        
                        # Update last login in employee record
                        update_by_id(EMP_CSV, u['id'], {
                            'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }, ['id','name','email','position','department','join_date','phone','skills','location','last_login','password_last_changed'])
                        
                        # Set session data
                        session['user_id'] = u['id']
                        session['username'] = u['username']
                        session['role'] = u.get('role', 'employee')
                        session['full_name'] = u.get('full_name', '')
                        
                        print(f"Login successful - Role: {u.get('role', 'employee')}")
                        
                        # Redirect based on role
                        role = u.get('role', 'employee')
                        if role == 'admin':
                            return redirect(url_for('admin_dashboard'))
                        elif role == 'manager':
                            return redirect(url_for('manager_dashboard'))
                        elif role == 'hr':
                            return redirect(url_for('hr_dashboard'))
                        elif role == 'teamlead':
                            return redirect(url_for('teamlead_dashboard'))
                        else:
                            return redirect(url_for('employee_dashboard'))
                    else:
                        print("Password verification failed!")
                except Exception as e:
                    print(f"Password check error for user {username}: {e}")
                    continue
            else:
                if u['username'] == username:
                    print(f"User found but inactive: {u['username']}")
        
        print("Login failed - no matching user or incorrect password")
        return render_template('login.html', error='Invalid email or password')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('fullName')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        designation = request.form.get('designation')
        department = request.form.get('department')
        skills = request.form.get('skills', '')
        
        print(f"Form data received: {full_name}, {email}, {phone}, {role}, {designation}, {department}, {skills}")
        
        # Validate required fields
        if not all([full_name, email, phone, role, designation, department, skills]):
            return render_template('signup.html', error='All fields are required')
        
        # Check if user already exists
        users = read_csv(USERS_CSV)
        if any(u['username'] == email for u in users):
            return render_template('signup.html', error='User with this email already exists')
        
        # Generate user ID and password
        user_id = str(uuid.uuid4())
        password = generate_secure_password()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create user record
        user_row = {
            'id': user_id,
            'username': email,
            'password_hash': generate_password_hash(password),
            'full_name': full_name,
            'role': role,
            'created_at': current_time,
            'is_active': 'true'
        }
        
        # Create employee record
        employee_row = {
            'id': user_id,
            'name': full_name,
            'email': email,
            'position': designation,
            'department': department,
            'join_date': current_time,
            'phone': phone,
            'skills': skills,
            'location': '',
            'last_login': '',
            'password_last_changed': current_time
        }
        
        print(f"User row: {user_row}")
        print(f"Employee row: {employee_row}")
        
        # Save to CSV files
        try:
            append_csv(USERS_CSV, user_row, ['id','username','password_hash','full_name','role','created_at','is_active'])
            print("User saved successfully")
            
            append_csv(EMP_CSV, employee_row, ['id','name','email','position','department','join_date','phone','skills','location','last_login','password_last_changed'])
            print("Employee saved successfully")
            
            # Verify the data was written
            users_after = read_csv(USERS_CSV)
            employees_after = read_csv(EMP_CSV)
            print(f"Users after: {len(users_after)}")
            print(f"Employees after: {len(employees_after)}")
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return render_template('signup.html', error=f'Error saving data: {e}')
        
        # Redirect to credentials page instead of showing message
        return redirect(url_for('show_credentials', 
                              employee_name=full_name,
                              username=email,
                              password=password,
                              role=role))
    
    return render_template('signup.html')

@app.route('/credentials')
def show_credentials():
    employee_name = request.args.get('employee_name', '')
    username = request.args.get('username', '')
    password = request.args.get('password', '')
    role = request.args.get('role', 'employee')
    
    if not all([employee_name, username, password]):
        return redirect(url_for('signup'))
    
    return render_template('credentials.html',
                         employee_name=employee_name,
                         username=username,
                         password=password,
                         role=role,
                         get_role_title=get_role_title,
                         get_role_description=get_role_description,
                         get_role_access_description=get_role_access_description)

def get_role_color(role):
    """Get CSS class for role badge colors"""
    role_colors = {
        'admin': 'badge-admin',
        'manager': 'badge-manager', 
        'hr': 'badge-warning',
        'teamlead': 'badge-info',
        'employee': 'badge-employee'
    }
    return role_colors.get(role, 'badge-employee')

def generate_secure_password():
    import random
    import string
    
    characters = string.ascii_letters + string.digits + '!@#$%^&*'
    
    # Generate 8-10 character base password
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8 + random.randint(0, 2)))
    
    # Add 1-2 special characters
    special_count = 1 + random.randint(0, 1)
    for _ in range(special_count):
        insert_pos = random.randint(0, len(password))
        special_char = random.choice('!@#$%^&*')
        password = password[:insert_pos] + special_char + password[insert_pos:]
    
    return password

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Role-based dashboards
@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role', 'employee')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'manager':
        return redirect(url_for('manager_dashboard'))
    elif role == 'hr':
        return redirect(url_for('hr_dashboard'))
    elif role == 'teamlead':
        return redirect(url_for('teamlead_dashboard'))
    else:
        return redirect(url_for('employee_dashboard'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Load data from CSV files
    employees = load_employees()
    tasks = load_tasks()
    projects = load_projects()
    
    # Calculate stats
    stats = {
        'total_employees': len(employees),
        'active_projects': len([p for p in projects if p.get('status') == 'active']),
        'completed_tasks': len([t for t in tasks if t.get('status') == 'completed']),
        'total_tasks': len(tasks),
        'completion_rate': calculate_completion_rate(tasks),
        'overdue_tasks': len([t for t in tasks if is_task_overdue(t)]),
        'total_projects': len(projects),
        'active_projects_count': len([p for p in projects if p.get('status') == 'active']),
        'completed_projects': len([p for p in projects if p.get('status') == 'completed']),
        'on_hold_projects': len([p for p in projects if p.get('status') == 'on-hold'])
    }
    
    # Recent activity
    recent_activity = [
        {
            'message': f"New project '{projects[0]['name'] if projects else 'Website'} created",
            'time': '2 hours ago',
            'icon': 'fas fa-project-diagram'
        },
        {
            'message': f"Task '{tasks[0]['title'] if tasks else 'Homepage'} completed",
            'time': '4 hours ago', 
            'icon': 'fas fa-check-circle'
        },
        {
            'message': f"New employee {employees[0]['name'] if employees else 'John'} added",
            'time': '1 day ago',
            'icon': 'fas fa-user-plus'
        }
    ]
    
    return render_template('admin_dashboard.html', 
                         username=session.get('username'), 
                         role=session.get('role'),
                         stats=stats,
                         recent_activity=recent_activity,
                         employees=employees,
                         tasks=tasks,
                         projects=projects)


@app.route('/manager/settings')
@login_required
def manager_settings():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    profile = find_by_id(EMP_CSV, user_id)
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='settings',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'],
                         profile=profile)

@app.route('/admin/employees')
@admin_required
def admin_employees():
    employees = load_employees()
    tasks = load_tasks()
    projects = load_projects()
    stats = {
        'total_employees': len(employees),
        'active_projects': len([p for p in projects if p.get('status') == 'active']),
        'completed_tasks': len([t for t in tasks if t.get('status') == 'completed']),
        'total_tasks': len(tasks),
        'completion_rate': calculate_completion_rate(tasks),
        'overdue_tasks': len([t for t in tasks if is_task_overdue(t)]),
        'total_projects': len(projects),
        'active_projects_count': len([p for p in projects if p.get('status') == 'active']),
        'completed_projects': len([p for p in projects if p.get('status') == 'completed']),
        'on_hold_projects': len([p for p in projects if p.get('status') == 'on-hold'])
    }
    recent_activity = [
        {
            'message': f"New project '{projects[0]['name'] if projects else 'Website'} created",
            'time': '2 hours ago',
            'icon': 'fas fa-project-diagram'
        },
        {
            'message': f"Task '{tasks[0]['title'] if tasks else 'Homepage'} completed",
            'time': '4 hours ago',
            'icon': 'fas fa-check-circle'
        },
        {
            'message': f"New employee {employees[0]['name'] if employees else 'John'} added",
            'time': '1 day ago',
            'icon': 'fas fa-user-plus'
        }
    ]
    return render_template('admin_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         stats=stats,
                         recent_activity=recent_activity,
                         employees=employees,
                         tasks=tasks,
                         projects=projects)

@app.route('/admin/projects')
@admin_required
def admin_projects():
    employees = load_employees()
    tasks = load_tasks()
    projects = load_projects()
    stats = {
        'total_employees': len(employees),
        'active_projects': len([p for p in projects if p.get('status') == 'active']),
        'completed_tasks': len([t for t in tasks if t.get('status') == 'completed']),
        'total_tasks': len(tasks),
        'completion_rate': calculate_completion_rate(tasks),
        'overdue_tasks': len([t for t in tasks if is_task_overdue(t)]),
        'total_projects': len(projects),
        'active_projects_count': len([p for p in projects if p.get('status') == 'active']),
        'completed_projects': len([p for p in projects if p.get('status') == 'completed']),
        'on_hold_projects': len([p for p in projects if p.get('status') == 'on-hold'])
    }
    recent_activity = [
        {
            'message': f"New project '{projects[0]['name'] if projects else 'Website'} created",
            'time': '2 hours ago',
            'icon': 'fas fa-project-diagram'
        },
        {
            'message': f"Task '{tasks[0]['title'] if tasks else 'Homepage'} completed",
            'time': '4 hours ago',
            'icon': 'fas fa-check-circle'
        },
        {
            'message': f"New employee {employees[0]['name'] if employees else 'John'} added",
            'time': '1 day ago',
            'icon': 'fas fa-user-plus'
        }
    ]
    return render_template('admin_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         stats=stats,
                         recent_activity=recent_activity,
                         employees=employees,
                         tasks=tasks,
                         projects=projects)

@app.route('/admin/tasks')
@admin_required
def admin_tasks():
    employees = load_employees()
    tasks = load_tasks()
    projects = load_projects()
    stats = {
        'total_employees': len(employees),
        'active_projects': len([p for p in projects if p.get('status') == 'active']),
        'completed_tasks': len([t for t in tasks if t.get('status') == 'completed']),
        'total_tasks': len(tasks),
        'completion_rate': calculate_completion_rate(tasks),
        'overdue_tasks': len([t for t in tasks if is_task_overdue(t)]),
        'total_projects': len(projects),
        'active_projects_count': len([p for p in projects if p.get('status') == 'active']),
        'completed_projects': len([p for p in projects if p.get('status') == 'completed']),
        'on_hold_projects': len([p for p in projects if p.get('status') == 'on-hold'])
    }
    recent_activity = [
        {
            'message': f"New project '{projects[0]['name'] if projects else 'Website'} created",
            'time': '2 hours ago',
            'icon': 'fas fa-project-diagram'
        },
        {
            'message': f"Task '{tasks[0]['title'] if tasks else 'Homepage'} completed",
            'time': '4 hours ago',
            'icon': 'fas fa-check-circle'
        },
        {
            'message': f"New employee {employees[0]['name'] if employees else 'John'} added",
            'time': '1 day ago',
            'icon': 'fas fa-user-plus'
        }
    ]
    return render_template('admin_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         stats=stats,
                         recent_activity=recent_activity,
                         employees=employees,
                         tasks=tasks,
                         projects=projects)

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    employees = load_employees()
    tasks = load_tasks()
    projects = load_projects()
    stats = {
        'total_employees': len(employees),
        'active_projects': len([p for p in projects if p.get('status') == 'active']),
        'completed_tasks': len([t for t in tasks if t.get('status') == 'completed']),
        'total_tasks': len(tasks),
        'completion_rate': calculate_completion_rate(tasks),
        'overdue_tasks': len([t for t in tasks if is_task_overdue(t)]),
        'total_projects': len(projects),
        'active_projects_count': len([p for p in projects if p.get('status') == 'active']),
        'completed_projects': len([p for p in projects if p.get('status') == 'completed']),
        'on_hold_projects': len([p for p in projects if p.get('status') == 'on-hold'])
    }
    recent_activity = [
        {
            'message': f"New project '{projects[0]['name'] if projects else 'Website'} created",
            'time': '2 hours ago',
            'icon': 'fas fa-project-diagram'
        },
        {
            'message': f"Task '{tasks[0]['title'] if tasks else 'Homepage'} completed",
            'time': '4 hours ago',
            'icon': 'fas fa-check-circle'
        },
        {
            'message': f"New employee {employees[0]['name'] if employees else 'John'} added",
            'time': '1 day ago',
            'icon': 'fas fa-user-plus'
        }
    ]
    return render_template('admin_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         stats=stats,
                         recent_activity=recent_activity,
                         employees=employees,
                         tasks=tasks,
                         projects=projects)

@app.route('/admin/skill-gap-analysis')
@admin_required
def skill_gap_analysis():
    employees = load_employees()
    tasks = load_tasks()
    projects = load_projects()
    stats = {
        'total_employees': len(employees),
        'active_projects': len([p for p in projects if p.get('status') == 'active']),
        'completed_tasks': len([t for t in tasks if t.get('status') == 'completed']),
        'total_tasks': len(tasks),
        'completion_rate': calculate_completion_rate(tasks),
        'overdue_tasks': len([t for t in tasks if is_task_overdue(t)]),
        'total_projects': len(projects),
        'active_projects_count': len([p for p in projects if p.get('status') == 'active']),
        'completed_projects': len([p for p in projects if p.get('status') == 'completed']),
        'on_hold_projects': len([p for p in projects if p.get('status') == 'on-hold'])
    }
    recent_activity = [
        {
            'message': f"New project '{projects[0]['name'] if projects else 'Website'} created",
            'time': '2 hours ago',
            'icon': 'fas fa-project-diagram'
        },
        {
            'message': f"Task '{tasks[0]['title'] if tasks else 'Homepage'} completed",
            'time': '4 hours ago',
            'icon': 'fas fa-check-circle'
        },
        {
            'message': f"New employee {employees[0]['name'] if employees else 'John'} added",
            'time': '1 day ago',
            'icon': 'fas fa-user-plus'
        }
    ]
    return render_template('admin_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         stats=stats,
                         recent_activity=recent_activity,
                         employees=employees,
                         tasks=tasks,
                         projects=projects)

@app.route('/admin/profile')
@admin_required
def admin_profile():
    employees = load_employees()
    tasks = load_tasks()
    projects = load_projects()
    stats = {
        'total_employees': len(employees),
        'active_projects': len([p for p in projects if p.get('status') == 'active']),
        'completed_tasks': len([t for t in tasks if t.get('status') == 'completed']),
        'total_tasks': len(tasks),
        'completion_rate': calculate_completion_rate(tasks),
        'overdue_tasks': len([t for t in tasks if is_task_overdue(t)]),
        'total_projects': len(projects),
        'active_projects_count': len([p for p in projects if p.get('status') == 'active']),
        'completed_projects': len([p for p in projects if p.get('status') == 'completed']),
        'on_hold_projects': len([p for p in projects if p.get('status') == 'on-hold'])
    }
    recent_activity = [
        {
            'message': f"New project '{projects[0]['name'] if projects else 'Website'} created",
            'time': '2 hours ago',
            'icon': 'fas fa-project-diagram'
        },
        {
            'message': f"Task '{tasks[0]['title'] if tasks else 'Homepage'} completed",
            'time': '4 hours ago',
            'icon': 'fas fa-check-circle'
        },
        {
            'message': f"New employee {employees[0]['name'] if employees else 'John'} added",
            'time': '1 day ago',
            'icon': 'fas fa-user-plus'
        }
    ]
    return render_template('admin_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         stats=stats,
                         recent_activity=recent_activity,
                         employees=employees,
                         tasks=tasks,
                         projects=projects)

@app.route('/admin/settings')
@admin_required
def admin_settings():
    employees = load_employees()
    tasks = load_tasks()
    projects = load_projects()
    stats = {
        'total_employees': len(employees),
        'active_projects': len([p for p in projects if p.get('status') == 'active']),
        'completed_tasks': len([t for t in tasks if t.get('status') == 'completed']),
        'total_tasks': len(tasks),
        'completion_rate': calculate_completion_rate(tasks),
        'overdue_tasks': len([t for t in tasks if is_task_overdue(t)]),
        'total_projects': len(projects),
        'active_projects_count': len([p for p in projects if p.get('status') == 'active']),
        'completed_projects': len([p for p in projects if p.get('status') == 'completed']),
        'on_hold_projects': len([p for p in projects if p.get('status') == 'on-hold'])
    }
    recent_activity = [
        {
            'message': f"New project '{projects[0]['name'] if projects else 'Website'} created",
            'time': '2 hours ago',
            'icon': 'fas fa-project-diagram'
        },
        {
            'message': f"Task '{tasks[0]['title'] if tasks else 'Homepage'} completed",
            'time': '4 hours ago',
            'icon': 'fas fa-check-circle'
        },
        {
            'message': f"New employee {employees[0]['name'] if employees else 'John'} added",
            'time': '1 day ago',
            'icon': 'fas fa-user-plus'
        }
    ]
    return render_template('admin_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         stats=stats,
                         recent_activity=recent_activity,
                         employees=employees,
                         tasks=tasks,
                         projects=projects)

@app.route('/hr/dashboard')
@login_required
def hr_dashboard():
    if session.get('role') != 'hr':
        return redirect(url_for('dashboard'))
    return render_template('hr_dashboard.html', username=session.get('username'), role=session.get('role'))

@app.route('/teamlead/dashboard')
@login_required
def teamlead_dashboard():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    # For initial implementation, reuse manager data aggregation
    manager_data = get_manager_data(user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='overview',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/teamlead/profile')
@login_required
def teamlead_profile():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    profile = find_by_id(EMP_CSV, user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='profile',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'],
                         profile=profile)

@app.route('/teamlead/settings')
@login_required
def teamlead_settings():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    profile = find_by_id(EMP_CSV, user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='settings',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'],
                         profile=profile)

# Individual employee view routes
@app.route('/employee/overview')
@login_required
def employee_overview():
    if session.get('role') not in ['employee', 'admin', 'manager', 'hr', 'teamlead']:
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    employee_data = get_employee_data(user_id)
    
    # Ensure skills is a list for template compatibility
    if employee_data['profile'].get('skills'):
        if isinstance(employee_data['profile']['skills'], str):
            employee_data['profile']['skills'] = [skill.strip() for skill in employee_data['profile']['skills'].split(',') if skill.strip()]
    else:
        employee_data['profile']['skills'] = []
    
    return render_template('employee_dashboard.html',
                         profile=employee_data['profile'],
                         stats=employee_data['stats'],
                         tasks=employee_data['tasks'],
                         projects=employee_data['projects'],
                         current_view='overview')

@app.route('/employee/profile')
@login_required
def employee_profile():
    if session.get('role') not in ['employee', 'admin', 'manager', 'hr', 'teamlead']:
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    employee_data = get_employee_data(user_id)
    
    # Ensure skills is a list for template compatibility
    if employee_data['profile'].get('skills'):
        if isinstance(employee_data['profile']['skills'], str):
            employee_data['profile']['skills'] = [skill.strip() for skill in employee_data['profile']['skills'].split(',') if skill.strip()]
    else:
        employee_data['profile']['skills'] = []
    
    return render_template('employee_dashboard.html',
                         profile=employee_data['profile'],
                         stats=employee_data['stats'],
                         tasks=employee_data['tasks'],
                         projects=employee_data['projects'],
                         current_view='profile')

@app.route('/employee/settings')
@login_required
def employee_settings():
    if session.get('role') not in ['employee', 'admin', 'manager', 'hr', 'teamlead']:
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    employee_data = get_employee_data(user_id)
    
    # Ensure skills is a list for template compatibility
    if employee_data['profile'].get('skills'):
        if isinstance(employee_data['profile']['skills'], str):
            employee_data['profile']['skills'] = [skill.strip() for skill in employee_data['profile']['skills'].split(',') if skill.strip()]
    else:
        employee_data['profile']['skills'] = []
    
    return render_template('employee_dashboard.html',
                         profile=employee_data['profile'],
                         stats=employee_data['stats'],
                         tasks=employee_data['tasks'],
                         projects=employee_data['projects'],
                         current_view='settings')

@app.route('/employee/tasks')
@login_required
def employee_tasks():
    if session.get('role') not in ['employee', 'admin', 'manager', 'hr', 'teamlead']:
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    employee_data = get_employee_data(user_id)
    
    return render_template('employee_dashboard.html',
                         profile=employee_data['profile'],
                         stats=employee_data['stats'],
                         tasks=employee_data['tasks'],
                         projects=employee_data['projects'],
                         current_view='tasks')

@app.route('/employee/projects')
@login_required
def employee_projects():
    if session.get('role') not in ['employee', 'admin', 'manager', 'hr', 'teamlead']:
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    employee_data = get_employee_data(user_id)
    
    return render_template('employee_dashboard.html',
                         profile=employee_data['profile'],
                         stats=employee_data['stats'],
                         tasks=employee_data['tasks'],
                         projects=employee_data['projects'],
                         current_view='projects')

@app.route('/employee/workload')
@login_required
def employee_workload():
    if session.get('role') not in ['employee', 'admin', 'manager', 'hr', 'teamlead']:
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    employee_data = get_employee_data(user_id)
    
    return render_template('employee_dashboard.html',
                         profile=employee_data['profile'],
                         stats=employee_data['stats'],
                         tasks=employee_data['tasks'],
                         projects=employee_data['projects'],
                         current_view='workload')

@app.route('/employee/leave')
@login_required
def employee_leave():
    if session.get('role') not in ['employee', 'admin', 'manager', 'hr', 'teamlead']:
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    employee_data = get_employee_data(user_id)
    
    return render_template('employee_dashboard.html',
                         profile=employee_data['profile'],
                         stats=employee_data['stats'],
                         tasks=employee_data['tasks'],
                         projects=employee_data['projects'],
                         current_view='leave')

@app.route('/employee/reports')
@login_required
def employee_reports():
    if session.get('role') not in ['employee', 'admin', 'manager', 'hr', 'teamlead']:
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    employee_data = get_employee_data(user_id)
    
    return render_template('employee_dashboard.html',
                         profile=employee_data['profile'],
                         stats=employee_data['stats'],
                         tasks=employee_data['tasks'],
                         projects=employee_data['projects'],
                         current_view='reports')

@app.route('/employee/notifications')
@login_required
def employee_notifications():
    if session.get('role') not in ['employee', 'admin', 'manager', 'hr', 'teamlead']:
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    employee_data = get_employee_data(user_id)
    
    return render_template('employee_dashboard.html',
                         profile=employee_data['profile'],
                         stats=employee_data['stats'],
                         tasks=employee_data['tasks'],
                         projects=employee_data['projects'],
                         current_view='notifications')

@app.route('/employee/dashboard')
@login_required
def employee_dashboard():
    if session.get('role') not in ['employee', 'admin', 'manager', 'hr', 'teamlead']:
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    employee_data = get_employee_data(user_id)
    
    # Ensure skills is a list for template compatibility
    if employee_data['profile'].get('skills'):
        if isinstance(employee_data['profile']['skills'], str):
            employee_data['profile']['skills'] = [skill.strip() for skill in employee_data['profile']['skills'].split(',') if skill.strip()]
    else:
        employee_data['profile']['skills'] = []
    
    return render_template('employee_dashboard.html', 
                         profile=employee_data['profile'],
                         stats=employee_data['stats'],
                         tasks=employee_data['tasks'],
                         projects=employee_data['projects'],
                         current_view='overview')

# Manager Dashboard Routes
@app.route('/manager/dashboard')
@login_required
def manager_dashboard():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    
    return render_template('manager_dashboard.html', 
                         username=session.get('username'), 
                         role=session.get('role'),
                         current_view='overview',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

# Manager: additional view routes
@app.route('/manager/leave')
@login_required
def manager_leave():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='leave',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/manager/workload-balancer')
@login_required
def manager_workload_balancer():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='workload-balancer',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/manager/skill-recommendations')
@login_required
def manager_skill_recommendations():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='skill-recommendations',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/manager/team-notes')
@login_required
def manager_team_notes():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='team-notes',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/manager/profile')
@login_required
def manager_profile():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='profile',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

# Manager APIs expected by dialogs and dashboard
@app.route('/api/manager/employees')
@login_required
def api_manager_employees():
    if session.get('role') != 'manager':
        return jsonify([])
    # Return employees suitable for selection in dialogs
    users = read_csv(USERS_CSV)
    role_map = {u['id']: u.get('role', 'employee') for u in users}
    emps = read_csv(EMP_CSV)
    def to_public(emp):
        return {
            'id': emp.get('id'),
            'name': emp.get('name'),
            'fullName': emp.get('name'),
            'email': emp.get('email'),
            'position': emp.get('position'),
            'department': emp.get('department'),
            'role': role_map.get(emp.get('id'), 'employee')
        }
    # Exclude admin/manager/hr from lists
    visible = [e for e in emps if role_map.get(e.get('id'), 'employee') not in ['admin','manager','hr']]
    return jsonify([to_public(e) for e in visible])

@app.route('/api/manager/projects')
@login_required
def api_manager_projects():
    # Ensure CSV has team_members column before we read
    ensure_projects_team_members()
    if session.get('role') != 'manager':
        return jsonify([])
    projects = read_csv(PROJECTS_CSV)
    members = read_csv(PROJECT_MEMBERS_CSV)
    # Build members map
    team_map = {}
    for m in members:
        pid = m.get('project_id')
        if not pid:
            continue
        team_map.setdefault(pid, []).append(m.get('employee_id'))
    # Normalize keys for frontend expectations
    normalized = []
    for p in projects:
        pid = p.get('id')
        team_list = team_map.get(pid, [])
        normalized.append({
            'id': p.get('id'),
            'name': p.get('name'),
            'description': p.get('description'),
            'ownerId': p.get('owner_id'),
            'status': p.get('status', 'planning'),
            'deadline': p.get('end_date'),
            'teamMembers': team_list,
            'team_members_count': len(team_list)
        })
    return jsonify(normalized)

# Team Lead APIs (parallel to manager, with role check = teamlead)
@app.route('/api/teamlead/employees')
@login_required
def api_teamlead_employees():
    if session.get('role') != 'teamlead':
        return jsonify([])
    users = read_csv(USERS_CSV)
    role_map = {u['id']: u.get('role', 'employee') for u in users}
    emps = read_csv(EMP_CSV)
    def to_public(emp):
        return {
            'id': emp.get('id'),
            'name': emp.get('name'),
            'fullName': emp.get('name'),
            'email': emp.get('email'),
            'position': emp.get('position'),
            'department': emp.get('department'),
            'role': role_map.get(emp.get('id'), 'employee')
        }
    visible = [e for e in emps if role_map.get(e.get('id'), 'employee') not in ['admin','manager','hr','teamlead']]
    return jsonify([to_public(e) for e in visible])

@app.route('/api/teamlead/projects')
@login_required
def api_teamlead_projects():
    if session.get('role') != 'teamlead':
        return jsonify([])
    projects = read_csv(PROJECTS_CSV)
    normalized = []
    for p in projects:
        normalized.append({
            'id': p.get('id'),
            'name': p.get('name'),
            'description': p.get('description'),
            'ownerId': p.get('owner_id'),
            'status': p.get('status', 'planning'),
            'deadline': p.get('end_date')
        })
    return jsonify(normalized)

@app.route('/api/teamlead/tasks')
@login_required
def api_teamlead_tasks():
    if session.get('role') != 'teamlead':
        return jsonify([])
    tasks = read_csv(TASKS_CSV)
    return jsonify(tasks)

@app.route('/api/teamlead/tasks/assign', methods=['POST'])
@login_required
def api_teamlead_assign_task():
    if session.get('role') != 'teamlead':
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(force=True) or {}
    task_id = str(uuid.uuid4())
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Resolve assignee name from employees.csv (fallback to provided)
    assignee_name = data.get('assignee_name','')
    try:
        emps = read_csv(EMP_CSV)
        for e in emps:
            if e.get('id') == data.get('assignee_id'):
                assignee_name = e.get('name') or assignee_name
                break
    except Exception:
        pass

    row = {
        'id': task_id,
        'title': data.get('title','Untitled Task'),
        'description': data.get('description',''),
        'project_id': data.get('project_id',''),
        'assignee_id': data.get('assignee_id',''),
        'assignee_name': assignee_name or '',
        'status': data.get('status','pending'),
        'priority': data.get('priority','medium'),
        'created_at': created_at,
        'due_date': data.get('due_date','')
    }
    append_csv(TASKS_CSV, row, ['id','title','description','project_id','assignee_id','assignee_name','status','priority','created_at','due_date'])
    return jsonify({'id': task_id, 'ok': True})

@app.route('/api/manager/tasks/<task_id>', methods=['PUT'])
@login_required
def api_manager_update_task(task_id):
    if session.get('role') != 'manager':
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(force=True) or {}
    # Map camelCase to underscore keys
    updates = {}
    if 'title' in data: updates['title'] = data['title']
    if 'description' in data: updates['description'] = data['description']
    if 'priority' in data: updates['priority'] = data['priority']
    if 'status' in data: updates['status'] = data['status']
    # due date can arrive as ISO or YYYY-MM-DD; store as YYYY-MM-DD
    if 'dueDate' in data:
        try:
            dt = datetime.fromisoformat(str(data['dueDate']).replace('Z',''))
            updates['due_date'] = dt.strftime('%Y-%m-%d')
        except Exception:
            updates['due_date'] = str(data['dueDate'])[:10]
    # hours
    if 'estimatedHours' in data: updates['estimated_hours'] = str(int(data['estimatedHours'] or 0))
    if 'actualHours' in data: updates['actual_hours'] = str(int(data['actualHours'] or 0))

    # Read existing tasks, update matching row, and write back preserving/adding fields
    rows = read_csv(TASKS_CSV)
    updated = False
    fieldnames = set()
    for r in rows:
        fieldnames.update(r.keys())
    fieldnames.update(['estimated_hours','actual_hours','due_date'])
    for r in rows:
        if str(r.get('id')) == str(task_id):
            rows = read_csv(TASKS_CSV)
    updated = False
    fieldnames = set()
    for r in rows:
        if r.get('id') == task_id:
            r.update(updates)
            updated = True
        fieldnames.update(r.keys())
    if not updated:
        return jsonify({'error': 'task_not_found'}), 404
    # Ensure assignee_name remains a column in output
    if 'assignee_name' not in fieldnames:
        fieldnames.add('assignee_name')
    write_csv(TASKS_CSV, rows, list(fieldnames))
    return jsonify({'ok': True})

# Team Notes APIs (CSV-backed, shared across roles)
@app.route('/api/notes', methods=['GET'])
@login_required
def api_notes_list():
    ensure_notes_csv()
    rows = read_csv(NOTES_CSV)
    return jsonify(rows)

@app.route('/api/notes', methods=['POST'])
@login_required
def api_notes_create():
    ensure_notes_csv()
    data = request.get_json(force=True) or {}
    note_id = str(uuid.uuid4())
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = {
        'id': note_id,
        'title': (data.get('title') or '').strip(),
        'content': data.get('content') or '',
        'author': session.get('full_name') or session.get('username') or 'User',
        'author_id': session.get('user_id',''),
        'priority': data.get('priority','medium'),
        'is_pinned': 'true' if data.get('is_pinned') in [True,'true','1'] else 'false',
        'created_at': now,
        'updated_at': now,
        'visible_to': 'all'
    }
    append_csv(NOTES_CSV, row, ['id','title','content','author','author_id','priority','is_pinned','created_at','updated_at','visible_to'])
    return jsonify({'ok': True, 'id': note_id})

@app.route('/api/notes/<note_id>', methods=['PUT'])
@login_required
def api_notes_update(note_id):
    ensure_notes_csv()
    data = request.get_json(force=True) or {}
    rows = read_csv(NOTES_CSV)
    updated = False
    for r in rows:
        if str(r.get('id')) == str(note_id):
            if 'title' in data: r['title'] = data['title']
            if 'content' in data: r['content'] = data['content']
            if 'priority' in data: r['priority'] = data['priority']
            if 'is_pinned' in data: r['is_pinned'] = 'true' if data.get('is_pinned') in [True,'true','1'] else 'false'
            r['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updated = True
            break
    if not updated:
        return jsonify({'error': 'not_found'}), 404
    write_csv(NOTES_CSV, rows, ['id','title','content','author','author_id','priority','is_pinned','created_at','updated_at','visible_to'])
    return jsonify({'ok': True})

@app.route('/api/notes/<note_id>', methods=['DELETE'])
@login_required
def api_notes_delete(note_id):
    ensure_notes_csv()
    rows = read_csv(NOTES_CSV)
    new_rows = [r for r in rows if str(r.get('id')) != str(note_id)]
    write_csv(NOTES_CSV, new_rows, ['id','title','content','author','author_id','priority','is_pinned','created_at','updated_at','visible_to'])
    return jsonify({'ok': True})

@app.route('/api/teamlead/projects/create', methods=['POST'])
@login_required
def api_teamlead_create_project():
    if session.get('role') != 'teamlead':
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(force=True) or {}
    project_id = str(uuid.uuid4())
    now = datetime.now().strftime('%Y-%m-%d')
    row = {
        'id': project_id,
        'name': data.get('name','').strip(),
        'description': data.get('description',''),
        'owner_id': session.get('user_id',''),
        'start_date': now,
        'end_date': data.get('deadline','') or '',
        'status': data.get('status','planning')
    }
    append_csv(PROJECTS_CSV, row, ['id','name','description','owner_id','start_date','end_date','status'])
    members = data.get('teamMembers', []) or []
    for emp_id in members:
        append_csv(PROJECT_MEMBERS_CSV, {
            'id': str(uuid.uuid4()),
            'project_id': project_id,
            'employee_id': emp_id
        }, ['id','project_id','employee_id'])
    return jsonify({'id': project_id, 'ok': True})

@app.route('/api/manager/projects/<project_id>', methods=['PUT'])
@login_required
def api_manager_update_project(project_id):
    if session.get('role') != 'manager':
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(force=True) or {}
    updates = {}
    # basic fields
    for k in ['name','description','status']:
        if k in data:
            updates[k] = data[k]
    # deadline -> end_date
    if 'deadline' in data:
        try:
            dt = datetime.fromisoformat(str(data['deadline']).replace('Z',''))
            updates['end_date'] = dt.strftime('%Y-%m-%d')
        except Exception:
            updates['end_date'] = str(data['deadline'])[:10]
    rows = read_csv(PROJECTS_CSV)
    updated = False
    fieldnames = set()
    for r in rows:
        fieldnames.update(r.keys())
    fieldnames.update(['end_date'])
    for r in rows:
        if str(r.get('id')) == str(project_id):
            for k,v in updates.items():
                r[k] = v
                fieldnames.add(k)
            updated = True
            break
    if not updated:
        return jsonify({'error': 'project_not_found'}), 404
    write_csv(PROJECTS_CSV, rows, list(fieldnames))
    return jsonify({'ok': True})

@app.route('/api/employee/tasks/update-status', methods=['POST'])
@login_required
def api_employee_update_task_status():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401
    data = request.get_json(force=True) or {}
    task_id = data.get('task_id') or data.get('id')
    new_status = data.get('status')
    if not task_id or not new_status:
        return jsonify({'error': 'missing parameters'}), 400
    # Ensure the task belongs to the employee
    tasks = read_csv(TASKS_CSV)
    task = next((t for t in tasks if t.get('id') == task_id and t.get('assignee_id') == user_id), None)
    if not task:
        return jsonify({'error': 'not found or forbidden'}), 404
    # Update status
    updated = update_by_id(TASKS_CSV, task_id, {'status': new_status}, ['id','title','description','project_id','assignee_id','assignee_name','status','priority','created_at','due_date'])
    if not updated:
        return jsonify({'error': 'update failed'}), 500
    return jsonify({'ok': True})

# Leave APIs
@app.route('/api/employee/leave')
@login_required
def api_employee_leave_list():
    ensure_leave_type_column()
    user_id = session.get('user_id')
    username = session.get('username')
    full_name = session.get('full_name')
    if not user_id and not username:
        return jsonify([])

    # Resolve employee candidates
    employee_rows = read_csv(EMP_CSV)
    candidate_ids = set()
    if user_id:
        for r in employee_rows:
            if r.get('id') == user_id:
                candidate_ids.add(r.get('id'))
                break
    if username:
        for r in employee_rows:
            if (r.get('email') or '').strip().lower() == str(username).strip().lower():
                candidate_ids.add(r.get('id'))
    if full_name:
        for r in employee_rows:
            if (r.get('name') or '').strip().lower() == str(full_name).strip().lower():
                candidate_ids.add(r.get('id'))

    rows = read_csv(LEAVE_CSV)
    mine = [l for l in rows if l.get('employee_id') in candidate_ids or (user_id and l.get('employee_id') == user_id)]
    # Normalize/augment
    for l in mine:
        # compute days if possible
        try:
            sd = datetime.strptime((l.get('start_date') or '')[:10], '%Y-%m-%d').date()
            ed = datetime.strptime((l.get('end_date') or '')[:10], '%Y-%m-%d').date()
            days = (ed - sd).days + 1
            l['days'] = max(days, 0)
        except Exception:
            l['days'] = 0
        l['type'] = l.get('type','')
    # Sort by applied_at desc
    mine.sort(key=lambda r: r.get('applied_at',''), reverse=True)
    return jsonify(mine)

@app.route('/api/employee/leave-request', methods=['POST'])
@login_required
def api_employee_leave_request():
    ensure_leave_type_column()
    data = request.get_json(force=True) or {}
    # Resolve employee id
    user_id = session.get('user_id')
    username = session.get('username')
    full_name = session.get('full_name')
    employee_rows = read_csv(EMP_CSV)
    employee_id = None
    # direct id
    for r in employee_rows:
        if user_id and r.get('id') == user_id:
            employee_id = r.get('id')
            break
    if not employee_id and username:
        for r in employee_rows:
            if (r.get('email') or '').strip().lower() == str(username).strip().lower():
                employee_id = r.get('id'); break
    if not employee_id and full_name:
        for r in employee_rows:
            if (r.get('name') or '').strip().lower() == str(full_name).strip().lower():
                employee_id = r.get('id'); break
    if not employee_id:
        return jsonify({'error':'employee_not_found'}), 400

    # Parse/validate dates (expecting ISO or yyyy-mm-dd). The UI may send dd-mm-yyyy; handle that
    sd_raw = (data.get('startDate') or data.get('start_date') or '').strip()
    ed_raw = (data.get('endDate') or data.get('end_date') or '').strip()
    def parse_date(s):
        for fmt in ('%Y-%m-%d','%d-%m-%Y'):
            try:
                return datetime.strptime(s, fmt).date()
            except Exception:
                pass
        return None
    sd = parse_date(sd_raw)
    ed = parse_date(ed_raw)
    if not sd or not ed or ed < sd:
        return jsonify({'error':'invalid_dates'}), 400

    row = {
        'id': str(uuid.uuid4()),
        'employee_id': employee_id,
        'start_date': sd.strftime('%Y-%m-%d'),
        'end_date': ed.strftime('%Y-%m-%d'),
        'reason': data.get('reason',''),
        'type': (data.get('type') or data.get('leaveType') or data.get('leave_type') or '').lower(),
        'status': 'pending',
        'applied_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    append_csv(LEAVE_CSV, row, ['id','employee_id','start_date','end_date','reason','type','status','applied_at'])
    return jsonify({'ok': True, 'id': row['id']})

@app.route('/api/employee/leave/apply', methods=['POST'])
@login_required
def api_employee_leave_apply():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401
    data = request.get_json(force=True) or {}
    leave_id = str(uuid.uuid4())
    row = {
        'id': leave_id,
        'employee_id': user_id,
        'start_date': data.get('start_date',''),
        'end_date': data.get('end_date',''),
        'reason': data.get('reason',''),
        'status': 'pending',
        'applied_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    append_csv(LEAVE_CSV, row, ['id','employee_id','start_date','end_date','reason','status','applied_at'])
    return jsonify({'ok': True, 'id': leave_id})

@app.route('/api/manager/leave')
@login_required
def api_manager_leave_list():
    if session.get('role') != 'manager':
        return jsonify([])
    status = request.args.get('status')
    rows = read_csv(LEAVE_CSV)
    if status:
        rows = [r for r in rows if (r.get('status') or '').lower() == status.lower()]
    return jsonify(rows)

@app.route('/api/manager/leave/update', methods=['POST'])
@login_required
def api_manager_leave_update():
    if session.get('role') != 'manager':
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(force=True) or {}
    leave_id = data.get('id')
    new_status = data.get('status')
    if not leave_id or new_status not in ['approved','rejected','pending']:
        return jsonify({'error': 'invalid'}), 400
    updated = update_by_id(LEAVE_CSV, leave_id, {'status': new_status}, ['id','employee_id','start_date','end_date','reason','status','applied_at'])
    if not updated:
        return jsonify({'error': 'not found'}), 404
    return jsonify({'ok': True})

# Profile APIs
@app.route('/api/employee/profile/update', methods=['POST'])
@login_required
def api_employee_profile_update():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401
    data = request.get_json(force=True) or {}
    fields = {}
    for k in ['name','email','phone','location','department','position','skills']:
        if k in data:
            v = data[k]
            if k == 'skills' and isinstance(v, str):
                v = ','.join([s.strip() for s in v.split(',') if s.strip()])
            fields[k] = v
    if not fields:
        return jsonify({'error': 'no changes'}), 400
    # Resolve employee row by id/email/name
    emps = read_csv(EMP_CSV)
    target_emp_id = None
    # 1) direct id
    for r in emps:
        if r.get('id') == user_id:
            target_emp_id = r.get('id'); break
    # 2) email matches username
    if not target_emp_id:
        username = session.get('username')
        if username:
            for r in emps:
                if (r.get('email') or '').strip().lower() == str(username).strip().lower():
                    target_emp_id = r.get('id'); break
    # 3) name matches full_name
    if not target_emp_id:
        full_name = session.get('full_name')
        if full_name:
            for r in emps:
                if (r.get('name') or '').strip().lower() == str(full_name).strip().lower():
                    target_emp_id = r.get('id'); break
    if not target_emp_id:
        return jsonify({'error': 'employee_not_found'}), 404
    ok = update_by_id(EMP_CSV, target_emp_id, fields, ["id","name","email","position","department","join_date","phone","skills","location","last_login","password_last_changed"])
    return jsonify({'ok': bool(ok)})

@app.route('/api/employee/password/update', methods=['POST'])
@login_required
def api_employee_password_update():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401
    # For demo, we just update password_last_changed timestamp on employees.csv
    ok = update_by_id(EMP_CSV, user_id, {'password_last_changed': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, ["id","name","email","position","department","join_date","phone","skills","location","last_login","password_last_changed"])
    return jsonify({'ok': bool(ok)})

# Alias to match frontend endpoint name
@app.route('/api/employee/password/change', methods=['POST'])
@login_required
def api_employee_password_change():
    return api_employee_password_update()

@app.route('/api/manager/tasks')
@login_required
def api_manager_tasks():
    if session.get('role') != 'manager':
        return jsonify([])
    tasks = read_csv(TASKS_CSV)
    return jsonify(tasks)

@app.route('/api/manager/tasks/assign', methods=['POST'])
@login_required
def api_manager_assign_task():
    if session.get('role') != 'manager':
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(force=True) or {}
    task_id = str(uuid.uuid4())
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = {
        'id': task_id,
        'title': data.get('title','').strip(),
        'description': data.get('description',''),
        'project_id': data.get('project','') or '',
        'assignee_id': data.get('assignedTo','') or '',
        'status': 'pending',
        'priority': data.get('priority','medium'),
        'created_at': created_at,
        'due_date': data.get('due_date','')
    }
    append_csv(TASKS_CSV, row, ['id','title','description','project_id','assignee_id','status','priority','created_at','due_date'])
    return jsonify({'id': task_id, 'ok': True})

@app.route('/api/manager/projects/create', methods=['POST'])
@login_required
def api_manager_create_project():
    if session.get('role') != 'manager':
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(force=True) or {}
    project_id = str(uuid.uuid4())
    now = datetime.now().strftime('%Y-%m-%d')
    row = {
        'id': project_id,
        'name': data.get('name','').strip(),
        'description': data.get('description',''),
        'owner_id': session.get('user_id',''),
        'start_date': now,
        'end_date': data.get('deadline','') or '',
        'status': data.get('status','planning')
    }
    append_csv(PROJECTS_CSV, row, ['id','name','description','owner_id','start_date','end_date','status'])
    # Save project members
    members = data.get('teamMembers', []) or []
    for emp_id in members:
        append_csv(PROJECT_MEMBERS_CSV, {
            'id': str(uuid.uuid4()),
            'project_id': project_id,
            'employee_id': emp_id
        }, ['id','project_id','employee_id'])
    return jsonify({'id': project_id, 'ok': True})

# Employee APIs (for logged-in employee dashboard)
@app.route('/api/employee/tasks')
@login_required
def api_employee_tasks():
    user_id = session.get('user_id')
    username = session.get('username')  # often email/username
    full_name = session.get('full_name')
    if not user_id and not username:
        return jsonify([])
    
    # Resolve the employee.id that corresponds to the current logged-in user
    employee_rows = read_csv(EMP_CSV)
    candidate_ids = set()
    # 1) Direct match on id
    if user_id:
        for r in employee_rows:
            if r.get('id') == user_id:
                candidate_ids.add(r.get('id'))
                break
    # 2) Match on email == username
    if username:
        for r in employee_rows:
            if (r.get('email') or '').strip().lower() == str(username).strip().lower():
                candidate_ids.add(r.get('id'))
    # 3) Match on name == full_name (fallback)
    if full_name:
        for r in employee_rows:
            if (r.get('name') or '').strip().lower() == str(full_name).strip().lower():
                candidate_ids.add(r.get('id'))

    tasks = read_csv(TASKS_CSV)
    # filter by any of the resolved employee ids; also include direct user_id if tasks were saved with users.id by mistake
    ids_to_match = set(candidate_ids)
    if user_id:
        ids_to_match.add(user_id)
    mine = [t for t in tasks if t.get('assignee_id') in ids_to_match]
    return jsonify(mine)

@app.route('/api/employee/projects')
@login_required
def api_employee_projects():
    # Ensure CSV has team_members column before we read
    ensure_projects_team_members()
    user_id = session.get('user_id')
    username = session.get('username')
    full_name = session.get('full_name')
    if not user_id and not username:
        return jsonify([])

    # Resolve candidate employee IDs for this session (same logic as api_employee_tasks)
    employee_rows = read_csv(EMP_CSV)
    candidate_ids = set()
    if user_id:
        for r in employee_rows:
            if r.get('id') == user_id:
                candidate_ids.add(r.get('id'))
                break
    if username:
        for r in employee_rows:
            if (r.get('email') or '').strip().lower() == str(username).strip().lower():
                candidate_ids.add(r.get('id'))
    if full_name:
        for r in employee_rows:
            if (r.get('name') or '').strip().lower() == str(full_name).strip().lower():
                candidate_ids.add(r.get('id'))

    projects = read_csv(PROJECTS_CSV)
    members = read_csv(PROJECT_MEMBERS_CSV)
    # Any membership row where employee_id equals any candidate id
    member_project_ids = {m['project_id'] for m in members if m.get('employee_id') in candidate_ids or (user_id and m.get('employee_id') == user_id)}
    # Visible projects: owned by this user_id OR membership contains any candidate id
    mine = [p for p in projects if (user_id and p.get('owner_id') == user_id) or p.get('id') in member_project_ids]
    # normalize
    normalized = [{
        'id': p.get('id'),
        'name': p.get('name'),
        'description': p.get('description'),
        'status': p.get('status', 'planning'),
        'startDate': p.get('start_date'),
        'endDate': p.get('end_date')
    } for p in mine]
    return jsonify(normalized)

# Manager View Routes
@app.route('/manager/overview')
@login_required
def manager_overview():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='overview',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/manager/employees')
@login_required
def manager_employees():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    # Apply optional filter
    flt = (request.args.get('filter') or '').lower()
    employees = manager_data['employees']
    if flt == 'active':
        employees = [e for e in employees if (e.get('last_login') or '').strip()]
    elif flt == 'on-leave':
        leaves = read_csv(LEAVE_CSV)
        today = datetime.now().date()
        def is_on_leave(emp_id):
            for r in leaves:
                if r.get('employee_id') == emp_id and (r.get('status') or '').lower() == 'approved':
                    try:
                        sd = datetime.strptime(r.get('start_date',''), '%Y-%m-%d').date()
                        ed = datetime.strptime(r.get('end_date',''), '%Y-%m-%d').date()
                    except Exception:
                        continue
                    if sd <= today <= ed:
                        return True
            return False
        employees = [e for e in employees if is_on_leave(e.get('id'))]

    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='employees',
                         stats=manager_data['stats'],
                         employees=employees,
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/manager/projects')
@login_required
def manager_projects():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    # Optional filter by status
    flt = (request.args.get('filter') or '').lower()
    projects = manager_data['projects']
    # Attach team member counts from PROJECT_MEMBERS_CSV
    try:
        members = read_csv(PROJECT_MEMBERS_CSV)
        count_map = {}
        for m in members:
            pid = m.get('project_id')
            if pid:
                count_map[pid] = count_map.get(pid, 0) + 1
        for p in projects:
            p['team_members_count'] = count_map.get(p.get('id'), 0)
    except Exception:
        pass
    if flt == 'active':
        projects = [p for p in projects if (p.get('status') or '').lower() in ['active','planning']]
    elif flt == 'completed':
        projects = [p for p in projects if (p.get('status') or '').lower() == 'completed']

    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='projects',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=projects)

@app.route('/manager/tasks')
@login_required
def manager_tasks():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    # Optional filter: in-progress, overdue
    flt = (request.args.get('filter') or '').lower()
    tasks = manager_data['tasks']
    if flt == 'in-progress':
        tasks = [t for t in tasks if (t.get('status') or '').lower() == 'in-progress']
    elif flt == 'overdue':
        today = datetime.now().date()
        def is_overdue(t):
            if (t.get('status') or '').lower() in ['completed','cancelled']:
                return False
            try:
                if t.get('due_date'):
                    dd = datetime.strptime(t['due_date'], '%Y-%m-%d').date()
                    return dd < today
            except Exception:
                return False
            return False
        tasks = [t for t in tasks if is_overdue(t)]

    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='tasks',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=tasks,
                         projects=manager_data['projects'])

@app.route('/manager/notifications')
@login_required
def manager_notifications():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='notifications',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/manager/reports')
@login_required
def manager_reports():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='reports',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

# Team Lead View Routes
@app.route('/teamlead/overview')
@login_required
def teamlead_overview():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='overview',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/teamlead/team-members')
@login_required
def teamlead_team_members():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='team-members',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/teamlead/projects')
@login_required
def teamlead_projects():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='projects',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/teamlead/tasks')
@login_required
def teamlead_tasks():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='tasks',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/teamlead/reports')
@login_required
def teamlead_reports():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='reports',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

if __name__ == '__main__':
    # Create sample users on startup
    create_sample_users()
    app.run(debug=True, port=5000)