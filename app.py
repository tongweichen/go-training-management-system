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

    # Read all students
    connection = sqlite3.connect("go_training.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, phone, status
        FROM students
        ORDER BY id DESC
        """
    )

    student_list = cursor.fetchall()

    # Get current classes for all students
    cursor.execute(
        """
        SELECT
            enrollments.student_id,
            classes.id AS class_id,
            classes.name AS class_name
        FROM enrollments
        JOIN classes
            ON enrollments.class_id = classes.id
        WHERE enrollments.status = 'active'
        ORDER BY classes.name
        """
    )

    enrollment_list = cursor.fetchall()

    # Group classes by student ID
    student_classes = {}

    for enrollment in enrollment_list:
        student_id = enrollment["student_id"]

        if student_id not in student_classes:
            student_classes[student_id] = []

        student_classes[student_id].append({
            "id": enrollment["class_id"],
            "name": enrollment["class_name"]
        })

    # Get all available classes
    cursor.execute(
        """
        SELECT id, name
        FROM classes
        ORDER BY name
        """
    )

    all_classes = cursor.fetchall()

    connection.close()

    return render_template(
        "students.html",
        students=student_list,
        student_classes=student_classes,
        all_classes=all_classes
    )


# Assign a Student to a Class
@app.route(
    "/students/<int:student_id>/assign",
    methods=["POST"]
)
def assign_student(student_id):

    class_id = request.form.get("class_id", type=int)

    if class_id is None:
        return "Please select a class", 400

    connection = sqlite3.connect("go_training.db")
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        connection.execute(
            """
            INSERT INTO enrollments
                (student_id, class_id, start_date, status)
            VALUES (?, ?, DATE('now'), 'active')
            """,
            (student_id, class_id)
        )

        connection.commit()

    except sqlite3.IntegrityError:
        connection.rollback()
        return "Student is already in this class or the selection is invalid", 400

    finally:
        connection.close()

    return redirect(url_for("students"))


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

    # Get student information
    cursor.execute(
        "SELECT id, name, phone FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    connection.close()

    if student is None:
        return "Student not found", 404

    return render_template("edit_student.html", student=student)


# Class Management - Add and View Classes
@app.route("/classes", methods=["GET", "POST"])
def classes():

    # Create a new class
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

    # Read all classes
    connection = sqlite3.connect("go_training.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, name, description FROM classes ORDER BY id DESC"
    )

    class_list = cursor.fetchall()

    connection.close()

    return render_template("classes.html", classes=class_list)


# Student Enrollment
@app.route("/enrollments", methods=["GET", "POST"])
def enrollments():

    connection = sqlite3.connect("go_training.db")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    cursor = connection.cursor()

    # Save student enrollment
    if request.method == "POST":

        student_id = request.form.get("student_id", type=int)
        class_id = request.form.get("class_id", type=int)

        if student_id is None or class_id is None:
            connection.close()
            return "Please select a student and a class", 400

        try:
            cursor.execute(
                """
                INSERT INTO enrollments (student_id, class_id)
                VALUES (?, ?)
                """,
                (student_id, class_id)
            )

            connection.commit()

        except sqlite3.IntegrityError:
            connection.rollback()
            connection.close()
            return "Student already enrolled or invalid selection", 400

        connection.close()

        return redirect(url_for("enrollments"))

    # Read students
    cursor.execute(
        "SELECT id, name FROM students ORDER BY name"
    )

    student_list = cursor.fetchall()

    # Read classes
    cursor.execute(
        "SELECT id, name FROM classes ORDER BY name"
    )

    class_list = cursor.fetchall()

    connection.close()

    return render_template(
        "enrollments.html",
        students=student_list,
        classes=class_list
    )


# Class Detail - View Enrolled Students
@app.route("/classes/<int:class_id>")
def class_detail(class_id):

    connection = sqlite3.connect("go_training.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    # Get class information
    cursor.execute(
        "SELECT id, name, description FROM classes WHERE id = ?",
        (class_id,)
    )

    class_info = cursor.fetchone()

    if class_info is None:
        connection.close()
        return "Class not found", 404

    # Get active students in the selected class
    cursor.execute(
        """
        SELECT students.id, students.name, students.phone
        FROM students
        JOIN enrollments
            ON students.id = enrollments.student_id
        WHERE enrollments.class_id = ?
          AND enrollments.status = 'active'
        ORDER BY students.name
        """,
        (class_id,)
    )

    student_list = cursor.fetchall()

    # Get other classes for student transfers
    cursor.execute(
        """
        SELECT id, name
        FROM classes
        WHERE id != ?
        ORDER BY name
        """,
        (class_id,)
    )

    other_classes = cursor.fetchall()

    connection.close()

    return render_template(
        "class_detail.html",
        class_info=class_info,
        students=student_list,
        other_classes=other_classes
    )


# Student Leaves a Class
@app.route(
    "/classes/<int:class_id>/leave/<int:student_id>",
    methods=["POST"]
)
def leave_class(class_id, student_id):

    connection = sqlite3.connect("go_training.db")
    connection.execute("PRAGMA foreign_keys = ON")

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE enrollments
        SET status = 'ended',
            end_date = DATE('now')
        WHERE student_id = ?
          AND class_id = ?
          AND status = 'active'
        """,
        (student_id, class_id)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("class_detail", class_id=class_id))


