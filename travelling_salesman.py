import random
import math
import time

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from tqdm import tqdm
from copy import deepcopy


def edge(one, two):
    return distance_matrix[one, two]

def mean(lst):
    return sum(lst)/len(lst)

def dist(cycle):
    total = 0

    for first in range(len(cycle)):
        a = cycle[first]
        b = cycle[(first + 1) % len(cycle)]
        total += edge(a, b)

    return total


def nearest_n(city, n):
    return nearest_list[city][:n]


def generate_move(state, a, b):
    new_state = state[:a] + state[b:a-1:-1] + state[b+1:]
    old_edges = (
        edge(state[a-1], state[a])
        + edge(state[b], state[(b+1) % CITIES]))
    new_edges = (
            edge(new_state[a - 1], new_state[a])
            + edge(new_state[b], new_state[(b + 1) % CITIES]))
    difference = new_edges - old_edges
    return new_state, difference


def generate_move_to(state):
    # S1 a...b-1
    # S2 b...c-1
    # S3 c...a-1

    a, b, c = sorted(random.sample(range(CITIES), 3))

    s1 = state[a:b]
    s2 = state[b:c]
    s3 = state[c:] + state[:a]

    # Starts and ends of each sector
    city_indexes = [
        [state[a], state[b - 1]],
        [state[b], state[c - 1]],
        [state[c], state[a - 1]]
    ]

    original_edge_sum = (
        edge(city_indexes[0][1], city_indexes[1][0])
        + edge(city_indexes[1][1], city_indexes[2][0])
        + edge(city_indexes[2][1], city_indexes[0][0])
    )

    proposed_edge_sums = np.array([
        (
                edge(city_indexes[0][0], city_indexes[1][0])
                + edge(city_indexes[1][1], city_indexes[2][0])
                + edge(city_indexes[2][1], city_indexes[0][1])
        ),
        (
                edge(city_indexes[0][1], city_indexes[1][1])
                + edge(city_indexes[1][0], city_indexes[2][0])
                + edge(city_indexes[2][1], city_indexes[0][0])
        ),
        (
                edge(city_indexes[0][1], city_indexes[1][0])
                + edge(city_indexes[1][1], city_indexes[2][1])
                + edge(city_indexes[2][0], city_indexes[0][0])
        ),
        (
                edge(city_indexes[0][1], city_indexes[2][0])
                + edge(city_indexes[2][1], city_indexes[1][0])
                + edge(city_indexes[1][1], city_indexes[0][0])
        ),
        (
                edge(city_indexes[0][0], city_indexes[2][0])
                + edge(city_indexes[2][1], city_indexes[1][0])
                + edge(city_indexes[1][1], city_indexes[0][1])
        ),
        (
                edge(city_indexes[0][1], city_indexes[2][1])
                + edge(city_indexes[2][0], city_indexes[1][0])
                + edge(city_indexes[1][1], city_indexes[0][0])
        ),
        (
                edge(city_indexes[0][1], city_indexes[2][0])
                + edge(city_indexes[2][1], city_indexes[1][1])
                + edge(city_indexes[1][0], city_indexes[0][0])
        )

    ])

    # routes = [s1[::-1] + s2 + s3,
    #           s1 + s2[::-1] + s3,
    #           s1 + s2 + s3[::-1],
    #           s1 + s3 + s2,
    #           s1[::-1] + s3 + s2,
    #           s1 + s3[::-1] + s2,
    #           s1 + s3 + s2[::-1]]

    shortest_edge_sum = np.min(proposed_edge_sums)

    delta = shortest_edge_sum - original_edge_sum
    shortest_index = np.argmin(proposed_edge_sums)

    shortest_state = None
    if shortest_index == 0:
        shortest_state = s1[::-1] + s2 + s3
    elif shortest_index == 1:
        shortest_state = s1 + s2[::-1] + s3
    elif shortest_index == 2:
        shortest_state = s1 + s2 + s3[::-1]
    elif shortest_index == 3:
        shortest_state = s1 + s3 + s2
    elif shortest_index == 4:
        shortest_state = s1[::-1] + s3 + s2
    elif shortest_index == 5:
        shortest_state = s1 + s3[::-1] + s2
    elif shortest_index == 6:
        shortest_state = s1 + s3 + s2[::-1]

    return shortest_state, delta


