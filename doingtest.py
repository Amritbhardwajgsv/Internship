import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

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
    # For the first station, only departure
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

xticks = sorted(set([v for v in x if v is not None]))
xticklabels = [sec_to_hhmm(v) for v in xticks]

plt.figure(figsize=(10, 6))
plt.step(x, y, where='post', linewidth=2)
plt.yticks(range(len(station_labels)), station_labels)
plt.xticks(xticks, xticklabels, rotation=45)
plt.xlabel("Time")
plt.ylabel("Station")
plt.title("Metro Train Timetable Control Chart")
plt.grid(True, axis='x', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.show()