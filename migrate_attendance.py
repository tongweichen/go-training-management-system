
import sqlite3

connection = sqlite3.connect("go_training.db")
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()

# Student attendance records
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    class_id INTEGER,
    lesson_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
)
""")

connection.commit()
connection.close()

print("Attendance table created successfully!")
