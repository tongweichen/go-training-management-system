import sqlite3

connection = sqlite3.connect("go_training.db")
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()

# Class sessions
cursor.execute("""
CREATE TABLE IF NOT EXISTS class_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    lesson_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    UNIQUE (class_id, lesson_date, start_time, end_time)
)
""")

# Attendance for each student
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'present',
    is_guest INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (session_id) REFERENCES class_sessions(id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    UNIQUE (session_id, student_id),
    CHECK (status IN ('present', 'late', 'leave', 'absent'))
)
""")

# Attendance change history
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attendance_id INTEGER NOT NULL,
    old_status TEXT,
    new_status TEXT,
    changed_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attendance_id) REFERENCES attendance_entries(id)
)
""")

connection.commit()
connection.close()

print("Batch attendance tables are ready.")
