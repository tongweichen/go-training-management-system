import sqlite3

connection = sqlite3.connect("go_training.db")

# Enable foreign key constraints
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()

# Students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# Classes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
)
""")

# Enrollments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    start_date TEXT,
    end_date TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    notes TEXT,

    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),

    CHECK(status IN ('active', 'ended'))
)
""")

# Prevent duplicate active enrollments
cursor.execute("""
CREATE UNIQUE INDEX IF NOT EXISTS unique_active_enrollment
ON enrollments(student_id, class_id)
WHERE status = 'active'
""")

connection.commit()
connection.close()

print("Database initialized successfully!")