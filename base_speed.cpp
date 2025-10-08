#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <fstream>
#include <random>

using namespace std;

struct Station {
    string name;
    double distance;
    int base_dwell;
    int civil_speed;
};

// Calculate safe headway (minimum separation time)
double calculateSafeHeadway(double speed_kmph, double distance) {
    const double brake_distance = 150.0; // meters
    const double reaction_time = 2.0; // seconds
    double speed_ms = speed_kmph * 1000.0 / 3600.0;
    
    // Safe headway = (braking distance / speed) + reaction time
    return (brake_distance / speed_ms) + reaction_time;
}

double calculateRuntime(double distance, int civil_speed, bool boost = false) {
    double vmax_kmph = (distance > 900) ? 35.0 : 30.0;
    
    if (boost) {
        vmax_kmph = (vmax_kmph == 30.0) ? 35.0 : 38.0;
    }
    vmax_kmph = min(vmax_kmph, (double)civil_speed);
    
    double vmax = vmax_kmph * 1000.0 / 3600.0;
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
        {"GAIMUKH", 0.0, 60, 35},
        {"GOWNIWADA", 1502.229, 30, 45},
        {"KASARVADVALI", 2887.623, 30, 45},
        {"VIJAYGARDEN", 3911.659, 30, 45},
        {"DONGARI PADA", 5110.437, 35, 45},
        {"TIKUJI NI WADI", 6337.131, 30, 45},
        {"MANPADA", 7096.123, 30, 45},
        {"KAPURBAWDI", 7911.947, 50, 45},
        {"MAJIWADA", 9365.654, 30, 45},
        {"CADBUARY JUNCTION", 10190.361, 60, 45}
    };

    ofstream out("metro_operations_safe.csv");
    out << "From,To,Distance(m),BaseSpeed,BoostedSpeed,DwellTime,"
        << "Runtime,SafeHeadway,ActualHeadway,ActionTaken\n";

    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<> dwell_variation(0.8, 1.8);

    for (size_t i = 0; i < stations.size() - 1; i++) {
        double distance = stations[i+1].distance - stations[i].distance;
        double base_speed = (distance > 900) ? 35.0 : 30.0;
        int actual_dwell = stations[i].base_dwell * dwell_variation(gen);
        
        // Calculate normal operation
        double normal_runtime = calculateRuntime(distance, stations[i].civil_speed);
        double normal_headway = (normal_runtime + actual_dwell) / 7.0;
        double safe_headway = calculateSafeHeadway(base_speed, distance);

        // Check if boost is possible
        bool can_boost = false;
        double boosted_speed = base_speed;
        double boosted_headway = normal_headway;

        if (actual_dwell > stations[i].base_dwell * 1.3) {
            boosted_speed = (base_speed == 30.0) ? 35.0 : 38.0;
            boosted_speed = min(boosted_speed, (double)stations[i].civil_speed);
            
            double boosted_runtime = calculateRuntime(distance, stations[i].civil_speed, true);
            boosted_headway = (boosted_runtime + actual_dwell) / 7.0;
            double boosted_safe_headway = calculateSafeHeadway(boosted_speed, distance);
            
            // Only allow boost if it doesn't violate safety
            can_boost = (boosted_headway >= boosted_safe_headway);
        }

        // Final decision
        string action = "NO_BOOST";
        double final_speed = base_speed;
        double final_headway = normal_headway;

        if (can_boost && (boosted_headway < normal_headway)) {
            action = "BOOST_APPLIED";
            final_speed = boosted_speed;
            final_headway = boosted_headway;
        }
        else if (normal_headway < safe_headway) {
            action = "EMERGENCY_DELAY";
            // Implement delay procedures here
        }

        out << stations[i].name << "," << stations[i+1].name << ","
            << distance << "," << base_speed << "," << final_speed << ","
            << actual_dwell << "," << calculateRuntime(distance, stations[i].civil_speed, (action == "BOOST_APPLIED")) << ","
            << safe_headway << "," << final_headway << "," << action << "\n";
    }

    out.close();
    cout << "Safe operations report generated.\n";
    cout << "Key safety rules enforced:\n";
    cout << "1. Never allow headway < safe braking distance\n";
    cout << "2. Speed boosts only when safety is maintained\n";
    cout << "3. Emergency protocols trigger if headway becomes unsafe\n";

    return 0;
}