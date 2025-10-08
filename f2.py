import matplotlib.pyplot as plt
from datetime import datetime, timedelta

stations = [
    "GAIMUKH",
    "GOWNIWADA",
    "KASARVADVALI",
    "VIJAYGARDEN",
    "DONGARI PADA",
    "TIKUJI NI WADI",
    "MANPADA",
    "KAPURBAWDI",
    "MAJIWADA",
    "CADBUARY JUNCTION"
]

def get_dwell_time(station, terminal_station):
    if station == terminal_station:
        return 180  # Turnaround at terminal
    elif station == "KAPURBAWDI":
        return 45
    else:
        return 30

def simulate_train_round_trip(start_station_idx, direction=1, start_time_str="05:00"):
    current_time = datetime.strptime(start_time_str, "%H:%M")
    times = []
    idx = start_station_idx
    n = len(stations)
    terminal_station = stations[0] if direction == -1 else stations[-1]
    # Forward journey
    while 0 <= idx < n:
        station = stations[idx]
        dwell = get_dwell_time(station, terminal_station)
        arrival_time = current_time.strftime("%H:%M")
        current_time += timedelta(seconds=dwell)
        departure_time = current_time.strftime("%H:%M")
        times.append((station, arrival_time, departure_time))
        # Travel to next station
        if (direction == 1 and idx < n-1) or (direction == -1 and idx > 0):
            current_time += timedelta(seconds=120)
        idx += direction
    # At terminal, turnaround (already included as dwell)
    idx -= direction  # Move back to terminal index
    # Reverse journey
    direction = -direction
    terminal_station = stations[start_station_idx]  # Now the original start is the terminal
    idx += direction  # Move to next station in reverse direction
    while 0 <= idx < n:
        station = stations[idx]
        dwell = get_dwell_time(station, terminal_station)
        arrival_time = current_time.strftime("%H:%M")
        current_time += timedelta(seconds=dwell)
        departure_time = current_time.strftime("%H:%M")
        times.append((station, arrival_time, departure_time))
        # Travel to next station
        if (direction == 1 and idx < n-1) or (direction == -1 and idx > 0):
            current_time += timedelta(seconds=120)
        idx += direction
    return times

# Simulate 7 round-trip trains
train1 = simulate_train_round_trip(0, direction=1, start_time_str="05:00")
train2 = simulate_train_round_trip(0, direction=1, start_time_str="05:05")
train3 = simulate_train_round_trip(0, direction=1, start_time_str="05:10")
train4 = simulate_train_round_trip(len(stations)-1, direction=-1, start_time_str="05:00")
train5 = simulate_train_round_trip(len(stations)-1, direction=-1, start_time_str="05:07")
kapurbawdi_idx = stations.index("KAPURBAWDI")
train6 = simulate_train_round_trip(kapurbawdi_idx, direction=1, start_time_str="05:00")
train7 = simulate_train_round_trip(kapurbawdi_idx, direction=-1, start_time_str="05:00")

def plot_control_chart_7trains(*train_lists, labels, colors):
    plt.figure(figsize=(14, 7))
    for train, label, color in zip(train_lists, labels, colors):
        x = []
        y = []
        for i, (station, arr, dep) in enumerate(train):
            station_idx = stations.index(station)
            # Flat line for dwell (waiting)
            x.append(datetime.strptime(arr, "%H:%M"))
            y.append(station_idx)
            x.append(datetime.strptime(dep, "%H:%M"))
            y.append(station_idx)
            # Slope for movement (if not last station in direction)
            if i < len(train) - 1:
                next_station, next_arr, _ = train[i+1]
                next_station_idx = stations.index(next_station)
                x.append(datetime.strptime(next_arr, "%H:%M"))
                y.append(next_station_idx)
        plt.plot(x, y, label=label, marker="o", color=color)
    plt.yticks(range(len(stations)), stations)
    plt.xlabel("Time")
    plt.ylabel("Stations")
    plt.title("Control Chart for 7 Trains (Round Trip, Flat = Waiting, Slope = Moving)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

plot_control_chart_7trains(
    train1, train2, train3, train4, train5, train6, train7,
    labels=[
        "Train 1 (Gaimukh↔Cadbuary)",
        "Train 2 (Gaimukh↔Cadbuary)",
        "Train 3 (Gaimukh↔Cadbuary)",
        "Train 4 (Cadbuary↔Gaimukh)",
        "Train 5 (Cadbuary↔Gaimukh)",
        "Train 6 (Kapurbawdi↔Cadbuary)",
        "Train 7 (Kapurbawdi↔Gaimukh)"
    ],
    colors=["blue", "green", "cyan", "red", "orange", "purple", "magenta"]
)