import sqlite3

connection = sqlite3.connect("go_training.db")
cursor = connection.cursor()

# Check existing columns
cursor.execute("PRAGMA table_info(students)")
columns = [column[1] for column in cursor.fetchall()]

# Add notes column
if "notes" not in columns:
    cursor.execute("""
        ALTER TABLE students
        ADD COLUMN notes TEXT
    """)
    connection.commit()
    print("Notes column added.")
else:
    print("Notes column already exists.")

connection.close()
