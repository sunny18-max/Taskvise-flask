# TaskVise – Intelligent Task & Workforce Management System

TaskVise is a **Flask-based, role-driven task and workforce management system** designed to help organizations efficiently manage projects, tasks, employees, and workloads.  
It simulates a real-world enterprise environment with **Managers, Team Leads, and Employees**, focusing on productivity, transparency, and balanced work distribution.

This project is lightweight and portable for **academic projects, hackathons, and demonstrations**, with support for **CSV storage** and **MySQL backend**.

---

## 🚀 Key Features

- 🔐 Secure authentication with role-based access
- 👥 Multiple user roles (Manager, Team Lead, Employee)
- 📁 Project creation and management
- ✅ Task assignment and tracking
- ⚖️ Workload balancing & monitoring
- 🧠 Skill-based task recommendations
- 🕒 Work time tracking
- 🌴 Leave management system
- 📝 Team notes & announcements
- 📊 Reports and productivity insights

---

## 🧑‍💼 User Roles

### 1. Manager
- Create and manage projects
- View overall workload distribution
- Monitor employee productivity
- Make data-driven decisions

### 2. Team Lead
- Assign and manage tasks
- Track team progress
- Coordinate project execution

### 3. Employee
- View assigned tasks
- Update task status
- Log working hours
- Apply for leave

---

## 🛠 Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript (Jinja Templates)
- **Storage:** CSV Files or MySQL
- **Authentication:** Session-based login
- **Security:** Password hashing (Werkzeug)

---

## MySQL Setup

TaskVise now supports MySQL as a storage backend.

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Set environment variables:
   - `TASKVISE_DB_BACKEND=mysql`
   - `MYSQL_HOST=127.0.0.1`
   - `MYSQL_PORT=3306`
   - `MYSQL_USER=root`
   - `MYSQL_PASSWORD=your_password`
   - `MYSQL_DATABASE=taskvise`
3. Initialize schema (and optionally migrate CSV data):
   - `python scripts/init_mysql.py`
   - `python scripts/init_mysql.py --migrate-csv --truncate`

Schema file: `database/mysql_schema.sql`

---

## MongoDB Setup

TaskVise now supports MongoDB backend (via `TASKVISE_DB_BACKEND=mongodb`).

1. Set environment variables:
   - `TASKVISE_DB_BACKEND=mongodb`
   - `MONGO_URI=mongodb+srv://saathvikk777_db_user:<db_password>@taskvise.3ruihac.mongodb.net/?appName=Taskvise`
   - `MONGO_DATABASE=taskvise`
2. Migrate CSV to MongoDB:
   - `python scripts/migrate_to_mongo.py`

## Node.js Express Backend

TaskVise also supports running a Node.js backend in parallel (does not replace Flask):

1. Install dependencies:
   - `npm install express cors mongoose csv-parser`
2. Run server:
   - `node server.js`
3. API endpoints:
   - `GET /api/users`, `GET /api/employees`, `GET /api/tasks`, `GET /api/projects`
   - `POST /api/:model` (simple append functionality)
   - `GET /node-status`



