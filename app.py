from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_from_directory
import csv, os, uuid
from collections import Counter
from email.message import EmailMessage
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import json
import re
import smtplib
import ssl
from datetime import datetime, timedelta
from urllib import parse, request as urllib_request, error as urllib_error

try:
    from taskvise_admin import admin_manager as taskvise_admin_manager
except Exception:
    taskvise_admin_manager = None

BASE_DIR = os.path.dirname(__file__)
TASKVISE_ADMIN_URL = os.environ.get('TASKVISE_ADMIN_URL', 'http://127.0.0.1:5051').rstrip('/')
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
EMP_CSV = os.path.join(DATA_DIR, "employees.csv")
TASKS_CSV = os.path.join(DATA_DIR, "tasks.csv")
PROJECTS_CSV = os.path.join(DATA_DIR, "projects.csv")
PROJECT_MEMBERS_CSV = os.path.join(DATA_DIR, "project_members.csv")
LEAVE_CSV = os.path.join(DATA_DIR, "leave.csv")
NOTES_CSV = os.path.join(DATA_DIR, "team_notes.csv")
WORK_CSV = os.path.join(DATA_DIR, "work.csv")
NOTIF_CSV = os.path.join(DATA_DIR, "notifications.csv")
SETTINGS_CSV = os.path.join(DATA_DIR, "settings.csv")
HELP_REQUESTS_CSV = os.path.join(DATA_DIR, "help_requests.csv")
CREDENTIALS_EXPORT_TXT = os.path.join(DATA_DIR, "login_credentials.txt")
TEAMS_CSV = os.path.join(DATA_DIR, "teams.csv")
PAYMENTS_CSV = os.path.join(DATA_DIR, "payments.csv")
AVATAR_UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads", "avatars")
TASK_SUBMISSIONS_CSV = os.path.join(DATA_DIR, "task_submissions.csv")
TASK_SUBMISSION_UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads", "task_submissions")

try:
    import mysql.connector
except Exception:
    mysql = None

try:
    from pymongo import MongoClient
except Exception:
    MongoClient = None

DB_BACKEND = os.environ.get(
    "TASKVISE_DB_BACKEND",
    "mongodb"
).strip().lower()

MONGO_REQUIRED = os.environ.get(
    "TASKVISE_MONGO_REQUIRED",
    "true"
).strip().lower() in {"1", "true", "yes", "on"}

MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)
MONGO_DATABASE = os.environ.get("MONGO_DATABASE", "taskvise")

MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "taskvise")
MIRROR_MYSQL = os.environ.get(
    "TASKVISE_MIRROR_MYSQL",
    "true"
).strip().lower() in {"1", "true", "yes", "on"}
MIRROR_MONGODB = os.environ.get(
    "TASKVISE_MIRROR_MONGODB",
    "true"
).strip().lower() in {"1", "true", "yes", "on"}
CSV_SHADOW_SYNC = os.environ.get(
    "TASKVISE_SYNC_CSV_SHADOW",
    "true"
).strip().lower() in {"1", "true", "yes", "on"}
EMAIL_NOTIFICATIONS_ENABLED = os.environ.get(
    "TASKVISE_EMAIL_NOTIFICATIONS",
    "true"
).strip().lower() in {"1", "true", "yes", "on"}
SMTP_HOST = os.environ.get("SMTP_HOST", "").strip()
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "").strip()
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM = os.environ.get("SMTP_FROM", SMTP_USER).strip()
SMTP_USE_TLS = os.environ.get(
    "SMTP_USE_TLS",
    "true"
).strip().lower() in {"1", "true", "yes", "on"}

SYSTEM_SETTINGS_USER_ID = "__system__"
DEFAULT_COMPANY_NAME = "TaskVise HyperScale Operations Consortium"
PLATFORM_FOUNDER_EMAIL = os.environ.get("TASKVISE_FOUNDER_EMAIL", "saathvikk202@gmail.com").strip() or "saathvikk202@gmail.com"
ROLE_DEFAULT_PASSWORDS = {
    "platform_admin": "saathvik@2026",
    "admin": "admin123",
    "manager": "manager123",
    "hr": "hr123",
    "teamlead": "lead123",
    "employee": "emp123",
}
WORKFORCE_ID_PREFIX = "EMP"
WORKFORCE_ID_WIDTH = 3
PROJECT_ID_PREFIX = "PRJ"
PROJECT_ID_WIDTH = 4
TASK_ID_PREFIX = "TSK"
TASK_ID_WIDTH = 5
PROJECT_MEMBER_ID_PREFIX = "PMB"
PROJECT_MEMBER_ID_WIDTH = 5
TEAM_BLUEPRINTS = [
    {
        "id": "TEAM001",
        "name": "Code Comets",
        "department": "Engineering",
        "manager_id": "EMP004",
        "teamlead_id": "EMP010",
        "member_ids": ["EMP016", "EMP018", "EMP019", "EMP021", "EMP042"],
        "tagline": "Debug fast, ship faster.",
        "focus_area": "Core engineering, platforms, and delivery acceleration",
    },
    {
        "id": "TEAM002",
        "name": "Feature Falcons",
        "department": "Product",
        "manager_id": "EMP005",
        "teamlead_id": "EMP013",
        "member_ids": ["EMP017", "EMP020", "EMP023", "EMP024", "EMP041"],
        "tagline": "Turning roadmap chaos into launch-day magic.",
        "focus_area": "Product planning, discovery, design, and feature launches",
    },
    {
        "id": "TEAM003",
        "name": "Audit Avengers",
        "department": "Finance",
        "manager_id": "EMP006",
        "teamlead_id": "EMP012",
        "member_ids": ["EMP022", "EMP030", "EMP031", "EMP034", "EMP035"],
        "tagline": "Clean books, calm systems, zero drama.",
        "focus_area": "Finance operations, systems control, and compliance readiness",
    },
    {
        "id": "TEAM004",
        "name": "Pixel Pulse",
        "department": "Marketing",
        "manager_id": "EMP007",
        "teamlead_id": "EMP011",
        "member_ids": ["EMP025", "EMP026", "EMP027", "EMP038", "EMP043"],
        "tagline": "Brand sparkle with measurable pipeline juice.",
        "focus_area": "Creative production, campaigns, and customer storytelling",
    },
    {
        "id": "TEAM005",
        "name": "Quota Crushers",
        "department": "Sales",
        "manager_id": "EMP008",
        "teamlead_id": "EMP014",
        "member_ids": ["EMP028", "EMP029", "EMP037", "EMP039", "EMP045"],
        "tagline": "Closing deals before the coffee gets cold.",
        "focus_area": "Revenue operations, enablement, and deal execution",
    },
    {
        "id": "TEAM006",
        "name": "Ops Oddballs",
        "department": "Operations",
        "manager_id": "EMP009",
        "teamlead_id": "EMP015",
        "member_ids": ["EMP032", "EMP033", "EMP036", "EMP040", "EMP044"],
        "tagline": "Chaos managed. Somehow stylishly.",
        "focus_area": "Operational excellence, support flow, and people enablement",
    },
]
ROLE_PAY_BANDS = {
    "platform_admin": 320000,
    "admin": 250000,
    "hr": 145000,
    "manager": 195000,
    "teamlead": 158000,
    "employee": 92000,
}
_ORG_STRUCTURE_BOOTSTRAPPED = False

STORAGE_TABLE_MAP = {
    USERS_CSV: "users",
    EMP_CSV: "employees",
    TASKS_CSV: "tasks",
    PROJECTS_CSV: "projects",
    PROJECT_MEMBERS_CSV: "project_members",
    LEAVE_CSV: "leave_requests",
    NOTES_CSV: "team_notes",
    WORK_CSV: "work_logs",
    NOTIF_CSV: "notifications",
    SETTINGS_CSV: "user_settings",
    TEAMS_CSV: "teams",
    PAYMENTS_CSV: "payments",
    TASK_SUBMISSIONS_CSV: "task_submissions",
}

MYSQL_DEFAULT_COLUMNS = {
    "users": ["id", "username", "password_hash", "full_name", "role", "created_at", "is_active"],
    "employees": ["id", "name", "email", "position", "department", "company", "join_date", "phone", "skills", "location", "last_login", "password_last_changed", "avatar_url", "status", "productivity"],
    "tasks": ["id", "title", "description", "project_id", "assignee_id", "assignee_name", "status", "priority", "created_at", "due_date", "estimated_hours", "actual_hours", "progress"],
    "projects": ["id", "name", "description", "owner_id", "start_date", "end_date", "status", "team_members", "company", "progress"],
    "project_members": ["id", "project_id", "employee_id"],
    "leave_requests": ["id", "employee_id", "start_date", "end_date", "reason", "type", "status", "applied_at"],
    "team_notes": ["id", "title", "content", "author", "author_id", "priority", "is_pinned", "created_at", "updated_at", "visible_to"],
    "work_logs": ["id", "employee_id", "task_id", "start_time", "end_time", "duration_minutes", "notes"],
    "notifications": ["id", "user_id", "title", "message", "type", "is_read", "created_at"],
    "teams": [
        "id", "name", "department", "manager_id", "manager_name", "teamlead_id", "teamlead_name",
        "member_ids", "tagline", "focus_area", "created_at", "updated_at"
    ],
    "payments": [
        "id", "employee_id", "employee_name", "role", "team_id", "team_name", "department",
        "base_salary", "bonus", "currency", "payment_status", "last_paid_date", "next_pay_date",
        "pay_cycle", "updated_at"
    ],
    "task_submissions": [
        "id", "task_id", "project_id", "employee_id", "employee_name", "manager_id", "teamlead_id",
        "recipient_ids", "original_filename", "stored_filename", "file_path", "file_size",
        "status", "notes", "created_at", "updated_at"
    ],
    "user_settings": [
        "id", "user_id", "email_notifications", "push_notifications", "task_reminders", "deadline_alerts",
        "theme", "language", "timezone", "updated_at", "company_name", "date_format", "session_timeout",
        "password_policy", "notify_task_assignments", "notify_project_updates", "notify_system_alerts",
        "desktop_notifications", "sound_alerts", "auto_backup", "data_retention", "api_access", "webhook_url"
    ],
}

_MYSQL_ENABLED = mysql is not None
_MONGO_ENABLED = MongoClient is not None
_MYSQL_BOOTSTRAPPED = False

if DB_BACKEND == "mysql" and mysql is None:
    print("mysql-connector-python is not installed. Falling back to CSV storage.")

if DB_BACKEND == "mongodb" and MongoClient is None:
    print("pymongo is not installed. Falling back to CSV storage.")


def _mongo_client():
    if not _MONGO_ENABLED:
        raise RuntimeError("MongoDB is not enabled or pymongo is not installed")
    return MongoClient(MONGO_URI)


def _mongo_collection(collection_name):
    client = _mongo_client()
    db = client[MONGO_DATABASE]
    return db[collection_name]


def _mongo_read_rows(path):
    collection_name = STORAGE_TABLE_MAP.get(path)
    if not collection_name:
        return []
    try:
        coll = _mongo_collection(collection_name)
        rows = []
        for doc in coll.find():
            row = {k: (str(v) if k == '_id' else v) for k,v in doc.items() if k != '_id'}
            rows.append(row)
        return rows
    except Exception as exc:
        if MONGO_REQUIRED and DB_BACKEND == "mongodb":
            raise RuntimeError(f"MongoDB read failed for {path}: {exc}") from exc
        print(f"MongoDB read error for {path}: {exc}. Falling back to CSV.")
        return _read_csv_file(path)


def _mongo_write_rows(path, rows, fieldnames):
    collection_name = STORAGE_TABLE_MAP.get(path)
    if not collection_name:
        return
    try:
        coll = _mongo_collection(collection_name)
        coll.delete_many({})
        if rows:
            coll.insert_many([{k: v for k, v in row.items()} for row in rows])
    except Exception as exc:
        if MONGO_REQUIRED and DB_BACKEND == "mongodb":
            raise RuntimeError(f"MongoDB write failed for {path}: {exc}") from exc
        print(f"MongoDB write error for {path}: {exc}. Falling back to CSV.")
        _write_csv_file(path, rows, fieldnames)


def _read_csv_file(path):
    if not os.path.exists(path):
        return []
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _write_csv_file(path, rows, fieldnames):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _mongo_append_row(path, row, fieldnames):
    collection_name = STORAGE_TABLE_MAP.get(path)
    if not collection_name:
        return

    try:
        coll = _mongo_collection(collection_name)
        coll.insert_one({k: v for k, v in row.items()})
    except Exception as exc:
        if MONGO_REQUIRED and DB_BACKEND == "mongodb":
            raise RuntimeError(f"MongoDB append failed for {path}: {exc}") from exc
        print(f"MongoDB append error for {path}: {exc}. Falling back to CSV.")
        if fieldnames is None:
            fieldnames = list(row.keys())
        _write_csv_file(path, _read_csv_file(path) + [row], fieldnames)


def _mongo_update_by_id(path, id, updates):
    """Direct MongoDB update by ID"""
    collection_name = STORAGE_TABLE_MAP.get(path)
    if not collection_name:
        return False

    try:
        coll = _mongo_collection(collection_name)
        result = coll.update_one({'id': id}, {'$set': updates})
        return result.matched_count > 0
    except Exception as exc:
        print(f"MongoDB update error for {path}: {exc}")
        return False


def _mongo_delete_by_id(path, id):
    """Direct MongoDB delete by ID"""
    collection_name = STORAGE_TABLE_MAP.get(path)
    if not collection_name:
        return False

    try:
        coll = _mongo_collection(collection_name)
        result = coll.delete_one({'id': id})
        return result.deleted_count > 0
    except Exception as exc:
        print(f"MongoDB delete error for {path}: {exc}")
        return False


def _mongo_bootstrap():
    if not _MONGO_ENABLED:
        return False
    try:
        for path in STORAGE_TABLE_MAP:
            collection_name = STORAGE_TABLE_MAP[path]
            coll = _mongo_collection(collection_name)
            coll.find_one()
        return True
    except Exception as exc:
        if MONGO_REQUIRED and DB_BACKEND == "mongodb":
            raise RuntimeError(f"MongoDB unavailable: {exc}") from exc
        print(f"MongoDB unavailable ({exc}). Falling back to CSV storage.")
        return False


def _use_mongo(path):
    return DB_BACKEND == 'mongodb' and _mongo_bootstrap()


def _collect_fieldnames(rows, preferred_fieldnames=None):
    names = []
    for name in preferred_fieldnames or []:
        if name and name not in names:
            names.append(name)
    for row in rows or []:
        for key in row.keys():
            if key and key not in names:
                names.append(key)
    return names


def _escape_identifier(name):
    return f"`{str(name).replace('`', '``')}`"


def _mysql_column_type(column_name):
    col = str(column_name or "").lower()
    if col == "id":
        return "VARCHAR(64)"
    if col in {"description", "reason", "notes", "content", "skills", "team_members"}:
        return "TEXT"
    if col in {"is_active", "is_pinned"}:
        return "VARCHAR(16)"
    if col in {"duration_minutes", "estimated_hours", "actual_hours"}:
        return "VARCHAR(32)"
    return "VARCHAR(255)"


def _mysql_connect(include_database=True):
    if mysql is None:
        raise RuntimeError("mysql-connector-python is not available")
    config = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "connection_timeout": int(os.environ.get("MYSQL_CONNECTION_TIMEOUT", "3")),
    }
    if include_database:
        config["database"] = MYSQL_DATABASE
    return mysql.connector.connect(**config)


def _mysql_ensure_database():
    conn = _mysql_connect(include_database=False)
    try:
        cur = conn.cursor()
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS {_escape_identifier(MYSQL_DATABASE)} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn.commit()
    finally:
        conn.close()


