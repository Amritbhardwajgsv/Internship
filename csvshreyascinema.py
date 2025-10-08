import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
from sklearn.ensemble import RandomForestRegressor

# --- Generate Data for Shreyas Cinema ---
times = pd.date_range("05:00", "23:59", freq="3min")  

# Simulate passengers (Poisson distribution)  
passengers = np.where(  
    times.hour.isin([6,8,9,10,17,18,19,20]),  # Rush hours (3 PM & 11 PM)  
    np.random.poisson(50, len(times)),  # High traffic  
    np.random.poisson(20, len(times))    # Low traffic  
)  

# Calculate dwell time (base dwell + passenger effect + noise)  
dwell = 30 + (passengers * 0.6721) + np.random.randint(0, 15, len(times))  

# Create DataFrame  
df = pd.DataFrame({  
    "Station": "CADBUARY",  
    "Time": times.strftime('%H:%M'),  
    "Minutes": times.hour * 60 + times.minute,  
    "Dwell_Time": dwell  
})  

# --- Train Random Forest Model ---
X = df[["Minutes"]]  
y = df["Dwell_Time"]  

model = RandomForestRegressor(n_estimators=100, random_state=42)  
model.fit(X, y)  

# Predict dwell time for all timestamps     
df["Predicted_Dwell"] = model.predict(X)  

# --- Save Predictions to CSV ---
csv_filename = "CADBUARY.csv"  
df.to_csv(csv_filename, index=False)  
print(f"Predictions saved to '{csv_filename}'")  

# --- Plot Actual vs Predicted Dwell Time ---
plt.figure(figsize=(12, 5))  
plt.scatter(df["Minutes"], df["Dwell_Time"], label="Actual Dwell Time", alpha=0.5)  
plt.plot(df["Minutes"], df["Predicted_Dwell"], color="red", label="Predicted Dwell Time")  
plt.xlabel("Time (minutes since midnight)")  
plt.ylabel("Dwell Time (seconds)")  
plt.title("Dwell Time at Shreyas Cinema (Actual vs Predicted)")  
plt.legend()  
plt.grid(True)  
plt.tight_layout()  
plt.show()  

# --- Interactive Prediction ---
while True:  
    user_input = input("Enter time (HH:MM) or 'exit': ").strip()  
    if user_input.lower() == 'exit':  
        break  
    try:  
        hour, minute = map(int, user_input.split(":"))  
        minutes_input = hour * 60 + minute  
        predicted_dwell = model.predict([[minutes_input]])[0]  
        print(f"Predicted dwell time at {user_input}: {predicted_dwell:.2f} seconds")  
    except:  
        print("Invalid format. Use HH:MM (e.g., 15:30).")
        
        