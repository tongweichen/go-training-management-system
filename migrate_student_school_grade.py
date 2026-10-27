
import sqlite3

connection = sqlite3.connect("go_training.db")
cursor = connection.cursor()

# Check existing columns
cursor.execute("PRAGMA table_info(students)")
columns = [column[1] for column in cursor.fetchall()]

# Add school column
if "school" not in columns:
    cursor.execute(
        """
        ALTER TABLE students
        ADD COLUMN school TEXT
        """
    )
    print("School column added.")
else:
    print("School column already exists.")

# Add grade column
if "grade" not in columns:
    cursor.execute(
        """
        ALTER TABLE students
        ADD COLUMN grade TEXT
        """
    )
    print("Grade column added.")
else:
    print("Grade column already exists.")

connection.commit()

# Check updated student information
cursor.execute(
    """
    SELECT id, name, school, grade
    FROM students
    ORDER BY id
    """
)

for student in cursor.fetchall():
    print(student)

connection.close()