def _mysql_existing_columns(table_name):
    conn = _mysql_connect(include_database=True)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
            """,
            (MYSQL_DATABASE, table_name),
        )
        return [row[0] for row in cur.fetchall()]
    finally:
        conn.close()


def _mysql_ensure_table(table_name, columns):
    cols = _collect_fieldnames([], columns) or ["id"]
    definitions = []
    has_id = False
    for col in cols:
        if col == "id":
            has_id = True
            definitions.append(f"{_escape_identifier(col)} {_mysql_column_type(col)} NOT NULL")
        else:
            definitions.append(f"{_escape_identifier(col)} {_mysql_column_type(col)} NULL")
    if not has_id:
        definitions.insert(0, "`id` VARCHAR(64) NOT NULL")
        has_id = True
    if has_id:
        definitions.append("PRIMARY KEY (`id`)")

    conn = _mysql_connect(include_database=True)
    try:
        cur = conn.cursor()
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {_escape_identifier(table_name)} "
            f"({', '.join(definitions)}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
        )
        conn.commit()
    finally:
        conn.close()


def _mysql_ensure_columns(table_name, columns):
    missing = []
    existing = set(_mysql_existing_columns(table_name))
    for col in _collect_fieldnames([], columns):
        if col and col not in existing:
            missing.append(col)
    if not missing:
        return

    conn = _mysql_connect(include_database=True)
    try:
        cur = conn.cursor()
        for col in missing:
            cur.execute(
                f"ALTER TABLE {_escape_identifier(table_name)} "
                f"ADD COLUMN {_escape_identifier(col)} {_mysql_column_type(col)} NULL"
            )
        conn.commit()
    finally:
        conn.close()


def _mysql_bootstrap():
    global _MYSQL_BOOTSTRAPPED, _MYSQL_ENABLED
    if not _MYSQL_ENABLED:
        return False
    if _MYSQL_BOOTSTRAPPED:
        return True

    try:
        _mysql_ensure_database()
        for table_name, columns in MYSQL_DEFAULT_COLUMNS.items():
            _mysql_ensure_table(table_name, columns)
        _MYSQL_BOOTSTRAPPED = True
        return True
    except Exception as exc:
        print(f"MySQL unavailable ({exc}). Falling back to CSV storage.")
        _MYSQL_ENABLED = False
        return False


def _use_database(path):
    if path not in STORAGE_TABLE_MAP:
        return False
    if DB_BACKEND == 'mysql':
        return _mysql_bootstrap()
    if DB_BACKEND == 'mongodb':
        return _mongo_bootstrap()
    return False


def _mysql_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value if value.strip() else None
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return str(value)


def _mysql_read_rows(path):
    table_name = STORAGE_TABLE_MAP.get(path)
    if not table_name:
        return []
    conn = _mysql_connect(include_database=True)
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM {_escape_identifier(table_name)}")
        rows = cur.fetchall() or []
        normalized = []
        for row in rows:
            normalized.append({
                key: "" if value is None else str(value)
                for key, value in row.items()
            })
        return normalized
    finally:
        conn.close()


def _mysql_write_rows(path, rows, fieldnames):
    table_name = STORAGE_TABLE_MAP.get(path)
    if not table_name:
        return

    incoming_fields = _collect_fieldnames(rows, fieldnames) or MYSQL_DEFAULT_COLUMNS.get(table_name, ["id"])
    _mysql_ensure_columns(table_name, incoming_fields)
    table_columns = _mysql_existing_columns(table_name)

    conn = _mysql_connect(include_database=True)
    try:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {_escape_identifier(table_name)}")
        if rows:
            col_sql = ", ".join(_escape_identifier(col) for col in table_columns)
            placeholders = ", ".join(["%s"] * len(table_columns))
            sql = f"INSERT INTO {_escape_identifier(table_name)} ({col_sql}) VALUES ({placeholders})"
            payload = []
            for row in rows:
                payload.append(tuple(_mysql_value(row.get(col, "")) for col in table_columns))
            cur.executemany(sql, payload)
        conn.commit()
    finally:
        conn.close()


def _mysql_append_row(path, row, fieldnames):
    table_name = STORAGE_TABLE_MAP.get(path)
    if not table_name:
        return

    incoming_fields = _collect_fieldnames([row], fieldnames) or MYSQL_DEFAULT_COLUMNS.get(table_name, ["id"])
    _mysql_ensure_columns(table_name, incoming_fields)
    table_columns = _mysql_existing_columns(table_name)

    conn = _mysql_connect(include_database=True)
    try:
        cur = conn.cursor()
        col_sql = ", ".join(_escape_identifier(col) for col in table_columns)
        placeholders = ", ".join(["%s"] * len(table_columns))
        sql = f"INSERT INTO {_escape_identifier(table_name)} ({col_sql}) VALUES ({placeholders})"
        values = tuple(_mysql_value(row.get(col, "")) for col in table_columns)
        cur.execute(sql, values)
        conn.commit()
    finally:
        conn.close()


def ensure_csv(path, headers):
    if _use_database(path):
        if DB_BACKEND == 'mysql':
            table_name = STORAGE_TABLE_MAP.get(path)
            if table_name:
                _mysql_ensure_columns(table_name, headers)
        return
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()


def ensure_notes_csv():
    ensure_csv(NOTES_CSV, ['id','title','content','author','author_id','priority','is_pinned','created_at','updated_at','visible_to'])


ensure_csv(USERS_CSV, ["id","username","password_hash","full_name","role","created_at","is_active"])
ensure_csv(EMP_CSV, ["id","name","email","position","department","company","join_date","phone","skills","location","last_login","password_last_changed","avatar_url","status","productivity"])
ensure_csv(TASKS_CSV, ["id","title","description","project_id","assignee_id","assignee_name","status","priority","created_at","due_date","estimated_hours","actual_hours","progress"])
ensure_csv(PROJECTS_CSV, ["id","name","description","owner_id","start_date","end_date","status","team_members","company","progress"])
ensure_csv(PROJECT_MEMBERS_CSV, ["id","project_id","employee_id"])
ensure_csv(LEAVE_CSV, ["id","employee_id","start_date","end_date","reason","type","status","applied_at"])
ensure_csv(WORK_CSV, ["id","employee_id","task_id","start_time","end_time","duration_minutes","notes"])
ensure_csv(NOTIF_CSV, ["id","user_id","title","message","type","is_read","created_at"])
ensure_csv(SETTINGS_CSV, ["id","user_id","email_notifications","push_notifications","task_reminders","deadline_alerts","theme","language","timezone","updated_at","company_name","date_format","session_timeout","password_policy","notify_task_assignments","notify_project_updates","notify_system_alerts","desktop_notifications","sound_alerts","auto_backup","data_retention","api_access","webhook_url"])
ensure_csv(HELP_REQUESTS_CSV, ["id","requester_id","requester_name","task_id","task_title","message","urgency","status","recipient_type","recipient_id","recipient_name","request_type","created_at","updated_at"])
ensure_csv(TEAMS_CSV, ["id","name","department","manager_id","manager_name","teamlead_id","teamlead_name","member_ids","tagline","focus_area","created_at","updated_at"])
ensure_csv(PAYMENTS_CSV, ["id","employee_id","employee_name","role","team_id","team_name","department","base_salary","bonus","currency","payment_status","last_paid_date","next_pay_date","pay_cycle","updated_at"])
ensure_csv(TASK_SUBMISSIONS_CSV, ["id","task_id","project_id","employee_id","employee_name","manager_id","teamlead_id","recipient_ids","original_filename","stored_filename","file_path","file_size","status","notes","created_at","updated_at"])
ensure_notes_csv()

USER_FIELDNAMES = ['id','username','password_hash','full_name','role','created_at','is_active']
EMP_FIELDNAMES = ['id','name','email','position','department','company','join_date','phone','skills','location','last_login','password_last_changed','avatar_url','status','productivity']
TASK_FIELDNAMES = ['id','title','description','project_id','assignee_id','assignee_name','status','priority','created_at','due_date','estimated_hours','actual_hours','progress']
PROJECT_FIELDNAMES = ['id','name','description','owner_id','start_date','end_date','status','team_members','company','progress']
PROJECT_MEMBER_FIELDNAMES = ['id','project_id','employee_id']
LEAVE_FIELDNAMES = ['id', 'employee_id', 'start_date', 'end_date', 'reason', 'type', 'status', 'applied_at']
NOTIFICATION_FIELDNAMES = ['id', 'user_id', 'title', 'message', 'type', 'is_read', 'created_at']
SETTINGS_FIELDNAMES = ['id', 'user_id', 'email_notifications', 'push_notifications', 'task_reminders', 'deadline_alerts', 'theme', 'language', 'timezone', 'updated_at', 'company_name', 'date_format', 'session_timeout', 'password_policy', 'notify_task_assignments', 'notify_project_updates', 'notify_system_alerts', 'desktop_notifications', 'sound_alerts', 'auto_backup', 'data_retention', 'api_access', 'webhook_url']
HELP_REQUEST_FIELDNAMES = ['id', 'requester_id', 'requester_name', 'task_id', 'task_title', 'message', 'urgency', 'status', 'recipient_type', 'recipient_id', 'recipient_name', 'request_type', 'created_at', 'updated_at']
TEAM_FIELDNAMES = ['id', 'name', 'department', 'manager_id', 'manager_name', 'teamlead_id', 'teamlead_name', 'member_ids', 'tagline', 'focus_area', 'created_at', 'updated_at']
PAYMENT_FIELDNAMES = ['id', 'employee_id', 'employee_name', 'role', 'team_id', 'team_name', 'department', 'base_salary', 'bonus', 'currency', 'payment_status', 'last_paid_date', 'next_pay_date', 'pay_cycle', 'updated_at']
TASK_SUBMISSION_FIELDNAMES = ['id', 'task_id', 'project_id', 'employee_id', 'employee_name', 'manager_id', 'teamlead_id', 'recipient_ids', 'original_filename', 'stored_filename', 'file_path', 'file_size', 'status', 'notes', 'created_at', 'updated_at']
VALID_LEAVE_STATUSES = {'pending', 'approved', 'rejected'}

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret")

GOOGLE_CLIENT_ID = os.environ.get(
    "GOOGLE_CLIENT_ID",
    "",
)
GOOGLE_CLIENT_SECRET = os.environ.get(
    "GOOGLE_CLIENT_SECRET",
    "",
)
GOOGLE_REDIRECT_URI = os.environ.get(
    "GOOGLE_REDIRECT_URI",
    ""
)

def create_sample_users():
    """Create sample users for testing"""
    reset_passwords = os.environ.get('TASKVISE_RESET_SAMPLE_PASSWORDS', '').strip().lower() in {'1', 'true', 'yes', 'on'}
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

    existing_users = read_csv(USERS_CSV)
    existing_employees = read_csv(EMP_CSV)
    existing_usernames = [user['username'] for user in existing_users]

    for sample in sample_users:
        if sample['username'] not in existing_usernames:
            user_id = get_next_workforce_id(existing_users, existing_employees)
            user_row = {
                'id': user_id,
                'username': sample['username'],
                'password_hash': generate_password_hash(sample['password']),
                'full_name': sample['full_name'],
                'role': sample['role'],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'is_active': 'true'
            }

            employee_row = {
                'id': user_id,
                'name': sample['full_name'],
                'email': sample['username'],
                'position': sample['role'].title(),
                'department': 'IT',
                'company': get_default_company_name(),
                'join_date': datetime.now().strftime('%Y-%m-%d'),
                'phone': '555-0100',
                'skills': 'Sample Skills',
                'location': 'Office',
                'last_login': '',
                'password_last_changed': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'avatar_url': '',
                'status': 'active',
                'productivity': '78'
            }

            append_csv(USERS_CSV, user_row, ['id','username','password_hash','full_name','role','created_at','is_active'])
            append_csv(EMP_CSV, employee_row, EMP_FIELDNAMES)
            existing_users.append(user_row)
            existing_employees.append(employee_row)
            print(f"Created sample user: {sample['username']}")
        elif reset_passwords:
            try:
                stored = next((u for u in existing_users if (u.get('username') == sample['username'])), None)
                if stored and stored.get('id'):
                    update_by_id(
                        USERS_CSV,
                        stored.get('id'),
                        {
                            'password_hash': generate_password_hash(sample['password']),
                            'is_active': 'true'
                        },
                        ['id','username','password_hash','full_name','role','created_at','is_active']
                    )
                    print(f"Reset sample password: {sample['username']}")
            except Exception as exc:
                print(f"Reset sample password error ({sample.get('username')}): {exc}")
    export_demo_credentials_file()

def read_csv(path):
    if _use_database(path):
        if DB_BACKEND == 'mysql':
            return _mysql_read_rows(path)
        if DB_BACKEND == 'mongodb':
            return _mongo_read_rows(path)
    if not os.path.exists(path):
        return []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def _sync_secondary_stores(path, rows, fieldnames=None):
    if path not in STORAGE_TABLE_MAP:
        return

    snapshot = rows or []
    table_name = STORAGE_TABLE_MAP.get(path)
    columns = _collect_fieldnames(snapshot, fieldnames) or MYSQL_DEFAULT_COLUMNS.get(table_name, [])

    if CSV_SHADOW_SYNC and (DB_BACKEND != 'csv' or not os.path.exists(path)):
        try:
            _write_csv_file(path, snapshot, columns)
        except Exception as exc:
            print(f"CSV shadow sync error for {path}: {exc}")

    if MIRROR_MYSQL and DB_BACKEND != 'mysql' and mysql is not None:
        try:
            if _mysql_bootstrap():
                _mysql_write_rows(path, snapshot, columns)
        except Exception as exc:
            print(f"MySQL mirror sync error for {path}: {exc}")

    if MIRROR_MONGODB and DB_BACKEND != 'mongodb' and MongoClient is not None:
        try:
            if _mongo_bootstrap():
                _mongo_write_rows(path, snapshot, columns)
        except Exception as exc:
            print(f"MongoDB mirror sync error for {path}: {exc}")


def sync_registered_storage_tables(paths=None):
    target_paths = [
        path for path in (paths or STORAGE_TABLE_MAP.keys())
        if path in STORAGE_TABLE_MAP
    ]
    for path in target_paths:
        rows = read_csv(path)
        default_fields = MYSQL_DEFAULT_COLUMNS.get(STORAGE_TABLE_MAP.get(path), [])
        _sync_secondary_stores(path, rows, _collect_fieldnames(rows, default_fields))

def write_csv(path, rows, fieldnames):
    if _use_database(path):
        if DB_BACKEND == 'mysql':
            _mysql_write_rows(path, rows, fieldnames)
        elif DB_BACKEND == 'mongodb':
            _mongo_write_rows(path, rows, fieldnames)
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    _sync_secondary_stores(path, rows, fieldnames)

def append_csv(path, row, fieldnames):
    if _use_database(path):
        if DB_BACKEND == 'mysql':
            _mysql_append_row(path, row, fieldnames)
        elif DB_BACKEND == 'mongodb':
            _mongo_append_row(path, row, fieldnames)
    else:
        exists = os.path.exists(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not exists or os.path.getsize(path) == 0:
                writer.writeheader()
            writer.writerow(row)
    _sync_secondary_stores(path, read_csv(path), fieldnames)

def find_by_id(path, id):
    rows = read_csv(path)
    for r in rows:
        if r.get("id") == id:
            return r
    return None

def merge_fieldnames(rows, preferred_fieldnames=None):
    names = []
    for name in preferred_fieldnames or []:
        if name and name not in names:
            names.append(name)
    for row in rows:
        for key in row.keys():
            if key and key not in names:
                names.append(key)
    return names

def update_by_id(path, id, updates, fieldnames=None):
    if _use_database(path) and DB_BACKEND == 'mongodb':
        updated = _mongo_update_by_id(path, id, updates)
        if updated:
            snapshot = read_csv(path)
            _sync_secondary_stores(path, snapshot, _collect_fieldnames(snapshot, fieldnames))
        return updated

    rows = read_csv(path)
    updated = False
    for r in rows:
        if r.get("id") == id:
            r.update(updates)
            updated = True
    if updated:
        write_csv(path, rows, merge_fieldnames(rows, fieldnames))
    return updated

def delete_by_id(path, id, fieldnames=None):
    if _use_database(path) and DB_BACKEND == 'mongodb':
        deleted = _mongo_delete_by_id(path, id)
        if deleted:
            snapshot = read_csv(path)
            _sync_secondary_stores(path, snapshot, _collect_fieldnames(snapshot, fieldnames))
        return deleted

    rows = read_csv(path)
    new = [r for r in rows if r.get("id") != id]
    if len(new) != len(rows):
        source_rows = new if new else rows
        write_csv(path, new, merge_fieldnames(source_rows, fieldnames))
        return True
    return False

def get_storage_targets_status():
    status = {
        'csv': True,
        'mongodb': False,
        'mysql': False,
        'warnings': [],
    }

    if MongoClient is not None:
        try:
            status['mongodb'] = bool(_mongo_bootstrap())
        except Exception as exc:
            status['warnings'].append(f"MongoDB sync unavailable: {exc}")
    else:
        status['warnings'].append('MongoDB client library is not installed.')

    if mysql is not None:
        try:
            status['mysql'] = bool(_mysql_bootstrap())
        except Exception as exc:
            status['warnings'].append(f"MySQL sync unavailable: {exc}")
        if not status['mysql']:
            status['warnings'].append(
                'MySQL sync is unavailable. Configure MYSQL_USER and MYSQL_PASSWORD for mirrored writes.'
            )
    else:
        status['warnings'].append('MySQL connector is not installed.')

    return status

def persist_workforce_profile(user_row, employee_row, *, sync_org=True):
    append_csv(USERS_CSV, user_row, USER_FIELDNAMES)
    append_csv(EMP_CSV, employee_row, EMP_FIELDNAMES)
    if sync_org:
        ensure_demo_org_integrity(force=True)
        sync_registered_storage_tables([
            USERS_CSV,
            EMP_CSV,
            TEAMS_CSV,
            PROJECTS_CSV,
            PROJECT_MEMBERS_CSV,
            TASKS_CSV,
            PAYMENTS_CSV,
            NOTIF_CSV,
        ])
    return get_storage_targets_status()

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

def platform_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(f"{TASKVISE_ADMIN_URL}/login")
        if session.get("role") != "platform_admin":
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated

def _looks_like_werkzeug_hash(value: str) -> bool:
    v = (value or "").strip()
    return ":" in v and "$" in v

def verify_password(stored_value, candidate_password: str) -> bool:
    """
    Accept either a werkzeug password hash or a legacy/plaintext password.
    This prevents "invalid for every login" when storage contains plaintext
    or slightly malformed hash strings (whitespace, etc.).
    """
    candidate = (candidate_password or "").strip()
    if not candidate:
        return False

    if stored_value is None:
        return False

    stored = str(stored_value).strip()
    if not stored:
        return False

    if _looks_like_werkzeug_hash(stored):
        return check_password_hash(stored, candidate)

    return stored == candidate

def get_role_title(role):
    role = normalize_role(role)
    role_titles = {
        'admin': 'Admin Credentials Generated!',
        'manager': 'Manager Credentials Generated!',
        'hr': 'HR Credentials Generated!',
        'teamlead': 'Team Lead Credentials Generated!',
        'employee': 'Employee Credentials Generated!'
    }
    return role_titles.get(role, 'Employee Credentials Generated!')

def get_role_description(role):
    role = normalize_role(role)
    role_descriptions = {
        'admin': 'Administrator account with full system access',
        'manager': 'Manager account with team management access',
        'hr': 'HR account with employee management access',
        'teamlead': 'Team Lead account with project team access',
        'employee': 'Employee account created successfully'
    }
    return role_descriptions.get(role, 'Employee account created successfully')

def get_role_access_description(role):
    role = normalize_role(role)
    access_descriptions = {
        'admin': 'Admin access includes all system privileges',
        'manager': 'Manager access includes team management features',
        'hr': 'HR access includes employee management and HR features',
        'teamlead': 'Team Lead access includes project team management',
        'employee': 'Employee can access personal dashboard and tasks'
    }
    return access_descriptions.get(role, 'Employee can access personal dashboard and tasks')

def _normalize_text(value):
    return str(value or '').strip().lower()

def normalize_role(value):
    aliases = {
        'lead': 'teamlead',
        'team lead': 'teamlead',
        'team-lead': 'teamlead',
        'administrator': 'admin',
        'platform admin': 'platform_admin',
        'platform-admin': 'platform_admin',
        'founder': 'platform_admin',
    }
    raw = _normalize_text(value)
    return aliases.get(raw, raw or 'employee')

def _truthy(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return _normalize_text(value) in {'1', 'true', 'yes', 'on'}

def resolve_employee_candidate_ids(user_id=None, username=None, full_name=None):
    employees = read_csv(EMP_CSV)
    ids = set()
    uid = str(user_id or '').strip()
    username_norm = _normalize_text(username)
    full_name_norm = _normalize_text(full_name)

    if uid:
        ids.add(uid)

    for emp in employees:
        emp_id = str(emp.get('id') or '').strip()
        if not emp_id:
            continue

        if uid and emp_id == uid:
            ids.add(emp_id)

        if username_norm and _normalize_text(emp.get('email')) == username_norm:
            ids.add(emp_id)

        if full_name_norm and _normalize_text(emp.get('name')) == full_name_norm:
            ids.add(emp_id)

    return ids, employees

def task_matches_employee(task, candidate_ids, username=None, full_name=None):
    ids = {str(v).strip() for v in (candidate_ids or set()) if str(v).strip()}
    assignee_id = str(task.get('assignee_id') or task.get('assignedTo') or '').strip()
    if assignee_id and assignee_id in ids:
        return True

    assignee_name = _normalize_text(task.get('assignee_name') or task.get('assigned_to_name'))
    full_name_norm = _normalize_text(full_name)
    username_norm = _normalize_text(username)
    username_local = username_norm.split('@')[0] if username_norm else ''

    if assignee_name and (
        assignee_name == full_name_norm or
        assignee_name == username_norm or
        (username_local and assignee_name == username_local)
    ):
        return True
    return False

def normalize_task_status(value):
    raw = _normalize_text(value)
    aliases = {
        'in progress': 'in-progress',
        'in_progress': 'in-progress',
        'todo': 'pending',
        'to do': 'pending',
        'done': 'completed',
    }
    return aliases.get(raw, raw or 'pending')

def normalize_project_status(value):
    raw = _normalize_text(value)
    aliases = {
        'on hold': 'on-hold',
        'on_hold': 'on-hold',
        'in progress': 'active',
        'in_progress': 'active',
    }
    return aliases.get(raw, raw or 'planning')

def get_user_settings_record(user_id):
    defaults = {
        'email_notifications': 'true',
        'push_notifications': 'false',
        'task_reminders': 'true',
        'deadline_alerts': 'true',
        'theme': 'system',
        'language': 'en',
        'timezone': 'UTC',
    }
    rows = read_csv(SETTINGS_CSV)
    existing = next((r for r in rows if str(r.get('user_id', '')) == str(user_id)), None)
    if existing:
        record = existing.copy()
    else:
        record = {'id': str(uuid.uuid4()), 'user_id': str(user_id)}

    for key, value in defaults.items():
        record[key] = str(record.get(key, value) or value)
    record['updated_at'] = str(record.get('updated_at') or datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return record, rows

def save_user_settings_record(user_id, incoming):
    record, rows = get_user_settings_record(user_id)
    for key in ['email_notifications', 'push_notifications', 'task_reminders', 'deadline_alerts', 'theme', 'language', 'timezone']:
        if key in incoming:
            record[key] = str(incoming.get(key) or record.get(key) or '')
    record['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    replaced = False
    for idx, row in enumerate(rows):
        if str(row.get('user_id', '')) == str(user_id):
            rows[idx] = record
            replaced = True
            break
    if not replaced:
        rows.append(record)

    write_csv(SETTINGS_CSV, rows, SETTINGS_FIELDNAMES)
    return record

def _safe_int(value, default=0):
    try:
        return int(float(str(value or default).strip()))
    except Exception:
        return default

def infer_primary_company_name(employees=None, projects=None):
    counter = Counter()
    for row in employees or read_csv(EMP_CSV):
        company = str(row.get('company') or '').strip()
        if company:
            counter[company] += 1
    for row in projects or read_csv(PROJECTS_CSV):
        company = str(row.get('company') or '').strip()
        if company:
            counter[company] += 1
    if counter:
        return counter.most_common(1)[0][0]
    return DEFAULT_COMPANY_NAME

def get_default_company_name():
    rows = read_csv(SETTINGS_CSV)
    existing = next((r for r in rows if str(r.get('user_id', '')) == SYSTEM_SETTINGS_USER_ID), None)
    if existing and str(existing.get('company_name') or '').strip():
        return str(existing.get('company_name')).strip()
    return infer_primary_company_name()

def get_admin_system_settings_record():
    rows = read_csv(SETTINGS_CSV)
    existing = next((r for r in rows if str(r.get('user_id', '')) == SYSTEM_SETTINGS_USER_ID), None)
    defaults = {
        'company_name': infer_primary_company_name(),
        'theme': 'executive',
        'language': 'en',
        'timezone': 'Asia/Kolkata',
        'date_format': 'dd/mm/yyyy',
        'session_timeout': '30',
        'password_policy': 'medium',
        'notify_task_assignments': 'true',
        'notify_project_updates': 'true',
        'notify_system_alerts': 'true',
        'desktop_notifications': 'true',
        'sound_alerts': 'false',
        'auto_backup': 'weekly',
        'data_retention': '12',
        'api_access': 'true',
        'webhook_url': '',
    }
    record = existing.copy() if existing else {'id': str(uuid.uuid4()), 'user_id': SYSTEM_SETTINGS_USER_ID}
    for key, value in defaults.items():
        record[key] = str(record.get(key, value) or value)
    record['updated_at'] = str(record.get('updated_at') or datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return record, rows

def save_admin_system_settings_record(incoming):
    record, rows = get_admin_system_settings_record()
    allowed_fields = {
        'company_name', 'theme', 'language', 'timezone', 'date_format', 'session_timeout',
        'password_policy', 'notify_task_assignments', 'notify_project_updates', 'notify_system_alerts',
        'desktop_notifications', 'sound_alerts', 'auto_backup', 'data_retention', 'api_access',
        'webhook_url'
    }
    for key in allowed_fields:
        if key not in incoming:
            continue
        value = incoming.get(key)
        if key in {'notify_task_assignments', 'notify_project_updates', 'notify_system_alerts', 'desktop_notifications', 'sound_alerts', 'api_access'}:
            record[key] = 'true' if _truthy(value) else 'false'
        else:
            record[key] = str(value or '').strip()
    if not record.get('company_name'):
        record['company_name'] = infer_primary_company_name()
    record['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    replaced = False
    for idx, row in enumerate(rows):
        if str(row.get('user_id', '')) == SYSTEM_SETTINGS_USER_ID:
            rows[idx] = record
            replaced = True
            break
    if not replaced:
        rows.append(record)

    write_csv(SETTINGS_CSV, rows, SETTINGS_FIELDNAMES)
    return record

def get_role_default_password(role):
    normalized_role = normalize_role(role)
    return ROLE_DEFAULT_PASSWORDS.get(normalized_role, ROLE_DEFAULT_PASSWORDS['employee'])

def build_demo_credentials_payload(users=None):
    rows = users if users is not None else read_csv(USERS_CSV)
    employee_lookup = _build_employee_index(read_csv(EMP_CSV))
    grouped = []
    role_order = ['platform_admin', 'admin', 'manager', 'hr', 'teamlead', 'employee']
    for role in role_order:
        members = []
        for user in rows:
            user_role = normalize_role(user.get('role'))
            if user_role != role:
                continue
            employee = employee_lookup.get(str(user.get('id', '')).strip(), {})
            members.append({
                'id': user.get('id', ''),
                'username': user.get('username', ''),
                'full_name': user.get('full_name', ''),
                'role': user_role,
                'password': get_role_default_password(role),
                'team_name': employee.get('team_name', user.get('team_name', '')),
                'manager_id': employee.get('manager_id', user.get('manager_id', '')),
                'teamlead_id': employee.get('teamlead_id', user.get('teamlead_id', '')),
            })
        if members:
            grouped.append({
                'role': role,
                'password': get_role_default_password(role),
                'users': sorted(
                    members,
                    key=lambda item: (
                        _prefixed_id_sort_key(item.get('id', ''), WORKFORCE_ID_PREFIX),
                        str(item.get('username', '')).lower(),
                    ),
                ),
            })
    return grouped

def export_demo_credentials_file(path=CREDENTIALS_EXPORT_TXT, users=None):
    role_labels = {
        'platform_admin': 'TaskVise Founder',
        'admin': 'Admin',
        'manager': 'Manager',
        'hr': 'HR',
        'teamlead': 'Team Lead',
        'employee': 'Employee',
    }
    grouped = build_demo_credentials_payload(users=users)
    lines = [
        'TaskVise Login Credentials',
        f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        '',
        'All accounts below are grouped by role with the current default login password for that role.',
        '',
    ]
    if not grouped:
        lines.append('No users found.')
    else:
        for group in grouped:
            role = str(group.get('role') or 'employee').strip().lower()
            lines.append(f"[{role_labels.get(role, role.title())}]")
            lines.append(f"Default password: {group.get('password', '')}")
            for user in group.get('users', []):
                user_id = str(user.get('id') or '').strip()
                full_name = str(user.get('full_name') or 'Unknown User').strip()
                username = str(user.get('username') or '').strip()
                team_name = str(user.get('team_name') or '').strip()
                manager_id = str(user.get('manager_id') or '').strip()
                teamlead_id = str(user.get('teamlead_id') or '').strip()
                extra_parts = []
                if team_name:
                    extra_parts.append(f"Team: {team_name}")
                if manager_id:
                    extra_parts.append(f"Manager: {manager_id}")
                if teamlead_id:
                    extra_parts.append(f"Lead: {teamlead_id}")
                extra_text = f" | {' | '.join(extra_parts)}" if extra_parts else ''
                if user_id:
                    lines.append(f"- {user_id} | {full_name} | {username}{extra_text}")
                else:
                    lines.append(f"- {full_name} | {username}{extra_text}")
            lines.append('')

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines).strip() + '\n')
    return path

def sync_demo_role_passwords():
    users = read_csv(USERS_CSV)
    if not users:
        export_demo_credentials_file(users=[])
        return 0

    changed = 0
    for user in users:
        role = str(user.get('role') or 'employee').strip().lower()
        desired_password = get_role_default_password(role)
        stored_value = user.get('password_hash') or user.get('password') or ''
        if verify_password(stored_value, desired_password):
            continue
        user['password_hash'] = generate_password_hash(desired_password)
        changed += 1

    if changed:
        write_csv(USERS_CSV, users, merge_fieldnames(users, USER_FIELDNAMES))
    export_demo_credentials_file(users=users)
    return changed

def get_employee_data(user_id):
    """Get comprehensive employee data for dashboard display"""
    username = session.get('username')
    full_name = session.get('full_name')

    candidate_ids, employees = resolve_employee_candidate_ids(user_id, username, full_name)

    employee = next((e for e in employees if str(e.get('id', '')) == str(user_id)), None)
    if not employee and username:
        employee = next((e for e in employees if _normalize_text(e.get('email')) == _normalize_text(username)), None)
    if not employee and full_name:
        employee = next((e for e in employees if _normalize_text(e.get('name')) == _normalize_text(full_name)), None)

    if not employee and candidate_ids:
        first_id = next(iter(candidate_ids))
        employee = next((e for e in employees if str(e.get('id', '')) == str(first_id)), None)

    if not employee:
        return {
            'profile': {
                'id': user_id,
                'name': session.get('full_name', 'Unknown'),
                'email': session.get('username', ''),
                'position': 'Unknown',
                'department': 'Unknown',
                'company': get_default_company_name(),
                'join_date': '',
                'phone': '',
                'skills': '',
                'location': '',
                'avatar_url': '',
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

    all_tasks = read_csv(TASKS_CSV)
    employee_tasks = [
        task for task in all_tasks
        if task_matches_employee(task, candidate_ids, username=username, full_name=full_name)
    ]

    normalized_tasks = []
    for task in employee_tasks:
        row = dict(task)
        row['status'] = normalize_task_status(row.get('status'))
        row['priority'] = str(row.get('priority') or 'medium').strip().lower()
        row['due_date'] = str(row.get('due_date') or row.get('dueDate') or '')[:10]
        row['created_at'] = str(row.get('created_at') or '')[:19]
        normalized_tasks.append(row)
    employee_tasks = normalized_tasks

    total_tasks = len(employee_tasks)
    completed_tasks = len([task for task in employee_tasks if task.get('status') == 'completed'])
    in_progress_tasks = len([task for task in employee_tasks if task.get('status') == 'in-progress'])

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

    all_projects = read_csv(PROJECTS_CSV)
    member_rows = read_csv(PROJECT_MEMBERS_CSV)
    member_project_ids = {m.get('project_id') for m in member_rows if m.get('employee_id') in candidate_ids}
    task_project_ids = {
        t.get('project_id')
        for t in employee_tasks
        if t.get('project_id')
    }
    visible_project_ids = member_project_ids.union(task_project_ids)
    employee_projects = [p for p in all_projects if p.get('owner_id') in candidate_ids or p.get('id') in visible_project_ids]
    active_projects = len([p for p in employee_projects if p.get('status') in ['active', 'planning']])

    if total_tasks == 0:
        workload = 'light'
    elif total_tasks <= 3:
        workload = 'balanced'
    else:
        workload = 'heavy'

    user = find_by_id(USERS_CSV, user_id)
    user_role = normalize_role(user.get('role', 'employee') if user else 'employee')

    profile_data = {
        'id': employee.get('id', user_id),
        'name': employee.get('name', 'Unknown'),
        'fullName': employee.get('name', 'Unknown'),
        'email': employee.get('email', ''),
        'position': employee.get('position', 'Unknown'),
        'department': employee.get('department', 'Unknown'),
        'company': employee.get('company', get_default_company_name()),
        'join_date': employee.get('join_date', ''),
        'phone': employee.get('phone', ''),
        'skills': employee.get('skills', ''),
        'location': employee.get('location', ''),
        'avatar_url': employee.get('avatar_url', ''),
        'designation': employee.get('position', ''),
        'role': user_role,
        'team_id': employee.get('team_id', ''),
        'team_name': employee.get('team_name', ''),
        'manager_id': employee.get('manager_id', ''),
        'teamlead_id': employee.get('teamlead_id', ''),
    }

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


def _prepare_dashboard_profile(profile):
    prepared = dict(profile or {})
    skills = prepared.get('skills')
    if isinstance(skills, str):
        prepared['skills'] = [skill.strip() for skill in skills.split(',') if skill.strip()]
    elif isinstance(skills, (list, tuple, set)):
        prepared['skills'] = [str(skill).strip() for skill in skills if str(skill).strip()]
    elif skills:
        prepared['skills'] = [str(skills).strip()]
    else:
        prepared['skills'] = []
    return prepared


def get_employee_dashboard_data(user_id):
    employee_data = get_employee_data(user_id)
    employee_data['profile'] = _prepare_dashboard_profile(employee_data.get('profile'))
    return employee_data

def get_manager_data(user_id):
    """Get comprehensive data for manager dashboard"""
    ensure_demo_org_integrity()
    ensure_projects_team_members()
    all_employees = _sort_rows_by_id(read_csv(EMP_CSV), WORKFORCE_ID_PREFIX)
    all_users = read_csv(USERS_CSV)
    all_tasks = read_csv(TASKS_CSV)
    all_projects = read_csv(PROJECTS_CSV)
    member_rows = read_csv(PROJECT_MEMBERS_CSV)
    teams = read_csv(TEAMS_CSV)
    payments = read_csv(PAYMENTS_CSV)
    normalized_user_id = str(user_id or '').strip()
    employee_lookup = _build_employee_index(all_employees)
    role_map = {
        str(user.get('id', '')).strip(): normalize_role(user.get('role', 'employee'))
        for user in all_users
        if str(user.get('id', '')).strip()
    }
    actor_row = employee_lookup.get(normalized_user_id, {})
    actor_role = role_map.get(normalized_user_id, normalize_role(actor_row.get('role', 'employee')))
    actor_team = get_team_record_for_user(normalized_user_id, teams)

    visible_employee_ids = set()
    visible_project_ids = set()
    visible_payments = []

    if actor_role == 'hr':
        visible_employee_ids = {
            str(emp.get('id', '')).strip()
            for emp in all_employees
            if str(emp.get('id', '')).strip() and role_map.get(str(emp.get('id', '')).strip(), 'employee') not in {'admin', 'platform_admin'}
        }
        visible_project_ids = {str(project.get('id', '')).strip() for project in all_projects if str(project.get('id', '')).strip()}
        visible_payments = payments
    elif actor_role == 'manager' and actor_team:
        visible_employee_ids = set(get_team_member_ids(actor_team, include_teamlead=True))
        visible_project_ids = {
            str(project.get('id', '')).strip()
            for project in all_projects
            if str(project.get('team_id', '')).strip() == str(actor_team.get('id', '')).strip()
        }
        visible_payments = [row for row in payments if str(row.get('team_id', '')).strip() == str(actor_team.get('id', '')).strip()]
    elif actor_role == 'teamlead' and actor_team:
        visible_employee_ids = set(get_team_member_ids(actor_team))
        visible_project_ids = {
            str(project.get('id', '')).strip()
            for project in all_projects
            if str(project.get('team_id', '')).strip() == str(actor_team.get('id', '')).strip()
        }
        visible_payments = [row for row in payments if str(row.get('team_id', '')).strip() == str(actor_team.get('id', '')).strip()]
    else:
        visible_employee_ids = set()
        visible_project_ids = set()
        visible_payments = []

    filtered_employees = []
    for emp in all_employees:
        emp_id = str(emp.get('id', '')).strip()
        if not emp_id or emp_id == normalized_user_id:
            continue
        role = role_map.get(emp_id, 'employee')
        if actor_role != 'hr' and emp_id not in visible_employee_ids:
            continue
        if actor_role == 'hr' and role in {'admin', 'platform_admin'}:
            continue
        emp_with_role = emp.copy()
        emp_with_role['role'] = role
        emp_with_role['fullName'] = emp.get('name', 'Unknown')
        emp_with_role['company'] = str(emp.get('company') or get_default_company_name()).strip()
        productivity = _safe_int(emp.get('productivity', ''), -1)
        if productivity < 0:
            productivity = calculate_employee_productivity(emp_id)
        emp_with_role['productivity'] = str(max(0, min(100, productivity)))
        filtered_employees.append(emp_with_role)
    filtered_employees = _sort_rows_by_id(filtered_employees, WORKFORCE_ID_PREFIX)

    visible_employee_index = {
        str(employee.get('id', '')).strip(): employee
        for employee in filtered_employees
        if str(employee.get('id', '')).strip()
    }

    projects = []
    for project in all_projects:
        project_id = str(project.get('id', '')).strip()
        if actor_role != 'hr' and project_id not in visible_project_ids:
            continue
        project_tasks = [
            task for task in all_tasks
            if str(task.get('project_id', '')).strip() == project_id
        ]
        completed_tasks = len([
            task for task in project_tasks
            if normalize_task_status(task.get('status')) == 'completed'
        ])
        estimated_hours = sum(_safe_int(task.get('estimated_hours', task.get('estimatedHours', 0)), 0) for task in project_tasks)
        actual_hours = sum(_safe_int(task.get('actual_hours', task.get('actualHours', 0)), 0) for task in project_tasks)
        owner_id = str(project.get('owner_id', '')).strip()
        owner = employee_lookup.get(owner_id, {})
        project_row = dict(project)
        team_member_ids = _normalize_list_strings(_parse_team_members(project, member_rows))
        project_row['team_members'] = ','.join(team_member_ids)
        project_row['team_members_count'] = len(team_member_ids)
        project_row['team_member_details'] = [
            {
                'id': member_id,
                'name': employee_lookup.get(member_id, {}).get('name', member_id),
                'position': employee_lookup.get(member_id, {}).get('position', ''),
                'department': employee_lookup.get(member_id, {}).get('department', ''),
            }
            for member_id in team_member_ids
        ]
        project_row['deadline'] = str(project.get('end_date', project.get('deadline', '')) or '')[:10]
        project_row['status'] = normalize_project_status(project.get('status', 'planning'))
        project_row['company'] = str(project.get('company') or get_default_company_name()).strip()
        project_row['progress'] = str(max(0, min(100, _safe_int(project.get('progress', 0), 0))))
        project_row['completed_tasks'] = completed_tasks
        project_row['total_tasks'] = len(project_tasks)
        project_row['estimated_hours'] = estimated_hours
        project_row['actual_hours'] = actual_hours
        project_row['owner_name'] = owner.get('name', project_row.get('owner_name', ''))
        projects.append(project_row)
    projects = sorted(projects, key=lambda item: _prefixed_id_sort_key(item.get('id', ''), PROJECT_ID_PREFIX))

    visible_project_ids = {str(project.get('id', '')).strip() for project in projects if str(project.get('id', '')).strip()}

    tasks = []
    for task in all_tasks:
        task_assignee_id = str(task.get('assignee_id', '')).strip()
        task_project_id = str(task.get('project_id', '')).strip()
        include_task = actor_role == 'hr' or task_project_id in visible_project_ids or task_assignee_id in visible_employee_ids
        if not include_task:
            continue
        task_row = dict(task)
        employee = employee_lookup.get(task_assignee_id, {})
        project = next((row for row in projects if str(row.get('id', '')).strip() == task_project_id), {})
        task_row['status'] = normalize_task_status(task_row.get('status'))
        task_row['priority'] = str(task_row.get('priority') or 'medium').strip().lower()
        task_row['due_date'] = str(task_row.get('due_date') or task_row.get('dueDate') or '')[:10]
        task_row['dueDate'] = task_row['due_date']
        task_row['estimated_hours'] = str(task_row.get('estimated_hours', task_row.get('estimatedHours', 0)) or 0)
        task_row['estimatedHours'] = task_row['estimated_hours']
        task_row['actual_hours'] = str(task_row.get('actual_hours', task_row.get('actualHours', 0)) or 0)
        task_row['actualHours'] = task_row['actual_hours']
        task_row['progress'] = str(max(0, min(100, _safe_int(task_row.get('progress', 0), 0))))
        task_row['assignee_name'] = task_row.get('assignee_name') or employee.get('name', '')
        task_row['project_name'] = project.get('name', task_row.get('project_name', ''))
        tasks.append(task_row)
    tasks = sorted(tasks, key=lambda item: _prefixed_id_sort_key(item.get('id', ''), TASK_ID_PREFIX))

    tasks_by_employee = {}
    for task in tasks:
        assignee_id = str(task.get('assignee_id', '')).strip()
        tasks_by_employee.setdefault(assignee_id, []).append(task)

    on_leave_ids = set()
    today = datetime.now().date()
    for leave in read_csv(LEAVE_CSV):
        if normalize_leave_status(leave.get('status')) != 'approved':
            continue
        employee_id = str(leave.get('employee_id', '')).strip()
        if employee_id not in visible_employee_index:
            continue
        try:
            start_date = datetime.strptime(str(leave.get('start_date') or '')[:10], '%Y-%m-%d').date()
            end_date = datetime.strptime(str(leave.get('end_date') or '')[:10], '%Y-%m-%d').date()
        except Exception:
            continue
        if start_date <= today <= end_date:
            on_leave_ids.add(employee_id)

    for employee in filtered_employees:
        employee_id = str(employee.get('id', '')).strip()
        employee_tasks = tasks_by_employee.get(employee_id, [])
        completed_tasks = len([
            task for task in employee_tasks
            if normalize_task_status(task.get('status')) == 'completed'
        ])
        total_tasks = len(employee_tasks)
        completion_rate = int(round((completed_tasks / max(total_tasks, 1)) * 100)) if total_tasks else 0
        productivity = max(0, min(100, _safe_int(employee.get('productivity', completion_rate), completion_rate)))
        skills_list = split_skills(employee.get('skills'))
        badge_key, badge_label = classify_employee_badge(productivity, completion_rate, len(skills_list), total_tasks)
        employee['productivity'] = str(productivity)
        employee['totalTasks'] = total_tasks
        employee['completedTasks'] = completed_tasks
        employee['completionRate'] = completion_rate
        employee['skills_list'] = skills_list
        employee['skillsCount'] = len(skills_list)
        employee['performance_badge_key'] = badge_key
        employee['performance_badge_label'] = badge_label
        employee['on_leave'] = 'true' if employee_id in on_leave_ids else 'false'
        employee['initials'] = employee.get('initials') or get_employee_initials(employee.get('name'))

    notifications = [
        {
            'id': row.get('id', ''),
            'title': row.get('title', 'Notification'),
            'message': row.get('message', ''),
            'type': str(row.get('type') or 'system').lower(),
            'is_read': _truthy(row.get('is_read')),
            'created_at': row.get('created_at', ''),
        }
        for row in read_csv(NOTIF_CSV)
        if str(row.get('user_id', '')).strip() == str(user_id).strip()
    ]
    notifications.sort(key=lambda row: row.get('created_at', ''), reverse=True)

    stats = {
        'totalEmployees': len(filtered_employees),
        'activeEmployees': len([e for e in filtered_employees if str(e.get('last_login') or '').strip()]),
        'totalProjects': len(projects),
        'activeProjects': len([p for p in projects if str(p.get('status') or '').lower() in ['active', 'planning']]),
        'totalTasks': len(tasks),
        'completedTasks': len([t for t in tasks if normalize_task_status(t.get('status')) == 'completed']),
        'overdueTasks': calculate_overdue_tasks(tasks),
        'totalHours': calculate_total_hours(tasks),
        'productivity': calculate_team_productivity(filtered_employees, tasks),
        'unreadNotifications': len([n for n in notifications if not n.get('is_read')]),
        'teamName': (actor_team or {}).get('name', 'Workforce Command'),
        'teamTagline': (actor_team or {}).get('tagline', ''),
        'teamFocus': (actor_team or {}).get('focus_area', ''),
        'managerName': (actor_team or {}).get('manager_name', ''),
        'teamLeadName': (actor_team or {}).get('teamlead_name', ''),
        'teamSize': len(get_team_member_ids(actor_team, include_teamlead=True)),
        'teamsCount': len(teams),
        'monthlyPayroll': sum(_safe_int(row.get('base_salary', 0), 0) + _safe_int(row.get('bonus', 0), 0) for row in visible_payments),
        'teamSummaries': [
            {
                'id': team.get('id', ''),
                'name': team.get('name', ''),
                'department': team.get('department', ''),
                'manager_id': team.get('manager_id', ''),
                'manager_name': team.get('manager_name', ''),
                'teamlead_id': team.get('teamlead_id', ''),
                'teamlead_name': team.get('teamlead_name', ''),
                'member_count': len(get_team_member_ids(team)),
                'tagline': team.get('tagline', ''),
                'focus_area': team.get('focus_area', ''),
            }
            for team in teams
        ],
    }

    return {
        'employees': filtered_employees,
        'tasks': tasks,
        'projects': projects,
        'stats': stats,
        'notifications': notifications,
        'payments': visible_payments,
        'teams': teams if actor_role == 'hr' else ([actor_team] if actor_team else []),
    }


def get_admin_data(user_id):
    """Get comprehensive data for admin dashboard with manager-style display"""
    all_employees = read_csv(EMP_CSV)
    all_tasks = read_csv(TASKS_CSV)
    all_projects = read_csv(PROJECTS_CSV)

    stats = {
        'totalEmployees': len(all_employees),
        'activeEmployees': len([e for e in all_employees if e.get('last_login')]),
        'totalProjects': len(all_projects),
        'activeProjects': len([p for p in all_projects if p.get('status') in ['active', 'planning']]),
        'totalTasks': len(all_tasks),
        'completedTasks': len([t for t in all_tasks if t.get('status') == 'completed']),
        'overdueTasks': calculate_overdue_tasks(all_tasks),
        'totalHours': calculate_total_hours(all_tasks),
        'productivity': calculate_team_productivity(all_employees, all_tasks),
        'unreadNotifications': 0
    }

    return {
        'employees': all_employees,
        'tasks': all_tasks,
        'projects': all_projects,
        'stats': stats,
        'notifications': []
    }


@app.route('/api/manager/stats')
@login_required
def api_manager_stats():
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify({})
    user_id = session.get('user_id')
    data = get_manager_data(user_id)
    return jsonify(data.get('stats', {}))

@app.route('/api/teamlead/stats')
@login_required
def api_teamlead_stats():
    if session.get('role') != 'teamlead':
        return jsonify({'error': 'forbidden'}), 403
    user_id = session.get('user_id')
    data = get_manager_data(user_id)
    return jsonify(data.get('stats', {}))

def calculate_overdue_tasks(tasks):
    """Calculate number of overdue tasks"""
    today = datetime.now().date()
    overdue = 0
    for task in tasks:
        status = normalize_task_status(task.get('status'))
        due_date_text = str(task.get('due_date') or task.get('dueDate') or '').strip()[:10]
        if status not in ['completed', 'cancelled'] and due_date_text:
            try:
                due_date = datetime.strptime(due_date_text, '%Y-%m-%d').date()
                if due_date < today:
                    overdue += 1
            except ValueError:
                continue
    return overdue

def calculate_total_hours(tasks):
    """Calculate total hours from task actual/estimated effort."""
    total = 0
    for task in tasks or []:
        total += _task_hour_value(task)
    return total

def calculate_team_productivity(employees, tasks):
    """Calculate team productivity percentage"""
    if not employees:
        return 0

    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if normalize_task_status(t.get('status')) == 'completed'])

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
    for e in employees or []:
        dt = _parse_date_any(e.get('join_date',''))
        if dt:
            items.append({
                'message': f"Employee '{e.get('name','Unknown')}' joined",
                'time': dt.strftime('%Y-%m-%d %H:%M') if dt.time() != datetime.min.time() else dt.strftime('%Y-%m-%d'),
                'icon': 'fas fa-user-plus'
            })
    for p in projects or []:
        dt = _parse_date_any(p.get('start_date',''))
        if dt:
            items.append({
                'message': f"Project '{p.get('name','Unnamed')}' started",
                'time': dt.strftime('%Y-%m-%d'),
                'icon': 'fas fa-project-diagram'
            })
    for t in tasks or []:
        dt = _parse_date_any(t.get('created_at',''))
        if dt:
            items.append({
                'message': f"Task '{t.get('title','Untitled')}' created",
                'time': dt.strftime('%Y-%m-%d %H:%M') if dt.time() != datetime.min.time() else dt.strftime('%Y-%m-%d'),
                'icon': 'fas fa-tasks'
            })
    def _dt_of(item):
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

def _normalize_list_strings(values):
    seen = set()
    ordered = []
    for value in values or []:
        item = str(value or '').strip()
        if not item or item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered

def _build_role_map(users=None):
    rows = users if users is not None else read_csv(USERS_CSV)
    return {
        str(row.get('id', '')).strip(): normalize_role(row.get('role', 'employee'))
        for row in rows
        if str(row.get('id', '')).strip()
    }

def _build_employee_index(employees=None):
    rows = employees if employees is not None else read_csv(EMP_CSV)
    return {
        str(row.get('id', '')).strip(): row
        for row in rows
        if str(row.get('id', '')).strip()
    }

def _parse_team_members(project_row, member_rows=None):
    members = _normalize_list_strings(str(project_row.get('team_members', '') or '').split(','))
    if members:
        return members
    project_id = str(project_row.get('id', '')).strip()
    if not project_id:
        return []
    related = [
        row.get('employee_id')
        for row in (member_rows or read_csv(PROJECT_MEMBERS_CSV))
        if str(row.get('project_id', '')).strip() == project_id
    ]
    return _normalize_list_strings(related)

def _next_prefixed_id(prefix, rows, width):
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$", re.IGNORECASE)
    highest = 0
    for row in rows or []:
        match = pattern.match(str(row.get('id', '')).strip())
        if match:
            highest = max(highest, int(match.group(1)))
    if highest:
        return f"{prefix}{highest + 1:0{width}d}"
    return f"{prefix}{uuid.uuid4().hex[:width].upper()}"

def _prefixed_id_sort_key(value, prefix=None):
    text = str(value or '').strip()
    if not text:
        return (2, float('inf'), '')
    if prefix:
        match = re.match(rf"^{re.escape(prefix)}(\d+)$", text, re.IGNORECASE)
        if match:
            return (0, int(match.group(1)), text.lower())
    suffix_match = re.search(r'(\d+)$', text)
    if suffix_match:
        return (1, int(suffix_match.group(1)), text.lower())
    return (2, float('inf'), text.lower())

def _sort_rows_by_id(rows, prefix=None, secondary_key='name'):
    return sorted(
        rows or [],
        key=lambda row: (
            _prefixed_id_sort_key((row or {}).get('id', ''), prefix),
            str((row or {}).get(secondary_key, '')).lower(),
        )
    )


def _team_blueprint_rows(employees=None):
    employee_lookup = _build_employee_index(employees)
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rows = []
    for blueprint in TEAM_BLUEPRINTS:
        manager = employee_lookup.get(blueprint['manager_id'], {})
        lead = employee_lookup.get(blueprint['teamlead_id'], {})
        rows.append({
            'id': blueprint['id'],
            'name': blueprint['name'],
            'department': blueprint['department'],
            'manager_id': blueprint['manager_id'],
            'manager_name': manager.get('name', blueprint['manager_id']),
            'teamlead_id': blueprint['teamlead_id'],
            'teamlead_name': lead.get('name', blueprint['teamlead_id']),
            'member_ids': ','.join(_normalize_list_strings(blueprint.get('member_ids', []))),
            'tagline': blueprint.get('tagline', ''),
            'focus_area': blueprint.get('focus_area', ''),
            'created_at': created_at,
            'updated_at': created_at,
        })
    return rows


def _build_team_indexes(team_rows=None):
    rows = team_rows if team_rows is not None else read_csv(TEAMS_CSV)
    by_id = {}
    by_member = {}
    for row in rows or []:
        team_id = str(row.get('id', '')).strip()
        if not team_id:
            continue
        by_id[team_id] = row
        manager_id = str(row.get('manager_id', '')).strip()
        teamlead_id = str(row.get('teamlead_id', '')).strip()
        member_ids = _normalize_list_strings(str(row.get('member_ids', '')).split(','))
        for employee_id in [manager_id, teamlead_id, *member_ids]:
            normalized_id = str(employee_id or '').strip()
            if normalized_id:
                by_member[normalized_id] = row
    return by_id, by_member


def get_team_record_for_user(user_id, team_rows=None):
    _by_id, by_member = _build_team_indexes(team_rows)
    return by_member.get(str(user_id or '').strip())


def get_team_member_ids(team_row, include_manager=False, include_teamlead=False):
    if not team_row:
        return []
    members = _normalize_list_strings(str(team_row.get('member_ids', '')).split(','))
    if include_teamlead and str(team_row.get('teamlead_id', '')).strip():
        members = [str(team_row.get('teamlead_id')).strip(), *members]
    if include_manager and str(team_row.get('manager_id', '')).strip():
        members = [str(team_row.get('manager_id')).strip(), *members]
    return _normalize_list_strings(members)


def _team_rotation_members(team_row):
    if not team_row:
        return []
    return _normalize_list_strings([
        str(team_row.get('teamlead_id', '')).strip(),
        *str(team_row.get('member_ids', '')).split(','),
    ])


def _project_team_assignment(project_row, team_rows):
    project_id = str(project_row.get('id', '')).strip()
    owner_id = str(project_row.get('owner_id', '')).strip()
    team = get_team_record_for_user(owner_id, team_rows)
    if team:
        return team
    sorted_teams = sorted(team_rows or [], key=lambda row: row.get('id', ''))
    if not sorted_teams:
        return None
    numeric = _prefixed_id_sort_key(project_id, PROJECT_ID_PREFIX)[1]
    if numeric == float('inf'):
        numeric = 1
    return sorted_teams[(int(numeric) - 1) % len(sorted_teams)]


def _project_member_selection(project_row, team_row):
    rotation = _team_rotation_members(team_row)
    if not rotation:
        return []
    owner_id = str(project_row.get('owner_id', '')).strip()
    if owner_id and owner_id in rotation:
        seed = rotation.index(owner_id)
    else:
        project_sort = _prefixed_id_sort_key(project_row.get('id', ''), PROJECT_ID_PREFIX)[1]
        seed = 0 if project_sort == float('inf') else int(project_sort) % len(rotation)
        owner_id = rotation[seed]
    ordered = rotation[seed:] + rotation[:seed]
    selected = [owner_id]
    for employee_id in ordered:
        if employee_id not in selected:
            selected.append(employee_id)
        if len(selected) >= 4:
            break
    return _normalize_list_strings(selected)


def _eligible_project_assignees(project_row, team_row):
    members = _normalize_list_strings(str(project_row.get('team_members', '')).split(','))
    manager_id = str(team_row.get('manager_id', '')).strip() if team_row else ''
    eligible = [member_id for member_id in members if member_id and member_id != manager_id]
    return eligible or members


def _salary_for_role(role):
    return _safe_int(ROLE_PAY_BANDS.get(normalize_role(role), ROLE_PAY_BANDS['employee']), ROLE_PAY_BANDS['employee'])


def ensure_platform_admin_account():
    users = read_csv(USERS_CSV)
    existing = next((row for row in users if normalize_role(row.get('role')) == 'platform_admin'), None)
    if existing:
        updated = False
        if str(existing.get('username') or '').strip().lower() != PLATFORM_FOUNDER_EMAIL.lower():
            existing['username'] = PLATFORM_FOUNDER_EMAIL
            updated = True
        password_hash = str(existing.get('password_hash') or '').strip()
        if not password_hash or not check_password_hash(password_hash, get_role_default_password('platform_admin')):
            existing['password_hash'] = generate_password_hash(get_role_default_password('platform_admin'))
            updated = True
        if str(existing.get('full_name') or '').strip() != 'TaskVise Founder':
            existing['full_name'] = 'TaskVise Founder'
            updated = True
        if str(existing.get('is_active') or '').strip().lower() != 'true':
            existing['is_active'] = 'true'
            updated = True
        if updated:
            write_csv(USERS_CSV, users, merge_fieldnames(users, USER_FIELDNAMES))
        return existing

    row = {
        'id': 'TVA001',
        'username': PLATFORM_FOUNDER_EMAIL,
        'password_hash': generate_password_hash(get_role_default_password('platform_admin')),
        'full_name': 'TaskVise Founder',
        'role': 'platform_admin',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'is_active': 'true',
    }
    append_csv(USERS_CSV, row, USER_FIELDNAMES)
    return row


def ensure_demo_org_integrity(force=False):
    global _ORG_STRUCTURE_BOOTSTRAPPED
    if _ORG_STRUCTURE_BOOTSTRAPPED and not force:
        return

    ensure_platform_admin_account()
    users = read_csv(USERS_CSV)
    employees = read_csv(EMP_CSV)
    projects = read_csv(PROJECTS_CSV)
    tasks = read_csv(TASKS_CSV)
    role_map = _build_role_map(users)
    employee_lookup = _build_employee_index(employees)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    today = datetime.now().date()
    teams = _team_blueprint_rows(employees)
    assigned_team_ids = {
        employee_id
        for team in teams
        for employee_id in [str(team.get('manager_id', '')).strip(), str(team.get('teamlead_id', '')).strip(), *str(team.get('member_ids', '')).split(',')]
        if str(employee_id or '').strip()
    }
    for employee in employees:
        employee_id = str(employee.get('id', '')).strip()
        role = role_map.get(employee_id, normalize_role(employee.get('role')))
        if not employee_id or employee_id in assigned_team_ids or role in {'admin', 'hr', 'platform_admin', 'manager', 'teamlead'}:
            continue
        target_team = next((
            team for team in teams
            if _normalize_text(team.get('department')) == _normalize_text(employee.get('department'))
        ), None)
        if not target_team:
            target_team = teams[0] if teams else None
        if not target_team:
            continue
        current_members = _normalize_list_strings(str(target_team.get('member_ids', '')).split(','))
        if employee_id not in current_members:
            current_members.append(employee_id)
            target_team['member_ids'] = ','.join(current_members)
            assigned_team_ids.add(employee_id)
    team_by_id, team_by_member = _build_team_indexes(teams)

    user_changed = False
    employee_changed = False
    project_changed = False
    task_changed = False
    member_rows = []
    member_counter = 1

    for user in users:
        user_id = str(user.get('id', '')).strip()
        role = normalize_role(user.get('role'))
        team = team_by_member.get(user_id)
        updates = {}
        if role == 'platform_admin':
            updates = {'full_name': user.get('full_name') or 'TaskVise Founder'}
        elif team:
            updates = {
                'team_id': team.get('id', ''),
                'team_name': team.get('name', ''),
                'manager_id': team.get('manager_id', ''),
                'teamlead_id': team.get('teamlead_id', ''),
            }
        else:
            updates = {'team_id': '', 'team_name': '', 'manager_id': '', 'teamlead_id': ''}
        for key, value in updates.items():
            if str(user.get(key, '')) != str(value):
                user[key] = value
                user_changed = True

    for employee in employees:
        employee_id = str(employee.get('id', '')).strip()
        role = role_map.get(employee_id, normalize_role(employee.get('role')))
        team = team_by_member.get(employee_id)
        updates = {
            'role': role,
            'team_id': team.get('id', '') if team else '',
            'team_name': team.get('name', '') if team else '',
            'manager_id': team.get('manager_id', '') if team else '',
            'teamlead_id': team.get('teamlead_id', '') if team else '',
        }
        for key, value in updates.items():
            if str(employee.get(key, '')) != str(value):
                employee[key] = value
                employee_changed = True

    employee_lookup = _build_employee_index(employees)

    for index, project in enumerate(projects):
        team = _project_team_assignment(project, teams)
        if not team:
            continue
        current_team_id = str(project.get('team_id', '')).strip()
        if current_team_id != str(team.get('id', '')).strip():
            project['team_id'] = team.get('id', '')
            project_changed = True
        for key in ['team_name', 'manager_id', 'teamlead_id']:
            source_key = key
            if key == 'team_name':
                desired = team.get('name', '')
            else:
                desired = team.get(key, '')
            if str(project.get(key, '')) != str(desired):
                project[key] = desired
                project_changed = True
        if str(project.get('owner_id', '')).strip() not in {team.get('manager_id', ''), team.get('teamlead_id', '')}:
            project['owner_id'] = team.get('manager_id', '') if index % 2 == 0 else team.get('teamlead_id', '')
            project_changed = True
        project_members = _project_member_selection(project, team)
        joined_members = ','.join(project_members)
        if str(project.get('team_members', '')).strip() != joined_members:
            project['team_members'] = joined_members
            project_changed = True
        for employee_id in project_members:
            member_rows.append({
                'id': f'{PROJECT_MEMBER_ID_PREFIX}{member_counter:0{PROJECT_MEMBER_ID_WIDTH}d}',
                'project_id': str(project.get('id', '')).strip(),
                'employee_id': employee_id,
            })
            member_counter += 1

    project_lookup = {str(project.get('id', '')).strip(): project for project in projects}
    task_buckets = {}
    for task in tasks:
        task_buckets.setdefault(str(task.get('project_id', '')).strip(), []).append(task)

    for project_id, project_tasks in task_buckets.items():
        project = project_lookup.get(project_id)
        team = team_by_id.get(str(project.get('team_id', '')).strip()) if project else None
        eligible = _eligible_project_assignees(project or {}, team)
        if not eligible:
            continue
        for offset, task in enumerate(sorted(project_tasks, key=lambda item: _prefixed_id_sort_key(item.get('id', ''), TASK_ID_PREFIX))):
            assignee_id = eligible[offset % len(eligible)]
            assignee = employee_lookup.get(assignee_id, {})
            desired_status = normalize_task_status(task.get('status'))
            desired_progress = max(0, min(100, _safe_int(task.get('progress', 0), 0)))
            if desired_status == 'completed':
                desired_progress = 100
            if desired_status == 'pending' and desired_progress > 0:
                desired_status = 'in-progress'
            if str(task.get('assignee_id', '')).strip() != assignee_id:
                task['assignee_id'] = assignee_id
                task_changed = True
            if str(task.get('assignee_name', '')).strip() != str(assignee.get('name', '')).strip():
                task['assignee_name'] = assignee.get('name', '')
                task_changed = True
            if str(task.get('status', '')).strip() != desired_status:
                task['status'] = desired_status
                task_changed = True
            if str(task.get('progress', '')) != str(desired_progress):
                task['progress'] = str(desired_progress)
                task_changed = True
            estimated_hours = max(1, _safe_int(task.get('estimated_hours', task.get('estimatedHours', 8)), 8))
            actual_hours = _safe_int(task.get('actual_hours', task.get('actualHours', 0)), 0)
            if desired_status in {'in-progress', 'review'} and actual_hours <= 0:
                task['actual_hours'] = str(max(1, estimated_hours // 2))
                task_changed = True
            elif desired_status == 'completed' and actual_hours <= 0:
                task['actual_hours'] = str(estimated_hours)
                task_changed = True

    if user_changed:
        write_csv(USERS_CSV, users, merge_fieldnames(users, USER_FIELDNAMES + ['team_id', 'team_name', 'manager_id', 'teamlead_id']))
    if employee_changed:
        write_csv(EMP_CSV, employees, merge_fieldnames(employees, EMP_FIELDNAMES + ['role', 'team_id', 'team_name', 'manager_id', 'teamlead_id']))
    write_csv(TEAMS_CSV, teams, TEAM_FIELDNAMES)
    if project_changed:
        write_csv(PROJECTS_CSV, projects, merge_fieldnames(projects, PROJECT_FIELDNAMES + ['team_id', 'team_name', 'manager_id', 'teamlead_id']))
    write_csv(PROJECT_MEMBERS_CSV, member_rows, PROJECT_MEMBER_FIELDNAMES)
    if task_changed:
        write_csv(TASKS_CSV, tasks, merge_fieldnames(tasks, TASK_FIELDNAMES))

    refreshed_employees = read_csv(EMP_CSV)
    refreshed_users = read_csv(USERS_CSV)
    role_map = _build_role_map(refreshed_users)
    payments = []
    for employee in refreshed_employees:
        employee_id = str(employee.get('id', '')).strip()
        if not employee_id:
            continue
        role = role_map.get(employee_id, normalize_role(employee.get('role')))
        team = get_team_record_for_user(employee_id, teams)
        productivity = max(0, min(100, _safe_int(employee.get('productivity', 0), 0)))
        base_salary = _salary_for_role(role)
        bonus = int(round(base_salary * (productivity / 100.0) * 0.08))
        last_paid = today.replace(day=1)
        if today.month == 12:
            next_paid = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_paid = today.replace(month=today.month + 1, day=1)
        payments.append({
            'id': f'PAY-{employee_id}',
            'employee_id': employee_id,
            'employee_name': employee.get('name', ''),
            'role': role,
            'team_id': team.get('id', '') if team else '',
            'team_name': team.get('name', '') if team else '',
            'department': employee.get('department', ''),
            'base_salary': str(base_salary),
            'bonus': str(bonus),
            'currency': 'INR',
            'payment_status': 'scheduled' if str(employee.get('status', 'active')).strip().lower() == 'active' else 'hold',
            'last_paid_date': last_paid.strftime('%Y-%m-%d'),
            'next_pay_date': next_paid.strftime('%Y-%m-%d'),
            'pay_cycle': 'monthly',
            'updated_at': timestamp,
        })
    write_csv(PAYMENTS_CSV, payments, PAYMENT_FIELDNAMES)
    export_demo_credentials_file(users=refreshed_users)
    _ORG_STRUCTURE_BOOTSTRAPPED = True

def _collect_id_rows(*collections):
    seen = set()
    rows = []
    for collection in collections:
        for row in collection or []:
            row_id = str((row or {}).get('id', '')).strip()
            if not row_id or row_id in seen:
                continue
            seen.add(row_id)
            rows.append({'id': row_id})
    return rows

def get_next_workforce_id(users=None, employees=None):
    return _next_prefixed_id(
        WORKFORCE_ID_PREFIX,
        _collect_id_rows(users if users is not None else read_csv(USERS_CSV), employees if employees is not None else read_csv(EMP_CSV)),
        WORKFORCE_ID_WIDTH,
    )

def get_next_project_id(projects=None):
    return _next_prefixed_id(
        PROJECT_ID_PREFIX,
        projects if projects is not None else read_csv(PROJECTS_CSV),
        PROJECT_ID_WIDTH,
    )

def get_next_task_id(tasks=None):
    return _next_prefixed_id(
        TASK_ID_PREFIX,
        tasks if tasks is not None else read_csv(TASKS_CSV),
        TASK_ID_WIDTH,
    )

def get_next_project_member_id(members=None):
    return _next_prefixed_id(
        PROJECT_MEMBER_ID_PREFIX,
        members if members is not None else read_csv(PROJECT_MEMBERS_CSV),
        PROJECT_MEMBER_ID_WIDTH,
    )

def _serialize_admin_employee(emp, role_map=None, default_company=None):
    roles = role_map or _build_role_map()
    employee_id = str(emp.get('id', '')).strip()
    role = roles.get(employee_id, normalize_role(emp.get('role', 'employee')))
    status = str(emp.get('status', 'active') or 'active').strip().lower()
    if status not in {'active', 'inactive'}:
        status = 'active'
    company_name = str(emp.get('company') or default_company or DEFAULT_COMPANY_NAME).strip()
    return {
        **emp,
        'id': employee_id,
        'name': emp.get('name', ''),
        'fullName': emp.get('name', ''),
        'email': emp.get('email', ''),
        'position': emp.get('position', ''),
        'department': emp.get('department', ''),
        'company': company_name,
        'phone': emp.get('phone', ''),
        'skills': emp.get('skills', ''),
        'location': emp.get('location', ''),
        'join_date': emp.get('join_date', ''),
        'last_login': emp.get('last_login', ''),
        'productivity': _safe_int(emp.get('productivity', 0), 0),
        'role': role,
        'team_id': emp.get('team_id', ''),
        'team_name': emp.get('team_name', ''),
        'manager_id': emp.get('manager_id', ''),
        'teamlead_id': emp.get('teamlead_id', ''),
        'status': status,
        'initials': ''.join(part[:1] for part in str(emp.get('name', '')).split()).upper()[:2],
    }

def _serialize_admin_project(project, employee_index=None, member_rows=None, default_company=None):
    employee_lookup = employee_index or _build_employee_index()
    team_member_ids = _parse_team_members(project, member_rows)
    owner = employee_lookup.get(str(project.get('owner_id', '')).strip(), {})
    team_members = []
    for member_id in team_member_ids:
        employee = employee_lookup.get(member_id, {})
        team_members.append({
            'id': member_id,
            'name': employee.get('name', member_id),
            'position': employee.get('position', ''),
            'department': employee.get('department', ''),
        })
    return {
        **project,
        'id': str(project.get('id', '')).strip(),
        'name': project.get('name', ''),
        'description': project.get('description', ''),
        'owner_id': str(project.get('owner_id', '')).strip(),
        'owner_name': owner.get('name', 'Unassigned'),
        'department': owner.get('department', project.get('department', 'Operations')),
        'company': project.get('company') or owner.get('company') or default_company or DEFAULT_COMPANY_NAME,
        'team_id': project.get('team_id', ''),
        'team_name': project.get('team_name', ''),
        'manager_id': project.get('manager_id', ''),
        'teamlead_id': project.get('teamlead_id', ''),
        'status': normalize_project_status(project.get('status', 'planning')),
        'deadline': str(project.get('end_date', project.get('deadline', '')) or '')[:10],
        'progress': max(0, min(100, int(project.get('progress', 0) or 0))),
        'team_members': team_member_ids,
        'team_members_count': len(team_member_ids),
        'team_member_details': team_members,
    }

def _serialize_admin_task(task, employee_index=None, project_lookup=None):
    employee_lookup = employee_index or _build_employee_index()
    projects = project_lookup or {}
    assignee_id = str(task.get('assignee_id', '')).strip()
    project_id = str(task.get('project_id', '')).strip()
    assignee = employee_lookup.get(assignee_id, {})
    project = projects.get(project_id, {})
    return {
        **task,
        'id': str(task.get('id', '')).strip(),
        'title': task.get('title', ''),
        'description': task.get('description', ''),
        'assignee_id': assignee_id,
        'assignee_name': task.get('assignee_name') or assignee.get('name', ''),
        'project_id': project_id,
        'project_name': project.get('name', task.get('project_name', '')),
        'status': normalize_task_status(task.get('status')),
        'priority': str(task.get('priority', 'medium') or 'medium').strip().lower(),
        'due_date': str(task.get('due_date', task.get('dueDate', '')) or '')[:10],
        'estimated_hours': str(task.get('estimated_hours', task.get('estimatedHours', '')) or '0'),
        'actual_hours': str(task.get('actual_hours', task.get('actualHours', '')) or '0'),
        'progress': max(0, min(100, int(task.get('progress', 0) or 0))),
    }

def get_admin_dashboard_payload():
    ensure_demo_org_integrity()
    ensure_projects_team_members()
    raw_employees = load_employees()
    raw_tasks = load_tasks()
    raw_projects = load_projects()
    default_company = infer_primary_company_name(raw_employees, raw_projects)
    users = read_csv(USERS_CSV)
    role_map = _build_role_map(users)
    employee_index = _build_employee_index(raw_employees)
    member_rows = read_csv(PROJECT_MEMBERS_CSV)

    employees = _sort_rows_by_id(
        [_serialize_admin_employee(emp, role_map, default_company) for emp in raw_employees],
        WORKFORCE_ID_PREFIX,
    )
    projects = sorted(
        [_serialize_admin_project(project, employee_index, member_rows, default_company) for project in raw_projects],
        key=lambda item: _prefixed_id_sort_key(item.get('id', ''), PROJECT_ID_PREFIX),
    )
    project_lookup = {project.get('id'): project for project in projects}
    tasks = sorted(
        [_serialize_admin_task(task, employee_index, project_lookup) for task in raw_tasks],
        key=lambda item: _prefixed_id_sort_key(item.get('id', ''), TASK_ID_PREFIX),
    )

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
        'on_hold_projects': len([p for p in projects if p.get('status') == 'on-hold']),
        'employees_managed': len(employees),
        'projects_overseen': len(projects),
        'tasks_assigned': len([t for t in tasks if str(t.get('assignee_id', '')).strip()]),
        'avg_productivity': int(round(sum(_safe_int(e.get('productivity', 0), 0) for e in employees) / max(len(employees), 1))),
        'total_hours': calculate_total_hours(tasks),
    }
    recent_activity = build_recent_activity(employees, projects, tasks)
    return {
        'employees': employees,
        'tasks': tasks,
        'projects': projects,
        'stats': stats,
        'recent_activity': recent_activity,
    }

DEPARTMENT_SKILL_BASELINES = {
    'engineering': ['Python', 'JavaScript', 'React', 'SQL', 'Testing'],
    'design': ['Figma', 'UI Design', 'UX Research', 'Prototyping'],
    'product': ['Product Strategy', 'Analytics', 'Roadmapping', 'User Research'],
    'marketing': ['SEO', 'Content Strategy', 'Analytics', 'Campaign Planning'],
    'sales': ['CRM', 'Negotiation', 'Lead Generation', 'Client Relations'],
    'hr': ['Recruitment', 'Training', 'Compliance', 'People Operations'],
    'finance': ['Forecasting', 'Excel', 'Budgeting', 'Reporting'],
    'it': ['AWS', 'Networking', 'Security', 'Automation'],
    'operations': ['Process Design', 'Reporting', 'Coordination', 'Analytics'],
}

PROJECT_SKILL_HINTS = {
    'ai': ['Python', 'Machine Learning', 'Analytics'],
    'assistant': ['Python', 'NLP', 'Analytics'],
    'cloud': ['AWS', 'Docker', 'Kubernetes'],
    'migration': ['AWS', 'Docker', 'Security'],
    'mobile': ['React', 'UI Design', 'Testing'],
    'redesign': ['Figma', 'UI Design', 'UX Research'],
    'api': ['Python', 'API Design', 'Testing'],
    'compliance': ['Compliance', 'Reporting', 'Process Design'],
    'marketing': ['SEO', 'Content Strategy', 'Analytics'],
    'sales': ['CRM', 'Negotiation', 'Client Relations'],
    'finance': ['Forecasting', 'Budgeting', 'Reporting'],
    'pipeline': ['Python', 'Data Engineering', 'Automation'],
    'security': ['Security', 'Networking', 'AWS'],
}

def _clean_skill_label(value):
    text = str(value or '').strip()
    if not text:
        return ''
    replacements = {
        'ui design': 'UI Design',
        'ux research': 'UX Research',
        'ci/cd': 'CI/CD',
        'node.js': 'Node.js',
        'react native': 'React Native',
        'people operations': 'People Operations',
        'api design': 'API Design',
        'machine learning': 'Machine Learning',
        'data engineering': 'Data Engineering',
    }
    normalized = re.sub(r'\s+', ' ', text).strip()
    lowered = normalized.lower()
    if lowered in replacements:
        return replacements[lowered]
    if normalized.isupper() and len(normalized) <= 5:
        return normalized
    return ' '.join(part[:1].upper() + part[1:] for part in normalized.split(' '))

def _parse_skills(raw_value):
    pieces = re.split(r'[,/|;]+', str(raw_value or ''))
    return _normalize_list_strings(_clean_skill_label(piece) for piece in pieces)

def _build_skill_vocabulary(employees):
    vocabulary = set()
    for employee in employees or []:
        vocabulary.update(_parse_skills(employee.get('skills', '')))
    for values in DEPARTMENT_SKILL_BASELINES.values():
        vocabulary.update(values)
    for values in PROJECT_SKILL_HINTS.values():
        vocabulary.update(values)
    return sorted(vocabulary)

def _extract_skills_from_text(text, vocabulary):
    lowered = _normalize_text(text)
    if not lowered:
        return []
    found = []
    for skill in vocabulary:
        if _normalize_text(skill) and _normalize_text(skill) in lowered:
            found.append(skill)
    for keyword, suggested_skills in PROJECT_SKILL_HINTS.items():
        if keyword in lowered:
            found.extend(suggested_skills)
    return _normalize_list_strings(found)

def _build_month_window(count=6):
    cursor = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    window = []
    for _ in range(count):
        window.append(cursor.strftime('%Y-%m'))
        if cursor.month == 1:
            cursor = cursor.replace(year=cursor.year - 1, month=12)
        else:
            cursor = cursor.replace(month=cursor.month - 1)
    return list(reversed(window))

def _month_label(month_key):
    try:
        return datetime.strptime(month_key, '%Y-%m').strftime('%b %Y')
    except Exception:
        return month_key

def _task_hour_value(task):
    actual = _safe_int(task.get('actual_hours', 0), 0)
    estimated = _safe_int(task.get('estimated_hours', 0), 0)
    return actual or estimated or 6

def build_admin_analytics_payload(employees, projects, tasks):
    employee_index = {str(employee.get('id', '')).strip(): employee for employee in employees}
    project_index = {str(project.get('id', '')).strip(): project for project in projects}
    default_company = infer_primary_company_name(employees, projects)
    tasks_by_employee = {}
    departments = sorted(
        {str(employee.get('department') or 'Operations').strip() for employee in employees}
        | {str(project.get('department') or 'Operations').strip() for project in projects}
    )

    for task in tasks:
        assignee_id = str(task.get('assignee_id', '')).strip()
        tasks_by_employee.setdefault(assignee_id, []).append(task)

    department_stats = []
    for department in [dept for dept in departments if dept]:
        department_employee_ids = {
            str(employee.get('id', '')).strip()
            for employee in employees
            if str(employee.get('department') or '').strip() == department
        }
        department_projects = [
            project for project in projects
            if str(project.get('department') or '').strip() == department
        ]
        department_tasks = [
            task for task in tasks
            if str(task.get('assignee_id', '')).strip() in department_employee_ids
            or str(task.get('project_id', '')).strip() in {str(project.get('id', '')).strip() for project in department_projects}
        ]
        completed_count = len([task for task in department_tasks if task.get('status') == 'completed'])
        productivity = int(round((completed_count / max(len(department_tasks), 1)) * 100))
        department_stats.append({
            'department': department,
            'employee_count': len(department_employee_ids),
            'project_count': len(department_projects),
            'task_count': len(department_tasks),
            'productivity': productivity,
            'avg_progress': int(round(sum(_safe_int(task.get('progress', 0), 0) for task in department_tasks) / max(len(department_tasks), 1))),
        })
    department_stats.sort(key=lambda item: (-item['productivity'], item['department']))

    month_keys = _build_month_window(6)
    monthly_lookup = {
        month_key: {'month': _month_label(month_key), 'tasks': 0, 'completed': 0, 'hours': 0}
        for month_key in month_keys
    }
    for task in tasks:
        created = _parse_date_any(task.get('created_at'))
        if not created:
            continue
        month_key = created.strftime('%Y-%m')
        if month_key not in monthly_lookup:
            continue
        monthly_lookup[month_key]['tasks'] += 1
        if task.get('status') == 'completed':
            monthly_lookup[month_key]['completed'] += 1
        monthly_lookup[month_key]['hours'] += _task_hour_value(task)
    monthly_stats = [monthly_lookup[key] for key in month_keys]

    top_performers = []
    for employee in employees:
        employee_id = str(employee.get('id', '')).strip()
        owned_tasks = tasks_by_employee.get(employee_id, [])
        completed = len([task for task in owned_tasks if task.get('status') == 'completed'])
        overdue = len([task for task in owned_tasks if is_task_overdue(task)])
        completion_rate = int(round((completed / max(len(owned_tasks), 1)) * 100))
        productivity = _safe_int(employee.get('productivity', completion_rate), completion_rate) or completion_rate
        score = int(round((productivity * 0.6) + (completion_rate * 0.4) - (overdue * 4)))
        top_performers.append({
            'id': employee_id,
            'name': employee.get('name', 'Unknown'),
            'department': employee.get('department', 'Operations'),
            'role': employee.get('role', 'employee'),
            'productivity': productivity,
            'completion_rate': completion_rate,
            'completed_tasks': completed,
            'total_tasks': len(owned_tasks),
            'score': max(score, 0),
        })
    top_performers.sort(key=lambda item: (-item['score'], -item['completed_tasks'], item['name']))
    top_performers = top_performers[:5]

    workload_insights = []
    for employee in employees:
        employee_id = str(employee.get('id', '')).strip()
        owned_tasks = tasks_by_employee.get(employee_id, [])
        active_tasks = len([task for task in owned_tasks if task.get('status') not in {'completed', 'cancelled'}])
        overdue_tasks = len([task for task in owned_tasks if is_task_overdue(task)])
        avg_progress = int(round(sum(_safe_int(task.get('progress', 0), 0) for task in owned_tasks) / max(len(owned_tasks), 1)))
        workload_state = 'Balanced'
        if active_tasks >= 7 or overdue_tasks >= 2:
            workload_state = 'Overloaded'
        elif active_tasks <= 2:
            workload_state = 'Light'
        workload_insights.append({
            'name': employee.get('name', 'Unknown'),
            'department': employee.get('department', 'Operations'),
            'active_tasks': active_tasks,
            'overdue_tasks': overdue_tasks,
            'avg_progress': avg_progress,
            'state': workload_state,
        })
    workload_insights.sort(key=lambda item: (-item['overdue_tasks'], -item['active_tasks'], item['name']))
    workload_insights = workload_insights[:6]

    role_distribution = []
    role_counts = Counter(str(employee.get('role') or 'employee').strip().lower() for employee in employees)
    for role, count in role_counts.most_common():
        role_distribution.append({'role': role, 'count': count})

    company_overview = []
    company_counts = Counter()
    for employee in employees:
        company = str(employee.get('company') or default_company).strip()
        if company:
            company_counts[company] += 1
    for project in projects:
        company = str(project.get('company') or default_company).strip()
        if company:
            company_counts[company] += 1
    for company, count in company_counts.most_common(4):
        project_count = len([project for project in projects if str(project.get('company') or default_company).strip() == company])
        employee_count = len([employee for employee in employees if str(employee.get('company') or default_company).strip() == company])
        company_overview.append({
            'company': company,
            'employee_count': employee_count,
            'project_count': project_count,
            'task_count': len([
                task for task in tasks
                if str(project_index.get(str(task.get('project_id', '')).strip(), {}).get('company') or '').strip() == company
            ]),
        })

    return {
        'department_stats': department_stats,
        'monthly_stats': monthly_stats,
        'top_performers': top_performers,
        'workload_insights': workload_insights,
        'role_distribution': role_distribution,
        'company_overview': company_overview,
    }

def build_admin_skill_gap_payload(employees, projects, tasks):
    employee_map = {str(employee.get('id', '')).strip(): employee for employee in employees}
    default_company = infer_primary_company_name(employees, projects)
    tasks_by_project = {}
    for task in tasks:
        project_id = str(task.get('project_id', '')).strip()
        tasks_by_project.setdefault(project_id, []).append(task)

    vocabulary = _build_skill_vocabulary(employees)
    rows = []
    missing_skill_counter = Counter()
    severity_counter = Counter()

    for project in projects:
        project_id = str(project.get('id', '')).strip()
        project_tasks = tasks_by_project.get(project_id, [])
        base_skills = DEPARTMENT_SKILL_BASELINES.get(_normalize_text(project.get('department')), ['Planning', 'Coordination', 'Reporting'])
        text_blob = ' '.join([
            str(project.get('name') or ''),
            str(project.get('description') or ''),
            ' '.join(str(task.get('title') or '') for task in project_tasks),
            ' '.join(str(task.get('description') or '') for task in project_tasks),
        ])
        required_skills = _normalize_list_strings(base_skills + _extract_skills_from_text(text_blob, vocabulary))

        team_member_ids = _parse_team_members(project)
        if project.get('owner_id'):
            team_member_ids = _normalize_list_strings(team_member_ids + [project.get('owner_id')])

        available_skills = []
        for member_id in team_member_ids:
            available_skills.extend(_parse_skills(employee_map.get(str(member_id).strip(), {}).get('skills', '')))
        available_skills = _normalize_list_strings(available_skills)

        required_set = set(required_skills)
        available_set = set(available_skills)
        matched = len(required_set & available_set)
        match_rate = int(round((matched / max(len(required_set), 1)) * 100)) if required_set else 100
        missing_skills = sorted(required_set - available_set)

        if missing_skills:
            if match_rate < 55 or len(missing_skills) >= 3:
                severity = 'high'
            elif match_rate < 80 or len(missing_skills) >= 2:
                severity = 'medium'
            else:
                severity = 'low'
        else:
            severity = 'low'

        if missing_skills:
            missing_skill_counter.update(missing_skills)
        severity_counter[severity] += 1

        recommendation = 'Current team can deliver with minor enablement.'
        if severity == 'high' and missing_skills:
            recommendation = f"Prioritize upskilling or hiring for {', '.join(missing_skills[:3])}."
        elif severity == 'medium' and missing_skills:
            recommendation = f"Cross-train the project squad on {', '.join(missing_skills[:2])}."
        elif severity == 'low' and missing_skills:
            recommendation = f"Schedule a short knowledge transfer on {missing_skills[0]}."

        rows.append({
            'project_id': project_id,
            'project_name': project.get('name', 'Unnamed Project'),
            'department': project.get('department', 'Operations'),
            'company': project.get('company') or default_company,
            'required_skills': required_skills,
            'available_skills': available_skills,
            'missing_skills': missing_skills,
            'match_rate': match_rate,
            'gap_severity': severity,
            'recommendation': recommendation,
            'team_members_count': len(team_member_ids),
        })

    rows.sort(key=lambda item: ({'high': 0, 'medium': 1, 'low': 2}.get(item['gap_severity'], 3), item['match_rate'], item['project_name']))
    avg_match = int(round(sum(item['match_rate'] for item in rows) / max(len(rows), 1))) if rows else 100

    return {
        'rows': rows,
        'summary': {
            'high': severity_counter.get('high', 0),
            'medium': severity_counter.get('medium', 0),
            'low': severity_counter.get('low', 0),
            'avg_match_rate': avg_match,
            'projects_analyzed': len(rows),
        },
        'missing_skill_counts': [
            {'skill': skill, 'count': count}
            for skill, count in missing_skill_counter.most_common(8)
        ],
        'recommended_training': [
            {'skill': skill, 'count': count}
            for skill, count in missing_skill_counter.most_common(5)
        ],
        'departments': sorted({str(project.get('department') or 'Operations').strip() for project in projects}),
    }

def _sync_project_members(project_id, team_member_ids):
    existing = read_csv(PROJECT_MEMBERS_CSV)
    retained = [row for row in existing if str(row.get('project_id', '')).strip() != str(project_id).strip()]
    for member_id in _normalize_list_strings(team_member_ids):
        next_member_id = get_next_project_member_id(retained)
        retained.append({
            'id': next_member_id,
            'project_id': str(project_id).strip(),
            'employee_id': member_id,
        })
    write_csv(
        PROJECT_MEMBERS_CSV,
        retained,
        merge_fieldnames(retained if retained else existing, PROJECT_MEMBER_FIELDNAMES),
    )

def ensure_projects_team_members():
    """Ensure projects.csv has a 'team_members' column and backfill from project_members.csv.
    team_members stored as comma-separated employee_ids.
    """
    try:
        rows = read_csv(PROJECTS_CSV)
        if not rows:
            return
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
        for r in rows:
            pid = r.get('id')
            r['team_members'] = ','.join([e for e in team_map.get(pid, []) if e])
        write_csv(
            PROJECTS_CSV,
            rows,
            merge_fieldnames(
                rows,
                ['id', 'name', 'description', 'owner_id', 'start_date', 'end_date', 'status', 'team_members']
            )
        )
    except Exception:
        pass

def normalize_leave_status(value):
    raw = str(value or '').strip().lower()
    aliases = {
        'approve': 'approved',
        'approved leave': 'approved',
        'accept': 'approved',
        'accepted': 'approved',
        'reject': 'rejected',
        'declined': 'rejected',
        'deny': 'rejected',
        'denied': 'rejected',
        'pending approval': 'pending',
        'awaiting approval': 'pending',
    }
    return aliases.get(raw, raw)

def _extract_datetime_text(value):
    text = str(value or '').strip()
    if not text:
        return ''
    match = re.search(r'\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}', text)
    if not match:
        return ''
    return match.group(0).replace('T', ' ')

def normalize_leave_row(row):
    source = row or {}
    extra = source.get('', '')
    normalized = {
        key: str(source.get(key, '') if source.get(key, '') is not None else '').strip()
        for key in LEAVE_FIELDNAMES
    }

    status_candidate = normalize_leave_status(normalized.get('status'))
    applied_candidate = normalize_leave_status(normalized.get('applied_at'))
    leave_type = (normalized.get('type') or '').strip().lower()

    if status_candidate not in VALID_LEAVE_STATUSES and applied_candidate in VALID_LEAVE_STATUSES:
        if not leave_type and status_candidate:
            leave_type = status_candidate
        status_candidate = applied_candidate
        normalized['applied_at'] = ''

    type_as_status = normalize_leave_status(leave_type)
    if status_candidate not in VALID_LEAVE_STATUSES and type_as_status in VALID_LEAVE_STATUSES:
        status_candidate = type_as_status
        leave_type = ''

    if status_candidate not in VALID_LEAVE_STATUSES and status_candidate:
        if not leave_type:
            leave_type = status_candidate
        status_candidate = ''

    if status_candidate not in VALID_LEAVE_STATUSES:
        status_candidate = 'pending'
    if not leave_type:
        leave_type = 'leave'

    applied_at = (normalized.get('applied_at') or '').strip()
    if normalize_leave_status(applied_at) in VALID_LEAVE_STATUSES or not applied_at:
        extracted = _extract_datetime_text(extra) or _extract_datetime_text(source.get('created_at', ''))
        if extracted:
            applied_at = extracted
    if not applied_at:
        applied_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    normalized['start_date'] = (normalized.get('start_date') or '')[:10]
    normalized['end_date'] = (normalized.get('end_date') or '')[:10]
    normalized['type'] = leave_type
    normalized['status'] = status_candidate
    normalized['applied_at'] = applied_at
    return normalized

def ensure_leave_data_integrity():
    try:
        rows = read_csv(LEAVE_CSV)
        if not rows:
            return []

        normalized_rows = []
        should_rewrite = False
        for row in rows:
            normalized = normalize_leave_row(row)
            normalized_rows.append(normalized)

            existing = {
                key: str(row.get(key, '') if row.get(key, '') is not None else '').strip()
                for key in LEAVE_FIELDNAMES
            }
            if existing != normalized:
                should_rewrite = True
            if any(k and k not in LEAVE_FIELDNAMES for k in row.keys()):
                should_rewrite = True

        if should_rewrite:
            write_csv(LEAVE_CSV, normalized_rows, LEAVE_FIELDNAMES)
        return normalized_rows
    except Exception:
        return []

def ensure_leave_type_column():
    """Back-compat wrapper used by existing routes."""
    ensure_leave_data_integrity()

def create_notification(user_id, title, message, notif_type='system'):
    if not user_id:
        return
    row = {
        'id': str(uuid.uuid4()),
        'user_id': str(user_id),
        'title': str(title or 'Notification'),
        'message': str(message or ''),
        'type': str(notif_type or 'system').lower(),
        'is_read': 'false',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    append_csv(NOTIF_CSV, row, NOTIFICATION_FIELDNAMES)


def send_email_notification(to_email, subject, message):
    recipient = str(to_email or '').strip()
    if not recipient or not EMAIL_NOTIFICATIONS_ENABLED:
        return False
    if not SMTP_HOST or not SMTP_FROM:
        print(f"Email notifications skipped for {recipient}: SMTP is not configured.")
        return False

    email = EmailMessage()
    email['From'] = SMTP_FROM
    email['To'] = recipient
    email['Subject'] = str(subject or 'TaskVise Notification')
    email.set_content(str(message or ''))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            if SMTP_USE_TLS:
                server.starttls(context=ssl.create_default_context())
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(email)
        return True
    except Exception as exc:
        print(f"Email notification error for {recipient}: {exc}")
        return False


def _get_user_notification_email(user_id):
    employee = find_by_id(EMP_CSV, user_id) or {}
    user = find_by_id(USERS_CSV, user_id) or {}
    return str(employee.get('email') or user.get('username') or '').strip()


def notify_user(user_id, title, message, notif_type='system', email_subject=None):
    if not user_id:
        return
    create_notification(user_id, title, message, notif_type)
    settings, _rows = get_user_settings_record(user_id)
    if _truthy(settings.get('email_notifications'), True):
        send_email_notification(
            _get_user_notification_email(user_id),
            email_subject or title,
            message,
        )


def notify_users(user_ids, title, message, notif_type='system', email_subject=None):
    for user_id in _normalize_list_strings(user_ids):
        notify_user(user_id, title, message, notif_type, email_subject=email_subject)


def notify_task_assignment(task_row, actor_label='Manager', is_new_assignment=False):
    assignee_id = str(task_row.get('assignee_id', '')).strip()
    if not assignee_id:
        return
    task_title = str(task_row.get('title') or 'Untitled Task').strip()
    project_name = ''
    if str(task_row.get('project_id', '')).strip():
        project = find_by_id(PROJECTS_CSV, task_row.get('project_id')) or {}
        project_name = str(project.get('name') or '').strip()
    due_date = str(task_row.get('due_date') or task_row.get('dueDate') or '').strip()[:10]

    if is_new_assignment:
        title = 'New Task Assigned'
        message = f'{actor_label} assigned "{task_title}" to you.'
    else:
        title = 'Task Updated'
        message = f'{actor_label} updated task "{task_title}".'

    detail_parts = []
    if project_name:
        detail_parts.append(f'Project: {project_name}')
    if due_date:
        detail_parts.append(f'Due: {due_date}')
    if task_row.get('status'):
        detail_parts.append(f'Status: {normalize_task_status(task_row.get("status"))}')
    if detail_parts:
        message = f'{message} ' + ' | '.join(detail_parts)

    notify_user(assignee_id, title, message, 'task', email_subject=title)


def notify_project_assignment(project_row, actor_label='Manager', is_new_assignment=False):
    project_name = str(project_row.get('name') or 'Untitled Project').strip()
    deadline = str(project_row.get('end_date') or project_row.get('deadline') or '').strip()[:10]
    team_members = _parse_team_members(project_row)
    owner_id = str(project_row.get('owner_id', '')).strip()
    recipients = _normalize_list_strings(team_members + ([owner_id] if owner_id else []))
    if not recipients:
        return

    if is_new_assignment:
        title = 'Project Assignment'
        message = f'{actor_label} added you to project "{project_name}".'
    else:
        title = 'Project Updated'
        message = f'{actor_label} updated project "{project_name}".'
    if deadline:
        message = f'{message} Deadline: {deadline}.'

    notify_users(recipients, title, message, 'project', email_subject=title)

def calculate_completion_rate(tasks):
    """Calculate task completion rate"""
    if not tasks:
        return "0%"
    completed = len([t for t in tasks if t.get('status') == 'completed'])
    return f"{(completed / len(tasks)) * 100:.0f}%"

def split_skills(value):
    return [item.strip() for item in str(value or '').split(',') if item.strip()]

def get_employee_initials(name):
    parts = [part for part in str(name or '').strip().split() if part]
    if not parts:
        return 'TV'
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()

def classify_employee_badge(productivity, completion_rate, skills_count, total_tasks):
    productivity = max(0, min(100, _safe_int(productivity, 0)))
    completion_rate = max(0, min(100, _safe_int(completion_rate, 0)))
    skills_count = max(0, _safe_int(skills_count, 0))
    total_tasks = max(0, _safe_int(total_tasks, 0))

    if productivity >= 90 and completion_rate >= 75 and skills_count >= 4:
        return ('top-performer', 'Top Performer')
    if productivity >= 82 and skills_count >= 4:
        return ('highly-skilled', 'Highly Skilled')
    if productivity >= 70 and (completion_rate >= 60 or total_tasks >= 3):
        return ('proficient', 'Proficient')
    if productivity >= 55 or skills_count >= 3:
        return ('steady', 'Steady Contributor')
    return ('needs-improvement', 'Needs Improvement')

def is_task_overdue(task):
    """Check if a task is overdue"""
    due_date_text = str(task.get('due_date') or task.get('dueDate') or '').strip()[:10]
    if not due_date_text:
        return False
    try:
        due_date = datetime.strptime(due_date_text, '%Y-%m-%d')
        return due_date < datetime.now() and normalize_task_status(task.get('status')) != 'completed'
    except:
        return False

def build_manager_analytics_payload(user_id):
    manager_data = get_manager_data(user_id)
    employees = manager_data.get('employees', [])
    tasks = manager_data.get('tasks', [])
    projects = manager_data.get('projects', [])
    analytics = build_admin_analytics_payload(employees, projects, tasks)

    tasks_by_employee = {}
    monthly_created = Counter()
    status_counter = Counter()
    for task in tasks:
        assignee_id = str(task.get('assignee_id', '')).strip()
        tasks_by_employee.setdefault(assignee_id, []).append(task)
        status_counter[normalize_task_status(task.get('status'))] += 1
        created_at = _parse_date_any(task.get('created_at'))
        if created_at:
            monthly_created[created_at.strftime('%Y-%m')] += 1

    employee_performance = []
    active_employees = 0
    for employee in employees:
        employee_id = str(employee.get('id', '')).strip()
        employee_tasks = tasks_by_employee.get(employee_id, [])
        completed_tasks = len([
            task for task in employee_tasks
            if normalize_task_status(task.get('status')) == 'completed'
        ])
        total_tasks = len(employee_tasks)
        overdue_tasks = len([task for task in employee_tasks if is_task_overdue(task)])
        completion_rate = int(round((completed_tasks / max(total_tasks, 1)) * 100))
        productivity = _safe_int(employee.get('productivity', completion_rate), completion_rate) or completion_rate
        if total_tasks or str(employee.get('last_login') or '').strip():
            active_employees += 1
        employee_performance.append({
            'employee_id': employee_id,
            'name': employee.get('fullName') or employee.get('name') or 'Unknown',
            'department': employee.get('department', 'Operations'),
            'role': normalize_role(employee.get('role', 'employee')),
            'teamName': employee.get('team_name', ''),
            'completedTasks': completed_tasks,
            'totalTasks': total_tasks,
            'completionRate': completion_rate,
            'productivity': max(0, min(100, productivity)),
            'overdueTasks': overdue_tasks,
        })

    employee_performance.sort(
        key=lambda item: (-item['productivity'], -item['completedTasks'], item['name'])
    )

    total_completed = len([
        task for task in tasks
        if normalize_task_status(task.get('status')) == 'completed'
    ])
    total_tasks = len(tasks)
    completion_rate = int(round((total_completed / max(total_tasks, 1)) * 100)) if total_tasks else 0
    avg_productivity = int(round(
        sum(item.get('productivity', 0) for item in employee_performance) / max(len(employee_performance), 1)
    )) if employee_performance else 0

    return {
        'teamSize': len(employees),
        'activeEmployees': active_employees,
        'totalProjects': len(projects),
        'activeProjects': len([
            project for project in projects
            if str(project.get('status') or '').strip().lower() in {'active', 'planning'}
        ]),
        'totalTasks': total_tasks,
        'completedTasks': total_completed,
        'completionRate': completion_rate,
        'avgProductivity': avg_productivity,
        'overdueTasks': calculate_overdue_tasks(tasks),
        'employeePerformance': employee_performance,
        'teamPerformance': employee_performance,
        'tasksByStatus': dict(status_counter),
        'departmentStats': analytics.get('department_stats', []),
        'monthlyStats': analytics.get('monthly_stats', []),
        'topPerformers': analytics.get('top_performers', []),
        'workloadInsights': analytics.get('workload_insights', []),
        'generatedAt': datetime.now().isoformat(),
    }


def get_team_members(manager_id):
    """Get all employees assigned to a manager"""
    ensure_demo_org_integrity()
    if not _use_database(USERS_CSV) or DB_BACKEND != 'mongodb':
        team = get_team_record_for_user(manager_id)
        return get_team_member_ids(team, include_teamlead=True)
    try:
        team_coll = _mongo_collection('team_assignments')
        team = team_coll.find_one({'manager_id': manager_id})
        if team:
            return team.get('employee_ids', [])
        return []
    except:
        return []


def get_manager_for_employee(employee_id):
    """Get the manager assigned to an employee"""
    ensure_demo_org_integrity()
    if not _use_database(USERS_CSV) or DB_BACKEND != 'mongodb':
        team = get_team_record_for_user(employee_id)
        return str((team or {}).get('manager_id') or '').strip() or None
    try:
        team_coll = _mongo_collection('team_assignments')
        team = team_coll.find_one({'employee_ids': employee_id})
        if team:
            return team.get('manager_id')
        return None
    except:
        return None


def get_teamlead_for_employee(employee_id):
    ensure_demo_org_integrity()
    team = get_team_record_for_user(employee_id)
    return str((team or {}).get('teamlead_id') or '').strip() or None


def get_project_notification_recipients(project_row, exclude_ids=None):
    exclude = {str(value).strip() for value in (exclude_ids or []) if str(value).strip()}
    team_members = _parse_team_members(project_row)
    recipients = _normalize_list_strings([
        str(project_row.get('owner_id', '')).strip(),
        str(project_row.get('manager_id', '')).strip(),
        str(project_row.get('teamlead_id', '')).strip(),
        *team_members,
    ])
    return [user_id for user_id in recipients if user_id not in exclude]


def notify_employee_progress_update(task_row, actor_id, update_label, update_value):
    task_id = str(task_row.get('id', '')).strip()
    task_title = str(task_row.get('title') or task_id or 'Task').strip()
    actor = find_by_id(EMP_CSV, actor_id) or {}
    actor_name = str(actor.get('name') or session.get('full_name') or actor_id or 'Employee').strip()
    recipients = _normalize_list_strings([
        get_manager_for_employee(actor_id),
        get_teamlead_for_employee(actor_id),
        str((find_by_id(PROJECTS_CSV, task_row.get('project_id')) or {}).get('owner_id') or '').strip(),
    ])
    recipients = [user_id for user_id in recipients if user_id and user_id != str(actor_id).strip()]
    if not recipients:
        return
    notify_users(
        recipients,
        'Employee Progress Update',
        f'{actor_name} updated "{task_title}" {update_label} to {update_value}.',
        'task',
        email_subject='Employee Progress Update',
    )


def _resolve_current_employee_context():
    user_id = session.get('user_id')
    username = session.get('username')
    full_name = session.get('full_name')
    candidate_ids, employees = resolve_employee_candidate_ids(user_id, username, full_name)

    employee = next((e for e in employees if str(e.get('id', '')).strip() == str(user_id or '').strip()), None)
    if not employee and username:
        employee = next((e for e in employees if _normalize_text(e.get('email')) == _normalize_text(username)), None)
    if not employee and full_name:
        employee = next((e for e in employees if _normalize_text(e.get('name')) == _normalize_text(full_name)), None)

    employee_id = str((employee or {}).get('id') or '').strip()
    if not employee_id and candidate_ids:
        employee_id = next(iter(candidate_ids))
        employee = next((e for e in employees if str(e.get('id', '')).strip() == str(employee_id)), employee)

    return employee_id, (employee or {}), candidate_ids, employees


def _resolve_session_employee_task(task_id):
    employee_id, employee, candidate_ids, _employees = _resolve_current_employee_context()
    username = session.get('username')
    full_name = session.get('full_name')
    task = next((
        row for row in read_csv(TASKS_CSV)
        if str(row.get('id') or '').strip() == str(task_id or '').strip()
        and task_matches_employee(row, candidate_ids, username=username, full_name=full_name)
    ), None)
    return task, employee_id, employee, candidate_ids


def _allowed_task_submission(filename):
    extension = str(filename or '').strip().lower().rsplit('.', 1)
    if len(extension) != 2:
        return False
    return extension[-1] in {'zip', '7z', 'rar'}


def _submission_download_path(row):
    rel_path = str((row or {}).get('file_path') or '').strip().replace('\\', '/')
    if not rel_path:
        return ''
    return url_for('static', filename=rel_path)


def _serialize_task_submission(row):
    item = dict(row or {})
    item['download_url'] = _submission_download_path(item)
    item['file_size'] = _safe_int(item.get('file_size'), 0)
    item['created_at'] = str(item.get('created_at') or '')[:19]
    item['updated_at'] = str(item.get('updated_at') or '')[:19]
    return item


def _help_request_recipient_label(employee_id, employee_index=None, users=None):
    normalized_id = str(employee_id or '').strip()
    employee_lookup = employee_index or _build_employee_index()
    employee = employee_lookup.get(normalized_id, {})
    if employee.get('name'):
        return str(employee.get('name')).strip()

    user_rows = users if users is not None else read_csv(USERS_CSV)
    user = next((row for row in user_rows if str(row.get('id', '')).strip() == normalized_id), {})
    if user.get('full_name'):
        return str(user.get('full_name')).strip()
    if user.get('username'):
        return str(user.get('username')).strip()
    return normalized_id


def _resolve_help_request_recipients(requester_id, recipient_type='manager', explicit_recipient_id=None):
    requester = str(requester_id or '').strip()
    explicit = str(explicit_recipient_id or '').strip()
    employees = read_csv(EMP_CSV)
    users = read_csv(USERS_CSV)
    employee_index = _build_employee_index(employees)
    role_map = _build_role_map(users)
    requester_row = employee_index.get(requester, {})

    recipients = []
    if explicit and explicit != requester:
        recipients.append(explicit)
    elif recipient_type == 'teammate':
        manager_id = get_manager_for_employee(requester)
        if manager_id:
            recipients.extend([
                member_id for member_id in _normalize_list_strings(get_team_members(manager_id))
                if member_id != requester
            ])
        if not recipients:
            same_department = _normalize_text(requester_row.get('department'))
            same_company = _normalize_text(requester_row.get('company'))
            for employee in employees:
                employee_id = str(employee.get('id') or '').strip()
                if not employee_id or employee_id == requester:
                    continue
                role = role_map.get(employee_id, 'employee')
                if role in {'admin', 'manager', 'hr'}:
                    continue
                if same_department and _normalize_text(employee.get('department')) != same_department:
                    continue
                if same_company and _normalize_text(employee.get('company')) != same_company:
                    continue
                recipients.append(employee_id)
    else:
        manager_id = get_manager_for_employee(requester)
        if manager_id and manager_id != requester:
            recipients.append(manager_id)
        if not recipients:
            fallback_manager = next((
                user_id for user_id, role in role_map.items()
                if role == 'manager' and user_id != requester
            ), '')
            if fallback_manager:
                recipients.append(fallback_manager)
        if not recipients:
            fallback_admin = next((
                user_id for user_id, role in role_map.items()
                if role == 'admin' and user_id != requester
            ), '')
            if fallback_admin:
                recipients.append(fallback_admin)

    normalized = _normalize_list_strings(recipients)
    return [
        {
            'id': recipient_id,
            'name': _help_request_recipient_label(recipient_id, employee_index=employee_index, users=users),
        }
        for recipient_id in normalized
    ]


def _normalize_help_request_rows(rows):
    normalized = []
    for row in rows or []:
        item = {field: str(row.get(field, '') or '').strip() for field in HELP_REQUEST_FIELDNAMES}
        if item['status'] not in {'pending', 'cancelled', 'accepted', 'completed'}:
            item['status'] = 'pending'
        if item['urgency'] not in {'low', 'medium', 'high'}:
            item['urgency'] = 'medium'
        normalized.append(item)
    normalized.sort(key=lambda entry: entry.get('created_at', ''), reverse=True)
    return normalized


def calculate_project_progress(project_id):
    """Calculate project progress based on tasks"""
    tasks = read_csv(TASKS_CSV)
    project_tasks = [t for t in tasks if t.get('project_id') == project_id]
    if not project_tasks:
        return 0

    progress_sum = sum(int(t.get('progress', 0) or 0) for t in project_tasks)
    return int(progress_sum / len(project_tasks)) if project_tasks else 0


def calculate_employee_productivity(employee_id):
    """Calculate productivity percentage for an employee"""
    tasks = read_csv(TASKS_CSV)
    emp_tasks = [t for t in tasks if t.get('assignee_id') == employee_id]

    if not emp_tasks:
        return 0

    completed = len([t for t in emp_tasks if t.get('status') == 'completed'])
    productivity = (completed / len(emp_tasks)) * 100

    return int(productivity)


def update_project_progress(project_id):
    """Update project progress in database"""
    if not _use_database(PROJECTS_CSV) or DB_BACKEND != 'mongodb':
        return
    try:
        progress = calculate_project_progress(project_id)
        proj_coll = _mongo_collection('projects')
        proj_coll.update_one({'id': project_id}, {'$set': {'progress': str(progress)}})
    except:
        pass


@app.route('/api/system/health')
def api_system_health():
    """Check system health including MongoDB and MySQL connectivity."""
    mongo_connected = False
    mongo_status = "Disconnected"
    mysql_connected = False
    mysql_status = "Disconnected"

    try:
        if MongoClient is not None:
            client = _mongo_client()
            client.admin.command('ping')
            mongo_connected = True
            mongo_status = "Connected"
    except Exception as e:
        mongo_status = f"Error: {str(e)[:50]}"

    try:
        if mysql is not None:
            conn = _mysql_connect(include_database=False)
            conn.close()
            mysql_connected = True
            mysql_status = "Connected"
    except Exception as e:
        mysql_status = f"Error: {str(e)[:50]}"

    return jsonify({
        'mongodb': {
            'connected': mongo_connected,
            'status': mongo_status,
            'uri': MONGO_URI if mongo_connected else 'N/A',
            'database': MONGO_DATABASE
        },
        'mysql': {
            'connected': mysql_connected,
            'status': mysql_status,
            'host': MYSQL_HOST,
            'database': MYSQL_DATABASE,
        },
        'backend': DB_BACKEND,
        'mirrors': {
            'mysql': MIRROR_MYSQL,
            'mongodb': MIRROR_MONGODB,
            'csv_shadow': CSV_SHADOW_SYNC,
        },
        'timestamp': datetime.now().isoformat()
    })

@app.route('/static/<path:p>')
def static_proxy(p):
    return send_from_directory(os.path.join(BASE_DIR, 'static'), p)

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

def _role_redirect(role):
    role = normalize_role(role)
    if role == 'platform_admin':
        return redirect(f"{TASKVISE_ADMIN_URL}/dashboard")
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    if role == 'manager':
        return redirect(url_for('manager_dashboard'))
    if role == 'hr':
        return redirect(url_for('hr_dashboard'))
    if role == 'teamlead':
        return redirect(url_for('teamlead_dashboard'))
    return redirect(url_for('employee_dashboard'))

def _start_user_session(user_row):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    normalized_role = normalize_role(user_row.get('role', 'employee'))
    update_by_id(EMP_CSV, user_row['id'], {
        'last_login': now
    }, EMP_FIELDNAMES)
    employee_row = find_by_id(EMP_CSV, user_row['id']) or {}

    session['user_id'] = user_row['id']
    session['username'] = user_row['username']
    session['role'] = normalized_role
    session['full_name'] = user_row.get('full_name', '')
    session['email'] = user_row.get('username', employee_row.get('email', ''))
    session['last_login'] = now
    session['join_date'] = employee_row.get('join_date', '')
    return _role_redirect(normalized_role)

def _google_redirect_uri():
    configured = (GOOGLE_REDIRECT_URI or '').strip()
    if configured:
        return configured
    return url_for('google_callback', _external=True)

@app.route('/auth/google')
def google_login():
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return render_template('login.html', error='Google Sign-In is not configured.')

    redirect_uri = _google_redirect_uri()
    parsed_redirect = parse.urlparse(redirect_uri)
    current_host = (request.host or '').split(':')[0].lower()
    target_host = (parsed_redirect.hostname or '').lower()
    if target_host and current_host and target_host != current_host:
        aligned_login_url = parse.urlunparse((
            request.scheme,
            parsed_redirect.netloc,
            url_for('google_login'),
            '',
            '',
            ''
        ))
        return redirect(aligned_login_url)

    state = uuid.uuid4().hex
    session['google_oauth_state'] = state
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'prompt': 'select_account',
    }
    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + parse.urlencode(params)
    return redirect(auth_url)

@app.route('/auth/google/callback')
def google_callback():
    if request.args.get('error'):
        return render_template('login.html', error='Google Sign-In was cancelled or denied.')

    state = request.args.get('state', '')
    expected_state = session.pop('google_oauth_state', None)
    if not state or not expected_state or state != expected_state:
        return render_template('login.html', error='Google Sign-In failed. Please try again.')

    code = request.args.get('code')
    if not code:
        return render_template('login.html', error='Google Sign-In failed. Missing authorization code.')

    try:
        redirect_uri = _google_redirect_uri()
        token_payload = parse.urlencode({
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }).encode('utf-8')

        token_request = urllib_request.Request(
            'https://oauth2.googleapis.com/token',
            data=token_payload,
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        with urllib_request.urlopen(token_request, timeout=12) as token_response:
            token_data = json.loads(token_response.read().decode('utf-8'))

        access_token = token_data.get('access_token', '')
        if not access_token:
            return render_template('login.html', error='Google Sign-In failed while getting access token.')

        profile_request = urllib_request.Request(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
        )
        with urllib_request.urlopen(profile_request, timeout=12) as profile_response:
            profile_data = json.loads(profile_response.read().decode('utf-8'))

        email = (profile_data.get('email') or '').strip().lower()
        if not email:
            return render_template('login.html', error='Google account email is unavailable.')

        users = read_csv(USERS_CSV)
        matched_user = next(
            (
                u for u in users
                if ((u.get('username') or u.get('email') or '').strip().lower() == email)
                and _truthy(u.get('is_active', 'true'), default=True)
            ),
            None
        )
        if not matched_user:
            session['google_profile'] = {
                'email': email,
                'full_name': profile_data.get('name', ''),
                'picture': profile_data.get('picture', '')
            }
            return redirect(url_for('google_onboarding'))

        return _start_user_session(matched_user)
    except urllib_error.HTTPError as e:
        body = ''
        try:
            body = e.read().decode('utf-8', errors='ignore')
        except Exception:
            body = ''
        print(f'Google OAuth HTTP error: {e.code} {body}')
        parsed = {}
        try:
            parsed = json.loads(body) if body else {}
        except Exception:
            parsed = {}
        error_code = str(parsed.get('error') or '').lower()
        error_description = str(parsed.get('error_description') or '').strip()
        lower_body = body.lower()
        if 'invalid_client' in lower_body or error_code == 'invalid_client':
            return render_template('login.html', error='Google OAuth client credentials are invalid. Recheck Client ID/Secret.')
        if 'redirect_uri_mismatch' in lower_body or error_code == 'redirect_uri_mismatch':
            return render_template(
                'login.html',
                error=f'Google redirect URI mismatch. Configure: {_google_redirect_uri()}'
            )
        if error_description:
            return render_template('login.html', error=f'Google Sign-In failed: {error_description}')
        return render_template('login.html', error='Google Sign-In is unavailable right now. Try email/password.')
    except urllib_error.URLError as e:
        reason = str(getattr(e, 'reason', '') or '').strip()
        print(f'Google OAuth URL error: {reason}')
        if reason:
            return render_template('login.html', error=f'Google Sign-In network error: {reason}')
        return render_template('login.html', error='Google Sign-In is unavailable right now. Try email/password.')
    except Exception as e:
        print(f'Google OAuth error: {e}')
        return render_template('login.html', error='Google Sign-In is unavailable right now. Try email/password.')


@app.route('/auth/google/onboarding', methods=['GET', 'POST'])
def google_onboarding():
    profile = session.get('google_profile')
    if not profile:
        return redirect(url_for('login'))

    if request.method == 'POST':
        role = request.form.get('role')
        designation = request.form.get('designation', '').strip()
        department = request.form.get('department', '').strip()
        skills = request.form.get('skills', '').strip()

        if not role or not designation or not department or not skills:
            return render_template('google_onboarding.html', profile=profile, error='All fields are required.')

        users = read_csv(USERS_CSV)
        if any(u.get('username', '').strip().lower() == profile.get('email', '') for u in users):
            session.pop('google_profile', None)
            return redirect(url_for('login'))

        new_user_id = get_next_workforce_id(users, read_csv(EMP_CSV))
        password = generate_secure_password()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        user_row = {
            'id': new_user_id,
            'username': profile.get('email', ''),
            'password_hash': generate_password_hash(password),
            'full_name': profile.get('full_name', ''),
            'role': normalize_role(role),
            'created_at': now,
            'is_active': 'true'
        }

        employee_row = {
            'id': new_user_id,
            'name': profile.get('full_name', ''),
            'email': profile.get('email', ''),
            'position': designation,
            'department': department,
            'company': get_default_company_name(),
            'join_date': now,
            'phone': '',
            'skills': skills,
            'location': '',
            'last_login': now,
            'password_last_changed': now,
            'avatar_url': profile.get('picture', ''),
            'status': 'active',
            'productivity': '80'
        }

        persist_workforce_profile(user_row, employee_row)

        if _use_database(USERS_CSV) and DB_BACKEND == 'mongodb':
            import time
            time.sleep(0.5)
            stored_users = read_csv(USERS_CSV)
            for u in stored_users:
                if u.get('id') == new_user_id:
                    user_row = u
                    break

        session.pop('google_profile', None)
        return _start_user_session(user_row)

    return render_template('google_onboarding.html', profile=profile)


def authenticate_user_credentials(username, password, allowed_roles=None):
    ensure_demo_org_integrity()
    username_norm = str(username or '').strip().lower()
    password_norm = str(password or '').strip()
    allowed = {normalize_role(role) for role in (allowed_roles or []) if normalize_role(role)}
    users = read_csv(USERS_CSV)

    for user in users:
        identifier = str(user.get('username') or user.get('email') or '').strip().lower()
        role = normalize_role(user.get('role', 'employee'))
        is_active = _truthy(user.get('is_active', 'true'), default=True)
        if identifier != username_norm or not is_active:
            continue
        if allowed and role not in allowed:
            continue
        stored_hash = user.get('password_hash')
        stored_plain = user.get('password')
        if stored_hash and verify_password(stored_hash, password_norm):
            return user
        if stored_plain is not None and verify_password(stored_plain, password_norm):
            return user
    return None


@app.route('/login', methods=['GET','POST'])
def login():
    ensure_demo_org_integrity()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        matched_user = authenticate_user_credentials(
            username,
            password,
            allowed_roles={'admin', 'manager', 'hr', 'teamlead', 'employee'}
        )
        if matched_user:
            return _start_user_session(matched_user)
        return render_template('login.html', error='Invalid email or password')

    return render_template('login.html')


@app.route('/taskvise-admin/login', methods=['GET', 'POST'])
def taskvise_admin_login():
    return redirect(f"{TASKVISE_ADMIN_URL}/login")

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('fullName')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        designation = request.form.get('designation')
        department = request.form.get('department')
        skills = request.form.get('skills', '')

        print(f"Form data received: {full_name}, {email}, {phone}, {role}, {designation}, {department}, {skills}")

        if not all([full_name, email, phone, role, designation, department, skills]):
            return render_template('signup.html', error='All fields are required')

        users = read_csv(USERS_CSV)
        if any(u['username'] == email for u in users):
            return render_template('signup.html', error='User with this email already exists')

        user_id = get_next_workforce_id(users, read_csv(EMP_CSV))
        password = generate_secure_password()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        user_row = {
            'id': user_id,
            'username': email,
            'password_hash': generate_password_hash(password),
            'full_name': full_name,
            'role': normalize_role(role),
            'created_at': current_time,
            'is_active': 'true'
        }

        employee_row = {
            'id': user_id,
            'name': full_name,
            'email': email,
            'position': designation,
            'department': department,
            'company': get_default_company_name(),
            'join_date': current_time,
            'phone': phone,
            'skills': skills,
            'location': '',
            'last_login': '',
            'password_last_changed': current_time,
            'avatar_url': '',
            'status': 'active',
            'productivity': '76'
        }

        print(f"User row: {user_row}")
        print(f"Employee row: {employee_row}")

        try:
            storage_status = persist_workforce_profile(user_row, employee_row)
            print("User and employee saved successfully")
            print(f"Storage status: {storage_status}")
        except Exception as e:
            print(f"Error saving account data: {e}")
            return render_template('signup.html', error=f'Error saving data: {e}')

        return redirect(url_for('show_credentials',
                              employee_id=user_id,
                              employee_name=full_name,
                              username=email,
                              password=password,
                              role=role))

    return render_template('signup.html')

@app.route('/credentials')
def show_credentials():
    employee_id = request.args.get('employee_id', '')
    employee_name = request.args.get('employee_name', '')
    username = request.args.get('username', '')
    password = request.args.get('password', '')
    role = request.args.get('role', 'employee')

    if not all([employee_name, username, password]):
        return redirect(url_for('signup'))

    return render_template('credentials.html',
                         employee_id=employee_id,
                         employee_name=employee_name,
                         username=username,
                         password=password,
                         role=role,
                         get_role_title=get_role_title,
                         get_role_description=get_role_description,
                         get_role_access_description=get_role_access_description)

def get_role_color(role):
    """Get CSS class for role badge colors"""
    role = normalize_role(role)
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

    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8 + random.randint(0, 2)))

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

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role', 'employee')
    if role == 'platform_admin':
        return redirect(f"{TASKVISE_ADMIN_URL}/dashboard")
    elif role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'manager':
        return redirect(url_for('manager_dashboard'))
    elif role == 'hr':
        return redirect(url_for('hr_dashboard'))
    elif role == 'teamlead':
        return redirect(url_for('teamlead_dashboard'))
    else:
        return redirect(url_for('employee_dashboard'))

def _render_admin_dashboard():
    payload = get_admin_dashboard_payload()
    analytics = build_admin_analytics_payload(payload['employees'], payload['projects'], payload['tasks'])
    skill_gap = build_admin_skill_gap_payload(payload['employees'], payload['projects'], payload['tasks'])
    system_settings, _settings_rows = get_admin_system_settings_record()
    demo_credentials = build_demo_credentials_payload()
    employee_data = get_employee_dashboard_data(session.get('user_id'))
    return render_template('admin_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         stats=payload['stats'],
                         recent_activity=payload['recent_activity'],
                         employees=payload['employees'],
                         tasks=payload['tasks'],
                         projects=payload['projects'],
                         analytics=analytics,
                         department_stats=analytics.get('department_stats', []),
                         monthly_stats=analytics.get('monthly_stats', []),
                         top_performers=analytics.get('top_performers', []),
                         workload_insights=analytics.get('workload_insights', []),
                         role_distribution=analytics.get('role_distribution', []),
                         company_overview=analytics.get('company_overview', []),
                         skill_gap=skill_gap,
                         skill_gap_rows=skill_gap.get('rows', []),
                         departments=skill_gap.get('departments', []),
                         profile=employee_data['profile'],
                         system_settings=system_settings,
                         demo_credentials=demo_credentials)


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return _render_admin_dashboard()


@app.route('/admin/employees')
@admin_required
def admin_employees():
    return _render_admin_dashboard()


@app.route('/admin/projects')
@admin_required
def admin_projects():
    return _render_admin_dashboard()


@app.route('/admin/tasks')
@admin_required
def admin_tasks():
    return _render_admin_dashboard()


@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    return _render_admin_dashboard()


@app.route('/api/admin/employees', methods=['GET', 'POST'])
@admin_required
def api_admin_employees():
    if request.method == 'GET':
        payload = get_admin_dashboard_payload()
        employees = _sort_rows_by_id(payload['employees'], WORKFORCE_ID_PREFIX)
        return jsonify(employees)

    if request.method == 'POST':
        data = request.get_json() or {}
        required = ['name', 'email', 'position', 'department', 'role']
        if any(not data.get(field) for field in required):
            return jsonify({'error': 'Missing required employee fields'}), 400

        all_users = read_csv(USERS_CSV)
        if any(u.get('username','').strip().lower() == data['email'].strip().lower() for u in all_users):
            return jsonify({'error': 'User with this email already exists'}), 409

        new_id = get_next_workforce_id(all_users, read_csv(EMP_CSV))
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        provided_password = str(data.get('password', '') or '').strip()
        login_password = provided_password or generate_secure_password()

        user_row = {
            'id': new_id,
            'username': data['email'].strip().lower(),
            'password_hash': generate_password_hash(login_password),
            'full_name': data['name'].strip(),
            'role': normalize_role(data['role']),
            'created_at': now,
            'is_active': 'true'
        }

        employee_row = {
            'id': new_id,
            'name': data['name'].strip(),
            'email': data['email'].strip().lower(),
            'position': data['position'].strip(),
            'department': data['department'].strip(),
            'company': str(data.get('company') or get_default_company_name()).strip(),
            'join_date': now,
            'phone': data.get('phone','').strip(),
            'skills': data.get('skills','').strip(),
            'location': data.get('location','').strip(),
            'last_login': '',
            'password_last_changed': now,
            'avatar_url': '',
            'status': 'active',
            'productivity': str(_safe_int(data.get('productivity', 78), 78))
        }

        storage_status = persist_workforce_profile(user_row, employee_row)

        return jsonify({
            'message': 'Employee created',
            'id': new_id,
            'temporary_password': None if provided_password else login_password,
            'storage_status': storage_status,
        }), 201


@app.route('/api/admin/employees/<employee_id>', methods=['DELETE'])
@admin_required
def api_admin_employees_delete(employee_id):
    deleted1 = delete_by_id(EMP_CSV, employee_id, EMP_FIELDNAMES)
    deleted2 = delete_by_id(USERS_CSV, employee_id, USER_FIELDNAMES)

    member_rows = read_csv(PROJECT_MEMBERS_CSV)
    filtered_members = [
        row for row in member_rows
        if str(row.get('employee_id', '')).strip() != str(employee_id).strip()
    ]
    if len(filtered_members) != len(member_rows):
        write_csv(
            PROJECT_MEMBERS_CSV,
            filtered_members,
            merge_fieldnames(filtered_members if filtered_members else member_rows, PROJECT_MEMBER_FIELDNAMES),
        )

    project_rows = read_csv(PROJECTS_CSV)
    project_changed = False
    for project in project_rows:
        current_members = _parse_team_members(project, filtered_members)
        next_members = [member_id for member_id in current_members if member_id != str(employee_id).strip()]
        if next_members != current_members:
            project['team_members'] = ','.join(next_members)
            project_changed = True
    if project_changed:
        write_csv(PROJECTS_CSV, project_rows, merge_fieldnames(project_rows, PROJECT_FIELDNAMES))

    task_rows = read_csv(TASKS_CSV)
    task_changed = False
    for task in task_rows:
        if str(task.get('assignee_id', '')).strip() == str(employee_id).strip():
            task['assignee_id'] = ''
            task['assignee_name'] = ''
            task_changed = True
    if task_changed:
        write_csv(TASKS_CSV, task_rows, merge_fieldnames(task_rows, TASK_FIELDNAMES))

    if deleted1 or deleted2:
        ensure_demo_org_integrity(force=True)
        return jsonify({'message':'Employee deleted'}), 200
    return jsonify({'error':'Employee not found'}), 404


@app.route('/api/admin/employees/<employee_id>', methods=['PUT'])
@admin_required
def api_admin_employees_update(employee_id):
    data = request.get_json(force=True) or {}
    if not data:
        return jsonify({'error': 'invalid_payload'}), 400

    allowed = ['name', 'email', 'position', 'department', 'company', 'phone', 'location', 'skills', 'role', 'status', 'productivity']
    employee_updates = {k: v for k, v in data.items() if k in allowed}
    if not employee_updates:
        return jsonify({'error': 'nothing_to_update'}), 400

    if 'email' in employee_updates:
        normalized_email = str(employee_updates['email'] or '').strip().lower()
        all_users = read_csv(USERS_CSV)
        collision = next(
            (
                user for user in all_users
                if str(user.get('id', '')).strip() != str(employee_id).strip()
                and str(user.get('username', '')).strip().lower() == normalized_email
            ),
            None
        )
        if collision:
            return jsonify({'error': 'email_already_exists'}), 409
        employee_updates['email'] = normalized_email

    if 'role' in employee_updates:
        employee_updates['role'] = normalize_role(employee_updates['role'])
    if 'status' in employee_updates:
        employee_updates['status'] = str(employee_updates['status'] or 'active').strip().lower()
    if 'company' in employee_updates:
        employee_updates['company'] = str(employee_updates['company'] or get_default_company_name()).strip()
    if 'productivity' in employee_updates:
        employee_updates['productivity'] = str(max(0, min(100, _safe_int(employee_updates.get('productivity', 0), 0))))

    updated_emp = update_by_id(EMP_CSV, employee_id, employee_updates, EMP_FIELDNAMES)

    user_updates = {}
    if 'role' in employee_updates:
        user_updates['role'] = employee_updates['role']
    if 'email' in employee_updates:
        user_updates['username'] = employee_updates['email']
    if 'name' in employee_updates:
        user_updates['full_name'] = employee_updates['name']
    if 'status' in employee_updates:
        user_updates['is_active'] = 'true' if employee_updates['status'] != 'inactive' else 'false'

    updated_user = False
    if user_updates:
        if update_by_id(USERS_CSV, employee_id, user_updates, USER_FIELDNAMES):
            updated_user = True

    if not updated_emp and not updated_user:
        return jsonify({'error': 'employee_not_found'}), 404

    ensure_demo_org_integrity(force=True)
    return jsonify({'ok': True})


@app.route('/api/admin/tasks', methods=['GET', 'POST'])
@admin_required
def api_admin_tasks():
    if request.method == 'GET':
        payload = get_admin_dashboard_payload()
        return jsonify(payload['tasks'])

    data = request.get_json(force=True) or {}
    title = str(data.get('title', '')).strip()
    assignee_id = str(data.get('assignedTo', data.get('assignee_id', '')) or '').strip()
    due_date = str(data.get('due_date', data.get('dueDate', '')) or '').strip()[:10]
    if not title or not assignee_id or not due_date:
        return jsonify({'error': 'Missing required task fields'}), 400

    employees = _build_employee_index()
    assignee = employees.get(assignee_id)
    if not assignee:
        return jsonify({'error': 'assignee_not_found'}), 404

    tasks = read_csv(TASKS_CSV)
    task_id = _next_prefixed_id('TSK', tasks, 5)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    row = {
        'id': task_id,
        'title': title,
        'description': str(data.get('description', '') or '').strip(),
        'project_id': str(data.get('project', data.get('project_id', '')) or '').strip(),
        'assignee_id': assignee_id,
        'assignee_name': assignee.get('name', ''),
        'status': normalize_task_status(data.get('status', 'pending')),
        'priority': str(data.get('priority', 'medium') or 'medium').strip().lower(),
        'created_at': now,
        'due_date': due_date,
        'estimated_hours': str(int(data.get('estimatedHours', data.get('estimated_hours', 0)) or 0)),
        'actual_hours': str(int(data.get('actualHours', data.get('actual_hours', 0)) or 0)),
        'progress': str(max(0, min(100, int(data.get('progress', 0) or 0)))),
    }
    append_csv(TASKS_CSV, row, TASK_FIELDNAMES)
    notify_task_assignment(row, actor_label=session.get('full_name') or 'Administrator', is_new_assignment=True)
    return jsonify({'ok': True, 'id': task_id}), 201


@app.route('/api/admin/tasks/<task_id>', methods=['PUT', 'DELETE'])
@admin_required
def api_admin_task_detail(task_id):
    if request.method == 'DELETE':
        task = find_by_id(TASKS_CSV, task_id)
        deleted = delete_by_id(TASKS_CSV, task_id, TASK_FIELDNAMES)
        if not deleted:
            return jsonify({'error': 'task_not_found'}), 404
        if task and str(task.get('assignee_id', '')).strip():
            notify_user(
                task.get('assignee_id'),
                'Task Removed',
                f'Task "{task.get("title", "Untitled Task")}" was removed from your assignments.',
                'task',
            )
        return jsonify({'ok': True})

    data = request.get_json(force=True) or {}
    task_before = find_by_id(TASKS_CSV, task_id)
    if not task_before:
        return jsonify({'error': 'task_not_found'}), 404
    updates = {}
    if 'title' in data:
        updates['title'] = str(data.get('title', '')).strip()
    if 'description' in data:
        updates['description'] = str(data.get('description', '') or '').strip()
    if 'priority' in data:
        updates['priority'] = str(data.get('priority', 'medium') or 'medium').strip().lower()
    if 'status' in data:
        updates['status'] = normalize_task_status(data.get('status'))
    if 'dueDate' in data or 'due_date' in data:
        updates['due_date'] = str(data.get('dueDate', data.get('due_date', '')) or '').strip()[:10]
    if 'estimatedHours' in data or 'estimated_hours' in data:
        updates['estimated_hours'] = str(int(data.get('estimatedHours', data.get('estimated_hours', 0)) or 0))
    if 'actualHours' in data or 'actual_hours' in data:
        updates['actual_hours'] = str(int(data.get('actualHours', data.get('actual_hours', 0)) or 0))
    if 'progress' in data:
        updates['progress'] = str(max(0, min(100, int(data.get('progress', 0) or 0))))
    if 'assignee_id' in data or 'assignedTo' in data:
        assignee_id = str(data.get('assignee_id', data.get('assignedTo', '')) or '').strip()
        employee = _build_employee_index().get(assignee_id)
        if assignee_id and not employee:
            return jsonify({'error': 'assignee_not_found'}), 404
        updates['assignee_id'] = assignee_id
        updates['assignee_name'] = employee.get('name', '') if employee else ''
    if 'project_id' in data or 'project' in data:
        updates['project_id'] = str(data.get('project_id', data.get('project', '')) or '').strip()
    if not updates:
        return jsonify({'error': 'nothing_to_update'}), 400

    updated = update_by_id(TASKS_CSV, task_id, updates, TASK_FIELDNAMES)
    if not updated:
        return jsonify({'error': 'task_not_found'}), 404
    task_after = find_by_id(TASKS_CSV, task_id) or {**task_before, **updates}
    if str(task_after.get('assignee_id', '')).strip():
        notify_task_assignment(
            task_after,
            actor_label=session.get('full_name') or 'Administrator',
            is_new_assignment=str(task_before.get('assignee_id', '')).strip() != str(task_after.get('assignee_id', '')).strip(),
        )
    return jsonify({'ok': True})


@app.route('/api/admin/projects', methods=['GET', 'POST'])
@admin_required
def api_admin_projects():
    if request.method == 'GET':
        payload = get_admin_dashboard_payload()
        return jsonify(payload['projects'])

    data = request.get_json(force=True) or {}
    name = str(data.get('name', '')).strip()
    deadline = str(data.get('deadline', data.get('end_date', '')) or '').strip()[:10]
    if not name or not deadline:
        return jsonify({'error': 'Missing required project fields'}), 400

    projects = read_csv(PROJECTS_CSV)
    project_id = _next_prefixed_id('PRJ', projects, 4)
    team_members = _normalize_list_strings(data.get('teamMembers', data.get('team_members', [])) or [])
    row = {
        'id': project_id,
        'name': name,
        'description': str(data.get('description', '') or '').strip(),
        'owner_id': str(data.get('owner_id', session.get('user_id', '')) or '').strip(),
        'start_date': datetime.now().strftime('%Y-%m-%d'),
        'end_date': deadline,
        'status': normalize_project_status(data.get('status', 'planning')),
        'team_members': ','.join(team_members),
        'company': str(data.get('company') or get_default_company_name()).strip(),
        'progress': str(max(0, min(100, int(data.get('progress', 0) or 0)))),
    }
    append_csv(PROJECTS_CSV, row, PROJECT_FIELDNAMES)
    _sync_project_members(project_id, team_members)
    notify_project_assignment(row, actor_label=session.get('full_name') or 'Administrator', is_new_assignment=True)
    return jsonify({'ok': True, 'id': project_id}), 201


@app.route('/api/admin/projects/<project_id>', methods=['PUT', 'DELETE'])
@admin_required
def api_admin_project_detail(project_id):
    if request.method == 'DELETE':
        deleted = delete_by_id(PROJECTS_CSV, project_id, PROJECT_FIELDNAMES)
        if not deleted:
            return jsonify({'error': 'project_not_found'}), 404
        _sync_project_members(project_id, [])
        task_rows = read_csv(TASKS_CSV)
        changed = False
        for task in task_rows:
            if str(task.get('project_id', '')).strip() == str(project_id).strip():
                task['project_id'] = ''
                changed = True
        if changed:
            write_csv(TASKS_CSV, task_rows, merge_fieldnames(task_rows, TASK_FIELDNAMES))
        return jsonify({'ok': True})

    data = request.get_json(force=True) or {}
    project_before = find_by_id(PROJECTS_CSV, project_id)
    if not project_before:
        return jsonify({'error': 'project_not_found'}), 404
    updates = {}
    if 'name' in data:
        updates['name'] = str(data.get('name', '')).strip()
    if 'description' in data:
        updates['description'] = str(data.get('description', '') or '').strip()
    if 'status' in data:
        updates['status'] = normalize_project_status(data.get('status', 'planning'))
    if 'deadline' in data or 'end_date' in data:
        updates['end_date'] = str(data.get('deadline', data.get('end_date', '')) or '').strip()[:10]
    if 'progress' in data:
        updates['progress'] = str(max(0, min(100, int(data.get('progress', 0) or 0))))
    if 'owner_id' in data:
        updates['owner_id'] = str(data.get('owner_id', '') or '').strip()
    if 'company' in data:
        updates['company'] = str(data.get('company') or get_default_company_name()).strip()
    team_members = None
    if 'teamMembers' in data or 'team_members' in data:
        team_members = _normalize_list_strings(data.get('teamMembers', data.get('team_members', [])) or [])
        updates['team_members'] = ','.join(team_members)
    if not updates:
        return jsonify({'error': 'nothing_to_update'}), 400

    updated = update_by_id(PROJECTS_CSV, project_id, updates, PROJECT_FIELDNAMES)
    if not updated:
        return jsonify({'error': 'project_not_found'}), 404
    if team_members is not None:
        _sync_project_members(project_id, team_members)
    project_after = find_by_id(PROJECTS_CSV, project_id) or {**project_before, **updates}
    notify_project_assignment(project_after, actor_label=session.get('full_name') or 'Administrator', is_new_assignment=False)
    return jsonify({'ok': True})


@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def api_admin_stats():
    payload = get_admin_dashboard_payload()
    tasks = payload['tasks']
    projects = payload['projects']
    employees = payload['employees']
    return jsonify({
        'totalEmployees': len(employees),
        'activeProjects': len([p for p in projects if p.get('status') in ['active','planning']]),
        'completedTasks': len([t for t in tasks if t.get('status') == 'completed']),
        'totalTasks': len(tasks)
    })


@app.route('/api/admin/settings', methods=['GET', 'PUT'])
@admin_required
def api_admin_settings_data():
    if request.method == 'GET':
        record, _rows = get_admin_system_settings_record()
        return jsonify(record)

    payload = request.get_json(force=True) or {}
    saved = save_admin_system_settings_record(payload)
    return jsonify({'ok': True, 'settings': saved})


@app.route('/admin/skill-gap-analysis')
@admin_required
def skill_gap_analysis():
    return _render_admin_dashboard()


@app.route('/admin/profile')
@admin_required
def admin_profile():
    return _render_admin_dashboard()


@app.route('/admin/settings')
@admin_required
def admin_settings():
    return _render_admin_dashboard()


@app.route('/manager/settings')
@login_required
def manager_settings():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    employee_data = get_employee_dashboard_data(user_id)
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='settings',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'],
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []),
                         profile=employee_data['profile'])




@app.route('/hr/dashboard')
@login_required
def hr_dashboard():
    if session.get('role') != 'hr':
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


@app.route('/hr/<string:view>')
@login_required
def hr_sub_view(view):
    if session.get('role') != 'hr':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    allowed = {
        'overview', 'employees', 'projects', 'tasks', 'leave', 'payments', 'workload-balancer',
        'skill-recommendations', 'team-notes', 'reports', 'notifications', 'profile', 'settings'
    }
    if view not in allowed:
        return redirect(url_for('hr_dashboard'))

    employee_data = get_employee_dashboard_data(user_id)
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view=view,
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'],
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []),
                         profile=employee_data['profile'])


@app.route('/teamlead/dashboard')
@login_required
def teamlead_dashboard():
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

@app.route('/teamlead/profile')
@login_required
def teamlead_profile():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    employee_data = get_employee_dashboard_data(user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='profile',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'],
                         profile=employee_data['profile'])

@app.route('/teamlead/settings')
@login_required
def teamlead_settings():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    employee_data = get_employee_dashboard_data(user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='settings',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'],
                         profile=employee_data['profile'])

@app.route('/employee/overview')
@login_required
def employee_overview():
    if session.get('role') not in ['employee', 'admin', 'manager', 'hr', 'teamlead']:
        return redirect(url_for('dashboard'))

    user_id = session['user_id']
    employee_data = get_employee_dashboard_data(user_id)

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
    employee_data = get_employee_dashboard_data(user_id)

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
    employee_data = get_employee_dashboard_data(user_id)

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
                         projects=manager_data['projects'],
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []))

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
                         projects=manager_data['projects'],
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []))

@app.route('/manager/payments')
@login_required
def manager_payments():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='payments',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'],
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []))

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
                         projects=manager_data['projects'],
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []))

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
                         projects=manager_data['projects'],
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []))

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
                         projects=manager_data['projects'],
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []))

@app.route('/manager/profile')
@login_required
def manager_profile():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    employee_data = get_employee_dashboard_data(user_id)
    return render_template('manager_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='profile',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'],
                         profile=employee_data['profile'])

@app.route('/api/manager/employees')
@login_required
def api_manager_employees():
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify([])
    manager_data = get_manager_data(session.get('user_id'))
    return jsonify(manager_data.get('employees', []))

@app.route('/api/manager/projects')
@login_required
def api_manager_projects():
    ensure_projects_team_members()
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify([])
    manager_data = get_manager_data(session.get('user_id'))
    return jsonify(manager_data.get('projects', []))

@app.route('/api/manager/notifications')
@login_required
def api_manager_notifications():
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify([])
    manager_data = get_manager_data(session.get('user_id'))
    return jsonify(manager_data.get('notifications', []))

@app.route('/api/manager/notifications/read-all', methods=['POST'])
@login_required
def api_manager_notifications_read_all():
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify({'error': 'forbidden'}), 403
    user_id = session.get('user_id')
    rows = read_csv(NOTIF_CSV)
    changed = False
    for row in rows:
        if str(row.get('user_id', '')).strip() != str(user_id).strip():
            continue
        if str(row.get('is_read', 'false')).lower() != 'true':
            row['is_read'] = 'true'
            changed = True
    if changed:
        write_csv(NOTIF_CSV, rows, merge_fieldnames(rows, NOTIFICATION_FIELDNAMES))
    return jsonify({'ok': True, 'updated': changed})

@app.route('/api/manager/notifications/<notification_id>/read', methods=['POST'])
@login_required
def api_manager_notification_read(notification_id):
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify({'error': 'forbidden'}), 403
    user_id = session.get('user_id')
    notification = find_by_id(NOTIF_CSV, notification_id)
    if not notification or str(notification.get('user_id', '')).strip() != str(user_id).strip():
        return jsonify({'error': 'notification_not_found'}), 404
    update_by_id(NOTIF_CSV, notification_id, {'is_read': 'true'}, NOTIFICATION_FIELDNAMES)
    return jsonify({'ok': True})

@app.route('/api/teamlead/notifications')
@login_required
def api_teamlead_notifications():
    if session.get('role') != 'teamlead':
        return jsonify({'error': 'forbidden'}), 403
    manager_data = get_manager_data(session.get('user_id'))
    return jsonify(manager_data.get('notifications', []))

@app.route('/api/teamlead/notifications/read-all', methods=['POST'])
@login_required
def api_teamlead_notifications_read_all():
    if session.get('role') != 'teamlead':
        return jsonify({'error': 'forbidden'}), 403
    user_id = session.get('user_id')
    rows = read_csv(NOTIF_CSV)
    changed = False
    for row in rows:
        if str(row.get('user_id', '')).strip() != str(user_id).strip():
            continue
        if str(row.get('is_read', 'false')).lower() != 'true':
            row['is_read'] = 'true'
            changed = True
    if changed:
        write_csv(NOTIF_CSV, rows, merge_fieldnames(rows, NOTIFICATION_FIELDNAMES))
    return jsonify({'ok': True, 'updated': changed})

@app.route('/api/teamlead/notifications/<notification_id>/read', methods=['POST'])
@login_required
def api_teamlead_notification_read(notification_id):
    if session.get('role') != 'teamlead':
        return jsonify({'error': 'forbidden'}), 403
    user_id = session.get('user_id')
    notification = find_by_id(NOTIF_CSV, notification_id)
    if not notification or str(notification.get('user_id', '')).strip() != str(user_id).strip():
        return jsonify({'error': 'notification_not_found'}), 404
    update_by_id(NOTIF_CSV, notification_id, {'is_read': 'true'}, NOTIFICATION_FIELDNAMES)
    return jsonify({'ok': True})

@app.route('/api/teamlead/employees')
@login_required
def api_teamlead_employees():
    if session.get('role') != 'teamlead':
        return jsonify([])
    manager_data = get_manager_data(session.get('user_id'))
    return jsonify(manager_data.get('employees', []))

@app.route('/api/teamlead/projects')
@login_required
def api_teamlead_projects():
    if session.get('role') != 'teamlead':
        return jsonify([])
    manager_data = get_manager_data(session.get('user_id'))
    return jsonify(manager_data.get('projects', []))

@app.route('/api/teamlead/tasks')
@login_required
def api_teamlead_tasks():
    if session.get('role') != 'teamlead':
        return jsonify([])
    manager_data = get_manager_data(session.get('user_id'))
    return jsonify(manager_data.get('tasks', []))

@app.route('/api/teamlead/analytics')
@login_required
def api_teamlead_analytics():
    if session.get('role') != 'teamlead':
        return jsonify({'error': 'forbidden'}), 403
    return jsonify(build_manager_analytics_payload(session.get('user_id')))

@app.route('/api/teamlead/tasks/assign', methods=['POST'])
@login_required
def api_teamlead_assign_task():
    if session.get('role') != 'teamlead':
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(force=True) or {}
    existing_tasks = read_csv(TASKS_CSV)
    task_id = get_next_task_id(existing_tasks)
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    assignee_id = str(data.get('assignee_id', data.get('assignedTo', '')) or '').strip()
    project_id = str(data.get('project_id', data.get('project', '')) or '').strip()
    assignee_name = data.get('assignee_name','')
    try:
        emps = read_csv(EMP_CSV)
        for e in emps:
            if str(e.get('id', '')).strip() == assignee_id:
                assignee_name = e.get('name') or assignee_name
                break
    except Exception:
        pass

    row = {
        'id': task_id,
        'title': data.get('title','Untitled Task'),
        'description': data.get('description',''),
        'project_id': project_id,
        'assignee_id': assignee_id,
        'assignee_name': assignee_name or '',
        'status': normalize_task_status(data.get('status','pending')),
        'priority': str(data.get('priority','medium') or 'medium').strip().lower(),
        'created_at': created_at,
        'due_date': str(data.get('due_date', data.get('dueDate', '')) or '')[:10],
        'estimated_hours': str(_safe_int(data.get('estimated_hours', data.get('estimatedHours', 0)), 0)),
        'actual_hours': str(_safe_int(data.get('actual_hours', data.get('actualHours', 0)), 0)),
        'progress': str(max(0, min(100, _safe_int(data.get('progress', 0), 0)))),
    }
    append_csv(TASKS_CSV, row, TASK_FIELDNAMES)
    notify_task_assignment(row, actor_label=session.get('full_name') or 'Team Lead', is_new_assignment=True)
    return jsonify({'id': task_id, 'ok': True})

@app.route('/api/teamlead/tasks/<task_id>', methods=['PUT', 'DELETE'])
@login_required
def api_teamlead_update_task(task_id):
    if session.get('role') != 'teamlead':
        return jsonify({'error': 'forbidden'}), 403
    return api_manager_update_task(task_id)

@app.route('/api/manager/tasks/<task_id>', methods=['PUT', 'DELETE'])
@login_required
def api_manager_update_task(task_id):
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify({'error': 'forbidden'}), 403

    if request.method == 'DELETE':
        task = find_by_id(TASKS_CSV, task_id)
        deleted = delete_by_id(TASKS_CSV, task_id, TASK_FIELDNAMES)
        if not deleted:
            return jsonify({'error': 'task_not_found'}), 404
        if task and str(task.get('assignee_id', '')).strip():
            notify_user(
                task.get('assignee_id'),
                'Task Removed',
                f'Task "{task.get("title", "Untitled Task")}" was removed from your assignments.',
                'task',
            )
        return jsonify({'ok': True})

    data = request.get_json(force=True) or {}
    existing_task = find_by_id(TASKS_CSV, task_id)
    if not existing_task:
        return jsonify({'error': 'task_not_found'}), 404

    updates = {}
    if 'title' in data:
        updates['title'] = str(data['title'] or '').strip()
    if 'description' in data:
        updates['description'] = str(data['description'] or '').strip()
    if 'priority' in data:
        updates['priority'] = str(data['priority'] or 'medium').strip().lower()
    if 'status' in data:
        updates['status'] = normalize_task_status(data['status'])
    if 'dueDate' in data or 'due_date' in data:
        raw_due_date = data.get('dueDate', data.get('due_date', ''))
        try:
            dt = datetime.fromisoformat(str(raw_due_date).replace('Z',''))
            updates['due_date'] = dt.strftime('%Y-%m-%d')
        except Exception:
            updates['due_date'] = str(raw_due_date)[:10]
    if 'estimatedHours' in data or 'estimated_hours' in data:
        updates['estimated_hours'] = str(max(0, _safe_int(data.get('estimatedHours', data.get('estimated_hours', 0)), 0)))
    if 'actualHours' in data or 'actual_hours' in data:
        updates['actual_hours'] = str(max(0, _safe_int(data.get('actualHours', data.get('actual_hours', 0)), 0)))
    if 'progress' in data:
        updates['progress'] = str(max(0, min(100, _safe_int(data.get('progress', 0), 0))))
    if 'project_id' in data or 'project' in data:
        updates['project_id'] = str(data.get('project_id', data.get('project', '')) or '').strip()
    if 'assignee_id' in data or 'assignedTo' in data:
        assignee_id = str(data.get('assignee_id', data.get('assignedTo', '')) or '').strip()
        assignee = next(
            (employee for employee in read_csv(EMP_CSV) if str(employee.get('id', '')).strip() == assignee_id),
            None,
        )
        if assignee_id and not assignee:
            return jsonify({'error': 'assignee_not_found'}), 404
        updates['assignee_id'] = assignee_id
        updates['assignee_name'] = assignee.get('name', '') if assignee else ''
    if not updates:
        return jsonify({'error': 'nothing_to_update'}), 400

    updated = update_by_id(TASKS_CSV, task_id, updates, TASK_FIELDNAMES)
    if not updated:
        return jsonify({'error': 'task_not_found'}), 404

    task_after = find_by_id(TASKS_CSV, task_id) or {**existing_task, **updates}
    if str(task_after.get('assignee_id', '')).strip():
        notify_task_assignment(
            task_after,
            actor_label=session.get('full_name') or session.get('role', 'Manager').title(),
            is_new_assignment=str(existing_task.get('assignee_id', '')).strip() != str(task_after.get('assignee_id', '')).strip(),
        )
    return jsonify({'ok': True})

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
    existing_projects = read_csv(PROJECTS_CSV)
    project_id = get_next_project_id(existing_projects)
    now = datetime.now().strftime('%Y-%m-%d')
    members = _normalize_list_strings(data.get('teamMembers', data.get('team_members', [])) or [])
    row = {
        'id': project_id,
        'name': data.get('name','').strip(),
        'description': data.get('description',''),
        'owner_id': str(data.get('owner_id') or session.get('user_id','')).strip(),
        'start_date': now,
        'end_date': str(data.get('deadline', data.get('end_date', '')) or '')[:10],
        'status': normalize_project_status(data.get('status','planning')),
        'team_members': ','.join(members),
        'company': str(data.get('company') or get_default_company_name()).strip(),
        'progress': str(max(0, min(100, _safe_int(data.get('progress', 0), 0)))),
    }
    append_csv(PROJECTS_CSV, row, PROJECT_FIELDNAMES)
    _sync_project_members(project_id, members)
    notify_project_assignment(row, actor_label=session.get('full_name') or 'Team Lead', is_new_assignment=True)
    return jsonify({'id': project_id, 'ok': True})

@app.route('/api/teamlead/projects/<project_id>', methods=['PUT'])
@login_required
def api_teamlead_update_project(project_id):
    if session.get('role') != 'teamlead':
        return jsonify({'error': 'forbidden'}), 403
    return api_manager_update_project(project_id)

@app.route('/api/teamlead/projects/<project_id>', methods=['DELETE'])
@login_required
def api_teamlead_delete_project(project_id):
    if session.get('role') != 'teamlead':
        return jsonify({'error': 'forbidden'}), 403
    return api_manager_delete_project(project_id)

@app.route('/api/manager/projects/<project_id>', methods=['PUT'])
@login_required
def api_manager_update_project(project_id):
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(force=True) or {}
    project_before = find_by_id(PROJECTS_CSV, project_id)
    if not project_before:
        return jsonify({'error': 'project_not_found'}), 404
    updates = {}
    for k in ['name', 'description']:
        if k in data:
            updates[k] = str(data[k] or '').strip()
    if 'status' in data:
        updates['status'] = normalize_project_status(data.get('status'))
    if 'deadline' in data or 'end_date' in data:
        raw_deadline = data.get('deadline', data.get('end_date', ''))
        try:
            dt = datetime.fromisoformat(str(raw_deadline).replace('Z',''))
            updates['end_date'] = dt.strftime('%Y-%m-%d')
        except Exception:
            updates['end_date'] = str(raw_deadline)[:10]
    if 'owner_id' in data:
        updates['owner_id'] = str(data.get('owner_id', '') or '').strip()
    if 'company' in data:
        updates['company'] = str(data.get('company') or get_default_company_name()).strip()
    if 'progress' in data:
        updates['progress'] = str(max(0, min(100, _safe_int(data.get('progress', 0), 0))))
    team_members = None
    if 'teamMembers' in data or 'team_members' in data:
        team_members = _normalize_list_strings(data.get('teamMembers', data.get('team_members', [])) or [])
        updates['team_members'] = ','.join(team_members)
    if not updates:
        return jsonify({'error': 'nothing_to_update'}), 400

    updated = update_by_id(PROJECTS_CSV, project_id, updates, PROJECT_FIELDNAMES)
    if not updated:
        return jsonify({'error': 'project_not_found'}), 404
    if team_members is not None:
        _sync_project_members(project_id, team_members)
    project_after = find_by_id(PROJECTS_CSV, project_id) or {**project_before, **updates}
    notify_project_assignment(
        project_after,
        actor_label=session.get('full_name') or session.get('role', 'Manager').title(),
        is_new_assignment=False,
    )
    return jsonify({'ok': True})

@app.route('/api/manager/projects/<project_id>', methods=['DELETE'])
@login_required
def api_manager_delete_project(project_id):
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify({'error': 'forbidden'}), 403

    deleted = delete_by_id(
        PROJECTS_CSV,
        project_id,
        ['id','name','description','owner_id','start_date','end_date','status']
    )
    if not deleted:
        return jsonify({'error': 'project_not_found'}), 404

    member_rows = read_csv(PROJECT_MEMBERS_CSV)
    filtered_members = [m for m in member_rows if str(m.get('project_id')) != str(project_id)]
    write_csv(
        PROJECT_MEMBERS_CSV,
        filtered_members,
        merge_fieldnames(member_rows, ['id', 'project_id', 'employee_id'])
    )

    task_rows = read_csv(TASKS_CSV)
    tasks_changed = False
    for task in task_rows:
        if str(task.get('project_id')) == str(project_id):
            task['project_id'] = ''
            tasks_changed = True
    if tasks_changed:
        write_csv(
            TASKS_CSV,
            task_rows,
            merge_fieldnames(task_rows, ['id','title','description','project_id','assignee_id','status','priority','created_at','due_date'])
        )

    return jsonify({'ok': True})

@app.route('/api/employee/tasks/update-status', methods=['POST'])
@login_required
def api_employee_update_task_status():
    ensure_demo_org_integrity()
    user_id = session.get('user_id')
    username = session.get('username')
    if not user_id and not username:
        return jsonify({'error': 'unauthorized'}), 401
    data = request.get_json(force=True) or {}
    task_id = data.get('task_id') or data.get('id')
    new_status = data.get('status')
    if not task_id or not new_status:
        return jsonify({'error': 'missing parameters'}), 400
    new_status = normalize_task_status(new_status)
    task, employee_id, _employee, _candidate_ids = _resolve_session_employee_task(task_id)
    if not task:
        return jsonify({'error': 'not found or forbidden'}), 404
    updates = {'status': new_status}
    if employee_id:
        updates['assignee_id'] = employee_id
    if new_status == 'completed':
        updates['progress'] = '100'
        if _safe_int(task.get('actual_hours', 0), 0) <= 0:
            updates['actual_hours'] = str(max(1, _safe_int(task.get('estimated_hours', 1), 1)))
    elif new_status == 'in-progress' and _safe_int(task.get('progress', 0), 0) <= 0:
        updates['progress'] = '10'
    updated = update_by_id(TASKS_CSV, task_id, updates, TASK_FIELDNAMES)
    if not updated:
        return jsonify({'error': 'update failed'}), 500
    updated_task = find_by_id(TASKS_CSV, task_id) or task
    if updated_task.get('project_id'):
        update_project_progress(updated_task['project_id'])
    notify_employee_progress_update(updated_task, employee_id or user_id, 'status', new_status.replace('-', ' '))
    return jsonify({'ok': True})


@app.route('/api/employee/tasks/start-timer', methods=['POST'])
@login_required
def api_employee_start_task_timer():
    ensure_demo_org_integrity()
    user_id = session.get('user_id')
    username = session.get('username')
    if not user_id and not username:
        return jsonify({'error': 'unauthorized'}), 401

    data = request.get_json(force=True) or {}
    task_id = str(data.get('task_id') or data.get('id') or '').strip()
    if not task_id:
        return jsonify({'error': 'missing_task_id'}), 400

    task, employee_id, _employee, _candidate_ids = _resolve_session_employee_task(task_id)
    if not task:
        return jsonify({'error': 'task_not_found'}), 404

    work_logs = read_csv(WORK_CSV)
    active_log = next((
        row for row in work_logs
        if str(row.get('employee_id', '')).strip() == str(employee_id or user_id).strip()
        and str(row.get('task_id', '')).strip() == task_id
        and not str(row.get('end_time') or '').strip()
    ), None)
    if active_log:
        return jsonify({'ok': True, 'already_running': True, 'work_log_id': active_log.get('id')})

    started_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    work_row = {
        'id': str(uuid.uuid4()),
        'employee_id': str(employee_id or user_id).strip(),
        'task_id': task_id,
        'start_time': started_at,
        'end_time': '',
        'duration_minutes': '0',
        'notes': str(data.get('notes') or 'Timer started from employee dashboard.').strip(),
    }
    append_csv(WORK_CSV, work_row, ['id', 'employee_id', 'task_id', 'start_time', 'end_time', 'duration_minutes', 'notes'])
    update_by_id(
        TASKS_CSV,
        task_id,
        {
            'assignee_id': str(employee_id or user_id).strip(),
            'status': 'in-progress',
            'progress': str(max(10, _safe_int(task.get('progress', 0), 0))),
        },
        TASK_FIELDNAMES,
    )
    updated_task = find_by_id(TASKS_CSV, task_id) or task
    if updated_task.get('project_id'):
        update_project_progress(updated_task['project_id'])
    notify_employee_progress_update(updated_task, employee_id or user_id, 'timer', 'started')
    return jsonify({'ok': True, 'work_log_id': work_row['id'], 'started_at': started_at})


@app.route('/api/employee/task-submissions')
@login_required
def api_employee_task_submissions():
    employee_id, _employee, candidate_ids, _employees = _resolve_current_employee_context()
    if not employee_id and not candidate_ids:
        return jsonify([])

    rows = [
        _serialize_task_submission(row)
        for row in read_csv(TASK_SUBMISSIONS_CSV)
        if str(row.get('employee_id') or '').strip() == str(employee_id or '').strip()
        or str(row.get('employee_id') or '').strip() in candidate_ids
    ]
    rows.sort(key=lambda row: row.get('created_at', ''), reverse=True)
    return jsonify(rows)


@app.route('/api/employee/tasks/upload', methods=['POST'])
@login_required
def api_employee_upload_task_submission():
    ensure_demo_org_integrity()
    employee_id, employee, candidate_ids, _employees = _resolve_current_employee_context()
    if not employee_id and not candidate_ids:
        return jsonify({'error': 'unauthorized'}), 401

    task_id = str(request.form.get('task_id') or '').strip()
    notes = str(request.form.get('notes') or '').strip()
    uploaded_file = request.files.get('submission') or request.files.get('file')
    if not task_id:
        return jsonify({'error': 'task_id_required'}), 400
    if not uploaded_file or not str(uploaded_file.filename or '').strip():
        return jsonify({'error': 'submission_file_required'}), 400
    if not _allowed_task_submission(uploaded_file.filename):
        return jsonify({'error': 'Only ZIP, RAR, and 7Z files are accepted.'}), 400

    task = next((
        row for row in read_csv(TASKS_CSV)
        if str(row.get('id') or '').strip() == task_id
        and task_matches_employee(
            row,
            candidate_ids,
            username=session.get('username'),
            full_name=session.get('full_name'),
        )
    ), None)
    if not task:
        return jsonify({'error': 'task_not_found'}), 404

    os.makedirs(TASK_SUBMISSION_UPLOAD_DIR, exist_ok=True)
    original_filename = secure_filename(uploaded_file.filename or 'submission.zip')
    stored_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}_{original_filename}"
    disk_path = os.path.join(TASK_SUBMISSION_UPLOAD_DIR, stored_filename)
    uploaded_file.save(disk_path)
    rel_static_path = os.path.join('uploads', 'task_submissions', stored_filename).replace('\\', '/')

    manager_id = str(get_manager_for_employee(employee_id) or '').strip()
    teamlead_id = str(get_teamlead_for_employee(employee_id) or '').strip()
    project_owner_id = str((find_by_id(PROJECTS_CSV, task.get('project_id')) or {}).get('owner_id') or '').strip()
    recipients = _normalize_list_strings([manager_id, teamlead_id, project_owner_id])
    recipients = [recipient for recipient in recipients if recipient and recipient != str(employee_id).strip()]

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    submission_row = {
        'id': str(uuid.uuid4()),
        'task_id': task_id,
        'project_id': str(task.get('project_id') or '').strip(),
        'employee_id': str(employee_id).strip(),
        'employee_name': str(employee.get('name') or session.get('full_name') or session.get('username') or 'Employee').strip(),
        'manager_id': manager_id,
        'teamlead_id': teamlead_id,
        'recipient_ids': ','.join(recipients),
        'original_filename': original_filename,
        'stored_filename': stored_filename,
        'file_path': rel_static_path,
        'file_size': str(os.path.getsize(disk_path)),
        'status': 'submitted',
        'notes': notes,
        'created_at': timestamp,
        'updated_at': timestamp,
    }
    append_csv(TASK_SUBMISSIONS_CSV, submission_row, TASK_SUBMISSION_FIELDNAMES)

    notify_users(
        recipients,
        'Task Package Uploaded',
        f'{submission_row["employee_name"]} uploaded "{original_filename}" for task "{task.get("title") or task_id}". Download: {_submission_download_path(submission_row)}',
        'task',
        email_subject='Task Package Uploaded',
    )

    return jsonify({'ok': True, 'submission': _serialize_task_submission(submission_row)})

@app.route('/api/employee/leave')
@login_required
def api_employee_leave_list():
    ensure_leave_data_integrity()
    user_id = session.get('user_id')
    username = session.get('username')
    full_name = session.get('full_name')
    if not user_id and not username:
        return jsonify([])

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

    rows = ensure_leave_data_integrity()
    mine = [l for l in rows if l.get('employee_id') in candidate_ids or (user_id and l.get('employee_id') == user_id)]
    for l in mine:
        try:
            sd = datetime.strptime((l.get('start_date') or '')[:10], '%Y-%m-%d').date()
            ed = datetime.strptime((l.get('end_date') or '')[:10], '%Y-%m-%d').date()
            days = (ed - sd).days + 1
            l['days'] = max(days, 0)
        except Exception:
            l['days'] = 0
        l['type'] = l.get('type','') or 'leave'
        l['status'] = normalize_leave_status(l.get('status'))
    mine.sort(key=lambda r: r.get('applied_at',''), reverse=True)
    return jsonify(mine)

@app.route('/api/employee/leave-request', methods=['POST'])
@login_required
def api_employee_leave_request():
    ensure_leave_data_integrity()
    data = request.get_json(force=True) or {}
    user_id = session.get('user_id')
    username = session.get('username')
    full_name = session.get('full_name')
    employee_rows = read_csv(EMP_CSV)
    employee_id = None
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
        'type': (data.get('type') or data.get('leaveType') or data.get('leave_type') or 'leave').lower(),
        'status': 'pending',
        'applied_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    append_csv(LEAVE_CSV, row, LEAVE_FIELDNAMES)
    return jsonify({'ok': True, 'id': row['id']})

@app.route('/api/employee/leave/apply', methods=['POST'])
@login_required
def api_employee_leave_apply():
    ensure_leave_data_integrity()
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401
    data = request.get_json(force=True) or {}
    leave_id = str(uuid.uuid4())
    row = {
        'id': leave_id,
        'employee_id': user_id,
        'start_date': (data.get('start_date') or data.get('startDate') or '')[:10],
        'end_date': (data.get('end_date') or data.get('endDate') or '')[:10],
        'reason': data.get('reason',''),
        'type': (data.get('type') or data.get('leaveType') or data.get('leave_type') or 'leave').lower(),
        'status': 'pending',
        'applied_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    append_csv(LEAVE_CSV, row, LEAVE_FIELDNAMES)
    return jsonify({'ok': True, 'id': leave_id})

@app.route('/api/manager/leave')
@login_required
def api_manager_leave_list():
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify([])
    actor_role = session.get('role')
    status = normalize_leave_status(request.args.get('status'))
    rows = ensure_leave_data_integrity()
    if actor_role not in {'hr', 'admin'}:
        visible_ids = {
            str(employee.get('id', '')).strip()
            for employee in get_manager_data(session.get('user_id')).get('employees', [])
            if str(employee.get('id', '')).strip()
        }
        rows = [row for row in rows if str(row.get('employee_id', '')).strip() in visible_ids]
    if status:
        rows = [r for r in rows if normalize_leave_status(r.get('status')) == status]
    return jsonify(rows)

@app.route('/api/manager/leave/update', methods=['POST'])
@login_required
def api_manager_leave_update():
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify({'error': 'forbidden'}), 403
    actor_role = session.get('role')
    data = request.get_json(force=True) or {}
    leave_id = data.get('id')
    new_status = normalize_leave_status(data.get('status'))
    if not leave_id or new_status not in VALID_LEAVE_STATUSES:
        return jsonify({'error': 'invalid'}), 400
    rows = ensure_leave_data_integrity()
    leave_row = next((r for r in rows if str(r.get('id')) == str(leave_id)), None)
    if not leave_row:
        return jsonify({'error': 'not found'}), 404
    if actor_role not in {'hr', 'admin'}:
        visible_ids = {
            str(employee.get('id', '')).strip()
            for employee in get_manager_data(session.get('user_id')).get('employees', [])
            if str(employee.get('id', '')).strip()
        }
        if str(leave_row.get('employee_id', '')).strip() not in visible_ids:
            return jsonify({'error': 'forbidden'}), 403

    updated = update_by_id(LEAVE_CSV, leave_id, {'status': new_status}, LEAVE_FIELDNAMES)
    if not updated:
        return jsonify({'error': 'not found'}), 404

    if new_status in ['approved', 'rejected']:
        leave_type = str(leave_row.get('type') or 'leave').replace('-', ' ').title()
        start_date = str(leave_row.get('start_date') or '')
        end_date = str(leave_row.get('end_date') or '')
        create_notification(
            leave_row.get('employee_id'),
            f"Leave Request {new_status.title()}",
            f"Your {leave_type} leave request ({start_date} to {end_date}) was {new_status}.",
            'leave',
        )
    return jsonify({'ok': True})

@app.route('/api/employee/notifications')
@login_required
def api_employee_notifications():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])

    rows = read_csv(NOTIF_CSV)
    mine = []
    for row in rows:
        if str(row.get('user_id', '')) != str(user_id):
            continue
        mine.append({
            'id': row.get('id', ''),
            'title': row.get('title', 'Notification'),
            'message': row.get('message', ''),
            'type': (row.get('type') or 'system').lower(),
            'is_read': str(row.get('is_read', 'false')).lower() == 'true',
            'created_at': row.get('created_at', ''),
        })

    mine.sort(key=lambda r: r.get('created_at', ''), reverse=True)
    return jsonify(mine)


@app.route('/api/employee/notifications/read-all', methods=['POST'])
@login_required
def api_employee_notifications_read_all():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401

    rows = read_csv(NOTIF_CSV)
    changed = False
    for row in rows:
        if str(row.get('user_id', '')).strip() != str(user_id).strip():
            continue
        if str(row.get('is_read', 'false')).lower() != 'true':
            row['is_read'] = 'true'
            changed = True
    if changed:
        write_csv(NOTIF_CSV, rows, merge_fieldnames(rows, NOTIFICATION_FIELDNAMES))
    return jsonify({'ok': True, 'updated': changed})


@app.route('/api/employee/notifications/<notification_id>/read', methods=['POST'])
@login_required
def api_employee_notification_read(notification_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401

    notification = find_by_id(NOTIF_CSV, notification_id)
    if not notification or str(notification.get('user_id', '')).strip() != str(user_id).strip():
        return jsonify({'error': 'notification_not_found'}), 404
    update_by_id(NOTIF_CSV, notification_id, {'is_read': 'true'}, NOTIFICATION_FIELDNAMES)
    return jsonify({'ok': True})


@app.route('/api/employee/notifications/<notification_id>', methods=['DELETE'])
@login_required
def api_employee_notification_delete(notification_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401

    notification = find_by_id(NOTIF_CSV, notification_id)
    if not notification or str(notification.get('user_id', '')).strip() != str(user_id).strip():
        return jsonify({'error': 'notification_not_found'}), 404
    delete_by_id(NOTIF_CSV, notification_id, NOTIFICATION_FIELDNAMES)
    return jsonify({'ok': True})

@app.route('/api/employee/profile/update', methods=['POST'])
@login_required
def api_employee_profile_update():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401
    data = request.get_json(force=True) or {}
    fields = {}
    user_updates = {}
    for k in ['name','email','phone','location','department','company','position','skills']:
        if k not in data:
            continue
        v = data[k]
        if k == 'skills' and isinstance(v, str):
            v = ','.join([s.strip() for s in v.split(',') if s.strip()])
        if k == 'email':
            v = str(v or '').strip().lower()
            if not v:
                continue
            users = read_csv(USERS_CSV)
            collision = next(
                (
                    user for user in users
                    if str(user.get('id', '')).strip() != str(user_id).strip()
                    and str(user.get('username', '')).strip().lower() == v
                ),
                None
            )
            if collision:
                return jsonify({'error': 'email_already_exists'}), 409
            user_updates['username'] = v
        elif k == 'name':
            user_updates['full_name'] = str(v or '').strip()
        fields[k] = v
    if not fields:
        return jsonify({'error': 'no changes'}), 400
    ids, _ = resolve_employee_candidate_ids(user_id, session.get('username'), session.get('full_name'))
    target_emp_id = next(iter(ids), None)
    if not target_emp_id:
        return jsonify({'error': 'employee_not_found'}), 404
    ok = update_by_id(EMP_CSV, target_emp_id, fields, EMP_FIELDNAMES)
    user_ok = True
    if user_updates:
        user_ok = update_by_id(USERS_CSV, user_id, user_updates, USER_FIELDNAMES)
        if user_updates.get('username'):
            session['username'] = user_updates['username']
        if user_updates.get('full_name'):
            session['full_name'] = user_updates['full_name']
    if ok or user_ok:
        ensure_demo_org_integrity(force=True)
    return jsonify({'ok': bool(ok or user_ok), 'success': bool(ok or user_ok)})

@app.route('/api/employee/profile/avatar', methods=['POST'])
@login_required
def api_employee_profile_avatar():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401

    avatar_file = request.files.get('avatar')
    if not avatar_file or not avatar_file.filename:
        return jsonify({'error': 'missing_file'}), 400

    original_name = secure_filename(avatar_file.filename)
    ext = os.path.splitext(original_name)[1].lower()
    if ext not in {'.png', '.jpg', '.jpeg', '.webp'}:
        return jsonify({'error': 'unsupported_file_type'}), 400

    try:
        os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)
        filename = f"{user_id}_{int(datetime.now().timestamp())}{ext}"
        disk_path = os.path.join(AVATAR_UPLOAD_DIR, filename)
        avatar_file.save(disk_path)

        rel_static_path = f"uploads/avatars/{filename}"
        ids, _ = resolve_employee_candidate_ids(user_id, session.get('username'), session.get('full_name'))
        target_emp_id = next(iter(ids), None)

        if target_emp_id:
            updated = update_by_id(EMP_CSV, target_emp_id, {'avatar_url': rel_static_path}, EMP_FIELDNAMES)
            if not updated:
                print(f"Warning: Couldn't update employee avatar row for id {target_emp_id}")
        else:
            print("Warning: no matching employee id found for avatar update (profile may be fallback account)")

        return jsonify({
            'ok': True,
            'success': True,
            'avatar_url': rel_static_path,
            'avatar_src': url_for('static', filename=rel_static_path)
        })
    except Exception as e:
        print(f"Avatar upload error:", e)
        return jsonify({'ok': False, 'success': False, 'error': str(e)}), 500

@app.route('/api/employee/password/update', methods=['POST'])
@login_required
def api_employee_password_update():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401
    data = request.get_json(force=True) or {}
    user_row = find_by_id(USERS_CSV, user_id)
    if not user_row:
        return jsonify({'error': 'user_not_found'}), 404

    current_password = str(data.get('current_password', data.get('currentPassword', '')) or '').strip()
    new_password = str(data.get('new_password', data.get('newPassword', '')) or '').strip()
    updates = {}

    if new_password:
        if not current_password:
            return jsonify({'error': 'current_password_required'}), 400
        stored_password = user_row.get('password_hash') or user_row.get('password') or ''
        if not verify_password(stored_password, current_password):
            return jsonify({'error': 'invalid_current_password'}), 400
        if len(new_password) < 6:
            return jsonify({'error': 'password_too_short'}), 400
        updates['password_hash'] = generate_password_hash(new_password)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_ok = True
    if updates:
        user_ok = update_by_id(USERS_CSV, user_id, updates, USER_FIELDNAMES)
    emp_ok = update_by_id(EMP_CSV, user_id, {'password_last_changed': timestamp}, EMP_FIELDNAMES)
    return jsonify({'ok': bool(user_ok and emp_ok), 'success': bool(user_ok and emp_ok)})

@app.route('/api/employee/password/change', methods=['POST'])
@login_required
def api_employee_password_change():
    return api_employee_password_update()

@app.route('/api/employee/settings')
@login_required
def api_employee_settings():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401
    settings, _rows = get_user_settings_record(user_id)
    return jsonify({
        'ok': True,
        'success': True,
        'settings': {
            'emailNotifications': _truthy(settings.get('email_notifications'), True),
            'pushNotifications': _truthy(settings.get('push_notifications')),
            'taskReminders': _truthy(settings.get('task_reminders'), True),
            'deadlineAlerts': _truthy(settings.get('deadline_alerts'), True),
            'theme': settings.get('theme', 'system'),
            'language': settings.get('language', 'en'),
            'timezone': settings.get('timezone', 'UTC'),
            'updatedAt': settings.get('updated_at', ''),
        }
    })

@app.route('/api/employee/settings/update', methods=['POST'])
@login_required
def api_employee_settings_update():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401

    data = request.get_json(force=True) or {}
    incoming = {
        'email_notifications': 'true' if _truthy(data.get('emailNotifications'), True) else 'false',
        'push_notifications': 'true' if _truthy(data.get('pushNotifications')) else 'false',
        'task_reminders': 'true' if _truthy(data.get('taskReminders'), True) else 'false',
        'deadline_alerts': 'true' if _truthy(data.get('deadlineAlerts'), True) else 'false',
        'theme': str(data.get('theme') or 'system'),
        'language': str(data.get('language') or 'en'),
        'timezone': str(data.get('timezone') or 'UTC'),
    }
    record = save_user_settings_record(user_id, incoming)
    return jsonify({'ok': True, 'success': True, 'settings': record})

@app.route('/api/employee/data/export')
@login_required
def api_employee_data_export():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401

    username = session.get('username')
    full_name = session.get('full_name')
    candidate_ids, _ = resolve_employee_candidate_ids(user_id, username, full_name)

    employee_data = get_employee_data(user_id)
    settings, _rows = get_user_settings_record(user_id)
    all_leaves = ensure_leave_data_integrity()
    leaves = [l for l in all_leaves if str(l.get('employee_id', '')) in {str(v) for v in candidate_ids}]
    notifications = [
        n for n in read_csv(NOTIF_CSV)
        if str(n.get('user_id', '')) == str(user_id)
    ]

    payload = {
        'exported_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user': {
            'id': user_id,
            'username': username,
            'full_name': full_name,
            'role': session.get('role', 'employee'),
        },
        'profile': employee_data.get('profile', {}),
        'stats': employee_data.get('stats', {}),
        'tasks': employee_data.get('tasks', []),
        'projects': employee_data.get('projects', []),
        'leave_requests': leaves,
        'notifications': notifications,
        'settings': settings,
    }
    return jsonify({'ok': True, 'success': True, 'data': payload})

@app.route('/api/employee/account/delete-request', methods=['POST'])
@login_required
def api_employee_account_delete_request():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'unauthorized'}), 401

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    users = read_csv(USERS_CSV)
    fieldnames = merge_fieldnames(users, ['id','username','password_hash','full_name','role','created_at','is_active','deletion_requested','deletion_requested_at'])
    ok = update_by_id(
        USERS_CSV,
        user_id,
        {'deletion_requested': 'true', 'deletion_requested_at': now},
        fieldnames
    )
    create_notification(
        user_id,
        'Account Deletion Request Submitted',
        'Your account deletion request has been recorded and sent for review.',
        'system'
    )
    return jsonify({'ok': bool(ok), 'success': bool(ok)})

@app.route('/api/manager/tasks')
@login_required
def api_manager_tasks():
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify([])
    manager_data = get_manager_data(session.get('user_id'))
    return jsonify(manager_data.get('tasks', []))

@app.route('/api/manager/tasks/assign', methods=['POST'])
@login_required
def api_manager_assign_task():
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(force=True) or {}
    existing_tasks = read_csv(TASKS_CSV)
    task_id = get_next_task_id(existing_tasks)
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    assignee_id = str(data.get('assignedTo', data.get('assignee_id', '')) or '').strip()
    project_id = str(data.get('project', data.get('project_id', '')) or '').strip()
    due_date = str(data.get('due_date', data.get('dueDate', '')) or '').strip()[:10]
    assignee_name = ''
    for employee in read_csv(EMP_CSV):
        if str(employee.get('id', '')).strip() == assignee_id:
            assignee_name = employee.get('name', '')
            break
    row = {
        'id': task_id,
        'title': data.get('title','').strip(),
        'description': data.get('description',''),
        'project_id': project_id,
        'assignee_id': assignee_id,
        'assignee_name': assignee_name,
        'status': normalize_task_status(data.get('status', 'pending')),
        'priority': str(data.get('priority','medium') or 'medium').strip().lower(),
        'created_at': created_at,
        'due_date': due_date,
        'estimated_hours': str(_safe_int(data.get('estimated_hours', data.get('estimatedHours', 0)), 0)),
        'actual_hours': str(_safe_int(data.get('actual_hours', data.get('actualHours', 0)), 0)),
        'progress': str(max(0, min(100, _safe_int(data.get('progress', 0), 0)))),
    }
    append_csv(TASKS_CSV, row, TASK_FIELDNAMES)
    ensure_demo_org_integrity(force=True)
    notify_task_assignment(row, actor_label=session.get('full_name') or session.get('role', 'Manager').title(), is_new_assignment=True)
    return jsonify({'id': task_id, 'ok': True})

@app.route('/api/manager/projects/create', methods=['POST'])
@login_required
def api_manager_create_project():
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json(force=True) or {}
    existing_projects = read_csv(PROJECTS_CSV)
    project_id = get_next_project_id(existing_projects)
    now = datetime.now().strftime('%Y-%m-%d')
    members = _normalize_list_strings(data.get('teamMembers', data.get('team_members', [])) or [])
    row = {
        'id': project_id,
        'name': data.get('name','').strip(),
        'description': data.get('description',''),
        'owner_id': str(data.get('owner_id') or session.get('user_id','')).strip(),
        'start_date': now,
        'end_date': str(data.get('deadline', data.get('end_date', '')) or '')[:10],
        'status': normalize_project_status(data.get('status','planning')),
        'team_members': ','.join(members),
        'company': str(data.get('company') or get_default_company_name()).strip(),
        'progress': str(max(0, min(100, _safe_int(data.get('progress', 0), 0)))),
    }
    append_csv(PROJECTS_CSV, row, PROJECT_FIELDNAMES)
    _sync_project_members(project_id, members)
    ensure_demo_org_integrity(force=True)
    notify_project_assignment(row, actor_label=session.get('full_name') or session.get('role', 'Manager').title(), is_new_assignment=True)
    return jsonify({'id': project_id, 'ok': True})


@app.route('/api/manager/team/members', methods=['GET'])
@login_required
def api_manager_team_members():
    """Get all employees under this manager"""
    if session.get('role') != 'manager':
        return jsonify([])

    manager_id = session.get('user_id')
    team_member_ids = get_team_members(manager_id)

    if not team_member_ids:
        return jsonify([])

    employees = read_csv(EMP_CSV)
    team_emps = [e for e in employees if e.get('id') in team_member_ids]

    result = []
    for emp in team_emps:
        result.append({
            'id': emp.get('id'),
            'name': emp.get('name'),
            'email': emp.get('email'),
            'position': emp.get('position'),
            'department': emp.get('department'),
            'productivity': calculate_employee_productivity(emp.get('id'))
        })

    return jsonify(result)

@app.route('/api/manager/team/assign', methods=['POST'])
@login_required
def api_manager_assign_team():
    """Assign employees to a manager."""
    if session.get('role') != 'manager':
        return jsonify({'error': 'forbidden'}), 403

    data = request.get_json(force=True) or {}
    manager_id = session.get('user_id')
    employee_ids = _normalize_list_strings(data.get('employee_ids', []))

    if DB_BACKEND != 'mongodb':
        ensure_demo_org_integrity()
        teams = read_csv(TEAMS_CSV)
        team = next((row for row in teams if str(row.get('manager_id', '')).strip() == str(manager_id).strip()), None)
        if not team:
            return jsonify({'error': 'team_not_found'}), 404

        # Ensure employees stay in one team only.
        for row in teams:
            if row is team:
                continue
            current_members = _normalize_list_strings(str(row.get('member_ids', '')).split(','))
            next_members = [member_id for member_id in current_members if member_id not in employee_ids]
            if next_members != current_members:
                row['member_ids'] = ','.join(next_members)

        team['member_ids'] = ','.join(employee_ids)
        team['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        write_csv(TEAMS_CSV, teams, TEAM_FIELDNAMES)
        ensure_demo_org_integrity(force=True)
        return jsonify({'ok': True})

    try:
        team_coll = _mongo_collection('team_assignments')
        team_coll.update_one(
            {'manager_id': manager_id},
            {'$set': {
                'manager_id': manager_id,
                'manager_name': session.get('full_name'),
                'employee_ids': employee_ids,
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }},
            upsert=True
        )
        return jsonify({'ok': True})
    except Exception as e:
        print(f"Team assignment error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/project/<project_id>/progress', methods=['PUT'])
@login_required
def api_update_project_progress(project_id):
    """Update project progress"""
    if session.get('role') not in ['manager', 'admin']:
        return jsonify({'error': 'forbidden'}), 403

    try:
        update_project_progress(project_id)
        progress = calculate_project_progress(project_id)
        return jsonify({'progress': progress, 'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/task/<task_id>/progress', methods=['PUT'])
@login_required
def api_update_task_progress(task_id):
    """Update task progress"""
    data = request.get_json(force=True) or {}
    progress = int(data.get('progress', 0))

    try:
        update_by_id(TASKS_CSV, task_id, {'progress': str(progress)}, TASK_FIELDNAMES)

        task = find_by_id(TASKS_CSV, task_id)
        if task and task.get('project_id'):
            update_project_progress(task['project_id'])
        actor_id = str(session.get('user_id') or (task or {}).get('assignee_id') or '').strip()
        if task and actor_id:
            notify_employee_progress_update(task, actor_id, 'progress', f'{progress}%')

        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/employee/help-requests')
@login_required
def api_employee_help_requests():
    employee_id, _employee, candidate_ids, _employees = _resolve_current_employee_context()
    if not employee_id:
        return jsonify({'error': 'employee_not_found'}), 404

    valid_requester_ids = {str(employee_id).strip()} | {str(value).strip() for value in candidate_ids or set()}
    requests = [
        row for row in _normalize_help_request_rows(read_csv(HELP_REQUESTS_CSV))
        if str(row.get('requester_id', '')).strip() in valid_requester_ids
    ]
    return jsonify({'requests': requests})


@app.route('/api/employee/help-request', methods=['POST'])
@login_required
def api_employee_help_request():
    employee_id, employee_row, candidate_ids, _employees = _resolve_current_employee_context()
    if not employee_id:
        return jsonify({'error': 'employee_not_found'}), 404

    data = request.get_json(force=True) or {}
    message = str(data.get('message') or '').strip()
    task_id = str(data.get('task_id', data.get('task', '')) or '').strip()
    urgency = str(data.get('urgency') or 'medium').strip().lower()
    recipient_type = str(data.get('recipient_type', data.get('recipientType', 'manager')) or 'manager').strip().lower()
    request_type = str(data.get('request_type', data.get('requestType', '')) or '').strip().lower()
    explicit_recipient_id = str(data.get('recipient_id', data.get('recipientId', '')) or '').strip()

    if not message:
        return jsonify({'error': 'message_required'}), 400
    if urgency not in {'low', 'medium', 'high'}:
        urgency = 'medium'
    if recipient_type not in {'manager', 'teammate'}:
        recipient_type = 'manager'
    if not request_type:
        request_type = 'collaboration' if recipient_type == 'teammate' else 'help'

    username = session.get('username')
    full_name = session.get('full_name')
    task = None
    if task_id:
        task = next((
            row for row in read_csv(TASKS_CSV)
            if str(row.get('id', '')).strip() == task_id
            and task_matches_employee(row, candidate_ids, username=username, full_name=full_name)
        ), None)
        if not task:
            return jsonify({'error': 'task_not_found'}), 404

    recipients = _resolve_help_request_recipients(
        employee_id,
        recipient_type=recipient_type,
        explicit_recipient_id=explicit_recipient_id,
    )
    if not recipients:
        return jsonify({'error': 'no_help_recipients_available'}), 400

    requester_name = str(employee_row.get('name') or session.get('full_name') or session.get('username') or 'Employee').strip()
    task_title = str((task or {}).get('title') or data.get('task_title', data.get('taskTitle', '')) or 'General workload support').strip()
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rows = []

    request_title = 'Help Request'
    request_verb = 'requested help'
    if request_type == 'collaboration':
        request_title = 'Collaboration Request'
        request_verb = 'requested collaboration'
    elif request_type == 'extension':
        request_title = 'Deadline Extension Request'
        request_verb = 'requested a deadline extension'

    for recipient in recipients:
        row = {
            'id': str(uuid.uuid4()),
            'requester_id': employee_id,
            'requester_name': requester_name,
            'task_id': task_id,
            'task_title': task_title,
            'message': message,
            'urgency': urgency,
            'status': 'pending',
            'recipient_type': recipient_type,
            'recipient_id': str(recipient.get('id') or '').strip(),
            'recipient_name': str(recipient.get('name') or '').strip(),
            'request_type': request_type,
            'created_at': created_at,
            'updated_at': created_at,
        }
        append_csv(HELP_REQUESTS_CSV, row, HELP_REQUEST_FIELDNAMES)
        rows.append(row)

        recipient_message = f'{requester_name} {request_verb}.'
        details = []
        if task_title:
            details.append(f'Task: {task_title}')
        details.append(f'Urgency: {urgency.title()}')
        if details:
            recipient_message = f'{recipient_message} ' + ' | '.join(details)
        recipient_message = f'{recipient_message} Message: {message}'

        notify_user(
            row['recipient_id'],
            request_title,
            recipient_message,
            'help',
            email_subject=request_title,
        )

    recipient_labels = ', '.join(row.get('recipient_name', '') for row in rows if row.get('recipient_name'))
    confirmation_message = f'Your request was sent to {recipient_labels or "the available team"}.'
    if task_title:
        confirmation_message = f'{confirmation_message} Task: {task_title}.'
    create_notification(employee_id, 'Help Request Sent', confirmation_message, 'help')

    return jsonify({
        'ok': True,
        'message': confirmation_message,
        'requests_created': len(rows),
        'requests': rows,
    })


@app.route('/api/employee/help-request/<request_id>', methods=['DELETE'])
@login_required
def api_employee_help_request_delete(request_id):
    employee_id, _employee, candidate_ids, _employees = _resolve_current_employee_context()
    if not employee_id:
        return jsonify({'error': 'employee_not_found'}), 404

    valid_requester_ids = {str(employee_id).strip()} | {str(value).strip() for value in candidate_ids or set()}
    request_row = next((
        row for row in read_csv(HELP_REQUESTS_CSV)
        if str(row.get('id', '')).strip() == str(request_id).strip()
        and str(row.get('requester_id', '')).strip() in valid_requester_ids
    ), None)
    if not request_row:
        return jsonify({'error': 'help_request_not_found'}), 404

    updated = update_by_id(
        HELP_REQUESTS_CSV,
        request_id,
        {
            'status': 'cancelled',
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        },
        HELP_REQUEST_FIELDNAMES,
    )
    if not updated:
        return jsonify({'error': 'help_request_not_found'}), 404

    recipient_id = str(request_row.get('recipient_id') or '').strip()
    task_title = str(request_row.get('task_title') or 'General workload support').strip()
    requester_name = str(request_row.get('requester_name') or session.get('full_name') or 'Employee').strip()

    if recipient_id:
        notify_user(
            recipient_id,
            'Help Request Cancelled',
            f'{requester_name} cancelled the help request for "{task_title}".',
            'help',
            email_subject='Help Request Cancelled',
        )
    create_notification(
        employee_id,
        'Help Request Cancelled',
        f'Your help request for "{task_title}" was cancelled.',
        'help',
    )

    return jsonify({'ok': True})

@app.route('/api/employee/team-info')
@login_required
def api_employee_team_info():
    """Get employee's manager and teammates"""
    user_id, _employee, candidate_ids, _employees = _resolve_current_employee_context()

    if not user_id and not candidate_ids:
        return jsonify({'manager': None, 'teammates': []})

    manager_id = get_manager_for_employee(user_id)
    manager_data = None
    teammates = []

    if manager_id:
        users = read_csv(USERS_CSV)
        manager = next((u for u in users if u.get('id') == manager_id), None)
        if manager:
            manager_data = {
                'id': manager.get('id'),
                'name': manager.get('full_name'),
                'email': manager.get('username')
            }

        team_member_ids = get_team_members(manager_id)
        if team_member_ids:
            employees = read_csv(EMP_CSV)
            for team_id in team_member_ids:
                if team_id != user_id:
                    emp = next((e for e in employees if e.get('id') == team_id), None)
                    if emp:
                        teammates.append({
                            'id': emp.get('id'),
                            'name': emp.get('name'),
                            'position': emp.get('position'),
                            'email': emp.get('email')
                        })

    return jsonify({
        'manager': manager_data,
        'teammates': teammates
    })

