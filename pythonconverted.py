import csv
import math
from datetime import timedelta, datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Station:
    def __init__(self, name, line, stype, distance, run_time, dwell_time, civil_speed):
        self.station_name = name
        self.line_name = line
        self.station_type = stype
        self.distance = distance
        self.run_time = run_time
        self.dwell_time = dwell_time
        self.civil_speed = civil_speed

stations = [
    Station("GAIMUKH", "LINE4", "METRO_6CAR", 0.0, 180, 180, 35),
    Station("GOWNIWADA", "LINE4", "METRO_6CAR", 1502.229, 180, 30, 45),
    Station("KASARVADVALI", "LINE4", "METRO_6CAR", 1385.394, 180, 30, 45),
    Station("VIJAYGARDEN", "LINE4", "METRO_6CAR", 1024.036, 180, 30, 45),
    Station("DONGARI PADA", "LINE4", "METRO_6CAR", 1198.778, 180, 30, 45),
    Station("TIKUJI NI WADI", "LINE4", "METRO_6CAR", 1226.694, 180, 30, 45),
    Station("MANPADA", "LINE4", "METRO_6CAR", 758.992, 180, 30, 45),
    Station("KAPURBAWDI", "LINE4", "METRO_6CAR", 815.824, 180, 30, 45),
    Station("MAJIWADA", "LINE4", "METRO_6CAR", 1453.707, 180, 30, 45),
    Station("CADBUARY JUNCTION", "LINE4", "METRO_6CAR", 824.707, 180, 180, 45)
]

def calculate_run_time(distance, civil_speed):
    brake_distance = 150.0
    buffer_distance = 50.0
    vmax_kmph = 35.0 if distance > 800 else 30.0
    vmax_kmph = min(vmax_kmph, civil_speed)
    vmax = vmax_kmph * 1000.0 / 3600.0

    accelerating_distance = distance / 8.0
    # Prevent division by zero or negative acceleration
    if accelerating_distance <= 0:
        accelerating_distance = 1.0

    accel = vmax * vmax / (2.0 * accelerating_distance)
    if accel <= 0:
        accel = 0.5  # set a minimum acceleration

    t_accel = vmax / accel
    t_decel = math.sqrt(2 * (brake_distance + buffer_distance) / accel)
    d_cruise = distance - accelerating_distance - brake_distance
    t_cruise = d_cruise / vmax if d_cruise > 0 else 0

    if d_cruise < 0:
        d_half = (distance - brake_distance) if (distance - brake_distance) > 0 else (distance / 2.0)
        if accel > 0 and d_half > 0:
            v_peak = math.sqrt(2 * accel * d_half)
            t_accel = v_peak / accel
            t_decel = math.sqrt(2 * brake_distance / accel)
        else:
            t_accel = t_decel = 0
        t_cruise = 0

    return t_accel + t_cruise + t_decel

def safest_headway(avg_speed, distance):
    buffer_distance = 50.0
    brake_distance = 150.0
    if distance > 800:
        top_speed = 35.0 * 1000.0 / 3600.0
    else:
        top_speed = 30.0 * 1000.0 / 3600.0
    return (brake_distance + buffer_distance) / top_speed

