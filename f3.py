import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

# ----------- Metro Station Data -----------
stations_data = [
    ("GAIMUKH", 0.0, 180, 35),
    ("GOWNIWADA", 1502.229, 30, 45),
    ("KASARVADVALI", 1385.394, 30, 45),
    ("VIJAYGARDEN", 1024.036, 30, 45),
    ("DONGARI PADA", 1198.778, 30, 45),
    ("TIKUJI NI WADI", 1226.694, 30, 45),
    ("MANPADA", 758.992, 30, 45),
    ("KAPURBAWDI", 815.824, 30, 45),
    ("MAJIWADA", 1453.707, 30, 45),
    ("CADBUARY JUNCTION", 824.707, 180, 45)
]
stations = [s[0] for s in stations_data]

def calculate_run_time(distance, civil_speed):
    if distance == 0:
        return 0
    # ★ Optimization logic:
    if distance < 900:
        vmax_kmph = 30.0  # No optimization
    elif 1100 <= distance < 1200:
        vmax_kmph = 33.0  # Moderate optimization
    elif distance >= 1250:
        vmax_kmph = 35.0  # Maximum optimization
    else:
        vmax_kmph = 30.0  # Default
    vmax_kmph = min(vmax_kmph, civil_speed)
    vmax = vmax_kmph * 1000 / 3600
    brake_distance = 150.0
    buffer_distance = 50.0
    accelerating_distance = distance / 8.0
    accel = vmax ** 2 / (2 * accelerating_distance)
    t_accel = vmax / accel
    t_decel = np.sqrt(2 * (brake_distance + buffer_distance) / accel)
    d_cruise = distance - accelerating_distance - brake_distance
    t_cruise = d_cruise / vmax if d_cruise > 0 else 0
    if d_cruise < 0:
        d_half = max(distance - brake_distance, distance / 2.0)
        v_peak = np.sqrt(2 * accel * d_half)
        t_accel = v_peak / accel
        t_decel = np.sqrt(2 * brake_distance / accel)
        t_cruise = 0
    return t_accel + t_cruise + t_decel  # in seconds

# ----------- ML Dwell Time Model for Each Station -----------
def generate_dwell_model(station_name, peak_hours):
    times = pd.date_range("05:00", "23:59", freq="3min")
    passengers = np.where(
        times.hour.isin(peak_hours),
        np.random.poisson(45, len(times)),
        np.random.poisson(20, len(times))
    )
    dwell = 30 + (passengers * 0.6721) + np.random.randint(0, 10, len(times))
    df = pd.DataFrame({
        "Station": station_name,
        "Minutes": times.hour * 60 + times.minute,
        "Dwell_Time": dwell
    })
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(df[["Minutes"]], df["Dwell_Time"])
    return model

ml_models = {
    station: generate_dwell_model(station, peak_hours=[8,9,17,18])
    for station in stations
}

def get_ml_dwell(station, terminal_station, current_time):
    if station == terminal_station:
        return 180  # Turnaround at terminal
    minutes = current_time.hour * 60 + current_time.minute
    dwell = ml_models[station].predict(pd.DataFrame({"Minutes": [minutes]}))[0]
    print(f"{station}: dwell={dwell}")
    return max(dwell, 30)  # or even 45 for clarity

def simulate_train_round_trip_ml(start_station_idx, direction=1, start_time_str="05:00"):
    current_time = datetime.strptime(start_time_str, "%H:%M")
    times = []
    idx = start_station_idx
    n = len(stations)
    terminal_station = stations[0] if direction == -1 else stations[-1]
    # Forward journey
    while 0 <= idx < n:
        station = stations[idx]
        dwell = get_ml_dwell(station, terminal_station, current_time)
        arrival_time = current_time.strftime("%H:%M:%S")
        current_time += timedelta(seconds=dwell)
        departure_time = current_time.strftime("%H:%M:%S")
        print(f"{station} | {arrival_time} -> {departure_time} | dwell: {dwell:.2f} sec")
        times.append((station, arrival_time, departure_time))
        # Travel to next station
        if (direction == 1 and idx < n-1) or (direction == -1 and idx > 0):
            from_idx, to_idx = idx, idx+direction
            dist = abs(stations_data[to_idx][1] - stations_data[from_idx][1])
            speed = stations_data[to_idx][3]
            current_time += timedelta(seconds=calculate_run_time(dist, speed))
        idx += direction
    # At terminal, turnaround dwell already included
    idx -= direction
    # Reverse journey
    direction = -direction
    terminal_station = stations[start_station_idx]
    idx += direction
    while 0 <= idx < n:
        station = stations[idx]
        dwell = get_ml_dwell(station, terminal_station, current_time)
        arrival_time = current_time.strftime("%H:%M:%S")
        current_time += timedelta(seconds=dwell)
        departure_time = current_time.strftime("%H:%M:%S")
        print(f"{station} | {arrival_time} -> {departure_time} | dwell: {dwell:.2f} sec")
        times.append((station, arrival_time, departure_time))
        if (direction == 1 and idx < n-1) or (direction == -1 and idx > 0):
            from_idx, to_idx = idx, idx+direction
            dist = abs(stations_data[to_idx][1] - stations_data[from_idx][1])
            speed = stations_data[to_idx][3]
            current_time += timedelta(seconds=calculate_run_time(dist, speed))  # ★
        idx += direction
    return times

