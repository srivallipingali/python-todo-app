from operator import index
import tkinter as tk
import sqlite3
import os
from datetime import datetime


# -----------------------------
# File used to store tasks
# -----------------------------

DATABASE_NAME="tasks.db"


# -----------------------------
# Theme settings
# -----------------------------

dark_mode = False


LIGHT_BG = "#F5F5F5"
LIGHT_FG = "#222222"
LIGHT_BUTTON = "#D8B4E2"
LIGHT_ENTRY = "#FFFFFF"

DARK_BG = "#222222"
DARK_FG = "#F20059"
DARK_BUTTON = "#6C4A8E"
DARK_ENTRY = "#333333"




# -----------------------------
# Initialize SQLite database
# -----------------------------

def initialize_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            description TEXT,
            completed INTEGER DEFAULT 0,
            due_date TEXT
        )
    """)

    connection.commit()

    # Add due_date to an existing database if it doesn't already exist
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [column[1] for column in cursor.fetchall()]

    if "due_date" not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")

    connection.commit()
    connection.close()


# -----------------------------
# Load tasks from SQLite
# -----------------------------

def load_tasks():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, task, description, completed, due_date
        FROM tasks
        ORDER BY id
    """)

    rows = cursor.fetchall()

    connection.close()

    tasks = []

    for row in rows:
        tasks.append({
            "id": row[0],
            "task": row[1],
            "description": row[2],
            "completed": bool(row[3]),
            "due_date": row[4]
        })

    return tasks

# -----------------------------
# Save tasks to SQLite
# -----------------------------

def save_tasks():

    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks")

    for task in tasks:

        cursor.execute(
            """
            INSERT INTO tasks
            (task, description, completed, due_date)
            VALUES (?, ?, ?, ?)
            """,
            (
                task["task"],
                task["description"],
                task["completed"],
                task.get("due_date", "")
            )
        )

    conn.commit()
    conn.close()
# -----------------------------
# Add a new task
# -----------------------------

