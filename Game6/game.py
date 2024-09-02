import random
import time
import heapq
from tkinter import Tk, Entry, Button, Canvas
import mysql.connector

# Generate random numbers and letter
random_numbers = [random.randint(5, 50) for _ in range(45)]
random_letter = chr(random.randint(ord('A'), ord('J')))
random_city = f"City {random_letter}"

# Define cities and city index
cities = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
city_index = {cities[i]: i for i in range(len(cities))}

# Generate random distances between cities
names = ["AJ", "BJ", "CJ", "DJ", "EJ", "FJ", "GJ", "HJ", "IJ", "AI", "BI", "CI", "DI", "EI", "FI",
         "GI", "HI", "AH", "BH", "CH", "DH", "EH", "FH", "GH", "AG", "BG", "CG", "DG", "EG", "FG",
         "AF", "BF", "CF", "DF", "EF", "AE", "BE", "CE", "DE", "AD", "BD", "CD", "AC", "BC", "AB"]

random_numbers_with_names = [[names[i], random_numbers[i]] for i in range(45)]

# Initialize the distance matrix
inf = float('inf')
distances = [[inf] * len(cities) for _ in range(len(cities))]

# Fill the distance matrix with the generated random distances
for pair, distance in random_numbers_with_names:
    if len(pair) == 2:  # Ensure the pair has exactly 2 characters
        from_city = pair[0]
        to_city = pair[1]
        from_idx = city_index[from_city]
        to_idx = city_index[to_city]
        distances[from_idx][to_idx] = distance
        distances[to_idx][from_idx] = distance  # Assuming it's a symmetric matrix

# Bellman-Ford algorithm to find shortest paths from the random city
def bellman_ford(dist_matrix, start_city_idx):
    num_cities = len(dist_matrix)
    dist = [inf] * num_cities
    pred = [None] * num_cities  # Predecessor array to store the path
    dist[start_city_idx] = 0

    # Relax edges up to (num_cities - 1) times
    for _ in range(num_cities - 1):
        for i in range(num_cities):
            for j in range(num_cities):
                if dist[i] != inf and dist[i] + dist_matrix[i][j] < dist[j]:
                    dist[j] = dist[i] + dist_matrix[i][j]
                    pred[j] = i  # Track the predecessor

    # Check for negative-weight cycles
    for i in range(num_cities):
        for j in range(num_cities):
            if dist[i] != inf and dist[i] + dist_matrix[i][j] < dist[j]:
                print("Graph contains a negative-weight cycle")
                return None, None

    return dist, pred

# Function to reconstruct the shortest path
def get_path(pred, start, end):
    path = []
    while end is not None:
        path.insert(0, cities[end])
        end = pred[end]
    if path[0] == cities[start]:
        return path
    return []

# Dijkstra's algorithm to find shortest paths from the start city
def dijkstra(dist_matrix, start_city_idx):
    num_cities = len(dist_matrix)
    dist = [inf] * num_cities
    pred = [None] * num_cities  # Predecessor array to store the path
    dist[start_city_idx] = 0
    priority_queue = [(0, start_city_idx)]  # (distance, city_idx)

    while priority_queue:
        current_dist, u = heapq.heappop(priority_queue)

        if current_dist > dist[u]:
            continue

        for v in range(num_cities):
            if dist_matrix[u][v] < inf:
                new_dist = dist[u] + dist_matrix[u][v]
                if new_dist < dist[v]:
                    dist[v] = new_dist
                    pred[v] = u
                    heapq.heappush(priority_queue, (new_dist, v))

    return dist, pred

# Compute shortest paths from the selected city using Bellman-Ford
start_city_idx = city_index[random_letter]
start_time = time.time()
shortest_paths_bf, predecessors_bf = bellman_ford(distances, start_city_idx)
end_time = time.time()
bellman_time = end_time - start_time

# Compute shortest paths from the selected city using Dijkstra
start_time = time.time()
shortest_paths_dj, predecessors_dj = dijkstra(distances, start_city_idx)
end_time = time.time()
dijkstra_time = end_time - start_time

# Tkinter GUI Setup
window = Tk()
window.title("Identify Shortest Path")
window.geometry("1440x1059")
window.configure(bg="#002D44")

distance_A = [0] * 20  # To store user inputs

def submit_handler():
    try:
        for i in range(10):
            distance_A[i] = int(entries[i].get())
        for i in range(10, 20):
            distance_A[i] = entries[i].get()
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def validate_user_input():
    is_valid = True
    for i in range(10):
        user_distance = distance_A[i]
        correct_distance = shortest_paths_bf[i]
        if user_distance != correct_distance:
            print(f"Incorrect distance for City {cities[i]}: Expected {correct_distance}, got {user_distance}")
            is_valid = False

    for i in range(10, 20):
        user_path = distance_A[i]
        correct_path = ''.join(get_path(predecessors_bf, start_city_idx, i - 10))
        if user_path != correct_path:
            print(f"Incorrect path for City {cities[i - 10]}: Expected {correct_path}, got {user_path}")
            is_valid = False

    if is_valid:
        print("All inputs are correct!")
        save_data_to_database(
            name="Player Name",
            time_bellman_ford=bellman_time,
            time_dijkstra=dijkstra_time,
            distance_A=distance_A,
        )
    else:
        print("Some inputs are incorrect.")

def save_data_to_database(name, time_bellman_ford, time_dijkstra, distance_A):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='pdsa_2'
        )

        cursor = connection.cursor()
        cursor.execute("SELECT MAX(game_round) FROM shortest_path")
        last_round = cursor.fetchone()[0]  # Fetch the last round number

        game_round = (last_round + 1) if last_round is not None else 1

        insert_query = """
        INSERT INTO shortest_path (
            game_round, name, Time_Bellman_Ford, Time_Dijkstra, distance_A, distance_B, distance_C, distance_D, distance_E, distance_F, distance_G, distance_H, distance_I, distance_J, path_A, path_B, path_C, path_D, path_E, path_F, path_G, path_H, path_I, path_J
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = (
            game_round, name, time_bellman_ford, time_dijkstra,
            distance_A[0], distance_A[1], distance_A[2], distance_A[3], distance_A[4],
            distance_A[5], distance_A[6], distance_A[7], distance_A[8], distance_A[9],
            distance_A[10], distance_A[11], distance_A[12], distance_A[13], distance_A[14],
            distance_A[15], distance_A[16], distance_A[17], distance_A[18], distance_A[19]
        )

        cursor.execute(insert_query, data)
        connection.commit()

        print("Data saved successfully.")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# GUI layout
canvas = Canvas(
    window,
    bg = "#002D44",
    height = 1059,
    width = 1440,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)

# Create input fields for distances and paths
entries = []
for i in range(20):
    entry = Entry(
        bd=0,
        bg="#4D6ADE",
        fg="#000716",
        highlightthickness=0
    )
    entry.place(
        x=164 + (i % 10) * 120,
        y=632 + (i // 10) * 80,
        width=71.85709381103516,
        height=59.06383514404297
    )
    entries.append(entry)

submit_button = Button(
    window,
    text="Submit",
    command=submit_handler
)
submit_button.place(
    x=700,
    y=900
)

window.mainloop()
