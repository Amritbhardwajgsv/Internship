import pandas as pd
from datetime import datetime, timedelta
import numpy as np
#import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# Column headers
columns = [
    'train_id', 'arrival_train_time', 'departuretime', 'train_station', 'train_line',
    'train_type', 'distancetonext', 'durationofmovementinsec', 'dwell_timein_sec',
    'civil speed limit', 'topspeedlimit'
]

# Station data: [station, line, type, distance, run_time, dwell_time, civil_speed]
dwell_time = 30  # seconds
# Dwell time at each station
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

# Configuration
headway = 10 * 60  # 0 minutes headway

# we will be calculating the number of train on the line 
num_train=17820/(headway+dwell_time) # 17820 is the total time in seconds for 24 hours
num_trains = int(num_train)  # Number of trains in 24 hours

all_data = []

for t in range(num_trains):
    train_id = f"t{t+1:03d}"
    start_time = datetime.strptime('04:57', '%H:%M') + timedelta(seconds=t * headway)
    for idx, s in enumerate(stations):
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

# Create DataFrame ONCE, after all data is collected
df = pd.DataFrame(all_data, columns=columns)
df.to_csv('train_schedule_326.csv', index=False)

# After your DataFrame is created
train_id = df['train_id'].unique()[0]
train_df = df[df['train_id'] == train_id]

# Filter out rows where topspeedlimit is empty
plot_df = train_df[train_df['topspeedlimit'] != '']


# Plot speed between stations (segment-wise)
segment_data = []
for i in range(len(stations) - 1):
    from_station = stations[i][0]
    to_station = stations[i + 1][0]
    distance = stations[i][3]  # distance to next station is in the current row
    run_time = stations[i][4]
    if distance is not None and run_time != 0:
        topspeed = (float(distance) / float(run_time)) * 3.6
    else:
        topspeed = None
    segment_data.append([from_station, to_station, distance, run_time, topspeed])

segment_df = pd.DataFrame(segment_data, columns=['from_station', 'to_station', 'distance', 'run_time', 'topspeed'])

plt.figure(figsize=(14, 5))
plt.plot(segment_df['from_station'] + ' → ' + segment_df['to_station'], segment_df['topspeed'], marker='o')
plt.xticks(rotation=90)
plt.xlabel('Segment')
plt.ylabel('Top Speed (km/h)')
plt.title('Speed Profile Between Stations')
plt.tight_layout()
plt.show()

turnaround_time = 15*60 # seconds at GAIMUKH before return (adjust as needed)

for t in range(num_trains):
    train_id = f"t{t+1:03d}_R"  # _R for return
    # Find the arrival time at GAIMUKH for this train
    forward_rows = [row for row in all_data if row[0] == f"t{t+1:03d}" and row[3] == 'GAIMUKH']
    if not forward_rows:
        continue  # skip if no forward trip to GAIMUKH
    last_arrival_str = forward_rows[0][1]
    last_arrival = datetime.strptime(last_arrival_str, '%H:%M')
    # Start return after turnaround
    start_time = last_arrival + timedelta(seconds=turnaround_time)
    for idx, s in enumerate(reversed(stations)):
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

# Create DataFrame ONCE, after all data is collected (forward + return)
df = pd.DataFrame(all_data, columns=columns)
df.to_csv('train_schedule_326_with_return.csv', index=False)


