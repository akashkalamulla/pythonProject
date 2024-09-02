import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import mysql.connector

# Set up the main application window
root = tk.Tk()
root.title("Sixteen Queens Puzzle")
root.geometry("800x800")
root.resizable(False, False)


# Set up the MySQL database connection
def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Your MySQL username
        password="",  # Your MySQL password
        database="pdsa_2"  # Your database name
    )


# Function to check for duplicate entries
def check_duplicate_entry(player_name, result):
    db = connect_to_database()
    cursor = db.cursor()

    query = """
    SELECT COUNT(*) FROM results WHERE player_name = %s AND result = %s
    """
    data = (player_name, result)

    cursor.execute(query, data)
    count = cursor.fetchone()[0]

    cursor.close()
    db.close()

    return count > 0


# Function to save the game result to the database
def save_to_database(player_name, time_taken, result):
    if check_duplicate_entry(player_name, result):
        messagebox.showwarning("Duplicate Entry", "This result has already been entered.")
        return

    db = connect_to_database()
    cursor = db.cursor()

    query = """
    INSERT INTO results (player_name, time_taken, result, date)
    VALUES (%s, %s, %s, %s)
    """
    data = (player_name, time_taken, result, datetime.now())

    cursor.execute(query, data)
    db.commit()

    cursor.close()
    db.close()

    messagebox.showinfo("Success", "Your result has been successfully saved.")


# Define global variables
start_time = None
timer_id = None
player_name = tk.StringVar()
grid_values = [[tk.StringVar() for _ in range(1)] for _ in range(16)]
selected_cells = [[None for _ in range(1)] for _ in range(16)]  # To track selected cells


# Function to start the game
def start_game():
    name = player_name.get().strip()
    if not name:
        messagebox.showwarning("Input Error", "Please enter your name.")
        return

    # Hide the name form and show the grid form
    name_frame.pack_forget()
    grid_frame.pack(fill='both', expand=True)
    display_name_label.config(text=f"Player: {name}")
    start_timer()


# Function to restart the game
def restart_game():
    stop_timer()
    for row in grid_values:
        for var in row:
            var.set('')
    for row_cells in selected_cells:
        for cell in row_cells:
            if cell:
                cell.config(bg='white')  # Reset cell color
    start_timer()


# Function to quit the game
def quit_game():
    stop_timer()
    grid_frame.pack_forget()
    name_frame.pack(fill='both', expand=True)


# Function to handle form submission
def submit_solution():
    # Retrieve and validate inputs
    solution = {}
    for i in range(16):
        value = grid_values[i][0].get()
        if value.isdigit() and 1 <= int(value) <= 16:
            solution[f'input{i + 1}'] = int(value)
        else:
            messagebox.showwarning("Invalid Input", f"Row {i + 1} input is invalid. Enter a number between 1 and 16.")
            return

    if validate_puzzle_solution(solution):
        elapsed_time = datetime.now() - start_time
        minutes, seconds = divmod(int(elapsed_time.total_seconds()), 60)
        messagebox.showinfo("Success",
                            f"Congratulations! Your answer is correct.\nPlayer: {player_name.get()}\nTime: {minutes:02}:{seconds:02}")

        # Save the result to the database
        save_to_database(player_name.get(), f"{minutes:02}:{seconds:02}", "correct")
    else:
        messagebox.showwarning("Incorrect", "The answer is wrong.")

        # Save the result to the database
        elapsed_time = datetime.now() - start_time
        minutes, seconds = divmod(int(elapsed_time.total_seconds()), 60)
        save_to_database(player_name.get(), f"{minutes:02}:{seconds:02}", "incorrect")


# Function to validate the solution
def validate_puzzle_solution(data):
    # Convert input dictionary to a list of positions
    positions = [data[f'input{i}'] for i in range(1, 17)]

    # Check for the same row, column, and diagonal conflicts
    for i in range(16):
        for j in range(i + 1, 16):
            if positions[i] == positions[j]:  # Same column
                return False
            if abs(positions[i] - positions[j]) == abs(i - j):  # Same diagonal
                return False
    return True


# Function to start the timer
def start_timer():
    global start_time, timer_id
    start_time = datetime.now()
    update_timer()


# Function to update the timer
def update_timer():
    global timer_id
    elapsed_time = (datetime.now() - start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    timer_label.config(text=f"Time: {minutes:02}:{seconds:02}")
    timer_id = root.after(1000, update_timer)


# Function to stop the timer
def stop_timer():
    if timer_id:
        root.after_cancel(timer_id)


# Name input frame
name_frame = tk.Frame(root)
name_frame.pack(fill='both', expand=True, padx=20, pady=20)

tk.Label(name_frame, text="Enter Your Name", font=("Arial", 18)).pack(pady=10)
name_entry = tk.Entry(name_frame, textvariable=player_name, font=("Arial", 14))
name_entry.pack(pady=10)
start_button = tk.Button(name_frame, text="Start Game", command=start_game, font=("Arial", 14))
start_button.pack(pady=10)

# Game grid frame
grid_frame = tk.Frame(root)
display_name_label = tk.Label(grid_frame, text="", font=("Arial", 18))
display_name_label.pack(pady=10)

control_frame = tk.Frame(grid_frame)
control_frame.pack(pady=10)

timer_label = tk.Label(control_frame, text="Time: 00:00", font=("Arial", 14))
timer_label.pack(side='left', padx=10)

restart_button = tk.Button(control_frame, text="Restart", command=restart_game, font=("Arial", 14))
restart_button.pack(side='left', padx=10)
quit_button = tk.Button(control_frame, text="Quit", command=quit_game, font=("Arial", 14))
quit_button.pack(side='left', padx=10)
submit_button = tk.Button(control_frame, text="Submit", command=submit_solution, font=("Arial", 14))
submit_button.pack(side='left', padx=10)

# Create the 16x16 grid
grid_container = tk.Frame(grid_frame)
grid_container.pack(pady=10)

# Create grid cells
for i in range(16):
    row_cells = []
    for j in range(16):
        cell = tk.Label(grid_container, text=str(j + 1), width=4, height=2, borderwidth=1, relief="solid",
                        font=("Arial", 10))
        cell.grid(row=i, column=j)
        cell.bind("<Button-1>", lambda e, i=i, j=j: on_cell_click(i, j))
        row_cells.append(cell)

    input_entry = tk.Entry(grid_container, textvariable=grid_values[i][0], width=4, font=("Arial", 10))
    input_entry.grid(row=i, column=16)
    input_entry.bind("<KeyRelease>", lambda e, i=i: update_grid_from_entry(i))

    selected_cells[i] = row_cells


def on_cell_click(row, col):
    # Deselect previously selected cell in the row
    for cell in selected_cells[row]:
        if cell.cget('bg') == 'lightblue':
            cell.config(bg='white')

    # Select the clicked cell
    selected_cells[row][col].config(bg='lightblue')
    grid_values[row][0].set(col + 1)


def update_grid_from_entry(row):
    try:
        value = int(grid_values[row][0].get())
        if 1 <= value <= 16:
            col = value - 1
            on_cell_click(row, col)
        else:
            # Reset to white if the value is out of range
            for cell in selected_cells[row]:
                cell.config(bg='white')
    except ValueError:
        pass  # Ignore if the entry is not a valid integer


root.mainloop()
