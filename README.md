# Python To-Do App

A lightweight desktop task manager built with Python and Tkinter. Tasks are
stored locally in a SQLite database, so the app works without a server or
external service.

## What It Does

- Create tasks with descriptions, priorities, labels, due dates, and end times.
- Mark tasks complete, star important tasks, edit them, or delete them.
- Search task titles and descriptions.
- Filter by priority, due status, or label.
- Sort by creation order, due date, or priority.
- View completion, remaining-task, overdue, and starred-task statistics.
- Switch between light and dark themes.
- Preserve existing task data when the database schema gains new fields.

## Technology

- Python 3
- Tkinter for the desktop interface
- SQLite for local persistence

The database file `tasks.db` is created in the project directory the first time
the application starts.

## Project Structure

```text
.
├── main.py          # Tkinter window, layout, and UI event handlers
├── database.py      # SQLite schema setup and task/label CRUD operations
├── task_utils.py    # Date-status and sorting rules
├── assets/          # Background images used by the interface
├── tasks.db         # Runtime data file, created automatically
└── README.md        # Project documentation
```

## Getting Started

### Requirements

- Python 3.9 or newer
- Tkinter available in your Python installation

Tkinter is normally included with Python on macOS and Windows. On some Linux
distributions it is provided by a separate package, such as `python3-tk`.

### Run the app

From the project directory:

```bash
python3 main.py
```

On systems where `python` points to Python 3, this also works:

```bash
python main.py
```

The application initializes `tasks.db`, loads existing tasks, and opens the
desktop window.

## Date and Time Formats

Use these formats when entering deadlines:

| Field | Format | Example |
| --- | --- | --- |
| Due date | `DD/MM/YYYY` | `07/09/2026` |
| End time | `HH:MM` in 24-hour time | `18:30` |

An end time requires a due date. Tasks without a deadline remain valid and are
shown as having no due date.

## Data and Maintenance

All task and label data is stored in the local `tasks.db` SQLite file. To back
up the application data, copy that file while the application is closed.

The database layer checks for expected task columns during startup and adds
missing columns when upgrading an older database. Do not edit the database
manually unless you have a separate backup.

## Development Checks

Compile the application modules with:

```bash
python3 -m py_compile main.py database.py task_utils.py
```

The application currently has no automated test suite. The persistence logic
can be exercised independently by importing `database.py` and passing it a
temporary SQLite database path.