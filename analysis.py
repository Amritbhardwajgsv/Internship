import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ======================
# 1. Load Your CSV Data
# ======================
# Replace with your actual data loading
data = {
    "Passengers": [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80],
    "Dwell_Time": [20, 25, 30, 35, 40, 50, 55, 60, 70, 75, 85, 90, 100, 110, 120]
}
df = pd.DataFrame(data)
X = df["Passengers"].values
y_true = df["Dwell_Time"].values

# ======================
# 2. Define RL Parameters
# ======================
# Discretize m and c (for simplicity)
m_range = np.linspace(0.0, 2.0, 20)  # Possible m values
c_range = np.linspace(0.0, 30.0, 20)  # Possible c values

# Q-Table: Key = (m_idx, c_idx), Value = Q-values for actions
Q = {}
for m_idx in range(len(m_range)):
    for c_idx in range(len(c_range)):
        Q[(m_idx, c_idx)] = np.zeros(4)  # 4 actions: [↑m, ↓m, ↑c, ↓c]

# Hyperparameters
alpha = 0.1  # Learning rate
gamma = 0.9  # Discount factor
epsilon = 0.3  # Exploration rate
episodes = 10  # Training iterations

# ======================
# 3. Q-Learning Algorithm
# ======================
def get_reward(m, c):
    y_pred = m * X + c
    mse = np.mean((y_true - y_pred) ** 2)
    return -mse  # Higher reward = lower error

for episode in range(episodes):
    # Random initial m and c
    m_idx = np.random.randint(0, len(m_range))
    c_idx = np.random.randint(0, len(c_range))
    m = m_range[m_idx]
    c = c_range[c_idx]
    
    while True:
        # Choose action (ε-greedy)
        if np.random.random() < epsilon:
            action = np.random.randint(0, 4)  # Explore
        else:
            action = np.argmax(Q[(m_idx, c_idx)])  # Exploit
        
        # Apply action
        if action == 0 and m_idx < len(m_range) - 1:  # ↑m
            new_m_idx = m_idx + 1
            new_c_idx = c_idx
        elif action == 1 and m_idx > 0:  # ↓m
            new_m_idx = m_idx - 1
            new_c_idx = c_idx
        elif action == 2 and c_idx < len(c_range) - 1:  # ↑c
            new_m_idx = m_idx
            new_c_idx = c_idx + 1
        elif action == 3 and c_idx > 0:  # ↓c
            new_m_idx = m_idx
            new_c_idx = c_idx - 1
        else:
            new_m_idx, new_c_idx = m_idx, c_idx  # No change if at boundary
        
        new_m = m_range[new_m_idx]
        new_c = c_range[new_c_idx]
        
        # Calculate reward
        reward = get_reward(new_m, new_c)
        
        # Update Q-Table
        Q[(m_idx, c_idx)][action] += alpha * (
            reward + gamma * np.max(Q[(new_m_idx, new_c_idx)]) - Q[(m_idx, c_idx)][action]
        )
        
        # Update state
        m_idx, c_idx = new_m_idx, new_c_idx
        m, c = new_m, new_c
        
        # Terminate if no improvement
        if reward >= -5.0:  # Stop if MSE < 5
            break

# ======================
# 4. Extract Best m and c
# ======================
best_q = -np.inf
best_m, best_c = 0.0, 0.0
for (m_idx, c_idx), q_values in Q.items():
    if np.max(q_values) > best_q:
        best_q = np.max(q_values)
        best_m = m_range[m_idx]
        best_c = c_range[c_idx]

print(f"Optimal parameters (RL): m = {best_m:.2f}, c = {best_c:.2f}")

# ======================
# 5. Plot Results
# ======================
y_pred_rl = best_m * X + best_c
plt.scatter(X, y_true, label="True Data")
plt.plot(X, y_pred_rl, color="red", label=f"RL Fit: y = {best_m:.2f}x + {best_c:.2f}")
plt.xlabel("Passengers")
plt.ylabel("Dwell Time (sec)")
plt.legend()
plt.show()