# ---------------------------------------------- ALGORITHMS ------------------------------------------------------------
def gd():

    history = [tour.copy()]

    moved = True
    while moved:
        moved = False
        lowest_delta = float('inf')
        best_state = None
        for i in range(1, CITIES):
            for j in range(i+1, CITIES):
                next_state, delta_e = generate_move(history[-1], i, j)
                if delta_e < lowest_delta:
                    lowest_delta = delta_e
                    best_state = next_state

        if lowest_delta < 0:
            moved = True
            history.append(best_state.copy())
    return history

def animate_gd(history):
    def update(frame):
        x_points = [city_coords[x][0] for x in history[frame]] + [city_coords[history[frame][0]][0]]
        y_points = [city_coords[y][1] for y in history[frame]] + [city_coords[history[frame][0]][1]]
        line.set_data(x_points, y_points)
        text.set_text(f"2-opt\n"
                         f"Distance: {dist(history[frame])}")
        return line,

    fig, ax = plt.subplots()
    fig.canvas.manager.window.geometry("+50+50")
    ax.scatter([city_coords[x][0] for x in tour], [city_coords[y][1] for y in tour], color='hotpink', zorder=5)
    line, = ax.plot([city_coords[x][0] for x in tour],
                          [city_coords[y][1] for y in tour], 'green')
    text = ax.text(
        0.02, 1.03,
        f"2-opt\n"
        f"Distance: {dist(history[0])}",
        transform=ax.transAxes,
        clip_on=False
    )

    return FuncAnimation(fig, update, interval=ANIMATION_TIME/len(history), frames=len(history), repeat=False)


# ----------------------------------------------------------------------------------------------------------------------


def to():
    history = [tour.copy()]

    no_move = 0
    while no_move < 20_000:
        no_move += 1
        next_state, delta_e = generate_move_to(history[-1])
        if delta_e < -0.00000001:
            history.append(next_state.copy())
            no_move = 0

    return history

def animate_to(history):
    def update(frame):
        x_points = [city_coords[x][0] for x in history[frame]] + [city_coords[history[frame][0]][0]]
        y_points = [city_coords[y][1] for y in history[frame]] + [city_coords[history[frame][0]][1]]
        line.set_data(x_points, y_points)
        text.set_text(f"3-opt\n"
                         f"Distance: {dist(history[frame])}")
        return line,

    fig, ax = plt.subplots()
    fig.canvas.manager.window.geometry("+650+50")
    ax.scatter([city_coords[x][0] for x in tour], [city_coords[y][1] for y in tour], color='hotpink', zorder=5)
    line, = ax.plot([city_coords[x][0] for x in tour],
                          [city_coords[y][1] for y in tour], 'purple')
    text = ax.text(
        0.02, 1.03,
        f"3-opt\n"
        f"Distance: {dist(history[0])}",
        transform=ax.transAxes,
        clip_on=False
    )

    return FuncAnimation(fig, update, interval=ANIMATION_TIME/len(history), frames=len(history), repeat=False)


# ----------------------------------------------------------------------------------------------------------------------


