import sqlite3

connection = sqlite3.connect("go_training.db")
connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()

# Student lesson balances
cursor.execute("""
CREATE TABLE IF NOT EXISTS student_balances (
    student_id INTEGER PRIMARY KEY,
    balance_units INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(id)
)
""")

# Lesson balance change history
cursor.execute("""
CREATE TABLE IF NOT EXISTS lesson_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    change_units INTEGER NOT NULL,
    balance_before INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    CHECK(transaction_type IN ('manual', 'lesson', 'payment')),
    CHECK(balance_after = balance_before + change_units)
)
""")

# Create a zero-balance account for existing students
cursor.execute("""
INSERT OR IGNORE INTO student_balances (student_id, balance_units)
SELECT id, 0
FROM students
""")

connection.commit()
connection.close()

print("Lesson balance tables created successfully!")