@app.route('/api/employee/tasks')
@login_required
def api_employee_tasks():
    user_id = session.get('user_id')
    username = session.get('username')
    full_name = session.get('full_name')
    if not user_id and not username:
        return jsonify([])

    candidate_ids, _ = resolve_employee_candidate_ids(user_id, username, full_name)
    tasks = read_csv(TASKS_CSV)
    mine = [
        t for t in tasks
        if task_matches_employee(t, candidate_ids, username=username, full_name=full_name)
    ]
    normalized = []
    for row in mine:
        item = dict(row)
        item['status'] = normalize_task_status(item.get('status'))
        item['priority'] = str(item.get('priority') or 'medium').strip().lower()
        item['due_date'] = str(item.get('due_date') or item.get('dueDate') or '')[:10]
        item['progress'] = int(item.get('progress', 0) or 0)
        normalized.append(item)
    return jsonify(normalized)

@app.route('/api/employee/projects')
@login_required
def api_employee_projects():
    ensure_projects_team_members()
    user_id = session.get('user_id')
    username = session.get('username')
    full_name = session.get('full_name')
    if not user_id and not username:
        return jsonify([])

    candidate_ids, _ = resolve_employee_candidate_ids(user_id, username, full_name)

    projects = read_csv(PROJECTS_CSV)
    members = read_csv(PROJECT_MEMBERS_CSV)
    tasks = read_csv(TASKS_CSV)

    ids_to_match = set(candidate_ids)

    member_project_ids = {
        m.get('project_id')
        for m in members
        if m.get('project_id') and m.get('employee_id') in ids_to_match
    }

    task_project_ids = {
        t.get('project_id')
        for t in tasks
        if t.get('project_id') and task_matches_employee(t, ids_to_match, username=username, full_name=full_name)
    }

    visible_project_ids = member_project_ids.union(task_project_ids)

    mine = [
        p for p in projects
        if (user_id and p.get('owner_id') == user_id) or p.get('id') in visible_project_ids
    ]
    normalized = [{
        'id': p.get('id'),
        'name': p.get('name'),
        'description': p.get('description'),
        'status': p.get('status', 'planning'),
        'startDate': p.get('start_date'),
        'endDate': p.get('end_date'),
        'progress': int(p.get('progress', 0) or 0)
    } for p in mine]
    return jsonify(normalized)

