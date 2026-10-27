import sqlite3

connection = sqlite3.connect("go_training.db")
cursor = connection.cursor()

cursor.execute("PRAGMA table_info(students)")
columns = [column[1] for column in cursor.fetchall()]

if "status" not in columns:
    cursor.execute(
        """
        ALTER TABLE students
        ADD COLUMN status TEXT NOT NULL DEFAULT 'active'
        """
    )

    connection.commit()
    print("Student status column added.")
else:
    print("Student status column already exists.")

cursor.execute(
    """
    SELECT id, name, status
    FROM students
    ORDER BY id
    """
)

for student in cursor.fetchall():
    print(student)

connection.close()