def add_task():

    task_text = task_entry.get().strip()
    due_date = due_date_entry.get().strip()
    description = description_entry.get("1.0", tk.END).strip()

    # Task name is required
    if not task_text:
        return

    # Validate date
    if due_date:

        try:
            datetime.strptime(due_date, "%d/%m/%Y")

        except ValueError:
            print("Invalid date. Please use DD/MM/YYYY.")
            return

    # Save task to SQLite
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (task, description, completed, due_date)
        VALUES (?, ?, ?, ?)
    """, (
        task_text,
        description,
        0,
        due_date
    ))

    connection.commit()
    connection.close()

    # Clear input fields
    task_entry.delete(0, tk.END)
    due_date_entry.delete(0, tk.END)
    description_entry.delete("1.0", tk.END)

    # Reload tasks
    tasks.clear()
    tasks.extend(load_tasks())

    display_tasks()


# -----------------------------
# Delete a task
# -----------------------------

def delete_task(index):

    task_id = tasks[index]["id"]

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    connection.commit()
    connection.close()

    tasks.clear()
    tasks.extend(load_tasks())

    display_tasks()

# -----------------------------
# Edit a task
# -----------------------------

def edit_task(index):

    task = tasks[index]

    edit_window = tk.Toplevel(window)
    edit_window.title("Edit Task")
    edit_window.geometry("500x450")
    edit_window.resizable(False, False)

    # -----------------------------
    # Task
    # -----------------------------

    task_label = tk.Label(
        edit_window,
        text="Task:",
        font=("Arial", 13, "bold")
    )

    task_label.pack(
        anchor="w",
        padx=30,
        pady=(25, 5)
    )

    edit_task_entry = tk.Entry(
        edit_window,
        width=45,
        font=("Arial", 13)
    )

    edit_task_entry.pack(
        padx=30,
        pady=5
    )

    edit_task_entry.insert(
        0,
        task["task"]
    )

    # -----------------------------
    # Due Date
    # -----------------------------

    due_date_label = tk.Label(
        edit_window,
        text="Due Date (DD/MM/YYYY):",
        font=("Arial", 13, "bold")
    )

    due_date_label.pack(
        anchor="w",
        padx=30,
        pady=(15, 5)
    )

    edit_due_date_entry = tk.Entry(
        edit_window,
        width=25,
        font=("Arial", 13)
    )

    edit_due_date_entry.pack(
        anchor="w",
        padx=30,
        pady=5
    )

    edit_due_date_entry.insert(
        0,
        task.get("due_date", "")
    )

    # -----------------------------
    # Description
    # -----------------------------

    description_label = tk.Label(
        edit_window,
        text="Description:",
        font=("Arial", 13, "bold")
    )

    description_label.pack(
        anchor="w",
        padx=30,
        pady=(15, 5)
    )

    edit_description_entry = tk.Text(
        edit_window,
        width=45,
        height=5,
        font=("Arial", 12)
    )

    edit_description_entry.pack(
        padx=30,
        pady=5
    )

    edit_description_entry.insert(
        "1.0",
        task.get("description", "")
    )

    # -----------------------------
    # Save Changes
    # -----------------------------

    def save_changes():

        new_task = edit_task_entry.get().strip()
        new_due_date = edit_due_date_entry.get().strip()
        new_description = edit_description_entry.get(
            "1.0",
            tk.END
        ).strip()

        if not new_task:
            return

        # Validate date
        if new_due_date:

            try:
                datetime.strptime(
                    new_due_date,
                    "%d/%m/%Y"
                )

            except ValueError:
                print("Invalid date. Use DD/MM/YYYY.")
                return

        # Update SQLite database
        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE tasks
            SET task = ?,
                description = ?,
                due_date = ?
            WHERE id = ?
        """, (
            new_task,
            new_description,
            new_due_date,
            task["id"]
        ))

        connection.commit()
        connection.close()

        # Update local task
        task["task"] = new_task
        task["description"] = new_description
        task["due_date"] = new_due_date

        # Refresh task list
        display_tasks()

        edit_window.destroy()

    save_button = tk.Button(
        edit_window,
        text="Save Changes",
        command=save_changes,
        font=("Arial", 13, "bold"),
        padx=20,
        pady=8
    )

    save_button.pack(
        pady=20
    )

    task = tasks[index]

    # Create edit window
    edit_window = tk.Toplevel(window)
    edit_window.title("Edit Task")
    edit_window.geometry("500x350")
    edit_window.resizable(False, False)

    # Task label
    task_label = tk.Label(
        edit_window,
        text="Task:",
        font=("Arial", 13, "bold")
    )
    task_label.pack(pady=(20, 5))

    # Task entry
    edit_task_entry = tk.Entry(
        edit_window,
        width=40,
        font=("Arial", 13)
    )
    edit_task_entry.pack(pady=5)

    # Put existing task name into entry
    edit_task_entry.insert(0, task["task"])

    # Description label
    description_label = tk.Label(
        edit_window,
        text="Description:",
        font=("Arial", 13, "bold")
    )
    description_label.pack(pady=(15, 5))

    # Description box
    edit_description = tk.Text(
        edit_window,
        width=40,
        height=6,
        font=("Arial", 12)
    )
    edit_description.pack(pady=5)

    # Put existing description into box
    edit_description.insert("1.0", task["description"])

    # Save changes
    def save_changes():

        new_task = edit_task_entry.get().strip()
        new_description = edit_description.get("1.0", tk.END).strip()

        if new_task:

            tasks[index]["task"] = new_task
            tasks[index]["description"] = new_description

            save_tasks()
            display_tasks()

            edit_window.destroy()

    save_button = tk.Button(
        edit_window,
        text="Save Changes",
        command=save_changes,
        font=("Arial", 12),
        padx=15,
        pady=7
    )

    save_button.pack(pady=15)

# -----------------------------
# Change task completion status
# -----------------------------