@app.route('/api/employee/tasks/<task_id>', methods=['GET'])
@login_required
def api_employee_get_task(task_id):
    """Get a specific task for employee with error handling"""
    user_id = session.get('user_id')
    username = session.get('username')
    if not user_id and not username:
        return jsonify({'error': 'unauthorized'}), 401

    task, _employee_id, _employee, _candidate_ids = _resolve_session_employee_task(task_id)

    if not task:
        return jsonify({'error': 'task not found', 'task_id': task_id}), 404

    return jsonify({
        'id': task.get('id'),
        'title': task.get('title'),
        'description': task.get('description'),
        'status': normalize_task_status(task.get('status')),
        'priority': str(task.get('priority') or 'medium').lower(),
        'progress': int(task.get('progress', 0) or 0),
        'project_id': task.get('project_id'),
        'due_date': task.get('due_date', '')[:10],
        'created_at': task.get('created_at', '')
    })

@app.route('/api/employee/tasks', methods=['POST'])
@login_required
def api_employee_create_task():
    """Create a new task for employee"""
    user_id = session.get('user_id')
    username = session.get('username')
    if not user_id and not username:
        return jsonify({'error': 'unauthorized'}), 401

    employee_id, employee, _candidate_ids, _employees = _resolve_current_employee_context()
    data = request.get_json(force=True) or {}
    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()
    project_id = data.get('project_id') or ''
    priority = (str(data.get('priority', 'medium')).strip().lower())
    due_date = data.get('due_date') or ''

    if not title:
        return jsonify({'error': 'title required'}), 400

    task_id = get_next_task_id(read_csv(TASKS_CSV))
    new_task = {
        'id': task_id,
        'title': title,
        'description': description,
        'project_id': project_id,
        'assignee_id': employee_id or user_id,
        'assignee_name': str((employee or {}).get('name') or session.get('full_name') or session.get('username') or 'Unknown').strip(),
        'status': 'pending',
        'priority': priority,
        'progress': '0',
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'due_date': str(due_date or '')[:10],
        'estimated_hours': '0',
        'actual_hours': '0',
    }

    append_csv(TASKS_CSV, new_task, TASK_FIELDNAMES)
    return jsonify({'ok': True, 'task_id': task_id}), 201

