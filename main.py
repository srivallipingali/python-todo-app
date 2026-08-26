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

def get_date_status(due_date):

    if not due_date:
        return ""

    today = datetime.now().date()

    due = datetime.strptime(
        due_date,
        "%d/%m/%Y"
    ).date()

    if due < today:
        return "🔴 Overdue"

    elif due == today:
        return "🟡 Due Today"

    else:
        return "🟢 Upcoming"


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
            due_date TEXT,
            priority TEXT DEFAULT 'Medium'
        )
    """)

    connection.commit()

    # Add due_date and priority columns to an existing database if they don't exist
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [column[1] for column in cursor.fetchall()]

    if "due_date" not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")

    if "priority" not in columns:
        cursor.execute(
            "ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'Medium'"
        )

    connection.commit()
    connection.close()


# -----------------------------
# Load tasks from SQLite
# -----------------------------

def load_tasks():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, task, description, completed, due_date, priority
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
            "due_date": row[4],
            "priority": row[5] if row[5] else "Medium"
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
            (task, description, completed, due_date, priority)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                task["task"],
                task["description"],
                task["completed"],
                task.get("due_date", ""),
                task.get("priority", "Medium")
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
    priority = priority_var.get()

    if not task_text:
        return

    # Validate date
    if due_date:

        try:
            datetime.strptime(
                due_date,
                "%d/%m/%Y"
            )

        except ValueError:
            print("Invalid date. Use DD/MM/YYYY.")
            return

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (task, description, completed, due_date, priority)
        VALUES (?, ?, ?, ?, ?)
    """, (
        task_text,
        description,
        0,
        due_date,
        priority
    ))

    connection.commit()
    connection.close()

    # Clear fields
    task_entry.delete(0, tk.END)
    due_date_entry.delete(0, tk.END)
    description_entry.delete("1.0", tk.END)

    priority_var.set("Medium")

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

    edit_main_frame = tk.Toplevel(window)
    edit_main_frame.title("Edit Task")
    edit_main_frame.geometry("500x450")
    edit_main_frame.resizable(False, False)

    # -----------------------------
    # Task
    # -----------------------------

    task_label = tk.Label(
        edit_main_frame,
        text="Task:",
        font=("Arial", 13, "bold")
    )

    task_label.pack(
        anchor="w",
        padx=30,
        pady=(25, 5)
    )

    edit_task_entry = tk.Entry(
        edit_main_frame,
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
        edit_main_frame,
        text="Due Date (DD/MM/YYYY):",
        font=("Arial", 13, "bold")
    )

    due_date_label.pack(
        anchor="w",
        padx=30,
        pady=(15, 5)
    )

    edit_due_date_entry = tk.Entry(
        edit_main_frame,
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
    # Priority
    # -----------------------------

    priority_label = tk.Label(
        edit_main_frame,
        text="Priority:",
        font=("Arial", 13, "bold")
    )

    priority_label.pack(
        anchor="w",
        padx=30,
        pady=(15, 5)
    )

    edit_priority_var = tk.StringVar(
        value=task.get("priority", "Medium")
    )

    edit_priority_menu = tk.OptionMenu(
        edit_main_frame,
        edit_priority_var,
        "High",
        "Medium",
        "Low"
    )

    edit_priority_menu.config(
        font=("Arial", 12),
        width=15
    )

    edit_priority_menu.pack(
        anchor="w",
        padx=30,
        pady=5
    )

    # Description label
    description_label = tk.Label(
        edit_main_frame,
        text="Description:",
        font=("Arial", 13, "bold")
    )

    description_label.pack(
        anchor="w",
        padx=30,
        pady=(15, 5)
    )

    # Description box
    edit_description = tk.Text(
        edit_main_frame,
        width=45,
        height=5,
        font=("Arial", 12)
    )

    edit_description.pack(
        padx=30,
        pady=5
    )

    # Put existing description into box
    edit_description.insert("1.0", task.get("description", ""))

    # Save changes
    def save_changes():

        new_task = edit_task_entry.get().strip()
        new_due_date = edit_due_date_entry.get().strip()
        new_description = edit_description.get("1.0", tk.END).strip()
        new_priority = edit_priority_var.get()

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
                due_date = ?,
                priority = ?
            WHERE id = ?
        """, (
            new_task,
            new_description,
            new_due_date,
            new_priority,
            task["id"]
        ))

        connection.commit()
        connection.close()

        # Update local task
        task["task"] = new_task
        task["description"] = new_description
        task["due_date"] = new_due_date
        task["priority"] = new_priority

        # Refresh task list
        display_tasks()

        edit_main_frame.destroy()

    save_button = tk.Button(
        edit_main_frame,
        text="Save Changes",
        command=save_changes,
        font=("Arial", 13, "bold"),
        padx=20,
        pady=8
    )

    save_button.pack(
        pady=20
    )

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

def search_tasks():
    search_text = search_entry.get().lower().strip()
    selected_priority = priority_filter_var.get()

    # Remove current task widgets
    for widget in task_frame.winfo_children():
        widget.destroy()

    task_vars.clear()

    # Apply both filters when the user searches by text and priority.
    filtered_tasks = [
        task for task in tasks
        if (
            not search_text
            or search_text in task["task"].lower()
            or search_text in task.get("description", "").lower()
        )
        and (
            selected_priority == "All priorities"
            or task.get("priority", "Medium") == selected_priority
        )
    ]

    # Display filtered tasks
    for index, task in enumerate(filtered_tasks):

        var = tk.BooleanVar(value=task["completed"])
        task_vars.append(var)

        checkbox = tk.Checkbutton(
            task_frame,
            text=task["task"],
            variable=var,
            command=lambda checked_var=var, t=task: toggle_searched_task(t, checked_var),
            font=("Arial", 14),
            anchor="w"
        )

        checkbox.grid(
            row=index,
            column=0,
            sticky="w",
            padx=15,
            pady=10
        )

        edit_button = tk.Button(
            task_frame,
            text="Edit",
            command=lambda t=task: edit_task(tasks.index(t)),
            font=("Arial", 11),
            width=8
        )

        edit_button.grid(
            row=index,
            column=1,
            padx=5,
            pady=10
        )

        delete_button = tk.Button(
            task_frame,
            text="Delete",
            command=lambda t=task: delete_task(tasks.index(t)),
            font=("Arial", 11),
            width=8
        )

        delete_button.grid(
            row=index,
            column=2,
            padx=5,
            pady=10
        )

    update_statistics()


def toggle_searched_task(task, checked_var=None):
    # Find the actual task in the main list
    index = tasks.index(task)

    if checked_var is not None:
        tasks[index]["completed"] = checked_var.get()
    else:
        tasks[index]["completed"] = task_vars[index].get()

    save_tasks()
    update_statistics()

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
            row=index * 4,
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
            row=index * 4,
            column=1,
            padx=10,
            pady=5
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
            row=index * 4,
            column=2,
            padx=10,
            pady=5
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
            row=index * 4 + 1,
            column=0,
            columnspan=3,
            sticky="w",
            padx=40,
            pady=(0, 2)
        )

        # -----------------------------
        # Due date
        # -----------------------------

        due_date_value = task.get("due_date", "")

        if due_date_value:
            date_status = get_date_status(due_date_value)
            due_text = f"Due: {due_date_value}   {date_status}"
        else:
            due_text = "No due date"

        due_date_label = tk.Label(
            task_frame,
            text=due_text,
            font=("Arial", 10),
            anchor="w"
        )

        due_date_label.grid(
            row=index * 4 + 2,
            column=0,
            columnspan=3,
            sticky="w",
            padx=40,
            pady=(0, 8)
        )

        # -----------------------------
        # Priority
        # -----------------------------

        priority = task.get("priority", "Medium")

        if priority == "High":
            priority_text = "🔴 High"
        elif priority == "Low":
            priority_text = "🟢 Low"
        else:
            priority_text = "🟡 Medium"

        priority_display = tk.Label(
            task_frame,
            text=f"Priority: {priority_text}",
            font=("Arial", 10),
            anchor="w"
        )

        priority_display.grid(
            row=index * 4 + 3,
            column=0,
            columnspan=3,
            sticky="w",
            padx=40,
            pady=(0, 8)
        )

    # Make columns behave correctly
    task_frame.grid_columnconfigure(0, weight=1)
    task_frame.grid_columnconfigure(1, weight=0)
    task_frame.grid_columnconfigure(2, weight=0)

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


    # Main main_frame
    main_frame.config(bg=bg)

    # Title
    title.config(
        bg=bg,
        fg=fg
    )

    task_label.config(
    bg=bg,
    fg=fg
    )

            # Top bar
    top_bar.config(bg=bg)

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
# Main window
# -----------------------------
window = tk.Tk()

window.title("My To-Do App")
window.geometry("1450x800")
window.resizable(True, True)


# -----------------------------
# Whole Page Scrollbar
# -----------------------------

main_canvas = tk.Canvas(
    window,
    highlightthickness=0
)

main_scrollbar = tk.Scrollbar(
    window,
    orient="vertical",
    command=main_canvas.yview
)

main_scrollbar.pack(
    side="right",
    fill="y"
)

main_canvas.pack(
    side="left",
    fill="both",
    expand=True
)

main_canvas.configure(
    yscrollcommand=main_scrollbar.set
)


# Frame containing the entire app

main_frame = tk.Frame(main_canvas)

main_main_frame = main_canvas.create_window(
    (0, 0),
    window=main_frame,
    anchor="nw"
)


# Update scrollable area

main_frame.bind(
    "<Configure>",
    lambda event: main_canvas.configure(
        scrollregion=main_canvas.bbox("all")
    )
)


# Make the page width match the main_frame

main_canvas.bind(
    "<Configure>",
    lambda event: main_canvas.itemconfig(
        main_main_frame,
        width=event.width
    )
)

def scroll_page(event):
    main_canvas.yview_scroll(
        int(-1 * (event.delta / 120)),
        "units"
    )


main_canvas.bind_all(
    "<MouseWheel>",
    scroll_page
)

light_image = tk.PhotoImage(file="light_background.png")
dark_image = tk.PhotoImage(file="dark_background.png")

background_label = tk.Label(main_frame, image=light_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# -----------------------------
# Title
# -----------------------------

title = tk.Label(
    main_frame,
    text="My To-Do List",
    font=("Arial", 24, "bold")
)

title.pack(pady=20)


# -----------------------------
# Task Entry
# -----------------------------

input_frame = tk.Frame(main_frame)

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
# Search Tasks
# -----------------------------

search_frame = tk.Frame(main_frame)

search_frame.pack(pady=5)

search_label = tk.Label(
    search_frame,
    text="🔎 Search Tasks:",
    font=("Arial", 13, "bold")
)

search_label.pack(side="left", padx=5)


search_entry = tk.Entry(
    search_frame,
    width=35,
    font=("Arial", 13)
)

search_entry.pack(side="left", padx=5)


search_button = tk.Button(
    search_frame,
    text="Search",
    command=search_tasks,
    font=("Arial", 11),
    padx=10,
    pady=5
)

search_button.pack(side="left", padx=5)


clear_search_button = tk.Button(
    search_frame,
    text="Clear",
    command=lambda: clear_search(),
    font=("Arial", 11),
    padx=10,
    pady=5
)

clear_search_button.pack(side="left", padx=5)

priority_filter_label = tk.Label(
    search_frame,
    text="Priority:",
    font=("Arial", 13, "bold")
)

priority_filter_label.pack(side="left", padx=(15, 5))

priority_filter_var = tk.StringVar(value="All priorities")

priority_filter_menu = tk.OptionMenu(
    search_frame,
    priority_filter_var,
    "All priorities",
    "High",
    "Medium",
    "Low",
    command=lambda _: search_tasks()
)

priority_filter_menu.config(
    font=("Arial", 11),
    width=12
)

priority_filter_menu.pack(side="left", padx=5)

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
# Priority
# -----------------------------

priority_frame = tk.Frame(input_frame)

priority_frame.grid(
    row=4,
    column=0,
    columnspan=2,
    sticky="w",
    padx=10,
    pady=5
)

priority_label = tk.Label(
    priority_frame,
    text="Priority:",
    font=("Arial", 13, "bold")
)

priority_label.pack(
    side="left",
    padx=(0, 15)
)

priority_var = tk.StringVar(value="Medium")

priority_menu = tk.OptionMenu(
    priority_frame,
    priority_var,
    "High",
    "Medium",
    "Low"
)

priority_menu.config(
    font=("Arial", 12),
    width=12
)

priority_menu.pack(
    side="left"
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
    row=6,
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
    row=7,
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
    row=7,
    column=1,
    padx=20,
    pady=10
)


# -----------------------------
# Scrollable Task Display Area
# -----------------------------

task_container = tk.Frame(
    main_frame,
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
task_frame.grid_columnconfigure(0, weight=1)
task_frame.grid_columnconfigure(1, weight=0)
task_frame.grid_columnconfigure(2, weight=0)

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

def clear_search():
    search_entry.delete(0, tk.END)
    priority_filter_var.set("All priorities")
    display_tasks()


# -----------------------------
# Statistics
# -----------------------------

# -----------------------------
# Top Bar
# -----------------------------

top_bar = tk.Frame(main_frame)
top_bar.pack(fill="x", padx=30, pady=10)

# Statistics - top left
statistics_label = tk.Label(
    top_bar,
    text="Total: 0    Completed: 0    Remaining: 0",
    font=("Arial", 13, "bold")
)

statistics_label.pack(side="left")


# Light / Dark Mode - top right
theme_button = tk.Button(
    top_bar,
    text="🌙 Dark Mode",
    command=toggle_theme,
    font=("Arial", 13),
    padx=15,
    pady=7
)

theme_button.pack(side="right")



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