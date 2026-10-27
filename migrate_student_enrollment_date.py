import sqlite3

connection = sqlite3.connect("go_training.db")
cursor = connection.cursor()

# Check existing columns
cursor.execute("PRAGMA table_info(students)")
columns = [column[1] for column in cursor.fetchall()]

# Add enrollment date
if "enrollment_date" not in columns:
    cursor.execute(
        """
        ALTER TABLE students
        ADD COLUMN enrollment_date TEXT
        """
    )

    connection.commit()
    print("Enrollment date column added.")
else:
    print("Enrollment date column already exists.")

# Check student information
cursor.execute(
    """
    SELECT id, name, enrollment_date
    FROM students
    ORDER BY id
    """
)

for student in cursor.fetchall():
    print(student)

connection.close()