@app.route('/api/employee/tasks/<task_id>', methods=['PUT'])
@login_required
def api_employee_update_task(task_id):
    """Update task details for employee"""
    user_id = session.get('user_id')
    username = session.get('username')
    if not user_id and not username:
        return jsonify({'error': 'unauthorized'}), 401

    data = request.get_json(force=True) or {}

    task, employee_id, _employee, _candidate_ids = _resolve_session_employee_task(task_id)

    if not task:
        return jsonify({'error': 'task not found or not owned'}), 404

    update_fields = {}
    if 'title' in data and data['title']:
        update_fields['title'] = data['title'].strip()
    if 'description' in data:
        update_fields['description'] = (data['description'] or '').strip()
    if 'priority' in data and data['priority']:
        update_fields['priority'] = str(data['priority']).strip().lower()
    if 'progress' in data:
        update_fields['progress'] = min(100, max(0, int(data['progress'] or 0)))
    if 'status' in data and data['status']:
        update_fields['status'] = normalize_task_status(data['status'])
    if 'due_date' in data:
        update_fields['due_date'] = (data['due_date'] or '')[:10]
    if employee_id:
        update_fields['assignee_id'] = employee_id

    if not update_fields:
        return jsonify({'error': 'no fields to update'}), 400

    updated = update_by_id(TASKS_CSV, task_id, update_fields, ['id','title','description','project_id','assignee_id','assignee_name','status','priority','created_at','due_date','progress'])

    if not updated:
        return jsonify({'error': 'update failed'}), 500

    updated_task = find_by_id(TASKS_CSV, task_id) or task
    if updated_task.get('project_id'):
        update_project_progress(updated_task['project_id'])
    notify_employee_progress_update(updated_task, employee_id or user_id, 'details', 'updated')

    return jsonify({'ok': True})

