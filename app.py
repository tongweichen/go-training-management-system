import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


# Homepage
@app.route("/")
def home():
    return render_template("index.html")


# Student Management - Add and View Students
@app.route("/students", methods=["GET", "POST"])
def students():

    # Add a new student
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()

        if not name:
            return "Student name is required", 400

        connection = sqlite3.connect("go_training.db")
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO students (name, phone) VALUES (?, ?)",
            (name, phone)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("students"))

    # Read all students from database
    connection = sqlite3.connect("go_training.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, phone FROM students ORDER BY id DESC"
    )

    student_list = cursor.fetchall()

    connection.close()

    return render_template("students.html", students=student_list)


# Edit Student Information
@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):

    connection = sqlite3.connect("go_training.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Save updated information
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()

        if not name:
            connection.close()
            return "Student name is required", 400

        cursor.execute(
            "UPDATE students SET name = ?, phone = ? WHERE id = ?",
            (name, phone, student_id)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("students"))

    # Get the current student's information
    cursor.execute(
        "SELECT id, name, phone FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    connection.close()

    if student is None:
        return "Student not found", 404

    return render_template("edit_student.html", student=student)

@app.route("/classes", methods=["GET", "POST"])
def classes():

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        if not name:
            return "Class name is required", 400

        connection = sqlite3.connect("go_training.db")

        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO classes (name, description) VALUES (?, ?)",
            (name, description)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("classes"))

    return render_template("classes.html")

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)