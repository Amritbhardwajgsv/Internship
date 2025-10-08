import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
    ['GANDHINGAR', 'LINE4', 'METRO_6CAR', 747.000, 180, 30, 45],
    ['NAVAL HOUSING', 'LINE4', 'METRO_6CAR', 745.156, 180, 30, 45],
    ['BHANDUP MAHAPALIKA', 'LINE4', 'METRO_6CAR', 1039.865, 180, 30, 45],
    ['BHANDUP METRO', 'LINE4', 'METRO_6CAR', 797.654, 180, 30, 45],
    ['SHANGRILLA', 'LINE4', 'METRO_6CAR', 1454.303, 180, 30, 45],
    ['SONAPUR', 'LINE4', 'METRO_6CAR', 1124.344, 180, 30, 45],
    ['MULUND FIRE STATION', 'LINE4', 'METRO_6CAR', 1339.919, 180, 30, 45],
    ['MULUND NAKA', 'LINE4', 'METRO_6CAR', 1212.231, 180, 30, 45],
    ['TEEN HAATH NAKA', 'LINE4', 'METRO_6CAR', 784.465, 180, 30, 45],
    ['RTO THANE', 'LINE4', 'METRO_6CAR', 964.956, 180, 30, 45],
    ['MAHAPALIKAMARG', 'LINE4', 'METRO_6CAR', 795.993, 180, 30, 45],
    ['CADBUARY JUNCTION', 'LINE4', 'METRO_6CAR', 824.707, 180, 30, 45],
    ['MAJIWADA', 'LINE4', 'METRO_6CAR', 1445.707, 180, 30, 45],
    ['KAPURBAWDI', 'LINE4', 'METRO_6CAR', 815.824, 180, 30, 45],
    ['MANPADA', 'LINE4', 'METRO_6CAR', 758.992, 180, 30, 45],
    ['TIKUJI NI WADI', 'LINE4', 'METRO_6CAR', 1226.694, 180, 30, 45],
    ['DONGARI PADA', 'LINE4', 'METRO_6CAR', 1198.778, 180, 30, 45],
    ['VIJAYGARDEN', 'LINE4', 'METRO_6CAR', 1024.036, 180, 30, 45],
    ['KASARVADVALI', 'LINE4', 'METRO_6CAR', 1385.394, 180, 30, 45],
    ['GOWNIWADA', 'LINE4', 'METRO_6CAR', 1502.229, 180, 30, 45],
    ['GAIMUKH', 'LINE4', 'METRO_6CAR', None, 180, 30, 45],
]

# Configuration
start_stations = ['BHAKTI PARK METRO', 'GANDHINGAR', 'CADBUARY JUNCTION', 'GAIMUKH']
trains_per_station = 2
headway = 10 * 60  # 10 minutes between departures from same station
turnaround_time = 15 * 60  # 15 minutes at terminal

def calculate_speed(distance, run_time, civil_speed):
    if distance is None or run_time == 0:
        return None
    speed = (float(distance) / float(run_time)) * 3.6  # m/s to km/h
    return min(speed, civil_speed)

def generate_journey(start_station, start_time, direction):
    """Generate timetable for one journey in specified direction"""
    journey_data = []
    start_idx = next(i for i, s in enumerate(stations) if s[0] == start_station)
    
    if direction == 'forward':
        sequence = stations[start_idx:]
        train_id = f"T{len(journey_data)//len(stations)+1:02d}F"
    else:
        sequence = list(reversed(stations[:start_idx+1]))
        train_id = f"T{len(journey_data)//len(stations)+1:02d}R"
    
    arrival = start_time
    for s in sequence:
        departure = arrival + timedelta(seconds=s[4] + s[5])
        topspeed = calculate_speed(s[3], s[4], s[6])
        
        journey_data.append({
            'train_id': train_id,
            'arrival_time': arrival.strftime('%H:%M'),
            'departure_time': departure.strftime('%H:%M'),
            'station': s[0],
            'direction': direction,
            'top_speed': round(topspeed, 2) if topspeed else None
        })
        arrival = departure
    
    # Add turnaround time at terminal
    terminal = sequence[-1][0]
    journey_data.append({
        'train_id': train_id,
        'arrival_time': arrival.strftime('%H:%M'),
        'departure_time': (arrival + timedelta(seconds=turnaround_time)).strftime('%H:%M'),
        'station': terminal,
        'direction': 'turnaround',
        'top_speed': None
    })
    
    return journey_data

# Generate timetable
all_journeys = []
base_time = datetime.strptime('05:00', '%H:%M')  # Start at 5:00

