import sqlite3

connection = sqlite3.connect("go_training.db")
cursor = connection.cursor()

# Check existing columns
cursor.execute("PRAGMA table_info(students)")
columns = [column[1] for column in cursor.fetchall()]

# Add birthday column if it does not exist
if "birthday" not in columns:
    cursor.execute(
        """
        ALTER TABLE students
        ADD COLUMN birthday TEXT
        """
    )

    connection.commit()
    print("Birthday column added.")
else:
    print("Birthday column already exists.")

# Show student information
cursor.execute(
    """
    SELECT id, name, birthday
    FROM students
    ORDER BY id
    """
)

for student in cursor.fetchall():
    print(student)

connection.close()
