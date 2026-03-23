import csv
import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

ADMIN_DIR = Path(__file__).resolve().parent
ROOT_DIR = ADMIN_DIR.parent
DATA_DIR = ROOT_DIR / 'data'
ADMIN_DATA_DIR = DATA_DIR / 'admin'

USERS_CSV = DATA_DIR / 'users.csv'
EMPLOYEES_CSV = DATA_DIR / 'employees.csv'
PROJECTS_CSV = DATA_DIR / 'projects.csv'
TASKS_CSV = DATA_DIR / 'tasks.csv'
TEAMS_CSV = DATA_DIR / 'teams.csv'
PAYMENTS_CSV = DATA_DIR / 'payments.csv'
NOTIFICATIONS_CSV = DATA_DIR / 'notifications.csv'
LEAVE_CSV = DATA_DIR / 'leave.csv'

COMPANIES_CSV = ADMIN_DATA_DIR / 'companies.csv'
COMPANY_METRICS_CSV = ADMIN_DATA_DIR / 'company_metrics.csv'
SETTINGS_JSON = ADMIN_DATA_DIR / 'settings.json'

COMPANY_FIELDS = [
    'id',
    'company_name',
    'industry',
    'country',
    'employees_count',
    'users_assigned',
    'signup_date',
    'status',
    'plan_type',
    'contact_email',
]

COMPANY_METRIC_FIELDS = [
    'id',
    'company_id',
    'date',
    'active_users',
    'tasks_completed',
    'projects_created',
    'working_hours',
]

FOUNDER_EMAIL = os.environ.get('TASKVISE_FOUNDER_EMAIL', 'saathvikk202@gmail.com')
FOUNDER_PASSWORD = os.environ.get('TASKVISE_FOUNDER_PASSWORD', 'saathvik@2026')