for station in start_stations:
    start_idx = next(i for i, s in enumerate(stations) if s[0] == station)
    for n in range(trains_per_station):
        train_num = f"{station[:3].upper()}{n+1:02d}"
        # Initial direction and sequence
        if station in ['GAIMUKH', 'CADBUARY JUNCTION']:
            forward_seq = list(reversed(stations[:start_idx+1]))
            terminal = forward_seq[-1][0]
        else:
            forward_seq = stations[start_idx:]
            terminal = forward_seq[-1][0]
        # Start at 5:00 plus headway for each train
        current_time = base_time + timedelta(seconds=n * headway)
        current_station = station
        direction = 'forward'
        seq = forward_seq
        while current_time < datetime.strptime('23:59', '%H:%M'):
            # Journey in current direction
            for s in seq:
                departure = current_time + timedelta(seconds=s[4] + s[5])
                topspeed = calculate_speed(s[3], s[4], s[6])
                all_journeys.append({
                    'train_id': train_num,
                    'arrival_time': current_time.strftime('%H:%M'),
                    'departure_time': departure.strftime('%H:%M'),
                    'station': s[0],
                    'direction': direction,
                    'top_speed': round(topspeed, 2) if topspeed else None
                })
                current_time = departure
            # Turnaround at terminal
            all_journeys.append({
                'train_id': train_num,
                'arrival_time': current_time.strftime('%H:%M'),
                'departure_time': (current_time + timedelta(seconds=turnaround_time)).strftime('%H:%M'),
                'station': seq[-1][0],
                'direction': 'turnaround',
                'top_speed': None
            })
            current_time = current_time + timedelta(seconds=turnaround_time)
            # Reverse direction and sequence for next leg
            if direction == 'forward':
                seq = list(reversed(seq))
                direction = 'return'
            else:
                seq = list(reversed(seq))
                direction = 'forward'

# Create DataFrame
df = pd.DataFrame(all_journeys)
df.to_csv('day_2.csv', index=False)

# Visualization
plt.figure(figsize=(15, 10))

# Station positions
station_order = [s[0] for s in stations]
station_pos = {s: i for i, s in enumerate(station_order)}

# Improved color mapping
colors = {
    'forward': '#0072B2',     # Blue
    'return': '#D55E00',      # Orange
    'turnaround': '#009E73'   # Green
}
markers = {
    'forward': 'o',
    'return': 's',
    'turnaround': 'D'
}

for train_id in df['train_id'].unique():
    train_data = df[df['train_id'] == train_id]
    times = [datetime.strptime(t, '%H:%M') for t in train_data['departure_time']]
    stations_visited = train_data['station']
    y_pos = [station_pos[s] for s in stations_visited]
    directions = train_data['direction']
    # Plot each segment by direction for better legend
    for direction in ['forward', 'return', 'turnaround']:
        mask = directions == direction
        if mask.any():
            plt.plot(
                [t for t, m in zip(times, mask) if m],
                [y for y, m in zip(y_pos, mask) if m],
                marker=markers[direction],
                color=colors[direction],
                linestyle='-' if direction != 'turnaround' else 'None',
                markersize=6 if direction != 'turnaround' else 10,
                label=direction.capitalize() if train_id == df['train_id'].unique()[0] else "",
                linewidth=2 if direction != 'turnaround' else 0
            )
            # Add arrival time as label (optional, comment out if too cluttered)
            for x, y, arr_time, m in zip(times, y_pos, train_data['arrival_time'], mask):
                if m and direction != 'turnaround':
                    plt.text(x, y, arr_time, fontsize=7, ha='right', va='bottom', color=colors[direction])

plt.yticks(range(len(station_order)), station_order)
plt.xlabel('Time')
plt.ylabel('Station')
plt.title('Train Schedule\nBlue=Forward, Orange=Return, Green Diamond=Turnaround')
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='upper left', bbox_to_anchor=(1.01, 1), title="Direction")
plt.xlim(datetime.strptime('00:00', '%H:%M'), datetime.strptime('23:59', '%H:%M'))
xtick_times = [datetime.strptime(f"{h:02d}:00", "%H:%M") for h in range(24)]
xtick_labels = [f"{h:02d}:00" for h in range(24)]
# Add a final tick at 24:00 (which is 23:59 + 1 minute)
xtick_times.append(datetime.strptime('23:59', '%H:%M') + timedelta(minutes=1))
xtick_labels.append('24:00')
plt.xticks(xtick_times, xtick_labels)
plt.tight_layout()
plt.show()