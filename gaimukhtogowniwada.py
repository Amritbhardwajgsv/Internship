import math
import matplotlib.pyplot as plt

# Segment data
distance = 1502.229  # GAIMUKH to GOWNIWADA
civil_speed = 45

# Parameters
brake_distance = 150.0
vmax_kmph = 35.0 if distance > 850 else 30.0
vmax_kmph = min(vmax_kmph, civil_speed)
vmax = vmax_kmph * 1000.0 / 3600.0  # km/h to m/s

accelerating_distance = distance / 8.0
accel = vmax * vmax / (2.0 * accelerating_distance) if accelerating_distance > 0 else 1.0

# Time to reach vmax
t_accel = vmax / accel if accel > 0 else 0
# Deceleration phase
t_decel = math.sqrt(2 * brake_distance / accel) if accel > 0 else 0
# Cruise
d_cruise = distance - accelerating_distance - brake_distance
t_cruise = d_cruise / vmax if d_cruise > 0 and vmax > 0 else 0

# If not enough distance to reach vmax
if d_cruise < 0:
    d_half = (distance - brake_distance) if (distance - brake_distance) > 0 else (distance / 2.0)
    v_peak = math.sqrt(2 * accel * d_half) if accel > 0 else 0
    t_accel = v_peak / accel if accel > 0 else 0
    t_decel = math.sqrt(2 * brake_distance / accel) if accel > 0 else 0
    t_cruise = 0
    vmax = v_peak

# Generate speed profile
dt = 0.5  # time step (s)
s = 0
t = 0
S = []
V = []

# Acceleration phase
while s < accelerating_distance and vmax > 0:
    speed = accel * t
    if speed > vmax:
        speed = vmax
    S.append(s)
    V.append(speed * 3.6)  # m/s to km/h
    t += dt
    s += speed * dt

# Cruise phase
while s < distance - brake_distance and vmax > 0:
    speed = vmax
    S.append(s)
    V.append(speed * 3.6)
    t += dt
    s += speed * dt

# Deceleration phase
t_decel_start = t
while s < distance and vmax > 0:
    t_since_decel = t - t_decel_start
    speed = vmax - accel * t_since_decel
    if speed < 0:
        speed = 0
    S.append(s)
    V.append(speed * 3.6)
    t += dt
    s += speed * dt

# Ensure last point is exactly at the end with speed 0
if S[-1] < distance:
    S.append(distance)
    V.append(0)

plt.figure(figsize=(8, 5))
plt.plot(S, V, label="GAIMUKH → GOWNIWADA")
plt.xlabel("Distance (m)")
plt.ylabel("Speed (km/h)")
plt.title("Speed Profile: GAIMUKH to GOWNIWADA")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()