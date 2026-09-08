import unittest
from datetime import datetime, timedelta

from add import task_utils


class TaskUtilsTests(unittest.TestCase):
    def test_task_utils_reports_dates_and_sorts_tasks(self):
        today = datetime.now()
        tomorrow = (today + timedelta(days=1)).strftime("%d/%m/%Y")
        yesterday = (today - timedelta(days=1)).strftime("%d/%m/%Y")
        today_str = today.strftime("%d/%m/%Y")

        self.assertEqual(task_utils.get_date_status(today_str), "🗓️ Due Today")
        self.assertEqual(task_utils.get_date_status(yesterday), "⚠️ Overdue")
        self.assertEqual(task_utils.get_date_status(tomorrow), "⏰ Upcoming")

        tasks = [
            {"task": "A", "due_date": tomorrow, "priority": "Low", "starred": False},
            {"task": "B", "due_date": today_str, "priority": "High", "starred": True},
        ]

        sorted_tasks = task_utils.sort_tasks(tasks, "Due date (earliest first)")
        self.assertEqual([task["task"] for task in sorted_tasks], ["B", "A"])

    def test_task_utils_sorts_by_priority_and_keeps_starred_first(self):
        tasks = [
            {"task": "Low", "priority": "Low", "starred": False},
            {"task": "High", "priority": "High", "starred": False},
            {"task": "Starred low", "priority": "Low", "starred": True},
        ]

        sorted_tasks = task_utils.sort_tasks(tasks, "Priority (low to high)")
        self.assertEqual([task["task"] for task in sorted_tasks], ["Starred low", "Low", "High"])


if __name__ == "__main__":
    unittest.main()