def sa():
    def initialise_temp_sa():
        state, = history
        c = 0
        bad_move_deltas = []
        while c < 1000:
            i, j = sorted(random.sample(range(1, CITIES), 2))
            _, init_delta = generate_move(state, i, j)
            if init_delta > 0:
                c += 1
                bad_move_deltas.append(init_delta)
        avg_bad_move_delta = sum(bad_move_deltas) / len(bad_move_deltas)
        return -avg_bad_move_delta / math.log(initial_probability)

    history = [tour.copy()]
    initial_probability = 0.9
    t = t0 = initialise_temp_sa()
    proposed_moves = 0
    accepted_moves = 0
    acceptance_rate = 1

    while t/t0 > 0.001:
        for _ in range(100):
            i, j = sorted(random.sample(range(1, CITIES), 2))
            proposed_state, delta_e = generate_move(history[-1], i, j)
            proposed_moves += 1
            if delta_e < 0:
                history.append(proposed_state.copy())
                accepted_moves += 1
            else:
                if random.random() < math.e ** -(delta_e / t):
                    history.append(proposed_state.copy())
                    accepted_moves += 1
            if proposed_moves % 10_000 == 0:
                acceptance_rate = accepted_moves / proposed_moves
                proposed_moves = 0
                accepted_moves = 0
        t *= 0.999
    return history

def animate_sa(history):
    def update(frame):
        x_points = [city_coords[x][0] for x in ani_history[frame]] + [city_coords[ani_history[frame][0]][0]]
        y_points = [city_coords[y][1] for y in ani_history[frame]] + [city_coords[ani_history[frame][0]][1]]
        line.set_data(x_points, y_points)
        text.set_text(f"Simulated Annealing (2-opt)\n"
                      f"Distance: {dist(ani_history[frame])}")
        return line,

    frames = 200
    ani_frames = np.linspace(0, len(history) - 1, frames, dtype=int)
    ani_history = [history[x] for x in ani_frames]

    fig, ax = plt.subplots()
    fig.canvas.manager.window.geometry("+800+50")
    ax.scatter([city_coords[x][0] for x in tour], [city_coords[y][1] for y in tour], color='hotpink', zorder=5)
    line, = ax.plot([city_coords[x][0] for x in tour],
                          [city_coords[y][1] for y in tour])
    text = ax.text(
        0.02, 1.03,
        f"Simulated Annealing (2-opt)\n"
        f"Distance: {dist(history[0])}",
        transform=ax.transAxes,
        clip_on=False
    )

    return FuncAnimation(fig, update, interval=ANIMATION_TIME/frames, frames=frames, repeat=False)


# ----------------------------------------------------------------------------------------------------------------------


def sato():
    def initialise_temp_sato():
        state, = history
        c = 0
        bad_move_deltas = []
        while c < 1000:
            _, init_delta = generate_move_to(state)
            if init_delta > 0:
                c += 1
                bad_move_deltas.append(init_delta)
        avg_bad_move_delta = sum(bad_move_deltas) / len(bad_move_deltas)
        return -avg_bad_move_delta / math.log(initial_probability)

    history = [tour.copy()]

    initial_probability = 0.9
    t = t0 = initialise_temp_sato()
    proposed_moves = 0
    accepted_moves = 0
    acceptance_rate = 1

    while t / t0 > 0.001:
        for _ in range(100):
            proposed_state, delta_e = generate_move_to(history[-1])
            proposed_moves += 1
            if delta_e < 0:
                history.append(proposed_state.copy())
                accepted_moves += 1
            else:
                if random.random() < math.e ** -(delta_e / t):
                    history.append(proposed_state.copy())
                    accepted_moves += 1
            if proposed_moves % 10_000 == 0:
                acceptance_rate = accepted_moves / proposed_moves
                proposed_moves = 0
                accepted_moves = 0
        t *= 0.999
    return history