def toggle_task(index):

    completed = task_vars[index].get()
    task_id = tasks[index]["id"]

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tasks
        SET completed = ?
        WHERE id = ?
    """, (int(completed), task_id))

    connection.commit()
    connection.close()

    tasks[index]["completed"] = completed

    update_statistics()


# -----------------------------
# Update task statistics
# -----------------------------

def update_statistics():
    total = len(tasks)

    completed = sum(
        1 for task in tasks
        if task["completed"]
    )

    remaining = total - completed

    statistics_label.config(
        text=f"Total: {total}    Completed: {completed}    Remaining: {remaining}"
    )


# -----------------------------
# Display all tasks
# -----------------------------

def display_tasks():

    # Remove existing task widgets
    for widget in task_frame.winfo_children():
        widget.destroy()

    task_vars.clear()

    for index, task in enumerate(tasks):

        var = tk.BooleanVar(value=task["completed"])
        task_vars.append(var)

        # -----------------------------
        # Task title
        # -----------------------------

        checkbox = tk.Checkbutton(
            task_frame,
            text=task["task"],
            variable=var,
            command=lambda i=index: toggle_task(i),
            font=("Arial", 14),
            anchor="w"
        )

        checkbox.grid(
            row=index * 3,
            column=0,
            sticky="w",
            padx=15,
            pady=(10, 0)
        )

        # -----------------------------
        # Edit button
        # -----------------------------

        edit_button = tk.Button(
            task_frame,
            text="Edit",
            command=lambda i=index: edit_task(i),
            font=("Arial", 11),
            width=8,
            padx=10,
            pady=5
        )

        edit_button.grid(
            row=index * 3,
            column=1,
            padx=5,
            pady=10
        )

        # -----------------------------
        # Delete button
        # -----------------------------

        delete_button = tk.Button(
            task_frame,
            text="Delete",
            command=lambda i=index: delete_task(i),
            font=("Arial", 11),
            width=8,
            padx=10,
            pady=5
        )

        delete_button.grid(
            row=index * 3,
            column=2,
            padx=5,
            pady=10
        )

        # -----------------------------
        # Description
        # -----------------------------

        description = tk.Label(
            task_frame,
            text=task.get("description", ""),
            font=("Arial", 11),
            anchor="w"
        )

        description.grid(
            row=index * 3 + 1,
            column=0,
            columnspan=3,
            sticky="w",
            padx=40,
            pady=(0, 2)
        )

        # -----------------------------
        # Due date
        # -----------------------------

        due_date = tk.Label(
            task_frame,
            text=f"Due: {task.get('due_date', '')}",
            font=("Arial", 10),
            anchor="w"
        )

        due_date.grid(
            row=index * 3 + 2,
            column=0,
            columnspan=3,
            sticky="w",
            padx=40,
            pady=(0, 8)
        )

    update_statistics()
# -----------------------------
# Light / Dark mode
# -----------------------------

def toggle_theme():

    global dark_mode

    dark_mode = not dark_mode

    if dark_mode:
        background_label.config(image=dark_image)
        bg = DARK_BG
        fg = DARK_FG
        button_bg = DARK_BUTTON
        entry_bg = DARK_ENTRY

        theme_button.config(text="☀ Light Mode")

    else:
        background_label.config(image=light_image)
        bg = LIGHT_BG
        fg = LIGHT_FG
        button_bg = LIGHT_BUTTON
        entry_bg = LIGHT_ENTRY

        theme_button.config(text="🌙 Dark Mode")


    # Main window
    window.config(bg=bg)

    # Title
    title.config(
        bg=bg,
        fg=fg
    )

    task_label.config(
    bg=bg,
    fg=fg
    )

    # Input frame
    input_frame.config(bg=bg)

    # Task frame
    task_frame.config(bg=bg)

    # Entry box
    task_entry.config(
        bg=entry_bg,
        fg=fg,
        insertbackground=fg
    )

    description_label.config(
    bg=bg,
    fg=fg
    )

    description_entry.config(
    bg=entry_bg,
    fg=fg,
    insertbackground=fg
    )

    # Buttons
    add_button.config(
        bg=button_bg,
        fg=fg
    )

    theme_button.config(
        bg=button_bg,
        fg=fg
    )

    # Statistics
    statistics_label.config(
        bg=bg,
        fg=fg
    )

    # Update task widgets
    for widget in task_frame.winfo_children():

        if isinstance(widget, tk.Checkbutton):

            widget.config(
                bg=bg,
                fg=fg,
                activebackground=bg,
                activeforeground=fg,
                selectcolor=button_bg
            )

        elif isinstance(widget, tk.Button):

            widget.config(
                bg=button_bg,
                fg=fg,
                activebackground=button_bg,
                activeforeground=fg
            )


# -----------------------------
# Main Window
# -----------------------------

window = tk.Tk()

window.title("My To-Do App")
window.geometry("1450x800")

# Allow window resizing
window.resizable(False, False)

light_image = tk.PhotoImage(file="light_background.png")
dark_image = tk.PhotoImage(file="dark_background.png")

background_label = tk.Label(window, image=light_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# -----------------------------
# Title
# -----------------------------

title = tk.Label(
    window,
    text="My To-Do List",
    font=("Arial", 24, "bold")
)

title.pack(pady=20)


# -----------------------------
# Task Entry
# -----------------------------

input_frame = tk.Frame(window)

input_frame.pack(pady=10)

# Task label
task_label = tk.Label(
    input_frame,
    text="Task:",
    font=("Arial", 12)
)

task_label.grid(
    row=0,
    column=0,
    sticky="w",
    padx=10,
    pady=(5, 0)
)

# Task entry
task_entry = tk.Entry(
    input_frame,
    width=40,
    font=("Arial", 15)
)

task_entry.grid(
    row=1,
    column=0,
    padx=10,
    pady=5
)

# -----------------------------
# Due Date
# -----------------------------

due_date_label = tk.Label(
    input_frame,
    text="Due Date (DD/MM/YYYY):",
    font=("Arial", 12)
)

due_date_label.grid(
    row=2,
    column=0,
    sticky="w",
    padx=10,
    pady=(5, 0)
)

due_date_entry = tk.Entry(
    input_frame,
    width=20,
    font=("Arial", 13)
)

due_date_entry.grid(
    row=3,
    column=0,
    sticky="w",
    padx=10,
    pady=5
)

# -----------------------------
# Description
# -----------------------------

description_label = tk.Label(
    input_frame,
    text="Description:",
    font=("Arial", 12)
)

description_label.grid(
    row=4,
    column=0,
    sticky="w",
    padx=10,
    pady=(5, 0)
)

description_entry = tk.Text(
    input_frame,
    width=40,
    height=3,
    font=("Arial", 12)
)

description_entry.grid(
    row=5,
    column=0,
    padx=10,
    pady=5
)

# -----------------------------
# Add Button
# -----------------------------

add_button = tk.Button(
    input_frame,
    text="Add Task",
    command=add_task,
    font=("Arial", 13),
    padx=15,
    pady=8
)

add_button.grid(
    row=5,
    column=1,
    padx=20,
    pady=10
)


# -----------------------------
# Scrollable Task Display Area
# -----------------------------

task_container = tk.Frame(
    window,
    width=600,
    height=350,
    bd=2,
    relief="groove"
)

task_container.pack(
    padx=20,
    pady=20
)

task_container.pack_propagate(False)

# Canvas
canvas = tk.Canvas(
    task_container,
    width=580,
    height=350
)

canvas.pack(
    side="left",
    fill="both",
    expand=True
)

# Scrollbar
scrollbar = tk.Scrollbar(
    task_container,
    orient="vertical",
    command=canvas.yview
)

scrollbar.pack(
    side="right",
    fill="y"
)

canvas.configure(
    yscrollcommand=scrollbar.set
)

# Frame containing the tasks
task_frame = tk.Frame(canvas)

canvas.create_window(
    (0, 0),
    window=task_frame,
    anchor="nw"
)

# Update scrolling area whenever tasks change
task_frame.bind(
    "<Configure>",
    lambda event: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

task_frame.grid_columnconfigure(0, weight=1)

# -----------------------------
# Store checkbox variables
# -----------------------------

task_vars = []


# -----------------------------
# Statistics
# -----------------------------

statistics_label = tk.Label(
    window,
    text="Total: 0    Completed: 0    Remaining: 0",
    font=("Arial", 13, "bold")
)

statistics_label.pack(pady=15)


# -----------------------------
# Light / Dark Mode Button
# -----------------------------

theme_button = tk.Button(
    window,
    text="🌙 Dark Mode",
    command=toggle_theme,
    font=("Arial", 13),
    padx=15,
    pady=7
)

theme_button.pack(pady=15)


# -----------------------------
# Load existing tasks
# -----------------------------

initialize_database()

tasks = load_tasks()

display_tasks()

# -----------------------------
# Run application
# -----------------------------

window.mainloop()