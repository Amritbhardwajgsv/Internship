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
    int max_speed; // Absolute maximum allowed speed
};

// Modified runtime calculation with speed boost option
double calculateRuntime(double distance, int civil_speed, bool boost = false) {
    // Apply 20% speed boost if requested (capped at max_speed)
    double vmax_kmph = min((distance > 800) ? 35.0 : 30.0, (double)civil_speed);
    if (boost) {
        vmax_kmph = min(vmax_kmph * 1.2, 40.0); // 20% boost, max 40 km/h
    }
    
    // Convert to m/s
    double vmax = vmax_kmph * 1000.0 / 3600.0;
    double accel_dist = distance / 8.0;
    double accel = (vmax * vmax) / (2.0 * accel_dist);
    double t_accel = vmax / accel;
    double t_decel = sqrt(2 * 200.0 / accel); // 150m brake + 50m buffer
    double cruise_dist = distance - accel_dist - 150.0;
    double t_cruise = (cruise_dist > 0) ? cruise_dist / vmax : 0;
    
    return t_accel + t_cruise + t_decel;
}

int main() {
    // Complete station list with all parameters
    vector<Station> stations = {
        {"GAIMUKH", 0.0, 60, 35, 40},
        {"GOWNIWADA", 1502.229, 30, 45, 50},
        {"KASARVADVALI", 2887.623, 30, 45, 50}, // 1502.229 + 1385.394
        {"VIJAYGARDEN", 3911.659, 30, 45, 50},  // 2887.623 + 1024.036
        {"DONGARI PADA", 5110.437, 35, 45, 50}, // 3911.659 + 1198.778
        {"TIKUJI NI WADI", 6337.131, 30, 45, 50}, // 5110.437 + 1226.694
        {"MANPADA", 7096.123, 30, 45, 50},      // 6337.131 + 758.992
        {"KAPURBAWDI", 7911.947, 50, 45, 50},   // 7096.123 + 815.824
        {"MAJIWADA", 9365.654, 30, 45, 50},     // 7911.947 + 1453.707
        {"CADBUARY JUNCTION", 10190.361, 60, 45, 50} // 9365.654 + 824.707
    };

    ofstream out("metro_speed_adjustments.csv");
    out << "From,To,Distance(m),BaseDwell,ActualDwell,BaseSpeed(km/h),"
        << "UsedSpeed(km/h),Runtime(s),SectionTime(s),Headway(s),SpeedBoostApplied\n";

    random_device rd;
    mt19937 gen(rd());
    uniform_real_distribution<> crowd_factor(0.7, 2.0); // Random crowding 70% to 200%

    for (size_t i = 0; i < stations.size() - 1; i++) {
        Station& from = stations[i];
        Station& to = stations[i+1];
        double distance = to.distance - from.distance;

        // Simulate random crowding (70% to 200% of base dwell)
        int actual_dwell = from.base_dwell * crowd_factor(gen);
        
        // Calculate normal operation
        double normal_runtime = calculateRuntime(distance, from.civil_speed);
        double normal_section_time = normal_runtime + actual_dwell;
        double normal_headway = normal_section_time / 7.0;

        // Decision to boost speed (if dwell >130% of normal)
        bool boost_needed = (actual_dwell > from.base_dwell * 1.3);
        double runtime = boost_needed ? 
            calculateRuntime(distance, from.civil_speed, true) : 
            normal_runtime;
            
        double used_speed = boost_needed ? 
            min(from.civil_speed * 1.2, static_cast<double>(from.max_speed)) : 
            from.civil_speed;
        
        double section_time = runtime + actual_dwell;
        double headway = section_time / 7.0;

        out << from.name << ","
            << to.name << ","
            << distance << ","
            << from.base_dwell << ","
            << actual_dwell << ","
            << from.civil_speed << ","
            << used_speed << ","
            << runtime << ","
            << section_time << ","
            << headway << ","
            << (boost_needed ? "YES" : "NO") << "\n";
    }

    out.close();
    cout << "Generated speed adjustment report for all stations:\n";
    cout << "1. GAIMUKH → GOWNIWADA\n";
    cout << "2. GOWNIWADA → KASARVADVALI\n";
    cout << "3. KASARVADVALI → VIJAYGARDEN\n";
    cout << "4. VIJAYGARDEN → DONGARI PADA\n";
    cout << "5. DONGARI PADA → TIKUJI NI WADI\n";
    cout << "6. TIKUJI NI WADI → MANPADA\n";
    cout << "7. MANPADA → KAPURBAWDI\n";
    cout << "8. KAPURBAWDI → MAJIWADA\n";
    cout << "9. MAJIWADA → CADBUARY JUNCTION\n";
    cout << "\nSee metro_speed_adjustments.csv for details\n";

    return 0;
}