# Transfer a Student to Another Class
@app.route(
    "/classes/<int:class_id>/transfer/<int:student_id>",
    methods=["POST"]
)
def transfer_student(class_id, student_id):

    new_class_id = request.form.get("new_class_id", type=int)

    if new_class_id is None or new_class_id == class_id:
        return "Please select a different class", 400

    connection = sqlite3.connect("go_training.db")
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        connection.execute("BEGIN IMMEDIATE")

        # Check that the student is currently enrolled
        current = connection.execute(
            """
            SELECT id FROM enrollments
            WHERE student_id = ?
              AND class_id = ?
              AND status = 'active'
            """,
            (student_id, class_id)
        ).fetchone()

        if current is None:
            connection.rollback()
            return "Active enrollment not found", 404

        # Check that the destination class exists
        destination = connection.execute(
            "SELECT id FROM classes WHERE id = ?",
            (new_class_id,)
        ).fetchone()

        if destination is None:
            connection.rollback()
            return "Destination class not found", 404

        # End the previous enrollment
        connection.execute(
            """
            UPDATE enrollments
            SET status = 'ended',
                end_date = DATE('now')
            WHERE id = ?
            """,
            (current[0],)
        )

        # Create a new enrollment
        connection.execute(
            """
            INSERT INTO enrollments
                (student_id, class_id, start_date, status, notes)
            VALUES (
                ?, ?, DATE('now'), 'active',
                'Transferred from another class'
            )
            """,
            (student_id, new_class_id)
        )

        connection.commit()

    except sqlite3.IntegrityError:
        connection.rollback()
        return "Student is already enrolled in the destination class", 400

    finally:
        connection.close()

    return redirect(url_for("class_detail", class_id=new_class_id))

# Remove a student from a class on the student list
@app.route(
    "/students/<int:student_id>/leave/<int:class_id>",
    methods=["POST"]
)
def leave_student_class(student_id, class_id):

    connection = sqlite3.connect("go_training.db")

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE enrollments
        SET status = 'ended',
            end_date = DATE('now')
        WHERE student_id = ?
          AND class_id = ?
          AND status = 'active'
        """,
        (student_id, class_id)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("students"))


# Update Student Class or Status
@app.route(
    "/students/<int:student_id>/update-status",
    methods=["POST"]
)
def update_student_status(student_id):

    selection = request.form.get("selection", "").strip()

    if not selection:
        return "Please select a class or status", 400

    connection = sqlite3.connect("go_training.db")
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        connection.execute("BEGIN IMMEDIATE")

        student = connection.execute(
            "SELECT id FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        if student is None:
            connection.rollback()
            return "Student not found", 404

        if selection not in ("unassigned", "withdrawn"):
            try:
                class_id = int(selection)
            except ValueError:
                connection.rollback()
                return "Invalid class selection", 400

            destination = connection.execute(
                "SELECT id FROM classes WHERE id = ?",
                (class_id,)
            ).fetchone()

            if destination is None:
                connection.rollback()
                return "Class not found", 404

            existing = connection.execute(
                """
                SELECT id FROM enrollments
                WHERE student_id = ?
                  AND class_id = ?
                  AND status = 'active'
                """,
                (student_id, class_id)
            ).fetchone()
        else:
            class_id = None
            existing = None

        # End other active enrollments
        if class_id is None:
            connection.execute(
                """
                UPDATE enrollments
                SET status = 'ended',
                    end_date = DATE('now')
                WHERE student_id = ?
                  AND status = 'active'
                """,
                (student_id,)
            )
        else:
            connection.execute(
                """
                UPDATE enrollments
                SET status = 'ended',
                    end_date = DATE('now')
                WHERE student_id = ?
                  AND class_id != ?
                  AND status = 'active'
                """,
                (student_id, class_id)
            )

        if selection == "withdrawn":
            connection.execute(
                """
                UPDATE students
                SET status = 'withdrawn'
                WHERE id = ?
                """,
                (student_id,)
            )
        else:
            connection.execute(
                """
                UPDATE students
                SET status = 'active'
                WHERE id = ?
                """,
                (student_id,)
            )

            if class_id is not None and existing is None:
                connection.execute(
                    """
                    INSERT INTO enrollments
                        (student_id, class_id, start_date, status)
                    VALUES (?, ?, DATE('now'), 'active')
                    """,
                    (student_id, class_id)
                )

        connection.commit()

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()

    return redirect(url_for("students"))


# Run the Flask Application
if __name__ == "__main__":
    app.run(debug=True)
