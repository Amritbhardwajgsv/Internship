import math
import matplotlib.pyplot as plt

# Define station data (segment length, not cumulative)
stations = [
    ("GAIMUKH", 0.0, 45),
    ("GOWNIWADA", 1502.229, 45),
    ("KASARVADVALI", 1385.394, 45),
    ("VIJAYGARDEN", 1024.036, 45),
    ("DONGARI PADA", 1198.778, 45),
    ("TIKUJI NI WADI", 1226.694, 45),
    ("MANPADA", 758.992, 45),
    ("KAPURBAWDI", 815.824, 45),
    ("MAJIWADA", 1453.707, 45),
    ("CADBUARY JUNCTION", 824.707, 45)
]

def calculate_run_time(distance, civil_speed):
    brake_distance = 150.0
    vmax_kmph = 35.0 if distance > 850 else 30.0
    vmax_kmph = min(vmax_kmph, civil_speed)
    vmax = vmax_kmph * 1000.0 / 3600.0  # km/h to m/s

    accelerating_distance = distance / 8.0
    accel = vmax * vmax / (2.0 * accelerating_distance) if accelerating_distance > 0 else 1.0
    t_accel = vmax / accel if accel > 0 else 0

    t_decel = math.sqrt(2 * brake_distance / accel) if accel > 0 else 0

    d_cruise = distance - accelerating_distance - brake_distance
    t_cruise = d_cruise / vmax if d_cruise > 0 and vmax > 0 else 0

    if d_cruise < 0:
        d_half = (distance - brake_distance) if (distance - brake_distance) > 0 else (distance / 2.0)
        v_peak = math.sqrt(2 * accel * d_half) if accel > 0 else 0
        t_accel = v_peak / accel if accel > 0 else 0
        t_decel = math.sqrt(2 * brake_distance / accel) if accel > 0 else 0
        t_cruise = 0

    return t_accel + t_cruise + t_decel

# Prepare data for CSV and plotting
from_stations = []
to_stations = []
distances = []
runtimes = []
avg_speeds = []

total_runtime = 0.0
total_distance = 0.0

for i in range(len(stations) - 1):
    from_station = stations[i][0]
    to_station = stations[i+1][0]
    distance = stations[i+1][1]  # segment length from previous
    civil_speed = min(stations[i][2], stations[i+1][2])
    runtime = calculate_run_time(distance, civil_speed)
    avg_speed = (distance / runtime) * 3.6 if runtime > 0 else 0  # km/h

    from_stations.append(from_station)
    to_stations.append(to_station)
    distances.append(distance)
    runtimes.append(runtime)
    avg_speeds.append(avg_speed)

    total_runtime += runtime
    total_distance += distance

# Print CSV-like output (optional)
print("From,To,Distance(m),RunTime(s),AverageSpeed(km/h)")
for i in range(len(from_stations)):
    print(f"{from_stations[i]},{to_stations[i]},{distances[i]:.3f},{runtimes[i]:.2f},{avg_speeds[i]:.2f}")
print(f"#Total running distance:,{total_distance:.3f}")
print(f"#Total run time (s):,{total_runtime:.2f}")
print(f"#Average speed (km/h):,{(total_distance / total_runtime) * 3.6:.2f}")

# Plot: Stations (X) vs Average Speed (Y)
plt.figure(figsize=(10, 6))
plt.plot(to_stations, avg_speeds, marker='o')
plt.xlabel('Station')
plt.ylabel('Average Speed (km/h)')
plt.title('Average Speed Profile Along Stations')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()

# Before plotting, add GAIMUKH with speed 0 at the start
stations_for_plot = [stations[0][0]] + to_stations
speeds_for_plot = [0] + avg_speeds

plt.figure(figsize=(10, 6))
plt.plot(stations_for_plot, speeds_for_plot, marker='o')
plt.xlabel('Station')
plt.ylabel('Average Speed (km/h)')
plt.title('Average Speed Profile Along Stations')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()

# Before plotting, add GAIMUKH with run time 0 at the start
stations_for_runtime_plot = [stations[0][0]] + to_stations
runtimes_for_plot = [0] + runtimes

plt.figure(figsize=(10, 6))
plt.plot(stations_for_runtime_plot, runtimes_for_plot, marker='o')
plt.xlabel('Station')
plt.ylabel('Run Time (s)')
plt.title('Run Time Between Stations')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()