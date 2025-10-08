import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV (skip comment lines)
df = pd.read_csv("section_3.csv", comment='#')

# Prepend the first station with speed 0
stations = [df['From'][0]] + list(df['To'])
avg_speeds = [0] + list(df['AverageSpeed(km/h)'])

plt.figure(figsize=(10, 6))
plt.plot(stations, avg_speeds, marker='o')
plt.xlabel('Station')
plt.ylabel('Average Speed (km/h)')
plt.title('Average Speed Profile Along Stations')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()