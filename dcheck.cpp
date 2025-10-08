#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <fstream>
#include <random>
#include <algorithm>

using namespace std;

struct Station {
    string name;
    double distance;
    int base_dwell;   // base (theoretical) dwell time in seconds
    int civil_speed;  // max allowed speed in kmph
};

// Calculate safe headway (minimum separation time) based on braking distance and reaction time
double calculateSafeHeadway(double speed_kmph, double distance) {
    const double brake_distance = 150.0; // meters
    const double reaction_time = 2.0; // seconds
    double speed_ms = speed_kmph * 1000.0 / 3600.0;

    // Safe headway = (braking distance / speed) + reaction time
    return (brake_distance / speed_ms) + reaction_time;
}

// Calculate runtime to cover given distance with acceleration, cruising and deceleration
double calculateRuntime(double distance, int civil_speed, bool boost = false) {
    double vmax_kmph = (distance > 900) ? 35.0 : 30.0;

    if (boost) {
        vmax_kmph = (vmax_kmph == 30.0) ? 35.0 : 38.0;
    }
    vmax_kmph = min(vmax_kmph, (double)civil_speed);

    double vmax = vmax_kmph * 1000.0 / 3600.0; // convert to m/s
    double accel_dist = distance / 8.0;
    double accel = (vmax * vmax) / (2.0 * accel_dist);
    double t_accel = vmax / accel;
    double t_decel = sqrt(2 * 200.0 / accel);
    double cruise_dist = distance - accel_dist - 150.0;
    double t_cruise = (cruise_dist > 0) ? cruise_dist / vmax : 0;

    return t_accel + t_cruise + t_decel;
}

int main() {
    vector<Station> stations = {
        {"GAIMUKH", 0.0, 45, 35},
        {"GOWNIWADA", 1502.229, 45, 45},
        {"KASARVADVALI", 2887.623, 30, 45},
        {"VIJAYGARDEN", 3911.659, 30, 45},
        {"DONGARI PADA", 5110.437, 30, 45},
        {"TIKUJI NI WADI", 6337.131, 30, 45},
        {"MANPADA", 7096.123, 30, 45},
        {"KAPURBAWDI", 7911.947, 45, 45},
        {"MAJIWADA", 9365.654, 30, 45},
        {"CADBUARY JUNCTION", 10190.361, 60, 45}
    };

    ofstream out("metro_operations_safe.csv");
    out << "From,To,Distance(m),BaseSpeed,BoostedSpeed,BaseDwell,ActualDwell,"
        << "Runtime,SafeHeadway,ActualHeadway,NormalHeadway7Trains,ActionTaken\n";

    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<> dwell_variation(0.8, 1.8);  // variation factor on base dwell

    for (size_t i = 0; i < stations.size() - 1; i++) {
        double distance = stations[i+1].distance - stations[i].distance;
        double base_speed = (distance > 900) ? 35.0 : 30.0;

        int actual_dwell = static_cast<int>(stations[i].base_dwell * dwell_variation(gen));

        // Calculate normal operation headway
        double normal_runtime = calculateRuntime(distance, stations[i].civil_speed);
        double normal_headway = (normal_runtime + actual_dwell) / 7.0;  // for 7 trains
        double safe_headway = calculateSafeHeadway(base_speed, distance);

        // Boost logic
        bool can_boost = false;
        double boosted_speed = base_speed;
        double boosted_headway = normal_headway;

        if (actual_dwell > stations[i].base_dwell * 1.3) {  // if dwell increased by 30%+
            boosted_speed = (base_speed == 30.0) ? 35.0 : 38.0;
            boosted_speed = min(boosted_speed, (double)stations[i].civil_speed);

            double boosted_runtime = calculateRuntime(distance, stations[i].civil_speed, true);
            boosted_headway = (boosted_runtime + actual_dwell) / 7.0; // <-- fix here
            double boosted_safe_headway = calculateSafeHeadway(boosted_speed, distance);

            can_boost = (boosted_headway >= boosted_safe_headway);
        }

        string action = "NO_BOOST";
        double final_speed = base_speed;
        double final_headway = normal_headway;

        if (can_boost) {
            action = "BOOST_APPLIED";
            final_speed = boosted_speed;
            final_headway = boosted_headway;
        }
        else if (normal_headway < safe_headway) {
            action = "EMERGENCY_DELAY";
        }

        // Add a column for "NormalHeadway7Trains" (no boost, always base speed)
        out << stations[i].name << "," << stations[i+1].name << ","
            << distance << "," << base_speed << "," << final_speed << ","
            << stations[i].base_dwell << "," << actual_dwell << ","
            << calculateRuntime(distance, stations[i].civil_speed, (action == "BOOST_APPLIED")) << ","
            << safe_headway << "," << final_headway << ","
            << normal_headway << "," // <-- new column
            << action << "\n";
    }

    out.close();

    cout << "Safe operations report generated.\n";
    cout << "Key safety rules enforced:\n";
    cout << "1. Never allow headway < safe braking distance\n";
    cout << "2. Speed boosts only when safety is maintained\n";
    cout << "3. Emergency protocols trigger if headway becomes unsafe\n";

    return 0;
}