def main():
    total_runtime = 0.0
    total_distance = 0.0
    total_dwell_time = 0.0

    with open("section_3.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["From", "To", "Distance(m)", "RunTime(s)", "DwellTime(s)", "TotalSectionTime(s)", "AverageSpeed(km/h)", "SafeHeadway(s)"])
        for i in range(len(stations) - 1):
            distance = stations[i+1].distance
            civil_speed = min(stations[i].civil_speed, stations[i+1].civil_speed)
            runtime = calculate_run_time(distance, civil_speed)
            dwell_time = stations[0].dwell_time if i == 0 else stations[i+1].dwell_time
            section_time = runtime + dwell_time
            avg_speed = (distance / runtime) * 3.6 if runtime > 0 else 0
            safe_headway = safest_headway(avg_speed, distance)

            writer.writerow([
                stations[i].station_name,
                stations[i+1].station_name,
                distance,
                runtime,
                dwell_time,
                section_time,
                avg_speed,
                safe_headway
            ])

            total_runtime += runtime
            total_distance += distance
            total_dwell_time += dwell_time

        total_dwell_time += stations[0].dwell_time  # Add starting terminal dwell

        overall_headway_min = ((total_runtime + total_dwell_time) * 2) / 7.0 / 60.0

        writer.writerow(["#Total running distance:", total_distance])
        writer.writerow(["#Total run time (s):", total_runtime])
        writer.writerow(["#Total dwell time (s):", total_dwell_time])
        writer.writerow(["#Overall headway for 7 trains (min):", overall_headway_min])

    print(f"Overall headway for 7 trains (min): {overall_headway_min}")
    print("CSV file 'section_3.csv' created. Open it in Excel.")

    generate_timetable()

def generate_timetable():
    with open("timetable_5to6.csv", "w", newline='') as timetable:
        writer = csv.writer(timetable)
        writer.writerow(["Station", "Arrival", "Departure"])

        current_time_sec = 5 * 3600  # 5:00 AM in seconds
        arrival = "--"
        departure = "05:00:00"
        writer.writerow([stations[0].station_name, arrival, departure])

        for i in range(1, len(stations)):
            # Use section distance (difference between consecutive stations)
            distance = stations[i].distance - stations[i-1].distance
            civil_speed = min(stations[i-1].civil_speed, stations[i].civil_speed)
            runtime = calculate_run_time(distance, civil_speed)

            # Arrival time at this station
            current_time_sec += int(runtime)
            arr_time = str(timedelta(seconds=current_time_sec))
            if len(arr_time) < 8:
                arr_time = "0" + arr_time

            dwell_time = stations[i].dwell_time
            current_time_sec += dwell_time

            dep_time = str(timedelta(seconds=current_time_sec))
            if len(dep_time) < 8:
                dep_time = "0" + dep_time

            # Only write if arrival is before 6:00 AM
            if current_time_sec <= 6 * 3600:
                writer.writerow([stations[i].station_name, arr_time, dep_time])
            else:
                if (current_time_sec - dwell_time) < 6 * 3600:
                    writer.writerow([stations[i].station_name, arr_time, "--"])
                break

    print("Timetable written to timetable_5to6.csv")

    # Read the timetable
    df = pd.read_csv("timetable_5to6.csv")

    # Convert time strings to seconds since 5:00:00
    def time_to_seconds(t):
        if t == "--":
            return None
        h, m, s = map(int, t.split(":"))
        return h*3600 + m*60 + s

    df['Arrival_sec'] = df['Arrival'].apply(time_to_seconds)
    df['Departure_sec'] = df['Departure'].apply(time_to_seconds)

    # Build the plot data
    y = []
    x = []
    station_labels = df['Station'].tolist()
    for i, row in df.iterrows():
        if row['Arrival'] != "--":
            x.append(row['Arrival_sec'])
            y.append(i)
        if row['Departure'] != "--":
            x.append(row['Departure_sec'])
            y.append(i)

    # Convert seconds to HH:MM for x-ticks
    def sec_to_hhmm(sec):
        h = sec // 3600
        m = (sec % 3600) // 60
        return f"{int(h):02d}:{int(m):02d}"

    import numpy as np
    plt.figure(figsize=(10, 6))
    plt.step(x, y, where='post', linewidth=2)
    plt.yticks(range(len(station_labels)), station_labels)

    # Set x-axis from journey start to journey end
    plt.xlim(min(x), max(x))
    xticks = np.arange(min(x), max(x)+1, 300)  # every 5 minutes
    xticklabels = [sec_to_hhmm(v) for v in xticks]
    plt.xticks(xticks, xticklabels, rotation=45)

    plt.xlabel("Time")
    plt.ylabel("Station")
    plt.title("Metro Train Control Chart (5:00 to 5:29)")
    plt.grid(True, axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()