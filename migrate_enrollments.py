import sqlite3

connection = sqlite3.connect("go_training.db")

try:
    cursor = connection.cursor()

    # Check the current database structure
    cursor.execute("PRAGMA table_info(enrollments)")
    columns = [row[1] for row in cursor.fetchall()]

    if "status" in columns:
        print("Migration already completed.")

    else:
        # Disable foreign key checks during migration
        connection.execute("PRAGMA foreign_keys = OFF")

        connection.execute("BEGIN IMMEDIATE")

        # Create the new enrollments table
        cursor.execute("""
        CREATE TABLE enrollments_new (
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

        # Copy existing enrollment records
        cursor.execute("""
        INSERT INTO enrollments_new
            (id, student_id, class_id, status, notes)
        SELECT
            id, student_id, class_id,
            'active', 'Migrated from previous version'
        FROM enrollments
        """)

        # Replace the old table
        cursor.execute("DROP TABLE enrollments")

        cursor.execute("""
        ALTER TABLE enrollments_new
        RENAME TO enrollments
        """)

        # Prevent duplicate active enrollments
        cursor.execute("""
        CREATE UNIQUE INDEX unique_active_enrollment
        ON enrollments(student_id, class_id)
        WHERE status = 'active'
        """)

        # Check foreign key relationships
        cursor.execute("PRAGMA foreign_key_check")

        if cursor.fetchall():
            raise ValueError("Foreign key validation failed")

        connection.commit()

        print("Enrollment migration completed successfully!")

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()