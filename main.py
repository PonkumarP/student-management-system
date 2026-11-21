from fastapi import FastAPI, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import models
import database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


def read_html(filename):
    with open(f"templates/{filename}", "r") as f:
        return f.read()


def make_alert(message, is_error=False):
    css_class = "alert-error" if is_error else "alert-success"
    return f'<div class="alert {css_class}">{message}</div>'


def make_student_table(students):
    if not students:
        return '''
        <div class="empty-message">
            <p>No students found. <a href="/add-student">Add your first student</a>.</p>
        </div>'''

    rows = ""
    for index, student in enumerate(students, start=1):
        rows += f"""
        <tr>
            <td>{index}</td>
            <td>{student.name}</td>
            <td>{student.register_number}</td>
            <td>{student.department}</td>
            <td>{student.email}</td>
            <td class="action-cell">
                <a href="/edit-student/{student.id}"
                   class="btn btn-small btn-orange">Edit</a>
                <a href="/delete-student/{student.id}"
                   class="btn btn-small btn-red"
                   onclick="return confirm('Are you sure you want to delete {student.name}?')"
                >Delete</a>
            </td>
        </tr>"""

    table = f"""
    <table class="student-table">
        <thead>
            <tr>
                <th>#</th>
                <th>Name</th>
                <th>Register Number</th>
                <th>Department</th>
                <th>Email</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>"""

    return table


def make_edit_form(student, message=None, is_error=False):
    alert_html = make_alert(message, is_error) if message else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Edit Student</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>

    <nav class="navbar">
        <span class="navbar-title">Student Management System</span>
        <div class="navbar-links">
            <a href="/">Home</a>
            <a href="/add-student">Add Student</a>
            <a href="/students">View Students</a>
        </div>
    </nav>

    <div class="container">
        <div class="form-card">

            <h2 class="form-title">Edit Student Details</h2>

            {alert_html}

            <form action="/edit-student/{student.id}" method="post">

                <div class="form-group">
                    <label for="name">Student Name</label>
                    <input type="text" id="name" name="name"
                           value="{student.name}" required>
                </div>

                <div class="form-group">
                    <label for="register_number">Register Number</label>
                    <input type="text" id="register_number" name="register_number"
                           value="{student.register_number}" required>
                </div>

                <div class="form-group">
                    <label for="department">Department</label>
                    <input type="text" id="department" name="department"
                           value="{student.department}" required>
                </div>

                <div class="form-group">
                    <label for="email">Email Address</label>
                    <input type="email" id="email" name="email"
                           value="{student.email}" required>
                </div>

                <div class="form-actions">
                    <button type="submit" class="btn btn-blue">Update Student</button>
                    <a href="/students" class="btn btn-grey">Cancel</a>
                </div>

            </form>
        </div>
    </div>

</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def home(db: Session = Depends(database.get_db)):
    total = db.query(models.Student).count()

    count_box = f"""
    <div class="count-box">
        <span class="count-number">{total}</span>
        <span class="count-label">Total Students Registered</span>
    </div>"""

    html = read_html("home.html")
    html = html.replace("TOTAL_STUDENTS_PLACEHOLDER", count_box)
    return HTMLResponse(content=html)


@app.get("/add-student", response_class=HTMLResponse)
def show_add_form():
    html = read_html("add_student.html")
    html = html.replace("MESSAGE_PLACEHOLDER", "")
    return HTMLResponse(content=html)


@app.post("/add-student", response_class=HTMLResponse)
def save_student(
    name:            str = Form(...),
    register_number: str = Form(...),
    department:      str = Form(...),
    email:           str = Form(...),
    db: Session = Depends(database.get_db)
):
    reg_exists = db.query(models.Student).filter(
        models.Student.register_number == register_number
    ).first()

    if reg_exists:
        html = read_html("add_student.html")
        html = html.replace("MESSAGE_PLACEHOLDER",
            make_alert("A student with this register number already exists.", is_error=True))
        return HTMLResponse(content=html)

    email_exists = db.query(models.Student).filter(
        models.Student.email == email
    ).first()

    if email_exists:
        html = read_html("add_student.html")
        html = html.replace("MESSAGE_PLACEHOLDER",
            make_alert("A student with this email already exists.", is_error=True))
        return HTMLResponse(content=html)

    new_student = models.Student(
        name=name,
        register_number=register_number,
        department=department,
        email=email
    )
    db.add(new_student)
    db.commit()

    html = read_html("add_student.html")
    html = html.replace("MESSAGE_PLACEHOLDER", make_alert("Student added successfully!"))
    return HTMLResponse(content=html)


@app.get("/students", response_class=HTMLResponse)
def view_students(db: Session = Depends(database.get_db)):
    all_students = db.query(models.Student).all()
    table_html = make_student_table(all_students)
    html = read_html("students.html")
    html = html.replace("STUDENT_TABLE_PLACEHOLDER", table_html)
    return HTMLResponse(content=html)


@app.get("/edit-student/{student_id}", response_class=HTMLResponse)
def show_edit_form(student_id: int, db: Session = Depends(database.get_db)):
    student = db.query(models.Student).filter(
        models.Student.id == student_id
    ).first()

    if not student:
        return RedirectResponse(url="/students", status_code=302)

    return HTMLResponse(content=make_edit_form(student))


@app.post("/edit-student/{student_id}", response_class=HTMLResponse)
def save_edit(
    student_id:      int,
    name:            str = Form(...),
    register_number: str = Form(...),
    department:      str = Form(...),
    email:           str = Form(...),
    db: Session = Depends(database.get_db)
):
    student = db.query(models.Student).filter(
        models.Student.id == student_id
    ).first()

    if not student:
        return RedirectResponse(url="/students", status_code=302)

    dup_reg = db.query(models.Student).filter(
        models.Student.register_number == register_number,
        models.Student.id != student_id
    ).first()

    if dup_reg:
        return HTMLResponse(content=make_edit_form(
            student,
            message="Another student already has this register number.",
            is_error=True
        ))

    dup_email = db.query(models.Student).filter(
        models.Student.email == email,
        models.Student.id != student_id
    ).first()

    if dup_email:
        return HTMLResponse(content=make_edit_form(
            student,
            message="Another student already has this email.",
            is_error=True
        ))

    student.name            = name
    student.register_number = register_number
    student.department      = department
    student.email           = email
    db.commit()

    return RedirectResponse(url="/students", status_code=302)


@app.get("/delete-student/{student_id}")
def delete_student(student_id: int, db: Session = Depends(database.get_db)):
    student = db.query(models.Student).filter(
        models.Student.id == student_id
    ).first()

    if student:
        db.delete(student)
        db.commit()

    return RedirectResponse(url="/students", status_code=302)
