import tkinter as tk
import sqlite3
import os


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
            completed INTEGER DEFAULT 0
        )
    """)

    connection.commit()
    connection.close()


# -----------------------------
# Load tasks from SQLite
# -----------------------------

def load_tasks():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, task, description, completed
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
            "completed": bool(row[3])
        })

    return tasks
# -----------------------------
# Add a new task
# -----------------------------

def add_task():
    task_text = task_entry.get().strip()
    description = description_entry.get("1.0", tk.END).strip()

    if task_text:

        connection = sqlite3.connect(DATABASE_NAME)
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO tasks (task, description, completed)
            VALUES (?, ?, ?)
        """, (task_text, description, 0))

        connection.commit()
        connection.close()

        task_entry.delete(0, tk.END)
        description_entry.delete("1.0", tk.END)

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

        # Task title
        checkbox = tk.Checkbutton(
            task_frame,
            text=task["task"],
            variable=var,
            command=lambda i=index: toggle_task(i),
            font=("Arial", 14),
            anchor="w"
        )

        checkbox.grid(
            row=index * 2,
            column=0,
            sticky="w",
            padx=15,
            pady=(10, 0)
        )

        # Task description
        description = tk.Label(
            task_frame,
            text=task.get("description", ""),
            font=("Arial", 11),
            anchor="w"
        )

        description.grid(
            row=index * 2 + 1,
            column=0,
            sticky="w",
            padx=40,
            pady=(0, 5)
        )

        # Delete button
        delete_button = tk.Button(
            task_frame,
            text="Delete",
            command=lambda i=index: delete_task(i),
            font=("Arial", 11),
            padx=12,
            pady=5
        )

        delete_button.grid(
            row=index * 2,
            column=1,
            rowspan=2,
            padx=15,
            pady=5
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

task_label = tk.Label(
    input_frame,
    text="Task:"
)

task_label.grid(
    row=0,
    column=0,
    sticky="w",
    padx=10
)

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

description_label = tk.Label(
    input_frame,
    text="Description:"
)

description_label.grid(
    row=2,
    column=0,
    sticky="w",
    padx=10
)

description_entry = tk.Text(
    input_frame,
    width=40,
    height=3,
    font=("Arial", 12)
)

description_entry.grid(
    row=3,
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
    row=3,
    column=1,
    padx=10,
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