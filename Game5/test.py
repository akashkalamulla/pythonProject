import os
import tkinter as tk
from tkinter import messagebox
import random
import time
import mysql.connector

# MySQL setup
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'pdsa_2'
}

# Establishing connection to MySQL
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
except mysql.connector.Error as err:
    print(f"Error: {err}")
    exit(1)

# Search algorithms
def binary_search(arr, x):
    low, high = 0, len(arr) - 1
    start_time = time.time()
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == x:
            return mid, time.time() - start_time
        elif arr[mid] < x:
            low = mid + 1
        else:
            high = mid - 1
    return -1, time.time() - start_time

def jump_search(arr, x):
    length = len(arr)
    step = int(length ** 0.5)
    prev, curr = 0, 0
    start_time = time.time()
    while curr < length and arr[curr] < x:
        prev = curr
        curr += step
    for i in range(prev, min(curr, length)):
        if arr[i] == x:
            return i, time.time() - start_time
    return -1, time.time() - start_time

def exponential_search(arr, x):
    if arr[0] == x:
        return 0, 0
    length = len(arr)
    i = 1
    start_time = time.time()
    while i < length and arr[i] <= x:
        i = i * 2
    return binary_search(arr[:min(i, length)], x)

def fibonacci_search(arr, x):
    length = len(arr)
    fib2 = 0
    fib1 = 1
    fibM = fib2 + fib1
    while fibM < length:
        fib2 = fib1
        fib1 = fibM
        fibM = fib2 + fib1
    offset = -1
    start_time = time.time()
    while fibM > 1:
        i = min(offset + fib2, length - 1)
        if arr[i] < x:
            fibM = fib1
            fib1 = fib2
            fib2 = fibM - fib1
            offset = i
        elif arr[i] > x:
            fibM = fib2
            fib1 -= fib2
            fib2 = fibM - fib1
        else:
            return i, time.time() - start_time
    if fib1 and arr[offset + 1] == x:
        return offset + 1, time.time() - start_time
    return -1, time.time() - start_time

def interpolation_search(arr, x):
    low, high = 0, len(arr) - 1
    start_time = time.time()
    while low <= high and arr[low] <= x <= arr[high]:
        pos = low + ((x - arr[low]) * (high - low)) // (arr[high] - arr[low])
        if arr[pos] == x:
            return pos, time.time() - start_time
        if arr[pos] < x:
            low = pos + 1
        else:
            high = pos - 1
    return -1, time.time() - start_time

# Game logic
def play_game():
    name = name_entry.get()
    if not name:
        messagebox.showwarning("Input Error", "Please enter your name.")
        return

    # Start new round
    start_game(name)

def start_game(name):
    for widget in root.winfo_children():
        widget.destroy()

    # Generate numbers and implement search
    numbers = sorted(random.sample(range(1, 1000001), 5000))
    target = random.choice(numbers)

    methods = {
        'Binary Search': binary_search,
        'Jump Search': jump_search,
        'Exponential Search': exponential_search,
        'Fibonacci Search': fibonacci_search,
        'Interpolation Search': interpolation_search
    }

    results = {}
    for method_name, method in methods.items():
        index, time_taken = method(numbers, target)
        results[method_name] = (index, time_taken)

        # Save to MySQL Database
        cursor.execute(
            """
            INSERT INTO predict_value (user_name, search_method, time_taken, index_value, target_value, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, method_name, time_taken, index, target, time.time())
        )
        conn.commit()

    random_choices = random.sample(range(5000), 3) + [results['Binary Search'][0]]
    random.shuffle(random_choices)

    tk.Label(root, text=f"Round Summary for {name}", bg='#4682b4', fg='white', font=('Arial', 16)).pack(pady=20)
    tk.Label(root, text=f"Target Number: {target}", bg='#4682b4', fg='white', font=('Arial', 14)).pack(pady=10)

    tk.Label(root, text="Guess the index of the target number:", bg='#4682b4', fg='white', font=('Arial', 14)).pack(pady=10)

    selected_index = tk.IntVar()
    for i, choice in enumerate(random_choices):
        tk.Radiobutton(root, text=f'Index {choice}', variable=selected_index, value=choice, bg='#f0f8ff',
                       font=('Arial', 14)).pack(anchor='w', padx=20, pady=5)

    def submit_guess():
        if selected_index.get() == results['Binary Search'][0]:
            messagebox.showinfo('Correct!', f'Well done, {name}! You guessed the right index.')
        else:
            messagebox.showinfo('Incorrect', 'Oops! That was not the correct index.')
        restart_game()

    tk.Button(root, text='Submit Guess', command=submit_guess, bg='#32cd32', fg='white', font=('Arial', 14)).pack(pady=20)

def restart_game():
    for widget in root.winfo_children():
        widget.destroy()
    tk.Label(root, text='Enter your name to start:', bg='#4682b4', fg='white', font=('Arial', 16)).pack(pady=20)
    name_entry = tk.Entry(root, font=('Arial', 14))
    name_entry.pack(pady=10)
    tk.Button(root, text='Start Game', command=play_game, bg='#ff4500', fg='white', font=('Arial', 14)).pack(pady=20)

# UI setup
root = tk.Tk()
root.title('Predict the Value Index Game')
root.geometry('600x500')
root.configure(bg='#4682b4')
root.minsize(600, 500)

tk.Label(root, text='Welcome to Predict the Value Index Game!', bg='#4682b4', fg='white', font=('Arial', 18, 'bold')).pack(pady=20)
tk.Label(root, text='Enter your name to start:', bg='#4682b4', fg='white', font=('Arial', 16)).pack(pady=20)

name_entry = tk.Entry(root, font=('Arial', 14))
name_entry.pack(pady=10)

tk.Button(root, text='Start Game', command=play_game, bg='#ff4500', fg='white', font=('Arial', 14)).pack(pady=20)

root.mainloop()

# Close the MySQL connection when the program ends
cursor.close()
conn.close()
