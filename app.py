import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/students", methods=["GET", "POST"])
def students():

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

    connection = sqlite3.connect("go_training.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("SELECT id, name, phone FROM students ORDER BY id DESC")
    student_list = cursor.fetchall()

    connection.close()

    return render_template("students.html", students=student_list)


if __name__ == "__main__":
    app.run(debug=True)