# Build cumulative distances at the start of your script
cumulative_distances = [0]
for i in range(1, len(stations_data)):
    cumulative_distances.append(cumulative_distances[-1] + stations_data[i][1])

# ----------- Simulate 7 ML Trains (Round Trip) -----------
train1 = simulate_train_round_trip_ml(0, direction=1, start_time_str="05:00")
train2 = simulate_train_round_trip_ml(0, direction=1, start_time_str="05:05")
train3 = simulate_train_round_trip_ml(0, direction=1, start_time_str="05:10")
train4 = simulate_train_round_trip_ml(len(stations)-1, direction=-1, start_time_str="05:00")
train5 = simulate_train_round_trip_ml(len(stations)-1, direction=-1, start_time_str="05:07")
kapurbawdi_idx = stations.index("KAPURBAWDI")
train6 = simulate_train_round_trip_ml(kapurbawdi_idx, direction=1, start_time_str="05:00")
train7 = simulate_train_round_trip_ml(kapurbawdi_idx, direction=-1, start_time_str="05:00")

def plot_control_chart_7trains(*train_lists, labels, colors):
    plt.figure(figsize=(14, 7))
    for train, label, color in zip(train_lists, labels, colors):
        x = []
        y = []
        star_x = []
        star_y = []
        double_star_x = []
        double_star_y = []
        for i, (station, arr, dep) in enumerate(train):
            station_idx = stations.index(station)
            x.append(datetime.strptime(arr, "%H:%M:%S"))
            y.append(station_idx)
            x.append(datetime.strptime(dep, "%H:%M:%S"))
            y.append(station_idx)
            if i < len(train) - 1:
                next_station, next_arr, _ = train[i+1]
                next_station_idx = stations.index(next_station)
                # Correct distance calculation for both directions:
                from_idx = station_idx
                to_idx = next_station_idx
                distance = abs(cumulative_distances[to_idx] - cumulative_distances[from_idx])
                if distance >= 1100:
                    t1 = datetime.strptime(dep, "%H:%M:%S")
                    t2 = datetime.strptime(next_arr, "%H:%M:%S")
                    mid_time = t1 + (t2 - t1) / 2
                    mid_station = (station_idx + next_station_idx) / 2
                    star_x.append(mid_time)
                    star_y.append(mid_station)
                x.append(datetime.strptime(next_arr, "%H:%M:%S"))
                y.append(next_station_idx)
        plt.plot(x, y, label=label, marker="o", color=color)
        # Plot single stars for >850m
        plt.plot(star_x, star_y, marker="*", color="gold", linestyle="None", markersize=15, label="Optimized")
        # Plot double stars for >1150m (use a different marker, e.g., "P" or "X")
        # plt.plot(double_star_x, double_star_y, marker="+", color="red", linestyle="None", markersize=15, label=f"{label} (Optimized >1150m)")
    plt.yticks(range(len(stations)), stations)
    plt.xlabel("Time")
    plt.ylabel("Stations")
    plt.title("Control Chart for 7 Trains (ML Dwell, Optimized Headway, Round Trip)")
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

print("Fixed dwell arrival:", fixed_train_full[-1][1], fixed_train_full[-1][2])
print("Optimized dwell arrival:", optimized_train_full[-1][1], optimized_train_full[-1][2])
print("ML dwell arrival:", ml_train_full[-1][1], ml_train_full[-1][2])

def simulate_train_full_times_optimized_fixed_dwell(start_time_str, fixed_dwell=30):
    times = []
    current_time = datetime.strptime(start_time_str, "%H:%M")
    # First station: departure only
    times.append((stations[0][0], None, current_time.strftime("%H:%M:%S")))
    for i in range(len(stations)-1):
        from_station, _, _, civil_speed = stations_data[i]
        to_station, distance, _, _ = stations_data[i+1]
        # Use optimized speed only where allowed
        if distance < 900:
            vmax_kmph = 30.0
        elif 900 <= distance < 1100:
            vmax_kmph = 36.0
        elif distance >= 1100:
            vmax_kmph = 38.0
        else:
            vmax_kmph = 30.0
        vmax_kmph = min(vmax_kmph, civil_speed)
        vmax = vmax_kmph * 1000 / 3600
        brake_distance = 150.0
        buffer_distance = 50.0
        accelerating_distance = distance / 8.0
        accel = vmax ** 2 / (2 * accelerating_distance)
        t_accel = vmax / accel
        t_decel = np.sqrt(2 * (brake_distance + buffer_distance) / accel)
        d_cruise = distance - accelerating_distance - brake_distance
        t_cruise = d_cruise / vmax if d_cruise > 0 else 0
        if d_cruise < 0:
            d_half = max(distance - brake_distance, distance / 2.0)
            v_peak = np.sqrt(2 * accel * d_half)
            t_accel = v_peak / accel
            t_decel = np.sqrt(2 * brake_distance / accel)
            t_cruise = 0
        runtime = t_accel + t_cruise + t_decel
        current_time += timedelta(seconds=runtime)
        arrival_time = current_time.strftime("%H:%M:%S")
        # Use fixed dwell
        current_time += timedelta(seconds=fixed_dwell)
        departure_time = current_time.strftime("%H:%M:%S")
        times.append((to_station, arrival_time, departure_time))
    return times