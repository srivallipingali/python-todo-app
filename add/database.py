import sqlite3


DEFAULT_DATABASE_NAME = "tasks.db"


def initialize_database(database_name=DEFAULT_DATABASE_NAME):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            description TEXT,
            completed INTEGER DEFAULT 0,
            start_time TEXT,
            due_date TEXT,
            end_time TEXT,
            priority TEXT DEFAULT 'Medium',
            label TEXT,
            starred INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS labels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("PRAGMA table_info(tasks)")
    columns = {column[1] for column in cursor.fetchall()}
    column_definitions = {
        "start_time": "TEXT",
        "due_date": "TEXT",
        "end_time": "TEXT",
        "priority": "TEXT DEFAULT 'Medium'",
        "label": "TEXT",
        "starred": "INTEGER DEFAULT 0",
    }

    for column, definition in column_definitions.items():
        if column not in columns:
            cursor.execute(
                f"ALTER TABLE tasks ADD COLUMN {column} {definition}"
            )

    connection.commit()
    connection.close()


def load_tasks(database_name=DEFAULT_DATABASE_NAME):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, task, description, completed, start_time, due_date,
               end_time, priority, label, starred
        FROM tasks
        ORDER BY id
    """)
    rows = cursor.fetchall()
    connection.close()

    return [
        {
            "id": row[0],
            "task": row[1],
            "description": row[2],
            "completed": bool(row[3]),
            "start_time": row[4],
            "due_date": row[5],
            "end_time": row[6],
            "priority": row[7] or "Medium",
            "label": row[8] or "",
            "starred": bool(row[9]),
        }
        for row in rows
    ]


def load_labels(database_name=DEFAULT_DATABASE_NAME):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM labels ORDER BY name COLLATE NOCASE")
    label_names = [row[0] for row in cursor.fetchall()]
    connection.close()
    return label_names


def save_tasks(tasks, database_name=DEFAULT_DATABASE_NAME):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM tasks")

    for task in tasks:
        cursor.execute(
            """
            INSERT INTO tasks
            (task, description, completed, start_time, due_date, end_time,
             priority, label, starred)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task["task"],
                task["description"],
                task["completed"],
                task.get("start_time", ""),
                task.get("due_date", ""),
                task.get("end_time", ""),
                task.get("priority", "Medium"),
                task.get("label", ""),
                int(task.get("starred", False)),
            ),
        )

    connection.commit()
    connection.close()


def add_task(task, database_name=DEFAULT_DATABASE_NAME):
    connection = sqlite3.connect(database_name)
    connection.execute(
        """
        INSERT INTO tasks
        (task, description, completed, start_time, due_date, end_time,
         priority, label, starred)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task["task"],
            task.get("description", ""),
            int(task.get("completed", False)),
            task.get("start_time", ""),
            task.get("due_date", ""),
            task.get("end_time", ""),
            task.get("priority", "Medium"),
            task.get("label", ""),
            int(task.get("starred", False)),
        ),
    )
    connection.commit()
    connection.close()


def update_task(task, database_name=DEFAULT_DATABASE_NAME):
    connection = sqlite3.connect(database_name)
    connection.execute(
        """
        UPDATE tasks
        SET task = ?, description = ?, due_date = ?, end_time = ?,
            priority = ?, label = ?
        WHERE id = ?
        """,
        (
            task["task"],
            task.get("description", ""),
            task.get("due_date", ""),
            task.get("end_time", ""),
            task.get("priority", "Medium"),
            task.get("label", ""),
            task["id"],
        ),
    )
    connection.commit()
    connection.close()


def delete_task(task_id, database_name=DEFAULT_DATABASE_NAME):
    connection = sqlite3.connect(database_name)
    connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()
    connection.close()


def set_task_completed(task_id, completed, database_name=DEFAULT_DATABASE_NAME):
    connection = sqlite3.connect(database_name)
    connection.execute(
        "UPDATE tasks SET completed = ? WHERE id = ?",
        (int(completed), task_id),
    )
    connection.commit()
    connection.close()


def set_task_starred(task_id, starred, database_name=DEFAULT_DATABASE_NAME):
    connection = sqlite3.connect(database_name)
    connection.execute(
        "UPDATE tasks SET starred = ? WHERE id = ?",
        (int(starred), task_id),
    )
    connection.commit()
    connection.close()


def add_label(label_name, database_name=DEFAULT_DATABASE_NAME):
    connection = sqlite3.connect(database_name)
    connection.execute(
        "INSERT OR IGNORE INTO labels (name) VALUES (?)",
        (label_name,),
    )
    connection.commit()
    connection.close()