@app.route('/api/employee/tasks/<task_id>', methods=['DELETE'])
@login_required
def api_employee_delete_task(task_id):
    """Delete task for employee"""
    user_id = session.get('user_id')
    username = session.get('username')
    if not user_id and not username:
        return jsonify({'error': 'unauthorized'}), 401

    task, _employee_id, _employee, _candidate_ids = _resolve_session_employee_task(task_id)

    if not task:
        return jsonify({'error': 'task not found or not owned'}), 404

    all_tasks = read_csv(TASKS_CSV)
    remaining = [t for t in all_tasks if t.get('id') != task_id]
    write_csv(TASKS_CSV, remaining, TASK_FIELDNAMES)

    return jsonify({'ok': True})

@app.route('/api/employee/<employee_id>')
@login_required
def api_get_employee_details(employee_id):
    """Get employee details - prevents 'not found' errors by validating first"""
    user_id = session.get('user_id')

    if user_id != employee_id and session.get('role') not in {'manager', 'admin', 'hr', 'teamlead'}:
        return jsonify({'error': 'forbidden'}), 403

    employees = read_csv(EMP_CSV)
    users = read_csv(USERS_CSV)
    employee = next((e for e in employees if str(e.get('id', '')).strip() == str(employee_id).strip()), None)
    user = next((u for u in users if str(u.get('id', '')).strip() == str(employee_id).strip()), None)

    if not employee and user:
        employee = {
            'id': user.get('id'),
            'name': user.get('full_name', ''),
            'email': user.get('username', user.get('email', '')),
            'position': normalize_role(user.get('role', 'employee')).title(),
            'department': '',
            'company': get_default_company_name(),
            'join_date': '',
            'phone': '',
            'skills': '',
            'location': '',
            'last_login': '',
            'avatar_url': '',
            'status': 'active' if _truthy(user.get('is_active', 'true'), True) else 'inactive',
            'productivity': '0',
        }

    if not employee:
        return jsonify({
            'error': 'employee not found',
            'employee_id': employee_id,
            'available_employees': [e.get('id') for e in employees[:5]]
        }), 404

    tasks = read_csv(TASKS_CSV)
    candidate_ids, _employee_rows = resolve_employee_candidate_ids(employee.get('id'), employee.get('email'), employee.get('name'))
    emp_tasks = [
        task for task in tasks
        if task_matches_employee(task, candidate_ids, username=employee.get('email'), full_name=employee.get('name'))
    ]
    completed = [t for t in emp_tasks if normalize_task_status(t.get('status')) == 'completed']
    completion_rate = int((len(completed) / len(emp_tasks) * 100) if emp_tasks else 0)
    normalized_role = normalize_role(user.get('role', 'employee') if user else employee.get('role', 'employee'))

    return jsonify({
        'id': employee.get('id'),
        'name': employee.get('name'),
        'email': employee.get('email'),
        'position': employee.get('position'),
        'department': employee.get('department'),
        'company': employee.get('company', get_default_company_name()),
        'phone': employee.get('phone'),
        'skills': employee.get('skills', ''),
        'location': employee.get('location'),
        'join_date': employee.get('join_date'),
        'last_login': employee.get('last_login', ''),
        'avatar_url': employee.get('avatar_url'),
        'role': normalized_role,
        'team_id': employee.get('team_id', ''),
        'team_name': employee.get('team_name', ''),
        'manager_id': employee.get('manager_id', ''),
        'teamlead_id': employee.get('teamlead_id', ''),
        'status': employee.get('status', 'active'),
        'totalTasks': len(emp_tasks),
        'completedTasks': len(completed),
        'completionRate': completion_rate,
        'productivity': _safe_int(employee.get('productivity', completion_rate), completion_rate) or completion_rate
    })