def animate_sato(history):
    def update(frame):
        x_points = [city_coords[x][0] for x in ani_history_sato[frame]] + [city_coords[ani_history_sato[frame][0]][0]]
        y_points = [city_coords[y][1] for y in ani_history_sato[frame]] + [city_coords[ani_history_sato[frame][0]][1]]
        line.set_data(x_points, y_points)
        text.set_text(f"Simulated Annealing (3-opt)\n"
                      f"Distance: {dist(ani_history_sato[frame])}")
        return line,

    frames = 200
    ani_frames_sato = np.linspace(0, len(history) - 1, frames, dtype=int)
    ani_history_sato = [history[x] for x in ani_frames_sato]

    fig, ax = plt.subplots()
    fig.canvas.manager.window.geometry("+800+650")
    ax.scatter([city_coords[x][0] for x in tour], [city_coords[y][1] for y in tour], color='hotpink', zorder=5)
    line, = ax.plot([city_coords[x][0] for x in tour],
                              [city_coords[y][1] for y in tour])
    text = ax.text(
        0.02, 1.03,
        f"Simulated Annealing (3-opt)\n"
        f"Distance: {dist(history[0])}",
        transform=ax.transAxes,
        clip_on=False
    )

    return FuncAnimation(fig, update, interval=ANIMATION_TIME/frames, frames=frames, repeat=False)


# ----------------------------------------------------------------------------------------------------------------------


def lk():
    neighbours = 6
    max_depth = 5

    def edge_exists(a, b, cities_dict):
        if a in cities_dict[b]:
            return True
        return False

    def create_edge(a, b, cities_dict):
        cities_dict[a].append(b)
        cities_dict[b].append(a)

        return cities_dict

    def remove_edge(a, b, cities_dict):
        cities_dict[a].remove(b)
        cities_dict[b].remove(a)

        return cities_dict

    def pick_edge(curr, cities_dict):
        og_city = curr
        next_city = cities_dict[curr][0]

        while True:
            if len(cities_dict[next_city]) == 1:
                return cities_dict[og_city][1]
            if next_city == og_city:
                return cities_dict[og_city][0]
            new_next_city = cities_dict[next_city][0] if cities_dict[next_city][0] != curr else cities_dict[next_city][1]
            curr, next_city = next_city, new_next_city

    def close_edge(cities_dict):
        close_dict = deepcopy(cities_dict)
        end_cities = []
        for node in close_dict:
            if len(close_dict[node]) == 1:
                end_cities.append(node)
        close_dict = create_edge(end_cities[0], end_cities[1], close_dict)
        return close_dict

    def dict_to_list(cities_dict):
        cities_list = [0]
        current_city = 0
        prev_city = -1
        while True:
            a, b = cities_dict[current_city]
            next_city = a if a != prev_city else b
            prev_city, current_city = current_city, next_city
            cities_list.append(current_city)
            if current_city == cities_list[0]:
                break
        return cities_list

    def recurse(t_i, cities_dict_input, visited, g_i, depth=0):
        nonlocal g_star_best
        nonlocal cities_dict_best
        og_g_i = g_i
        for t_next in nearest_n(t_i, neighbours):
            cities_dict = deepcopy(cities_dict_input)
            g_i = og_g_i
            if t_next in visited:
                continue
            if edge_exists(t_i, t_next, cities_dict):
                continue
            g_i -= edge(t_i, t_next)
            if g_i < 0:
                continue

            cities_dict = create_edge(t_i, t_next, cities_dict)
            t_final = pick_edge(t_next, cities_dict)

            cities_dict = remove_edge(t_next, t_final, cities_dict)

            g_i += edge(t_next, t_final)
            g_star = g_i - edge(t_final, t1)
            if g_star > g_star_best:
                g_star_best = g_star
                cities_dict_best = close_edge(cities_dict)
            if g_i > 0:
                visited.add(t_next)
                visited.add(t_final)
                if depth < max_depth:
                    recurse(t_final, deepcopy(cities_dict), visited.copy(), g_i, depth+1)

    history = [tour.copy()]
    cities = {}
    for i, city in enumerate(history[-1]):
        cities[city] = [history[-1][i - 1], history[-1][(i + 1) % CITIES]]
    for _ in range(1000):
        t1 = random.randint(0, CITIES-1)  # start city
        t2 = cities[t1][random.randint(0, 1)]  # second city
        cities = remove_edge(t1, t2, cities)
        g_star_best = 0
        cities_dict_best = {}
        og_visited = {t1, t2}

        recurse(t2, deepcopy(cities), og_visited.copy(), edge(t1, t2))
        if g_star_best > 0:
            history.append(dict_to_list(cities_dict_best))
            for i, city in enumerate(history[-1]):
                cities[city] = [history[-1][i - 1], history[-1][(i + 1) % CITIES]]
        else:
            cities = close_edge(cities)
    return history
    # ---------------------------------------- ANIMATION ------------------------------------------

