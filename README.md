# Student Management System

A simple CRUD web application built with Python, FastAPI, PostgreSQL, HTML, and CSS.

---

## Folder Structure

```
student_management/
│
├── main.py          ← All routes (URL paths) and logic
├── database.py      ← Database connection setup
├── models.py        ← Defines the students table
├── requirements.txt ← Python packages to install
│
├── templates/
│   ├── home.html         ← Home page
│   ├── add_student.html  ← Add student form
│   ├── students.html     ← View all students table
│   └── edit_student.html ← Edit student form
│
└── static/
    └── style.css    ← All CSS styles
```

---

## Step-by-Step Setup

### Step 1 — Install PostgreSQL

If PostgreSQL is not installed on your Mac:

```bash
brew install postgresql@15
brew services start postgresql@15
```

### Step 2 — Create the Database

Open the PostgreSQL shell:

```bash
psql postgres
```

Then run this command inside the shell:

```sql
CREATE DATABASE student_db;
\q
```

### Step 3 — Update Database Password in database.py

Open `database.py` and find this line:

```python
DATABASE_URL = "postgresql://postgres:password@localhost:5432/student_db"
```

Replace `postgres` with your PostgreSQL username and `password` with your actual password.

If you are using the default macOS PostgreSQL install with no password, use:

```python
DATABASE_URL = "postgresql://your_mac_username@localhost:5432/student_db"
```

### Step 4 — Create a Python Virtual Environment

A virtual environment keeps project packages separate from your system Python.

```bash
cd student_management
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

You should now see `(venv)` at the start of your terminal line.

### Step 5 — Install Required Packages

```bash
pip install -r requirements.txt
```

This installs: FastAPI, Uvicorn (server), SQLAlchemy (database), psycopg2 (PostgreSQL driver), Jinja2 (HTML templates), python-multipart (form data).

### Step 6 — Run the Application

```bash
uvicorn main:app --reload
```

- `main` = the file `main.py`
- `app` = the FastAPI instance inside main.py
- `--reload` = automatically restarts when you save a file (useful during development)

### Step 7 — Open in Browser

Go to: **http://127.0.0.1:8000**

---

## What Each File Does

| File | Purpose |
|------|---------|
| `database.py` | Connects Python to your PostgreSQL database using SQLAlchemy |
| `models.py` | Defines the shape of the `students` table (columns and types) |
| `main.py` | Contains all the routes — what happens when you visit each URL |
| `templates/home.html` | The home page with student count and navigation buttons |
| `templates/add_student.html` | The form to add a new student |
| `templates/students.html` | Displays all students in a table with Edit and Delete options |
| `templates/edit_student.html` | Pre-filled form to update an existing student |
| `static/style.css` | All the visual styling (colors, layout, fonts) |

---

## URL Reference

| URL | What it does |
|-----|-------------|
| `GET /` | Home page |
| `GET /add-student` | Show add student form |
| `POST /add-student` | Save new student to database |
| `GET /students` | View all students |
| `GET /edit-student/{id}` | Show edit form for a student |
| `POST /edit-student/{id}` | Save updated student details |
| `GET /delete-student/{id}` | Delete a student |
