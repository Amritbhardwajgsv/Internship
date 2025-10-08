import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Column headers
columns = [
    'train_id', 'arrival_train_time', 'departuretime', 'train_station', 'train_line',
    'train_type', 'distancetonext', 'durationofmovementinsec', 'dwell_timein_sec',
    'civil speed limit', 'topspeedlimit'
]

# Station data: [station, line, type, distance, run_time, dwell_time, civil_speed]
stations = [
    ['BHAKTI PARK METRO', 'LINE4', 'METRO_6CAR', 1014.37, 180, 30, 45],
    ['WADALA TT', 'LINE4', 'METRO_6CAR', 916.806, 180, 30, 45],
    ['ANIKNAGARBUSDEPOT', 'LINE4', 'METRO_6CAR', 1651.480, 180, 30, 45],
    ['SIDDHARTHCOLONY', 'LINE4', 'METRO_6CAR', 2421.413, 180, 30, 45],
    ['GARODIA NAGAR', 'LINE4', 'METRO_6CAR', 1662.149, 180, 30, 45],
    ['PANT NAGAR', 'LINE4', 'METRO_6CAR', 1148.172, 180, 30, 45],
    ['LAXMINAGAR', 'LINE4', 'METRO_6CAR', 952.884, 180, 30, 45],
    ['SHREYAS CINEMA', 'LINE4', 'METRO_6CAR', 745.313, 180, 30, 45],
    ['GODREJ COMPANY', 'LINE4', 'METRO_6CAR', 709.649, 180, 30, 45],
    ['VIKHROLI METRO', 'LINE4', 'METRO_6CAR', 1017.761, 180, 30, 45],
    ['SURYA NAGAR', 'LINE4', 'METRO_6CAR', 973.585, 180, 30, 45],
    ['GANDHINGAR ', 'LINE4', 'METRO_6CAR', 747, 747, 30, 45],
    ['NAVAL HOUSING', 'LINE4', 'METRO_6CAR', 745.156, 180, 30, 45],
    ['BHANDUP MAHAPALIKA', 'LINE4', 'METRO_6CAR', 1039.865, 180, 30, 45],
    ['BHANDUP METRO', 'LINE4', 'METRO_6CAR', 797.654, 180, 30, 45],
    ['SHANGRILLA', 'LINE4', 'METRO_6CAR', 1454.303, 180, 30, 45],
    ['SONAPUR', 'LINE4', 'METRO_6CAR', 1124.344, 180, 30, 45],
    ['MULUND FIRE STATION', 'LINE4', 'METRO_6CAR', 1339.919, 180, 30, 45],
    ['MULUND NAKA', 'LINE4', 'METRO_6CAR', 1212.231, 180, 30, 45],
    ['TEEN HAATH NAKA', 'LINE4', 'METRO_6CAR', 784.465, 180, 30, 45],
    ['RTO THANE', 'LINE4', 'METRO_6CAR', 964.956, 180, 30, 45],
    ['MAHAPALIIKAMARG', 'LINE4', 'METRO_6CAR', 795.993, 180, 30, 45],
    ['CADBUARY JUNCTION ', 'LINE4', 'METRO_6CAR', 824.707, 180, 30, 45],
    ['MAJIWADA', 'LINE4', 'METRO_6CAR', 1445.707, 180, 30, 45],
    ['KAPURBAWDI', 'LINE4', 'METRO_6CAR', 815.824, 180, 30, 45],
    ['MANPADA', 'LINE4', 'METRO_6CAR', 758.992, 180, 30, 45],
    ['TIKUJI NI WADI', 'LINE4', 'METRO_6CAR', 1226.694, 180, 30, 45],
    ['DONGARI PADA', 'LINE4', 'METRO_6CAR', 1198.778, 180, 30, 45],
    ['VIJAYGARDEN ', 'LINE4', 'METRO_6CAR', 1024.036, 180, 30, 45],
    ['KASARVADVALI ', 'LINE4', 'METRO_6CAR', 1385.394, 180, 30, 45],
    ['GOWNIWADA ', 'LINE4', 'METRO_6CAR', 1502.229, 180, 30, 45],
    ['GAIMUKH', 'LINE4', 'METRO_6CAR', None, 180, 30, 45],  # Distance is None here
]

