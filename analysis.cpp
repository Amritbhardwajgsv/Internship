#include <iostream>
#include <vector>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <limits>
#include <algorithm>

using namespace std;

// Data (replace with your own if needed)
vector<double> passengers = {10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80};
vector<double> dwell_time = {20, 25, 30, 35, 40, 50, 55, 60, 70, 75, 85, 90, 100, 110, 120};

double get_reward(double m, double c, const vector<double>& X, const vector<double>& y_true) {
    double mse = 0.0;
    for (size_t i = 0; i < X.size(); ++i) {
        double y_pred = m * X[i] + c;
        mse += pow(y_true[i] - y_pred, 2);
    }
    mse /= X.size();
    return -mse; // Higher reward = lower error
}

int main() {
    srand((unsigned)time(0));

    // Discretize m and c
    int m_steps = 20, c_steps = 20;
    vector<double> m_range(m_steps), c_range(c_steps);
    for (int i = 0; i < m_steps; ++i) m_range[i] = 0.0 + i * (2.0 / (m_steps - 1));
    for (int i = 0; i < c_steps; ++i) c_range[i] = 0.0 + i * (30.0 / (c_steps - 1));

    // Q-table: [m_idx][c_idx][action]
    vector<vector<vector<double>>> Q(m_steps, vector<vector<double>>(c_steps, vector<double>(4, 0.0)));

    // Hyperparameters
    double alpha = 0.1, gamma = 0.9, epsilon = 0.3;
    int episodes = 10;

    // Q-learning
    for (int episode = 0; episode < episodes; ++episode) {
        int m_idx = rand() % m_steps;
        int c_idx = rand() % c_steps;
        double m = m_range[m_idx];
        double c = c_range[c_idx];

        while (true) {
            int action;
            if ((double)rand() / RAND_MAX < epsilon) {
                action = rand() % 4; // Explore
            } else {
                action = max_element(Q[m_idx][c_idx].begin(), Q[m_idx][c_idx].end()) - Q[m_idx][c_idx].begin();
            }

            int new_m_idx = m_idx, new_c_idx = c_idx;
            if (action == 0 && m_idx < m_steps - 1) new_m_idx = m_idx + 1; // ↑m
            else if (action == 1 && m_idx > 0) new_m_idx = m_idx - 1;     // ↓m
            else if (action == 2 && c_idx < c_steps - 1) new_c_idx = c_idx + 1; // ↑c
            else if (action == 3 && c_idx > 0) new_c_idx = c_idx - 1;     // ↓c

            double new_m = m_range[new_m_idx];
            double new_c = c_range[new_c_idx];

            double reward = get_reward(new_m, new_c, passengers, dwell_time);

            Q[m_idx][c_idx][action] += alpha * (reward + gamma * *max_element(Q[new_m_idx][new_c_idx].begin(), Q[new_m_idx][new_c_idx].end()) - Q[m_idx][c_idx][action]);

            m_idx = new_m_idx;
            c_idx = new_c_idx;
            m = new_m;
            c = new_c;

            if (reward >= -5.0) break; // Stop if MSE < 5
        }
    }

    // Extract best m and c
    double best_q = -numeric_limits<double>::infinity();
    double best_m = 0.0, best_c = 0.0;
    for (int m_idx = 0; m_idx < m_steps; ++m_idx) {
        for (int c_idx = 0; c_idx < c_steps; ++c_idx) {
            double max_q = *max_element(Q[m_idx][c_idx].begin(), Q[m_idx][c_idx].end());
            if (max_q > best_q) {
                best_q = max_q;
                best_m = m_range[m_idx];
                best_c = c_range[c_idx];
            }
        }
    }

    cout << "Optimal parameters (RL): m = " << best_m << ", c = " << best_c << endl;
    cout << "Predicted dwell times: ";
    for (size_t i = 0; i < passengers.size(); ++i) {
        cout << (best_m * passengers[i] + best_c) << " ";
    }
    cout << endl;

    return 0;
}