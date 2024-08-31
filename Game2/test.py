import tkinter as tk
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error
import json
import time


# Database connection
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='pdsa_2',
            user='root',
            password=''  # Replace with your MySQL password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


# Create table if it doesn't exist
def create_table():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                player_name VARCHAR(255) NOT NULL,
                time_taken VARCHAR(255) NOT NULL,
                solution TEXT NOT NULL
            )
        ''')
        connection.commit()
        cursor.close()
        connection.close()


create_table()


class SixteenQueensApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sixteen Queens Puzzle")

        # Initialize variables
        self.player_name = tk.StringVar()
        self.grid_inputs = [[tk.IntVar() for _ in range(16)] for _ in range(16)]
        self.start_time = None
        self.timer_id = None

        # Set up UI
        self.setup_ui()

    def setup_ui(self):
        # Name entry frame
        self.name_frame = tk.Frame(self.root)
        self.name_frame.pack(pady=20)

        tk.Label(self.name_frame, text="Enter Your Name:").pack(side=tk.LEFT, padx=5)
        tk.Entry(self.name_frame, textvariable=self.player_name).pack(side=tk.LEFT, padx=5)
        tk.Button(self.name_frame, text="Start Game", command=self.start_game).pack(side=tk.LEFT, padx=5)

        # Grid frame
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(pady=20)

        for i in range(16):
            tk.Label(self.grid_frame, text=f"{i + 1}st row").grid(row=i, column=0, padx=5, pady=5)
            for j in range(16):
                cell = tk.Label(self.grid_frame, text=str(j + 1), borderwidth=1, relief="solid", width=3)
                cell.grid(row=i, column=j + 1, padx=2, pady=2)
                cell.bind("<Button-1>", lambda e, row=i, col=j: self.highlight_cell(row, col))

            tk.Entry(self.grid_frame, textvariable=self.grid_inputs[i][j], width=5).grid(row=i, column=17, padx=5,
                                                                                         pady=5)

        # Control buttons and timer
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)

        self.timer_label = tk.Label(self.control_frame, text="Time: 00:00")
        self.timer_label.pack(side=tk.LEFT, padx=10)

        tk.Button(self.control_frame, text="Restart", command=self.restart_game).pack(side=tk.LEFT, padx=10)
        tk.Button(self.control_frame, text="Quit Game", command=self.quit_game).pack(side=tk.LEFT, padx=10)

        tk.Button(self.control_frame, text="Submit", command=self.submit_solution).pack(side=tk.LEFT, padx=10)

    def start_game(self):
        if self.player_name.get().strip() == "":
            messagebox.showwarning("Input Error", "Please enter your name.")
            return
        self.name_frame.pack_forget()
        self.grid_frame.pack(pady=20)
        self.control_frame.pack(pady=10)
        self.start_time = time.time()
        self.update_timer()

    def highlight_cell(self, row, col):
        for j in range(16):
            self.grid_frame.grid_slaves(row=row, column=j + 1)[0].config(bg="white")
        self.grid_frame.grid_slaves(row=row, column=col + 1)[0].config(bg="yellow")
        self.grid_inputs[row][col].set(col + 1)

    def update_timer(self):
        elapsed_time = int(time.time() - self.start_time)
        minutes, seconds = divmod(elapsed_time, 60)
        self.timer_label.config(text=f"Time: {minutes:02}:{seconds:02}")
        self.timer_id = self.root.after(1000, self.update_timer)

    def submit_solution(self):
        # Check if self.timer_id is valid before cancelling
        if self.timer_id is not None:
            try:
                self.root.after_cancel(self.timer_id)
            except ValueError:
                pass  # Ignore if the timer_id is not valid

        solution_data = {f"input{i + 1}": self.grid_inputs[i][j].get() for i in range(16) for j in range(16)}
        valid = all(1 <= self.grid_inputs[i][j].get() <= 16 for i in range(16) for j in range(16))

        if not valid:
            messagebox.showerror("Validation Error", "All inputs must be numbers between 1 and 16.")
            return

        connection = create_connection()
        if connection:
            cursor = connection.cursor()

            solution_json = json.dumps(solution_data)
            cursor.execute('SELECT * FROM results WHERE solution = %s', (solution_json,))
            existing_result = cursor.fetchone()

            if existing_result:
                messagebox.showinfo("Duplicate Entry", "Answer already entered. Try a new answer.")
            elif self.validate_puzzle_solution(solution_data):
                time_taken = self.timer_label.cget("text").split(" ")[1]
                cursor.execute('INSERT INTO results (player_name, time_taken, solution) VALUES (%s, %s, %s)',
                               (self.player_name.get(), time_taken, solution_json))
                connection.commit()
                messagebox.showinfo("Success",
                                    f"Congratulations {self.player_name.get()}, your answer is correct. Time taken: {time_taken}")
            else:
                messagebox.showerror("Incorrect Answer", "Your answer is incorrect. Try again.")

            cursor.close()
            connection.close()
        else:
            messagebox.showerror("Database Error", "Failed to connect to the database.")

    def validate_puzzle_solution(self, data):
        positions = [data[f'input{i + 1}'] for i in range(16)]
        for i in range(16):
            for j in range(i + 1, 16):
                if positions[i] == positions[j]:
                    return False
                if abs(positions[i] - positions[j]) == abs(i - j):
                    return False
        return True

    def restart_game(self):
        if self.timer_id is not None:
            try:
                self.root.after_cancel(self.timer_id)
            except ValueError:
                pass  # Ignore if the timer_id is not valid
        for row in range(16):
            for col in range(16):
                self.grid_inputs[row][col].set(0)
                self.grid_frame.grid_slaves(row=row, column=col + 1)[0].config(bg="white")
        self.start_game()

    def quit_game(self):
        if self.timer_id is not None:
            try:
                self.root.after_cancel(self.timer_id)
            except ValueError:
                pass  # Ignore if the timer_id is not valid
        self.grid_frame.pack_forget()
        self.control_frame.pack_forget()
        self.name_frame.pack(pady=20)


if __name__ == '__main__':
    root = tk.Tk()
    app = SixteenQueensApp(root)
    root.mainloop()