def animate_lk(history):
    def update(frame):
        x_points = [city_coords[x][0] for x in history[frame]] + [city_coords[history[frame][0]][0]]
        y_points = [city_coords[y][1] for y in history[frame]] + [city_coords[history[frame][0]][1]]
        line.set_data(x_points, y_points)
        text.set_text(f"Lin-Kernighan\n"
                      f"Distance: {dist(history[frame])}")
        return line,

    fig, ax = plt.subplots()
    fig.canvas.manager.window.geometry("+1350+50")
    ax.scatter([city_coords[x][0] for x in tour], [city_coords[y][1] for y in tour], color='hotpink', zorder=5)

    line, = ax.plot([city_coords[x][0] for x in tour + [tour[0]]],
                    [city_coords[y][1] for y in tour + [tour[0]]], 'maroon')
    text = ax.text(
        0.02, 1.03,
        f"Lin-Kernighan\n"
        f"Distance: {dist(history[0])}",
        transform=ax.transAxes,
        clip_on=False
    )

    return FuncAnimation(fig, update, interval=ANIMATION_TIME / len(history), frames=len(history),
                         repeat=False)


CITIES_LIST = [10, 25, 50, 75, 100]
ANIMATION_TIME = 1
ANIMATION_TIME *= 1000
ITERATIONS = 10

init_lengths = []
gd_lengths = []
to_lengths = []
sa_lengths = []
sato_lengths = []
lk_lengths = []

gd_times = []
to_times = []
sa_times = []
sato_times = []
lk_times = []

for CITIES in CITIES_LIST:
    for _ in tqdm(range(ITERATIONS)):
        city_coords = np.random.rand(CITIES, 2) * 100
        distance_matrix = np.linalg.norm(city_coords[None] - city_coords[:, None], axis=2)
        nearest_list = [sorted([x for x in range(CITIES) if x != i], key=lambda y: edge(y, i)) for i in range(CITIES)]
        tour = list(range(CITIES))

        start = time.perf_counter()
        gd_h = gd()
        break_1 = time.perf_counter()
        to_h = to()
        break_2 = time.perf_counter()
        sa_h = sa()
        break_3 = time.perf_counter()
        sato_h = [sato()[-1]]
        break_4 = time.perf_counter()
        lk_h = lk()
        end = time.perf_counter()

        init_lengths.append(dist(tour))
        gd_lengths.append(dist(gd_h[-1]))
        to_lengths.append(dist(to_h[-1]))
        sa_lengths.append(dist(sa_h[-1]))
        sato_lengths.append(dist(sato_h[-1]))
        lk_lengths.append(dist(lk_h[-1]))

        gd_times.append(break_1 - start)
        to_times.append(break_2 - break_1)
        sa_times.append(break_3 - break_2)
        sato_times.append(break_4 - break_3)
        lk_times.append(end - break_4)

    print(
        CITIES, "\n",
        mean(init_lengths), mean(gd_lengths), mean(to_lengths), mean(sa_lengths), mean(sato_lengths), mean(lk_lengths),
        "\n", mean(gd_times), mean(to_times), mean(sa_times), mean(sato_times), mean(lk_times))

def animate_all():
    animations = [
        animate_lk(lk_h),


                  ]

    plt.show()