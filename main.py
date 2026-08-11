import tkinter as tk
import json

#Main Window
window = tk.Tk()

window.title("My To-Do App")
window.geometry("1450x800")

#Title
title = tk.Label(
    window,
    text="My To-Do List",
    font=("Impact", 40),
    fg="light blue",
    bg="purple"
)

title.pack(pady=20)

#Functions
def add_task():  #Function to add a task to the list
    task = task_entry.get()

    if task:
        task_list.insert(tk.END, task)
        task_entry.delete(0, tk.END)

def delete_task():
    selected = task_list.curselection()

    if selected:
        task_list.delete(selected)   

def complete_task():
    selected = task_list.curselection()

    if selected:
        task = task_list.get(selected)
        task_list.delete(selected)
        task_list.insert(selected, "✓ " + task)    

def save_tasks():
    tasks = task_list.get(0, tk.END)

    with open("tasks.json", "w") as file:
        json.dump(tasks, file)     

def load_tasks():
    try:
        with open("tasks.json", "r") as file:
            tasks = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []

    for task in tasks:
        task_list.insert(tk.END, task)


#Buttons and Entry
task_entry = tk.Entry(
    window,
    width=35,
    font=("Arial", 14)
)

task_entry.pack(pady=10)

add_button = tk.Button(
    window,
    text="Add Task",
    font=("Arial", 12),
    command=add_task
)

add_button.pack(pady=10)

task_list = tk.Listbox(
    window,
    width=45,
    height=12,
    font=("Arial", 13)
)

task_list.pack(pady=20)

delete_button = tk.Button(
    window,
    text="Delete Task",
    command=delete_task
)

delete_button.pack(pady=5)

complete_button = tk.Button(
    window,
    text="Complete Task",
    command=complete_task
)

complete_button.pack(pady=5)

save_button = tk.Button(
    window,
    text="Save Tasks",
    command=save_tasks
)

save_button.pack(pady=5)

load_tasks()
window.mainloop()