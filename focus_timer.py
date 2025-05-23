import tkinter as tk
from tkinter import messagebox
import threading
import time
from task_manager import add_focus_time
from config import *

"""
Create and run the full-screen focus timer interface for the selected task.
Handles countdown logic, pause/resume, and early termination options.
"""
def launch_focus_ui(task, refresh_callback, update_focus_label):
    pause_used = False
    focus_win = tk.Toplevel()
    focus_win.attributes("-fullscreen", True)
    focus_win.protocol("WM_DELETE_WINDOW", lambda: None)
    focus_win.configure(bg="#0f0f0f")

    FONT_TIMER = ("Consolas", 80, "bold")
    FONT_TITLE_TOP = ("Arial", 30, "italic")
    COLOR_BTN = "#2458A5"
    COLOR_BTN_HOVER = "#3399FF"

    def on_enter(e):
        e.widget.config(bg=COLOR_BTN_HOVER)

    def on_leave(e):
        e.widget.config(bg=COLOR_BTN)

    title_label = tk.Label(focus_win, text=f"Focusing: {task['name']}", font=FONT_TITLE_TOP, fg=COLOR_TEXT, bg="#0f0f0f")
    title_label.pack(pady=30)

    timer_label = tk.Label(focus_win, text="00:00", font=FONT_TIMER, fg=COLOR_TEXT, bg="#0f0f0f")
    timer_label.pack(expand=True)

    duration = task['duration']
    remaining_seconds = duration * 60
    pause_flag = threading.Event()

    """
     Countdown logic for the timer, updates UI every second.
     """
    def countdown():
        nonlocal remaining_seconds
        while remaining_seconds > 0:
            if pause_flag.is_set():
                time.sleep(1)
                continue
            mins, secs = divmod(remaining_seconds, 60)
            timer_label.config(text=f"{mins:02d}:{secs:02d}")
            time.sleep(1)
            remaining_seconds -= 1

        task['done'] = True
        add_focus_time(duration)
        update_focus_label()
        refresh_callback()
        messagebox.showinfo("Notice", f"Task '{task['name']}' completed!")
        focus_win.destroy()

    """
    Triggered when user clicks 'End'. Offers discard or record partial session.
    """
    def handle_task_end():
        nonlocal remaining_seconds
        elapsed = (duration * 60 - remaining_seconds) // 60
        if elapsed < 1:
            confirm = tk.Toplevel(focus_win)
            confirm.title("Notice")
            confirm.geometry("500x150")
            confirm.configure(bg="#0f0f0f")

            def close_and_return():
                confirm.destroy()
                focus_win.destroy()

            tk.Label(confirm, text="Focus time less than 1 minute will not be recorded.", font=FONT_MAIN, fg=COLOR_TEXT, bg="#0f0f0f").pack(pady=20)
            confirm_button = tk.Button(confirm, text="OK", font=FONT_MAIN, bg=COLOR_BTN, fg="white", command=close_and_return)
            confirm_button.pack(pady=10)
            confirm_button.bind("<Enter>", on_enter)
            confirm_button.bind("<Leave>", on_leave)
            return

        dialog = tk.Toplevel(focus_win)
        dialog.title("End Options")
        dialog.geometry("400x220")
        dialog.configure(bg="#0f0f0f")

        def discard():
            dialog.destroy()
            focus_win.destroy()

        def finish():
            task['done'] = True
            add_focus_time(elapsed)
            update_focus_label()
            refresh_callback()
            dialog.destroy()
            focus_win.destroy()

        def cancel():
            dialog.destroy()

        tk.Label(dialog, text="Focus time exceeded 1 minute. Choose an option:", font=FONT_MAIN, fg=COLOR_TEXT, bg="#0f0f0f").pack(pady=15)
        for txt, cmd in [
            ("Discard and do not record", discard),
            ("Finish early and record time", finish),
            ("Cancel", cancel)
        ]:
            confirm_button = tk.Button(dialog, text=txt, font=FONT_MAIN, bg=COLOR_BTN, fg="white", command=cmd)
            confirm_button.pack(pady=5)
            confirm_button.bind("<Enter>", on_enter)
            confirm_button.bind("<Leave>", on_leave)

    """
    Triggered when 'Pause' is clicked. Allows 1-time pause selection.
    Opens pause selection popup and initiates pause flow.
    """
    def pause_task():
        nonlocal pause_used, remaining_seconds
        if pause_used:
            temp = tk.Toplevel(focus_win)
            temp.title("Notice")
            temp.geometry("300x150")
            temp.configure(bg="#0f0f0f")
            tk.Label(temp, text="Each task can only be paused once.", font=FONT_MAIN, fg=COLOR_TEXT, bg="#0f0f0f").pack(pady=20)
            confirm_button = tk.Button(temp, text="OK", font=FONT_MAIN, bg=COLOR_BTN, fg="white", command=temp.destroy)
            confirm_button.pack(pady=10)
            confirm_button.bind("<Enter>", on_enter)
            confirm_button.bind("<Leave>", on_leave)
            return

        pause_win = tk.Toplevel(focus_win)
        pause_win.title("Pause Timer")
        pause_win.geometry("500x350")
        pause_win.attributes("-topmost", True)
        pause_win.configure(bg="#0f0f0f")
        tk.Label(pause_win, text="Select pause duration (minutes):", font=FONT_TITLE, fg=COLOR_TEXT, bg="#0f0f0f").pack(pady=10)

        pause_var = tk.IntVar(value=1)
        for i in range(1, 6):
            tk.Radiobutton(pause_win, text=f"{i} minute{'s' if i > 1 else ''}", variable=pause_var, value=i, font=FONT_MAIN,
                           fg=COLOR_TEXT, bg="#0f0f0f", activebackground="#0f0f0f", selectcolor="#0f0f0f").pack(anchor='w', padx=20, pady=2)

        def confirm_pause():
            pause_win.destroy()
            start_pause_timer(pause_var.get())

        confirm_button = tk.Button(pause_win, text="Confirm", font=FONT_MAIN, bg=COLOR_BTN, fg="white", command=confirm_pause)
        confirm_button.pack(pady=20)
        confirm_button.bind("<Enter>", on_enter)
        confirm_button.bind("<Leave>", on_leave)

    """
    Shows a countdown screen for the selected pause duration.
    During pause, main countdown is halted.
    """
    def start_pause_timer(minutes):
        nonlocal remaining_seconds, pause_used
        pause_used = True
        pause_flag.set()

        pause_seconds = minutes * 60
        pause_popup = tk.Toplevel()
        pause_popup.title("Paused")
        pause_popup.geometry("600x400")
        pause_popup.attributes("-topmost", True)
        pause_popup.configure(bg="#0f0f0f")
        pause_label = tk.Label(pause_popup, text="", font=("Consolas", 32), fg=COLOR_TEXT, bg="#0f0f0f")
        pause_label.pack(pady=30)

        def resume():
            pause_popup.destroy()
            pause_flag.clear()

        resume_button = tk.Button(pause_popup, text="Resume Timer", font=("Arial", 18), bg=COLOR_BTN, fg="white", command=resume)
        resume_button.pack(pady=20)
        resume_button.bind("<Enter>", on_enter)
        resume_button.bind("<Leave>", on_leave)

        def tick():
            nonlocal pause_seconds
            if pause_seconds <= 0:
                pause_popup.destroy()
                pause_flag.clear()
                return
            mins, secs = divmod(pause_seconds, 60)
            pause_label.config(text=f"Time remaining: {mins:02d}:{secs:02d}")
            pause_seconds -= 1
            pause_popup.after(1000, tick)

        tick()

    pause_btn = tk.Button(focus_win, text="Pause", font=FONT_MAIN, bg=COLOR_BTN, fg="white", command=pause_task,
                          width=14, height=2)
    pause_btn.pack(side='left', padx=40, pady=10)
    pause_btn.bind("<Enter>", on_enter)
    pause_btn.bind("<Leave>", on_leave)

    end_btn = tk.Button(focus_win, text="End", font=FONT_MAIN, bg=COLOR_BTN, fg="white", command=handle_task_end,
                        width=14, height=2)
    end_btn.pack(side='right', padx=40, pady=10)
    end_btn.bind("<Enter>", on_enter)
    end_btn.bind("<Leave>", on_leave)

    threading.Thread(target=countdown, daemon=True).start()
