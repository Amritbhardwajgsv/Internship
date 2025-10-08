import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('metro_operations_safe.csv')

plt.figure(figsize=(10,6))

# Scatter points only
plt.scatter(df['BaseDwell'], df['NormalHeadway7Trains'], color='blue', label='Base Dwell vs Normal Headway (points)')
plt.scatter(df['ActualDwell'], df['ActualHeadway'], color='red', label='Actual Dwell vs Actual Headway (points)')

# Sort data by BaseDwell to draw line smoothly
df_base_sorted = df.sort_values(by='BaseDwell')
plt.plot(df_base_sorted['BaseDwell'], df_base_sorted['NormalHeadway7Trains'], color='blue', linestyle='-', label='Base Dwell vs Normal Headway (line)')

# Sort data by ActualDwell to draw line smoothly
df_actual_sorted = df.sort_values(by='ActualDwell')
plt.plot(df_actual_sorted['ActualDwell'], df_actual_sorted['ActualHeadway'], color='red', linestyle='-', label='Actual Dwell vs Actual Headway (line)')

plt.xlabel('Dwell Time (seconds)')
plt.ylabel('Headway (seconds)')
plt.title('Dwell Time vs Headway')
plt.legend()
plt.grid(True)
plt.show()
plt.requested_backend()