@app.route('/api/employee/analytics')
@login_required
def api_employee_analytics():
    """Get employee analytics and performance metrics"""
    user_id = session.get('user_id')
    username = session.get('username')
    full_name = session.get('full_name')
    if not user_id and not username:
        return jsonify({'error': 'unauthorized'}), 401

    candidate_ids, _employees = resolve_employee_candidate_ids(user_id, username, full_name)
    tasks = read_csv(TASKS_CSV)
    projects = read_csv(PROJECTS_CSV)
    emp_tasks = [
        t for t in tasks
        if task_matches_employee(t, candidate_ids, username=username, full_name=full_name)
    ]

    statuses = {}
    for t in emp_tasks:
        status = normalize_task_status(t.get('status'))
        statuses[status] = statuses.get(status, 0) + 1

    priorities = {}
    for t in emp_tasks:
        priority = str(t.get('priority', 'medium')).lower()
        priorities[priority] = priorities.get(priority, 0) + 1

    completed = len([t for t in emp_tasks if normalize_task_status(t.get('status')) == 'completed'])
    total = len(emp_tasks)
    completion_rate = int((completed / total * 100) if total > 0 else 0)
    visible_project_ids = {
        str(t.get('project_id') or '').strip()
        for t in emp_tasks
        if str(t.get('project_id') or '').strip()
    }

    return jsonify({
        'totalTasks': total,
        'completedTasks': completed,
        'completionRate': completion_rate,
        'tasksByStatus': statuses,
        'tasksByPriority': priorities,
        'averageProgress': completion_rate,
        'activeProjects': len([
            p for p in projects
            if str(p.get('id') or '').strip() in visible_project_ids
            and str(p.get('status') or '').strip().lower() != 'completed'
        ]),
        'generatedAt': datetime.now().isoformat()
    })

