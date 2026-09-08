import sqlite3
import tempfile
import unittest
from pathlib import Path

from add import database


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tempdir.name) / "tasks.db"
        database.initialize_database(str(self.db_path))

    def tearDown(self):
        self.tempdir.cleanup()

    def test_initialize_database_creates_expected_tables(self):
        self.assertTrue(self.db_path.exists())

        with sqlite3.connect(self.db_path) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }

        self.assertIn("tasks", tables)
        self.assertIn("labels", tables)

    def test_initialize_database_adds_missing_columns_to_existing_schema(self):
        legacy_db_path = Path(self.tempdir.name) / "legacy.db"

        with sqlite3.connect(legacy_db_path) as connection:
            connection.execute(
                """
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    description TEXT,
                    completed INTEGER DEFAULT 0
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE labels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
                """
            )
            connection.execute(
                "INSERT INTO tasks (task, description, completed) VALUES (?, ?, ?)",
                ("Legacy task", "Existing entry", 0),
            )
            connection.commit()

        database.initialize_database(str(legacy_db_path))

        with sqlite3.connect(legacy_db_path) as connection:
            columns = [
                row[1] for row in connection.execute("PRAGMA table_info(tasks)")
            ]

        self.assertIn("start_time", columns)
        self.assertIn("due_date", columns)
        self.assertIn("end_time", columns)
        self.assertIn("priority", columns)
        self.assertIn("label", columns)
        self.assertIn("starred", columns)

    def test_add_task_and_load_tasks_round_trip(self):
        database.add_task(
            {
                "task": "Buy milk",
                "description": "Groceries for the week",
                "completed": False,
                "start_time": "08:00",
                "due_date": "09/09/2026",
                "end_time": "18:00",
                "priority": "High",
                "label": "Errands",
                "starred": True,
            },
            str(self.db_path),
        )

        tasks = database.load_tasks(str(self.db_path))

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["task"], "Buy milk")
        self.assertEqual(tasks[0]["description"], "Groceries for the week")
        self.assertFalse(tasks[0]["completed"])
        self.assertEqual(tasks[0]["start_time"], "08:00")
        self.assertEqual(tasks[0]["due_date"], "09/09/2026")
        self.assertEqual(tasks[0]["end_time"], "18:00")
        self.assertEqual(tasks[0]["priority"], "High")
        self.assertEqual(tasks[0]["label"], "Errands")
        self.assertTrue(tasks[0]["starred"])

    def test_save_tasks_persists_task_rows(self):
        tasks = [
            {
                "task": "Sweep kitchen",
                "description": "",
                "completed": True,
                "start_time": "",
                "due_date": "",
                "end_time": "",
                "priority": "Low",
                "label": "Housework",
                "starred": False,
            }
        ]

        database.save_tasks(tasks, str(self.db_path))

        self.assertEqual(database.load_tasks(str(self.db_path))[0]["task"], "Sweep kitchen")
        self.assertEqual(database.load_tasks(str(self.db_path))[0]["label"], "Housework")

    def test_save_tasks_replaces_existing_tasks(self):
        initial_tasks = [
            {
                "task": "Old task",
                "description": "To be replaced",
                "completed": False,
                "start_time": "",
                "due_date": "",
                "end_time": "",
                "priority": "Medium",
                "label": "",
                "starred": False,
            }
        ]

        database.save_tasks(initial_tasks, str(self.db_path))

        replacement_tasks = [
            {
                "task": "New task",
                "description": "Fresh data",
                "completed": True,
                "start_time": "09:00",
                "due_date": "10/09/2026",
                "end_time": "17:00",
                "priority": "High",
                "label": "Work",
                "starred": True,
            }
        ]

        database.save_tasks(replacement_tasks, str(self.db_path))

        saved_tasks = database.load_tasks(str(self.db_path))
        self.assertEqual(len(saved_tasks), 1)
        self.assertEqual(saved_tasks[0]["task"], "New task")
        self.assertTrue(saved_tasks[0]["starred"])

    def test_label_helpers_only_return_explicitly_added_labels(self):
        database.add_label("Errands", str(self.db_path))
        database.add_label("Housework", str(self.db_path))

        self.assertEqual(database.load_labels(str(self.db_path)), ["Errands", "Housework"])

    def test_add_label_is_idempotent(self):
        database.add_label("Errands", str(self.db_path))
        database.add_label("Errands", str(self.db_path))

        self.assertEqual(database.load_labels(str(self.db_path)), ["Errands"])

    def test_update_task_and_delete_task_crud_flow(self):
        database.add_task(
            {
                "task": "Buy milk",
                "description": "Weekly groceries",
                "priority": "High",
                "label": "Errands",
            },
            str(self.db_path),
        )

        tasks = database.load_tasks(str(self.db_path))
        task = tasks[0]

        task["task"] = "Buy oat milk"
        task["description"] = "Plant-based milk"
        task["priority"] = "Low"
        task["label"] = "Groceries"

        database.update_task(task, str(self.db_path))

        updated_task = database.load_tasks(str(self.db_path))[0]
        self.assertEqual(updated_task["task"], "Buy oat milk")
        self.assertEqual(updated_task["description"], "Plant-based milk")
        self.assertEqual(updated_task["priority"], "Low")
        self.assertEqual(updated_task["label"], "Groceries")

        database.delete_task(task["id"], str(self.db_path))

        self.assertEqual(database.load_tasks(str(self.db_path)), [])

    def test_set_task_completed_and_starred_update_values(self):
        database.add_task(
            {
                "task": "Write report",
                "description": "Finish the draft",
            },
            str(self.db_path),
        )

        database.set_task_completed(1, True, str(self.db_path))
        database.set_task_starred(1, True, str(self.db_path))

        task = database.load_tasks(str(self.db_path))[0]

        self.assertTrue(task["completed"])
        self.assertTrue(task["starred"])


if __name__ == "__main__":
    unittest.main()
