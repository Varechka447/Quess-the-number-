import tkinter as tk
from tkinter import messagebox
import random
import datetime
import os
import json

#Главное окно приложения
root = tk.Tk()
root.title("Угадай число")
root.geometry("600x500")

current_diff = "easy"
secret_number = None
attempts = 0
game_start_time = None

ranges = {
    "easy": (1, 10),
    "medium": (1, 50),
    "hard": (1, 100)
}

stats = {
    "wins": 0,
    "losses": 0,
    "total_wrong_guesses": 0
}
#Окно статистики
stats_window = None
wins_label = None
losses_label = None
wrongs_label = None

log_file = os.path.join(os.path.dirname(__file__), "guess_game.log")
stats_file = os.path.join(os.path.dirname(__file__), "guess_stats.json")

#Инициализация лога
def init_log():
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=== Лог игры 'Угадай число' ===\n")
            f.write("Формат: [Время] СОБЫТИЕ: описание\n\n")

#Запись в лог всех действий игрока
def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)

#Сброс цвета кнопок
def load_stats():
    global stats
    if os.path.exists(stats_file):
        try:
            with open(stats_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                stats["wins"] = data.get("wins", 0)
                stats["losses"] = data.get("losses", 0)
                stats["total_wrong_guesses"] = data.get("total_wrong_guesses", 0)
        except Exception:
            pass

def save_stats():
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def select_diff(diff):
    global current_diff
    current_diff = diff
    default_bg = "SystemButtonFace"
    easy_btn.config(bg=default_bg)
    medium_btn.config(bg=default_bg)
    hard_btn.config(bg=default_bg)

    if diff == "easy":
        easy_btn.config(bg="lightgreen")
    elif diff == "medium":
        medium_btn.config(bg="lightgreen")
    else:
        hard_btn.config(bg="lightgreen")

def start_game():
    global secret_number, attempts, game_start_time
    game_start_time = datetime.datetime.now()
    min_val, max_val = ranges[current_diff]
    secret_number = random.randint(min_val, max_val)
    attempts = 0

    log(f"НОВАЯ ИГРА | сложность: {current_diff} | диапазон: {min_val}–{max_val} | загаданное: {secret_number}")

    range_label.config(text=f"Угадайте число от {min_val} до {max_val}")
    feedback_label.config(text="")
    entry.delete(0, tk.END)

    diff_frame.pack_forget()
    start_btn.pack_forget()
    guess_frame.pack(expand=True)

def make_guess(event=None):
    global attempts, secret_number, game_start_time
    try:
        guess = int(entry.get().strip())
    except ValueError:
        feedback_label.config(text="Введите целое число!")
        entry.delete(0, tk.END)
        return

    attempts += 1

    if guess == secret_number:
        duration = datetime.datetime.now() - game_start_time
        stats["wins"] += 1
        save_stats()
        update_stats_if_open()

        log(f"ПОБЕДА | попыток: {attempts} | время игры: {duration.total_seconds():.1f} сек | число: {secret_number}")

        messagebox.showinfo("Победа!", f"Вы угадали число {secret_number} за {attempts} попыток!")
        reset_to_start()
    else:
        stats["total_wrong_guesses"] += 1
        save_stats()
        update_stats_if_open()

        if guess > secret_number:
            feedback_label.config(text="Слишком большое! Введите число меньше.")
            log(f"Попытка {attempts}: {guess} -> слишком большое")
        else:
            feedback_label.config(text="Слишком маленькое! Введите число больше.")
            log(f"Попытка {attempts}: {guess} -> слишком маленькое")

        entry.delete(0, tk.END)

#Кнопка "Сдаться"
def surrender():
    global attempts, secret_number, game_start_time
    duration = datetime.datetime.now() - game_start_time
    stats["losses"] += 1
    save_stats()
    update_stats_if_open()

    log(f"СДАЛСЯ | попыток: {attempts} | время игры: {duration.total_seconds():.1f} сек | загаданное было: {secret_number}")

    messagebox.showinfo("Поражение", f"Вы сдались. Загаданное число было {secret_number}.")
    reset_to_start()

#Возврат в главное окно
def reset_to_start():
    global secret_number, attempts, game_start_time
    guess_frame.pack_forget()
    diff_frame.pack(anchor="nw", padx=20, pady=20)
    start_btn.pack(expand=True, pady=120)
    secret_number = None
    attempts = 0
    game_start_time = None

#Окно статистики
def open_stats():
    global stats_window, wins_label, losses_label, wrongs_label

    if stats_window and stats_window.winfo_exists():
        stats_window.lift()
        return

#Создание нового окна
    stats_window = tk.Toplevel(root)
    stats_window.title("Статистика")
    stats_window.geometry("340x220")
    stats_window.resizable(False, False)

    tk.Label(stats_window, text="Статистика игры", font=("Arial", 14)).pack(pady=10)
#Вывод статистики
    wins_label = tk.Label(stats_window, text=f"Победы: {stats['wins']}", font=("Arial", 16), fg="green")
    wins_label.pack(pady=5)

    losses_label = tk.Label(stats_window, text=f"Поражения: {stats['losses']}", font=("Arial", 16), fg="red")
    losses_label.pack(pady=5)

    wrongs_label = tk.Label(stats_window, text=f"Всего неверных попыток: {stats['total_wrong_guesses']}",
                            font=("Arial", 14), fg="#555")
    wrongs_label.pack(pady=8)

    tk.Button(stats_window, text="Закрыть", command=stats_window.destroy).pack(pady=10)

def update_stats_if_open():
    global wins_label, losses_label, wrongs_label, stats_window
    if stats_window and stats_window.winfo_exists():
        if wins_label:
            wins_label.config(text=f"Победы: {stats['wins']}")
        if losses_label:
            losses_label.config(text=f"Поражения: {stats['losses']}")
        if wrongs_label:
            wrongs_label.config(text=f"Всего неверных попыток: {stats['total_wrong_guesses']}")

init_log()
load_stats()

#Главное меню выбора сложности
diff_frame = tk.Frame(root)
diff_frame.pack(anchor="nw", padx=20, pady=20)

easy_btn = tk.Button(diff_frame, text="Лёгкий (1-10)", font=("Arial", 12), width=15,
                     command=lambda: select_diff("easy"))
easy_btn.pack(side="left", padx=5)

medium_btn = tk.Button(diff_frame, text="Средний (1-50)", font=("Arial", 12), width=15,
                       command=lambda: select_diff("medium"))
medium_btn.pack(side="left", padx=5)

hard_btn = tk.Button(diff_frame, text="Тяжёлый (1-100)", font=("Arial", 12), width=15,
                     command=lambda: select_diff("hard"))
hard_btn.pack(side="left", padx=5)

start_btn = tk.Button(root, text="СТАРТ", font=("Arial", 24), bg="green", fg="white",
                      command=start_game)
start_btn.pack(expand=True, pady=120)

#Игровое окно
guess_frame = tk.Frame(root)

range_label = tk.Label(guess_frame, text="", font=("Arial", 14))
range_label.pack(pady=20)

#Поле ввода числа
entry = tk.Entry(guess_frame, font=("Arial", 20), width=10, justify="center")
entry.pack(pady=10)
entry.bind("<Return>", make_guess)

btns_frame = tk.Frame(guess_frame)
btns_frame.pack(pady=10)

guess_btn = tk.Button(btns_frame, text="Угадать", font=("Arial", 14), bg="blue", fg="white",
                      command=make_guess)
guess_btn.pack(side="left", padx=20)

surrender_btn = tk.Button(btns_frame, text="Сдаться", font=("Arial", 14), bg="red", fg="white",
                          command=surrender)
surrender_btn.pack(side="left", padx=20)

feedback_label = tk.Label(guess_frame, text="", font=("Arial", 12), fg="red")
feedback_label.pack(pady=20)

stats_btn = tk.Button(root, text="Статистика", font=("Arial", 12),
                      command=open_stats)
stats_btn.pack(side="bottom", anchor="se", padx=20, pady=20)

select_diff("easy")

root.mainloop()