@app.route('/api/employee/reports')
@login_required
def api_employee_reports():
    """Get employee reports with detailed metrics"""
    user_id = session.get('user_id')
    username = session.get('username')
    full_name = session.get('full_name')
    if not user_id and not username:
        return jsonify({'error': 'unauthorized'}), 401

    candidate_ids, _employees = resolve_employee_candidate_ids(user_id, username, full_name)
    tasks = read_csv(TASKS_CSV)
    projects = read_csv(PROJECTS_CSV)
    leave = read_csv(LEAVE_CSV)

    emp_tasks = [
        t for t in tasks
        if task_matches_employee(t, candidate_ids, username=username, full_name=full_name)
    ]
    emp_projects = [
        p for p in projects
        if str(p.get('owner_id') or '').strip() in candidate_ids
        or any(member_id in candidate_ids for member_id in _normalize_list_strings(str(p.get('team_members', '')).split(',')))
    ]
    emp_leave = [l for l in leave if str(l.get('employee_id') or '').strip() in candidate_ids]

    tasks_by_month = {}
    for t in emp_tasks:
        try:
            month = (t.get('created_at') or '')[:7]
            if month:
                tasks_by_month[month] = tasks_by_month.get(month, 0) + 1
        except:
            pass

    completed_count = len([t for t in emp_tasks if normalize_task_status(t.get('status')) == 'completed'])
    total_count = len(emp_tasks)
    completion_percent = int((completed_count / total_count * 100) if total_count > 0 else 0)

    return jsonify({
        'reportTitle': 'Employee Performance Report',
        'period': f"{datetime.now().year}-{str(datetime.now().month).zfill(2)}",
        'generatedAt': datetime.now().isoformat(),
        'summary': {
            'totalTasks': total_count,
            'completedTasks': completed_count,
            'pendingTasks': len([t for t in emp_tasks if normalize_task_status(t.get('status')) == 'pending']),
            'inProgressTasks': len([t for t in emp_tasks if normalize_task_status(t.get('status')) == 'in-progress']),
            'completionRate': completion_percent,
            'totalProjects': len(emp_projects),
            'totalLeaves': len(emp_leave),
            'approvedLeaves': len([l for l in emp_leave if normalize_leave_status(l.get('status')) == 'approved']),
            'pendingLeaves': len([l for l in emp_leave if normalize_leave_status(l.get('status')) == 'pending'])
        },
        'tasksTrend': tasks_by_month,
        'performanceGrade': 'A' if completion_percent >= 80 else 'B' if completion_percent >= 60 else 'C'
    })

@app.route('/api/manager/analytics')
@login_required
def api_manager_analytics():
    """Get manager analytics for team performance"""
    user_id = session.get('user_id')
    if session.get('role') not in ['manager', 'hr', 'admin', 'teamlead']:
        return jsonify({'error': 'forbidden'}), 403

    return jsonify(build_manager_analytics_payload(user_id))

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
                         projects=manager_data['projects'],
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []))

@app.route('/manager/employees')
@login_required
def manager_employees():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))

    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
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
                         projects=manager_data['projects'],
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []))

@app.route('/manager/projects')
@login_required
def manager_projects():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))

    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    flt = (request.args.get('filter') or '').lower()
    projects = manager_data['projects']
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
                         projects=projects,
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []))

@app.route('/manager/tasks')
@login_required
def manager_tasks():
    if session.get('role') != 'manager':
        return redirect(url_for('dashboard'))

    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
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
                         projects=manager_data['projects'],
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []))

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
                         projects=manager_data['projects'],
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []))

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
                         projects=manager_data['projects'],
                         notifications=manager_data.get('notifications', []),
                         payments=manager_data.get('payments', []),
                         teams=manager_data.get('teams', []))

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

@app.route('/teamlead/workload-balancer')
@login_required
def teamlead_workload_balancer():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='workload-balancer',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/teamlead/workload')
@app.route('/teamlead/workload/')
@login_required
def teamlead_workload_alias():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    return redirect(url_for('teamlead_workload_balancer'))

@app.route('/teamlead/skill-recommendations')
@login_required
def teamlead_skill_recommendations():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='skill-recommendations',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/teamlead/skill-development')
@app.route('/teamlead/skill-development/')
@app.route('/teamlead/skills')
@login_required
def teamlead_skill_development_alias():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    return redirect(url_for('teamlead_skill_recommendations'))

@app.route('/teamlead/notifications')
@login_required
def teamlead_notifications():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    user_id = session['user_id']
    manager_data = get_manager_data(user_id)
    return render_template('teamlead_dashboard.html',
                         username=session.get('username'),
                         role=session.get('role'),
                         current_view='notifications',
                         stats=manager_data['stats'],
                         employees=manager_data['employees'],
                         tasks=manager_data['tasks'],
                         projects=manager_data['projects'])

@app.route('/teamlead/notification')
@app.route('/teamlead/notification/')
@login_required
def teamlead_notifications_alias():
    if session.get('role') != 'teamlead':
        return redirect(url_for('dashboard'))
    return redirect(url_for('teamlead_notifications'))

@app.route('/api/taskvise/companies', methods=['GET'])
@platform_admin_required
def get_taskvise_companies():
    try:
        if taskvise_admin_manager is not None:
            companies = taskvise_admin_manager.get_all_companies()
        else:
            company_csv = os.path.join(BASE_DIR, 'data', 'admin', 'companies.csv')
            ensure_csv(company_csv, ['id', 'company_name', 'industry', 'country', 'employees_count', 'users_assigned', 'signup_date', 'status', 'plan_type', 'contact_email'])
            companies = read_csv(company_csv)
        return jsonify({'success': True, 'companies': companies})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/taskvise/companies', methods=['POST'])
@platform_admin_required
def add_taskvise_company():
    try:
        data = request.json
        company = {
            'company_name': data.get('company_name'),
            'industry': data.get('industry'),
            'country': data.get('country'),
            'employees_count': data.get('employees_count', 0),
            'users_assigned': data.get('users_assigned', 0),
            'plan_type': data.get('plan_type', 'professional'),
            'contact_email': data.get('contact_email')
        }
        if taskvise_admin_manager is not None:
            company = taskvise_admin_manager.add_company(company)
        else:
            company_csv = os.path.join(BASE_DIR, 'data', 'admin', 'companies.csv')
            ensure_csv(company_csv, ['id', 'company_name', 'industry', 'country', 'employees_count', 'users_assigned', 'signup_date', 'status', 'plan_type', 'contact_email'])
            companies = read_csv(company_csv)
            company['id'] = str(max([int(c.get('id', 0)) for c in companies] + [0]) + 1)
            company['signup_date'] = datetime.now().strftime('%Y-%m-%d')
            company['status'] = 'active'
            append_csv(company_csv, company, ['id', 'company_name', 'industry', 'country', 'employees_count', 'users_assigned', 'signup_date', 'status', 'plan_type', 'contact_email'])
        return jsonify({'success': True, 'company': company})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/taskvise/companies/<company_id>', methods=['PUT'])
@platform_admin_required
def update_taskvise_company(company_id):
    try:
        data = request.json
        if taskvise_admin_manager is not None:
            taskvise_admin_manager.update_company(company_id, data)
        else:
            company_csv = os.path.join(BASE_DIR, 'data', 'admin', 'companies.csv')
            update_by_id(company_csv, company_id, data, ['id', 'company_name', 'industry', 'country', 'employees_count', 'users_assigned', 'signup_date', 'status', 'plan_type', 'contact_email'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/taskvise/companies/<company_id>', methods=['DELETE'])
@platform_admin_required
def delete_taskvise_company(company_id):
    try:
        if taskvise_admin_manager is not None:
            taskvise_admin_manager.delete_company(company_id)
        else:
            company_csv = os.path.join(BASE_DIR, 'data', 'admin', 'companies.csv')
            delete_by_id(company_csv, company_id, ['id', 'company_name', 'industry', 'country', 'employees_count', 'users_assigned', 'signup_date', 'status', 'plan_type', 'contact_email'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/taskvise/admin/stats', methods=['GET'])
@platform_admin_required
def get_taskvise_admin_stats():
    try:
        ensure_demo_org_integrity()
        if taskvise_admin_manager is not None:
            companies = taskvise_admin_manager.get_all_companies()
            admin_stats = taskvise_admin_manager.get_admin_statistics()
        else:
            company_csv = os.path.join(BASE_DIR, 'data', 'admin', 'companies.csv')
            ensure_csv(company_csv, ['id', 'company_name', 'industry', 'country', 'employees_count', 'users_assigned', 'signup_date', 'status', 'plan_type', 'contact_email'])
            companies = read_csv(company_csv)
            admin_stats = {}
        users = read_csv(USERS_CSV)
        employees = read_csv(EMP_CSV)
        projects = read_csv(PROJECTS_CSV)
        tasks = read_csv(TASKS_CSV)
        teams = read_csv(TEAMS_CSV)
        payments = read_csv(PAYMENTS_CSV)
        role_distribution = Counter(normalize_role(user.get('role', 'employee')) for user in users)
        tasks_by_status = Counter(normalize_task_status(task.get('status')) for task in tasks)
        stats = {
            'total_companies': admin_stats.get('total_companies', len(companies)),
            'active_companies': admin_stats.get('active_companies', len([c for c in companies if c.get('status') == 'active'])),
            'total_employees': len(employees),
            'total_users': len([user for user in users if normalize_role(user.get('role')) != 'platform_admin']),
            'enterprise_plans': admin_stats.get('enterprise_plans', len([c for c in companies if c.get('plan_type') == 'enterprise'])),
            'professional_plans': admin_stats.get('professional_plans', len([c for c in companies if c.get('plan_type') == 'professional'])),
            'total_projects': len(projects),
            'active_projects': len([project for project in projects if normalize_project_status(project.get('status')) in {'active', 'planning'}]),
            'total_tasks': len(tasks),
            'completed_tasks': len([task for task in tasks if normalize_task_status(task.get('status')) == 'completed']),
            'total_teams': len(teams),
            'monthly_payroll': sum(_safe_int(row.get('base_salary', 0), 0) + _safe_int(row.get('bonus', 0), 0) for row in payments if str(row.get('payment_status', '')).strip().lower() != 'hold'),
            'role_distribution': dict(role_distribution),
            'tasks_by_status': dict(tasks_by_status),
            'recent_activity': build_recent_activity(employees, projects, tasks, limit=8),
        }
        
        return jsonify({'success': True, **stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/taskvise/admin/settings', methods=['POST'])
@platform_admin_required
def save_taskvise_settings():
    try:
        data = request.json
        settings_dir = os.path.join(BASE_DIR, 'data', 'admin')
        os.makedirs(settings_dir, exist_ok=True)
        settings_file = os.path.join(settings_dir, 'settings.json')
        
        with open(settings_file, 'w') as f:
            json.dump(data, f)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/taskvise-admin')
@platform_admin_required
def taskvise_admin_dashboard():
    return redirect(f"{TASKVISE_ADMIN_URL}/dashboard")

if __name__ == '__main__':
    create_sample_users()
    ensure_demo_org_integrity(force=True)
    sync_demo_role_passwords()
    debug_enabled = _truthy(os.environ.get('TASKVISE_DEBUG', 'true'), default=True)
    reloader_override = os.environ.get('TASKVISE_USE_RELOADER')
    if reloader_override is None:
        use_reloader = os.name != 'nt'
    else:
        use_reloader = _truthy(reloader_override, default=False)
    app.run(
        debug=debug_enabled,
        port=_safe_int(os.environ.get('PORT', '5000'), 5000),
        use_reloader=use_reloader,
    )
