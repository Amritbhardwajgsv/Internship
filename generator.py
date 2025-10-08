import pandas as pd  
import numpy as np  
import matplotlib.pyplot as plt  
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR

# Generate timestamps (1-min intervals)  
times = pd.date_range("05:00", "23:59", freq="1min")  

# Simulate passengers (Poisson distribution)  
passengers = np.where(  
    
    times.hour.isin([7, 9, 17, 18]),  # Rush hours  
    np.random.poisson(50, len(times)),  
    np.random.poisson(20, len(times))  
)  

# Calculate dwell time (with noise)  
dwell = 30 + (passengers * 0.5) + np.random.randint(0, 15, len(times))  

# Extrac
# t only the time part as string (HH:MM)
time_only = times.strftime('%H:%M')

# Create DataFrame for KASARVADVALI only  
df = pd.DataFrame({  
    "Time": time_only,  
    "Dwell_Time": dwell  
})  

# Convert time to minutes since midnight for regression
df["Minutes"] = times.hour * 60 + times.minute

# Plot Dwell Time vs Time (scatter)
plt.figure(figsize=(12, 5))
plt.scatter(df["Minutes"], df["Dwell_Time"], label="Dwell Time (points)")
plt.xlabel("Time (minutes since midnight)")
plt.ylabel("Dwell Time (seconds)")
plt.title("Dwell Time at KASARVADVALI Throughout the Day")

# Linear Regression
X = df[["Minutes"]]
y = df["Dwell_Time"]
model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
plt.plot(df["Minutes"], y_pred, color="red", label="Linear Regression")
# Linear Regression Equation
print("Linear Regression: y = {:.2f} * Minutes + {:.2f}".format(model.coef_[0], model.intercept_))

# Polynomial Regression (degree 5)
poly = PolynomialFeatures(degree=5)
X_poly = poly.fit_transform(X)
poly_model = LinearRegression()
poly_model.fit(X_poly, y)
y_poly_pred = poly_model.predict(X_poly)
plt.plot(df["Minutes"], y_poly_pred, color="green", label="Polynomial Regression (deg=5)")
print("Polynomial Regression Coefficients (degree=5):")
print(poly_model.coef_)
print("Intercept:", poly_model.intercept_)
# Polynomial Regression Equation
coefs = poly_model.coef_
equation = " + ".join([f"{coefs[i]:.2e}*Minutes^{i}" for i in range(len(coefs))])
print("Polynomial Regression Equation: y =", equation)

# Random Forest Regression
rf = RandomForestRegressor(n_estimators=100, random_state=42)
rf.fit(X, y)
y_rf_pred = rf.predict(X)
plt.plot(df["Minutes"], y_rf_pred, color="orange", label="Random Forest")

# Support Vector Regression
svr = SVR(kernel='rbf')
svr.fit(X, y)
y_svr_pred = svr.predict(X)
plt.plot(df["Minutes"], y_svr_pred, color="purple", label="SVR (RBF kernel)")

# Example predictions
minutes_val = 600  # Example: 10:00 AM (600 minutes since midnight)
print("Random Forest Prediction at 10:00:", rf.predict([[minutes_val]])[0])
print("SVR Prediction at 10:00:", svr.predict([[minutes_val]])[0])

plt.legend()
plt.tight_layout()
plt.show()

# --- Interactive Input for Prediction using Random Forest ---
while True:
    user_input = input("Enter time in HH:MM format (or 'exit' to quit): ").strip()
    if user_input.lower() == 'exit':
        break
    try:
        # Convert HH:MM to minutes since midnight
        hour, minute = map(int, user_input.split(":"))
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError
        minutes_input = hour * 60 + minute

        # Predict dwell time
        predicted_dwell = rf.predict([[minutes_input]])[0]
        print(f"Predicted dwell time at {user_input} is: {predicted_dwell:.2f} seconds")
    except:
        print("Invalid input. Please enter time in HH:MM format.")
