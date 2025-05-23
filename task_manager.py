import json
import os

# File to persistently store all task data
SAVE_FILE = "tasks.json"

# Memory list to hold current task entries
tasks = []

# Counter for total minutes spent in focus sessions
total_focus_minutes = 0

"""
Load task data from the save file into the global tasks list.
Called when the app starts.
"""
def load_tasks():
    global tasks
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            tasks.extend(json.load(f))

"""
Save the current tasks list to a JSON file.
Called after any task list update.
"""
def save_tasks():
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

"""
Return the full list of current tasks.
Typically used to refresh the UI task list.
"""
def get_tasks():
    return tasks

"""
Create a new task dictionary and add it to the task list.
Returns (success, task/message) for validation and UI use.
"""
def create_task_entry(name, tag, due, duration, is_timed):
    if not name or name == "Task Name":
        return False, "Please enter a task name."

    if is_timed:
        if not duration.isdigit() or int(duration) <= 0:
            return False, "Please enter a valid timer duration (minutes)."

    task = {
        "name": name,
        "tag": tag if tag != "Tag" else "",
        "due": due,
        "done": False,
        "timed": is_timed,
        "duration": int(duration) if is_timed else 0
    }
    tasks.append(task)
    return True, task

"""
Delete the task at the specified index from the task list.
Index is passed from the listbox selection.
"""
def remove_task_by_index(index):
    if 0 <= index < len(tasks):
        tasks.pop(index)

"""
Toggle the 'done' status of a task at the given index.
Useful for marking tasks as complete or undoing.
"""
def change_task_status(index):
    if 0 <= index < len(tasks):
        tasks[index]['done'] = not tasks[index]['done']

"""
Increment the global focus counter by the given number of minutes.
Called when a timer successfully completes or early finish is confirmed.
"""
def add_focus_time(minutes):
    global total_focus_minutes
    total_focus_minutes += minutes

"""
Return a formatted string representing total focused time.
Used in the main UI to update the 'focus time' label.
"""
def format_focus_summary():
    hours = total_focus_minutes // 60
    minutes = total_focus_minutes % 60
    if hours:
        return f"You’ve already focused for   🧠  {hours} h {minutes} min"
    else:
        return f"You’ve already focused for   🧠  {minutes} min"
