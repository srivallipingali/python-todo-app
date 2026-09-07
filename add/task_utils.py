from datetime import datetime

DATE_FORMAT = "%d/%m/%Y"
TIME_FORMAT = "%H:%M"


def get_date_status(due_date, end_time=""):
    if not due_date:
        return ""

    due = datetime.strptime(due_date, DATE_FORMAT)
    if end_time:
        parsed_time = datetime.strptime(end_time, TIME_FORMAT)
        due = due.replace(hour=parsed_time.hour, minute=parsed_time.minute)
    else:
        due = due.replace(hour=23, minute=59, second=59)

    now = datetime.now()
    if now > due:
        return "⚠️ Overdue"
    if now.date() == due.date():
        return "🗓️ Due Today"
    return "⏰ Upcoming"


def sort_tasks(task_list, selected_sort):
    if selected_sort == "Default order":
        sorted_tasks = list(task_list)
    else:
        priority_order = {"High": 0, "Medium": 1, "Low": 2}

        def due_date_key(task):
            due_date = task.get("due_date", "")
            if not due_date:
                return datetime.max

            due = datetime.strptime(due_date, DATE_FORMAT)
            end_time = task.get("end_time", "")
            if end_time:
                parsed_time = datetime.strptime(end_time, TIME_FORMAT)
                due = due.replace(hour=parsed_time.hour, minute=parsed_time.minute)
            else:
                due = due.replace(hour=23, minute=59, second=59)
            return due

        if selected_sort == "Due date (earliest first)":
            sorted_tasks = sorted(task_list, key=due_date_key)
        elif selected_sort == "Due date (latest first)":
            sorted_tasks = sorted(task_list, key=due_date_key, reverse=True)
        else:
            reverse_priority = selected_sort == "Priority (low to high)"
            sorted_tasks = sorted(
                task_list,
                key=lambda task: priority_order.get(
                    task.get("priority", "Medium"), 1
                ),
                reverse=reverse_priority,
            )

    return sorted(
        sorted_tasks,
        key=lambda task: task.get("starred", False),
        reverse=True,
    )