start_stations = [
    'BHAKTI PARK METRO',
    'GANDHINGAR ',
    'CADBUARY JUNCTION ',
    'GAIMUKH'
]
trains_per_start = 2
headway = 10 * 60  # 10 minutes between trains from the same start

all_data = []
train_counter = 1

for start_station in start_stations:
    start_idx = next(i for i, s in enumerate(stations) if s[0].strip() == start_station.strip())
    for n in range(trains_per_start):
        train_id = f"t{train_counter:03d}"
        train_counter += 1
        # Forward journey
        start_time = datetime.strptime('04:57', '%H:%M') + timedelta(seconds=n * headway)
        for idx, s in enumerate(stations[start_idx:]):
            if idx == 0:
                arrival = start_time
            else:
                arrival = departure
            departure = arrival + timedelta(seconds=s[4] + s[5])
            if s[3] is not None:
                topspeed = (float(s[3]) / float(s[4])) * 3.6
            else:
                topspeed = None
            all_data.append([
                train_id,
                arrival.strftime('%H:%M'),
                (arrival + timedelta(seconds=s[4])).strftime('%H:%M:%S'),
                s[0], s[1], s[2],
                s[3], s[4], s[5], s[6],
                round(topspeed, 2) if topspeed is not None else ''
            ])
        # Return journey
        turnaround_time = 15 * 60  # 15 minutes at end before return
        last_arrival = departure
        return_id = f"{train_id}_R"
        for idx, s in enumerate(reversed(stations[:start_idx+1])):
            if idx == 0:
                arrival = last_arrival + timedelta(seconds=turnaround_time)
            else:
                arrival = departure
            departure = arrival + timedelta(seconds=s[4] + s[5])
            if s[3] is not None:
                topspeed = (float(s[3]) / float(s[4])) * 3.6
            else:
                topspeed = None
            all_data.append([
                return_id,
                arrival.strftime('%H:%M'),
                (arrival + timedelta(seconds=s[4])).strftime('%H:%M:%S'),
                s[0], s[1], s[2],
                s[3], s[4], s[5], s[6],
                round(topspeed, 2) if topspeed is not None else ''
            ])

df = pd.DataFrame(all_data, columns=columns)
df.to_csv('train_schedule_8_custom.csv', index=False)
# After your DataFrame is created
import matplotlib.pyplot as plt

# Plot speed profile for a single train (e.g., the first forward train)
first_forward_train = [tid for tid in df['train_id'].unique() if not tid.endswith('_R')][0]
train_df = df[df['train_id'] == first_forward_train]
plot_df = train_df[train_df['topspeedlimit'] != '']

plt.figure(figsize=(14, 5))
plt.plot(plot_df['train_station'], plot_df['topspeedlimit'].astype(float), marker='o')
plt.xticks(rotation=90)
plt.xlabel('Station')
plt.ylabel('Top Speed (km/h)')
plt.title(f'Speed Profile for {first_forward_train}')
plt.tight_layout()
plt.show()

# Plot speed profile for a return train (optional)
first_return_train = [tid for tid in df['train_id'].unique() if tid.endswith('_R')][0]
return_df = df[df['train_id'] == first_return_train]
plot_return_df = return_df[return_df['topspeedlimit'] != '']

plt.figure(figsize=(14, 5))
plt.plot(plot_return_df['train_station'], plot_return_df['topspeedlimit'].astype(float), marker='o', color='orange')
plt.xticks(rotation=90)
plt.xlabel('Station')
plt.ylabel('Top Speed (km/h)')
plt.title(f'Speed Profile for {first_return_train} (Return)')
plt.tight_layout()
plt.show()