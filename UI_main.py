import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
import datetime

from config import *
from task_manager import *
from focus_timer import launch_focus_ui

# ================= GUI Initialization =================
# Create main application window with title and theme colors
root = tk.Tk()
root.title("FocusBuddy - A Smart To-Do Companion")
root.geometry("1000x750")
root.configure(bg=COLOR_BG)

# ================= Hover Effects =================
# Hover effect for buttons
def on_enter(e):
    e.widget.config(bg=COLOR_BUTTON_HOVER)
def on_leave(e):
    e.widget.config(bg=COLOR_BUTTON)

# ================= Input Fields =================
# Create top input area for new tasks
frame_input = tk.Frame(root, bg=COLOR_FRAME)
frame_input.pack(pady=20, padx=20, fill='x')

# Input for task name
entry_task = tk.Entry(frame_input, width=35, font=FONT_MAIN, bg=COLOR_ENTRY_BG, fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
entry_task.insert(0, "Task Name")
entry_task.bind("<FocusIn>", lambda e: entry_task.delete(0, tk.END) if entry_task.get() == "Task Name" else None)
entry_task.grid(row=0, column=0, padx=10, pady=8)

# Input for tag
entry_tag = tk.Entry(frame_input, width=20, font=FONT_MAIN, bg=COLOR_ENTRY_BG, fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
entry_tag.insert(0, "Tag")
entry_tag.bind("<FocusIn>", lambda e: entry_tag.delete(0, tk.END) if entry_tag.get() == "Tag" else None)
entry_tag.grid(row=0, column=1, padx=10, pady=8)

# Date selector for due date
entry_due = DateEntry(frame_input, width=14, font=FONT_MAIN, date_pattern='yyyy-mm-dd', background=COLOR_BUTTON, foreground=COLOR_TEXT)
entry_due.grid(row=0, column=2, padx=10, pady=8)

# Input for duration in minutes
entry_duration = tk.Entry(frame_input, width=10, font=FONT_MAIN, bg=COLOR_ENTRY_BG, fg=COLOR_TEXT, insertbackground=COLOR_TEXT)
entry_duration.grid(row=1, column=1, padx=10)
entry_duration.insert(0, "25")
entry_duration.config(state='disabled')

# Checkbox to mark task as timed
var_is_timed = tk.BooleanVar()
check_timed = tk.Checkbutton(frame_input, text="Timed Task", font=FONT_MAIN, variable=var_is_timed, command=lambda: entry_duration.config(state='normal' if var_is_timed.get() else 'disabled'), bg=COLOR_FRAME, fg=COLOR_TEXT, activebackground=COLOR_FRAME, activeforeground=COLOR_TEXT, selectcolor=COLOR_FRAME)
check_timed.grid(row=1, column=0, padx=10, pady=5, sticky='w')

# ================= Task List Display =================
# Refresh the displayed list of tasks
def refresh_task_list():
    listbox_tasks.delete(0, tk.END)
    for task in get_tasks():
        status = "✔" if task['done'] else "☐"
        timed_info = f" ⏱{task['duration']}min" if task.get("timed") else ""
        display = f"{status} {task['name']} [Tag: {task['tag']}] Due: {task['due']}{timed_info}"
        listbox_tasks.insert(tk.END, display)

# Update focus summary label
def update_focus_display():
    label_focus.config(text=format_focus_summary())

# ================= Task Actions =================
# Add new task to list
def add_task():
    name = entry_task.get()
    tag = entry_tag.get()
    due = entry_due.get()
    duration = entry_duration.get()
    is_timed = var_is_timed.get()

    result, task = create_task_entry(name, tag, due, duration, is_timed)
    if not result:
        messagebox.showwarning("Warning", task)
        return

    save_tasks()
    refresh_task_list()

    if is_timed:
        launch_focus_ui(task, refresh_task_list, update_focus_display)

    # Reset inputs
    entry_task.delete(0, tk.END)
    entry_task.insert(0, "Task Name")
    entry_tag.delete(0, tk.END)
    entry_tag.insert(0, "Tag")
    entry_due.set_date(datetime.today())
    entry_duration.config(state='normal')
    entry_duration.delete(0, tk.END)
    entry_duration.insert(0, "25")
    entry_duration.config(state='disabled')
    var_is_timed.set(False)

# Delete selected task
def delete_task():
    selected = listbox_tasks.curselection()
    if not selected:
        return
    index = selected[0]
    remove_task_by_index(index)
    save_tasks()
    refresh_task_list()

# Toggle completion of selected task
def mark_done():
    selected = listbox_tasks.curselection()
    if not selected:
        return
    index = selected[0]
    change_task_status(index)
    save_tasks()
    refresh_task_list()

# ================= Buttons =================
# Add Task button
btn_add = tk.Button(frame_input, text="Add Task", command=add_task)
btn_add.grid(row=0, column=4, rowspan=2, padx=20, pady=10)
btn_add.config(bg=COLOR_BUTTON, fg=COLOR_TEXT, activebackground=COLOR_BUTTON_HOVER, font=FONT_MAIN, relief="flat", cursor="hand2", height=2, width=12)
btn_add.bind("<Enter>", on_enter)
btn_add.bind("<Leave>", on_leave)

# Task list display box
listbox_tasks = tk.Listbox(root, width=110, height=15, font=("Consolas", 16), bg=COLOR_ENTRY_BG, fg=COLOR_TEXT, selectbackground="#3399FF", selectforeground="white", activestyle='none', borderwidth=0, highlightthickness=0, selectmode=tk.SINGLE)
listbox_tasks.pack(pady=25, padx=40)

# Complete/Delete buttons
frame_buttons = tk.Frame(root, bg=COLOR_BG)
frame_buttons.pack(pady=25)

btn_done = tk.Button(frame_buttons, text="Complete", command=mark_done)
btn_done.grid(row=0, column=0, padx=10, ipadx=10, ipady=5)
btn_done.config(bg=COLOR_BUTTON, fg=COLOR_TEXT, activebackground=COLOR_BUTTON_HOVER, font=FONT_MAIN, relief="flat", cursor="hand2")
btn_done.bind("<Enter>", on_enter)
btn_done.bind("<Leave>", on_leave)

btn_delete = tk.Button(frame_buttons, text="Delete", command=delete_task)
btn_delete.grid(row=0, column=1, padx=10, ipadx=10, ipady=5)
btn_delete.config(bg=COLOR_BUTTON, fg=COLOR_TEXT, activebackground=COLOR_BUTTON_HOVER, font=FONT_MAIN, relief="flat", cursor="hand2")
btn_delete.bind("<Enter>", on_enter)
btn_delete.bind("<Leave>", on_leave)

# Label for focus summary
label_focus = tk.Label(root, text=format_focus_summary(), font=FONT_TITLE, fg=COLOR_TEXT, bg=COLOR_BG)
label_focus.pack(pady=20)

# ================= Program Start =================
# Load saved tasks and populate UI
load_tasks()
refresh_task_list()
root.mainloop()