def _ensure_directory(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _read_csv(path):
    file_path = Path(path)
    if not file_path.exists():
        return []
    with file_path.open('r', newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        return list(reader) if reader else []


def _write_csv(path, rows, fieldnames):
    _ensure_directory(path)
    with Path(path).open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _append_csv(path, row, fieldnames):
    _ensure_directory(path)
    file_path = Path(path)
    write_header = not file_path.exists() or file_path.stat().st_size == 0
    with file_path.open('a', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow({field: row.get(field, '') for field in fieldnames})


def _safe_int(value, default=0):
    try:
        return int(float(str(value or '').strip()))
    except Exception:
        return default


def _normalize_role(value):
    return str(value or 'employee').strip().lower() or 'employee'


def _normalize_task_status(value):
    raw = str(value or 'pending').strip().lower()
    if raw in {'in progress', 'in_progress'}:
        return 'in-progress'
    if raw == 'done':
        return 'completed'
    return raw or 'pending'


def _normalize_project_status(value):
    raw = str(value or 'planning').strip().lower()
    if raw == 'in progress':
        return 'active'
    return raw or 'planning'


def _truthy(value):
    return str(value or '').strip().lower() in {'1', 'true', 'yes', 'on'}


def _parse_datetime(value):
    text = str(value or '').strip()
    if not text:
        return None
    for fmt in (
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
    ):
        try:
            return datetime.strptime(text, fmt)
        except Exception:
            continue
    try:
        return datetime.fromisoformat(text.replace('Z', ''))
    except Exception:
        return None


def _next_numeric_id(rows):
    values = [_safe_int(row.get('id'), 0) for row in rows]
    return str(max(values + [0]) + 1)


def ensure_companies_csv():
    rows = _read_csv(COMPANIES_CSV)
    if not Path(COMPANIES_CSV).exists():
        _write_csv(COMPANIES_CSV, rows, COMPANY_FIELDS)
    if rows:
        return

    employees = _read_csv(EMPLOYEES_CSV)
    users = _read_csv(USERS_CSV)
    projects = _read_csv(PROJECTS_CSV)
    company_name = next(
        (
            str(row.get('company', '')).strip()
            for row in employees + projects
            if str(row.get('company', '')).strip()
        ),
        'TaskVise Demo Workspace',
    )
    signup_dates = [
        _parse_datetime(row.get('created_at'))
        for row in users
        if _parse_datetime(row.get('created_at'))
    ]
    signup_date = min(signup_dates).strftime('%Y-%m-%d') if signup_dates else datetime.now().strftime('%Y-%m-%d')
    seeded = {
        'id': '1',
        'company_name': company_name,
        'industry': 'Technology',
        'country': 'India',
        'employees_count': str(len(employees)),
        'users_assigned': str(len([row for row in users if _normalize_role(row.get('role')) != 'platform_admin'])),
        'signup_date': signup_date,
        'status': 'active',
        'plan_type': 'enterprise',
        'contact_email': FOUNDER_EMAIL,
    }
    _write_csv(COMPANIES_CSV, [seeded], COMPANY_FIELDS)


def ensure_metrics_csv():
    if not Path(COMPANY_METRICS_CSV).exists():
        _write_csv(COMPANY_METRICS_CSV, [], COMPANY_METRIC_FIELDS)


def ensure_founder_account():
    rows = _read_csv(USERS_CSV)
    if not rows:
        return

    existing = next((row for row in rows if _normalize_role(row.get('role')) == 'platform_admin'), None)
    if existing:
        updated = False
        if str(existing.get('username') or '').strip().lower() != FOUNDER_EMAIL.lower():
            existing['username'] = FOUNDER_EMAIL
            updated = True
        password_hash = str(existing.get('password_hash') or '')
        if not password_hash or not check_password_hash(password_hash, FOUNDER_PASSWORD):
            existing['password_hash'] = generate_password_hash(FOUNDER_PASSWORD)
            updated = True
        if str(existing.get('full_name') or '').strip() != 'TaskVise Founder':
            existing['full_name'] = 'TaskVise Founder'
            updated = True
        if str(existing.get('is_active') or '').strip().lower() != 'true':
            existing['is_active'] = 'true'
            updated = True
        if updated:
            fieldnames = []
            for row in rows:
                for key in row.keys():
                    if key not in fieldnames:
                        fieldnames.append(key)
            _write_csv(USERS_CSV, rows, fieldnames)
        return

    fieldnames = list(rows[0].keys())
    for field in ['id', 'username', 'password_hash', 'full_name', 'role', 'created_at', 'is_active']:
        if field not in fieldnames:
            fieldnames.append(field)

    rows.append({
        'id': 'TVA001',
        'username': FOUNDER_EMAIL,
        'password_hash': generate_password_hash(FOUNDER_PASSWORD),
        'full_name': 'TaskVise Founder',
        'role': 'platform_admin',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_active': 'true',
    })
    _write_csv(USERS_CSV, rows, fieldnames)


def _sync_company_rollups(companies):
    users = _read_csv(USERS_CSV)
    employees = _read_csv(EMPLOYEES_CSV)
    projects = _read_csv(PROJECTS_CSV)

    if not companies:
        return companies

    company_names = [
        str(row.get('company', '')).strip()
        for row in employees + projects
        if str(row.get('company', '')).strip()
    ]
    default_company_name = company_names[0] if company_names else companies[0].get('company_name', 'TaskVise Demo Workspace')
    total_users = len([row for row in users if _normalize_role(row.get('role')) != 'platform_admin'])
    total_employees = len(employees)

    for index, company in enumerate(companies):
        if index == 0 and not str(company.get('company_name', '')).strip():
            company['company_name'] = default_company_name
        if index == 0:
            company['employees_count'] = str(total_employees)
            company['users_assigned'] = str(total_users)
            company['status'] = company.get('status') or 'active'
            company['plan_type'] = company.get('plan_type') or 'enterprise'
            company['contact_email'] = company.get('contact_email') or FOUNDER_EMAIL
    return companies


def get_all_companies():
    ensure_companies_csv()
    companies = _sync_company_rollups(_read_csv(COMPANIES_CSV))
    if companies:
        _write_csv(COMPANIES_CSV, companies, COMPANY_FIELDS)
    return companies


def get_company_by_id(company_id):
    company_id = str(company_id)
    return next((company for company in get_all_companies() if str(company.get('id')) == company_id), None)


def add_company(company_data):
    companies = get_all_companies()
    company = {
        'id': _next_numeric_id(companies),
        'company_name': str(company_data.get('company_name') or '').strip(),
        'industry': str(company_data.get('industry') or '').strip(),
        'country': str(company_data.get('country') or '').strip(),
        'employees_count': str(company_data.get('employees_count') or 0),
        'users_assigned': str(company_data.get('users_assigned') or 0),
        'signup_date': datetime.now().strftime('%Y-%m-%d'),
        'status': str(company_data.get('status') or 'active').strip().lower(),
        'plan_type': str(company_data.get('plan_type') or 'professional').strip().lower(),
        'contact_email': str(company_data.get('contact_email') or '').strip(),
    }
    companies.append(company)
    _write_csv(COMPANIES_CSV, companies, COMPANY_FIELDS)
    return company


def update_company(company_id, updates):
    companies = get_all_companies()
    target_id = str(company_id)
    for company in companies:
        if str(company.get('id')) != target_id:
            continue
        for field in COMPANY_FIELDS:
            if field == 'id':
                continue
            if field in updates:
                company[field] = str(updates.get(field) or '')
        break
    _write_csv(COMPANIES_CSV, companies, COMPANY_FIELDS)


def delete_company(company_id):
    companies = [company for company in get_all_companies() if str(company.get('id')) != str(company_id)]
    _write_csv(COMPANIES_CSV, companies, COMPANY_FIELDS)


def record_company_metrics(company_id, active_users, tasks_completed, projects_created, working_hours):
    ensure_metrics_csv()
    metric = {
        'id': str(int(datetime.now().timestamp())),
        'company_id': str(company_id),
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'active_users': str(active_users),
        'tasks_completed': str(tasks_completed),
        'projects_created': str(projects_created),
        'working_hours': str(working_hours),
    }
    _append_csv(COMPANY_METRICS_CSV, metric, COMPANY_METRIC_FIELDS)
    return metric


def get_company_metrics(company_id, limit=30):
    ensure_metrics_csv()
    metrics = [
        row for row in _read_csv(COMPANY_METRICS_CSV)
        if str(row.get('company_id')) == str(company_id)
    ]
    metrics.sort(key=lambda row: row.get('date', ''))
    return metrics[-max(1, int(limit)) :]


def load_platform_settings():
    if not SETTINGS_JSON.exists():
        return {
            'enable_signups': True,
            'maintenance_mode': False,
            'backup_interval': 24,
        }
    with SETTINGS_JSON.open('r', encoding='utf-8') as handle:
        data = json.load(handle)
    return {
        'enable_signups': bool(data.get('enable_signups', True)),
        'maintenance_mode': bool(data.get('maintenance_mode', False)),
        'backup_interval': _safe_int(data.get('backup_interval', 24), 24),
    }


def save_platform_settings(settings):
    ADMIN_DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        'enable_signups': bool(settings.get('enable_signups', True)),
        'maintenance_mode': bool(settings.get('maintenance_mode', False)),
        'backup_interval': _safe_int(settings.get('backup_interval', 24), 24),
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    with SETTINGS_JSON.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2)
    return payload


def authenticate_founder(username, password):
    ensure_founder_account()
    users = _read_csv(USERS_CSV)
    normalized_username = str(username or '').strip().lower()
    for user in users:
        if _normalize_role(user.get('role')) != 'platform_admin':
            continue
        if str(user.get('username') or '').strip().lower() != normalized_username:
            continue
        password_hash = str(user.get('password_hash') or '')
        if password_hash and check_password_hash(password_hash, password or ''):
            return user
    if normalized_username == FOUNDER_EMAIL.lower() and str(password or '') == FOUNDER_PASSWORD:
        return {
            'id': 'TVA001',
            'username': FOUNDER_EMAIL,
            'full_name': 'TaskVise Founder',
            'role': 'platform_admin',
        }
    return None


def _team_member_ids(team):
    raw = str((team or {}).get('member_ids') or '')
    return [member.strip() for member in raw.split(',') if member.strip()]


def _build_recent_activity(employees, projects, tasks, notifications, limit=10):
    activity = []

    for employee in employees:
        joined = _parse_datetime(employee.get('join_date'))
        if joined:
            activity.append({
                'message': f"Employee joined: {employee.get('name', 'Unknown')} ({employee.get('id', '')})",
                'time': joined.strftime('%Y-%m-%d'),
                'icon': 'employee',
                'sort_key': joined,
            })

    for project in projects:
        created = _parse_datetime(project.get('start_date'))
        if created:
            activity.append({
                'message': f"Project tracked: {project.get('name', 'Untitled Project')}",
                'time': created.strftime('%Y-%m-%d'),
                'icon': 'project',
                'sort_key': created,
            })

    for task in tasks:
        created = _parse_datetime(task.get('created_at'))
        if created:
            activity.append({
                'message': f"Task update: {task.get('title', 'Untitled Task')} ({_normalize_task_status(task.get('status'))})",
                'time': created.strftime('%Y-%m-%d'),
                'icon': 'task',
                'sort_key': created,
            })

    for notification in notifications:
        created = _parse_datetime(notification.get('created_at'))
        if created:
            activity.append({
                'message': notification.get('title') or 'Notification posted',
                'time': created.strftime('%Y-%m-%d %H:%M'),
                'icon': str(notification.get('type') or 'system').lower(),
                'sort_key': created,
            })

    activity.sort(key=lambda item: item['sort_key'], reverse=True)
    return [
        {
            'message': item['message'],
            'time': item['time'],
            'icon': item['icon'],
        }
        for item in activity[:limit]
    ]


def get_platform_snapshot():
    ensure_founder_account()
    companies = get_all_companies()
    ensure_metrics_csv()

    users = _read_csv(USERS_CSV)
    employees = _read_csv(EMPLOYEES_CSV)
    projects = _read_csv(PROJECTS_CSV)
    tasks = _read_csv(TASKS_CSV)
    teams = _read_csv(TEAMS_CSV)
    payments = _read_csv(PAYMENTS_CSV)
    notifications = _read_csv(NOTIFICATIONS_CSV)
    leaves = _read_csv(LEAVE_CSV)

    product_roles = [user for user in users if _normalize_role(user.get('role')) != 'platform_admin']
    role_distribution = Counter(_normalize_role(user.get('role')) for user in product_roles)
    tasks_by_status = Counter(_normalize_task_status(task.get('status')) for task in tasks)
    projects_by_status = Counter(_normalize_project_status(project.get('status')) for project in projects)

    today = datetime.now().date()
    on_leave_today = 0
    for leave in leaves:
        if str(leave.get('status') or '').strip().lower() != 'approved':
            continue
        start = _parse_datetime(leave.get('start_date'))
        end = _parse_datetime(leave.get('end_date'))
        if start and end and start.date() <= today <= end.date():
            on_leave_today += 1

    team_lookup = {str(team.get('id', '')): team for team in teams}
    payroll_by_team = []
    for team in teams:
        team_id = str(team.get('id', ''))
        team_payments = [row for row in payments if str(row.get('team_id', '')) == team_id]
        team_total = sum(_safe_int(row.get('base_salary'), 0) + _safe_int(row.get('bonus'), 0) for row in team_payments)
        payroll_by_team.append({
            'team_id': team_id,
            'team_name': team.get('name', ''),
            'manager_name': team.get('manager_name', ''),
            'teamlead_name': team.get('teamlead_name', ''),
            'member_count': len(_team_member_ids(team)),
            'payroll_total': team_total,
        })
    payroll_by_team.sort(key=lambda row: row['payroll_total'], reverse=True)

    completed_tasks_by_team = Counter()
    project_counts_by_team = Counter()
    for project in projects:
        team_id = str(project.get('team_id', ''))
        if team_id:
            project_counts_by_team[team_id] += 1
    for task in tasks:
        if _normalize_task_status(task.get('status')) != 'completed':
            continue
        team_id = ''
        project_id = str(task.get('project_id', ''))
        if project_id:
            project = next((row for row in projects if str(row.get('id', '')) == project_id), None)
            if project:
                team_id = str(project.get('team_id', ''))
        if not team_id:
            assignee_id = str(task.get('assignee_id', ''))
            employee = next((row for row in employees if str(row.get('id', '')) == assignee_id), None)
            if employee:
                team_id = str(employee.get('team_id', ''))
        if team_id:
            completed_tasks_by_team[team_id] += 1

    team_leaderboard = []
    for team in teams:
        team_id = str(team.get('id', ''))
        team_leaderboard.append({
            'team_name': team.get('name', ''),
            'focus_area': team.get('focus_area', ''),
            'completed_tasks': completed_tasks_by_team.get(team_id, 0),
            'active_projects': project_counts_by_team.get(team_id, 0),
            'member_count': len(_team_member_ids(team)),
        })
    team_leaderboard.sort(key=lambda row: (row['completed_tasks'], row['active_projects']), reverse=True)

    active_projects = [
        project for project in projects
        if _normalize_project_status(project.get('status')) in {'active', 'planning'}
    ]
    active_employees = [
        employee for employee in employees
        if str(employee.get('last_login') or '').strip()
    ]

    companies_by_plan = Counter(str(company.get('plan_type') or 'professional').strip().lower() for company in companies)
    companies_by_country = Counter(str(company.get('country') or 'Unknown').strip() for company in companies)
    companies_by_industry = Counter(str(company.get('industry') or 'General').strip() for company in companies)

    stats = {
        'success': True,
        'total_companies': len(companies),
        'active_companies': len([company for company in companies if str(company.get('status') or '').lower() == 'active']),
        'total_employees': len(employees),
        'total_users': len(product_roles),
        'active_users': len(active_employees),
        'enterprise_plans': companies_by_plan.get('enterprise', 0),
        'professional_plans': companies_by_plan.get('professional', 0),
        'total_projects': len(projects),
        'active_projects': len(active_projects),
        'total_tasks': len(tasks),
        'completed_tasks': len([task for task in tasks if _normalize_task_status(task.get('status')) == 'completed']),
        'total_teams': len(teams),
        'monthly_payroll': sum(
            _safe_int(row.get('base_salary'), 0) + _safe_int(row.get('bonus'), 0)
            for row in payments
            if str(row.get('payment_status') or '').strip().lower() != 'hold'
        ),
        'unread_notifications': len([row for row in notifications if not _truthy(row.get('is_read'))]),
        'on_leave_today': on_leave_today,
        'role_distribution': dict(role_distribution),
        'tasks_by_status': dict(tasks_by_status),
        'projects_by_status': dict(projects_by_status),
        'companies_by_plan': dict(companies_by_plan),
        'companies_by_country': dict(companies_by_country),
        'companies_by_industry': dict(companies_by_industry),
        'recent_activity': _build_recent_activity(employees, projects, tasks, notifications, limit=10),
        'payroll_by_team': payroll_by_team[:6],
        'team_leaderboard': team_leaderboard[:6],
        'settings': load_platform_settings(),
    }
    return stats


def get_admin_statistics():
    snapshot = get_platform_snapshot()
    return {
        'total_companies': snapshot.get('total_companies', 0),
        'active_companies': snapshot.get('active_companies', 0),
        'total_employees': snapshot.get('total_employees', 0),
        'total_users': snapshot.get('total_users', 0),
        'enterprise_plans': snapshot.get('enterprise_plans', 0),
        'professional_plans': snapshot.get('professional_plans', 0),
        'industries': sorted(snapshot.get('companies_by_industry', {}).keys()),
    }


ensure_companies_csv()
ensure_metrics_csv()
