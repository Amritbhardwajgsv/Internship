#include<iostream>
#include<vector>
#include<string>
#include<functional>
#include<cmath>
#include<algorithm>
#include<fstream>

using namespace std;
struct station {
    string station_name;
    string line_name;
    string station_type;
    double distance;
    int run_time;
    int dwell_time;
    int civil_speed;
};

struct TimetableEntry {
    string train_id;
    string arrival_time;
    string departure_time;
    string station;
    string direction;
    double top_speed_that_canbe_achieved;
};
const vector<string> START_STATIONS = {"BHAKTI PARK METRO", "GANDHINAGAR"};
const int TRAINS_PER_STATION = 2;
const int HEADWAY = 10*60; // 10 minutes
const int TERMINAL_TURNAROUND =6*60; // 15 minutes
//const int INTERMEDIATE_TURNAROUND = 1; // 1 minute
vector<station> stations = {
    {"BHAKTI PARK METRO", "LINE4", "METRO_6CAR", 0, 180, 30, 45},
    {"WADALA TT", "LINE4", "METRO_6CAR", 1014.37, 180, 30, 45},
    {"ANIKNAGARBUSDEPOT", "LINE4", "METRO_6CAR", 916.806, 180, 30, 45},
    {"SIDDHARTHCOLONY", "LINE4", "METRO_6CAR", 1651.480, 180, 30, 45},
    {"GARODIA NAGAR", "LINE4", "METRO_6CAR", 2421.413, 180, 30, 45},
    {"PANT NAGAR", "LINE4", "METRO_6CAR", 1662.149, 180, 30, 45},
    {"LAXMINAGAR", "LINE4", "METRO_6CAR", 1148.172, 180, 30, 45},
    {"SHREYAS CINEMA", "LINE4", "METRO_6CAR", 952.884, 180, 30, 45},
    {"GODREJ COMPANY", "LINE4", "METRO_6CAR", 745.313, 180, 30, 45},
    {"VIKHROLI METRO", "LINE4", "METRO_6CAR", 709.649, 180, 30, 45},
    {"SURYA NAGAR", "LINE4", "METRO_6CAR", 1017.761, 180, 30, 45},
    {"GANDHINAGAR", "LINE4", "METRO_6CAR", 973.585, 180, 30, 45}

};
double calculate_run_time(double distance, int civil_speed) {
    const double brake_distance = 150.0; // meters for braking
    double vmax_kmph = (distance > 800) ? 35.0 : 30.0;
    vmax_kmph = std::min(vmax_kmph, (double)civil_speed);
    double vmax = vmax_kmph * 1000.0 / 3600.0; // km/h to m/s

    // 1. Accelerating distance (your logic: distance/8)
    double accelerating_distance = distance / 8.0;

    // 2. Acceleration needed to reach vmax in accelerating_distance: v^2 = 2*a*s => a = v^2/(2*s)
    double accel = vmax * vmax / (2.0 * accelerating_distance);

    // 3. Time to reach vmax: v = u + at => t = v/a
    double t_accel = vmax / accel;

    // 4. Deceleration phase: vmax to 0 over brake_distance (assume deceleration = accel for simplicity)
    double t_decel = sqrt(2 * brake_distance / accel);

    // 5. Cruise distance and time
    double d_cruise = distance - accelerating_distance - brake_distance;
    double t_cruise = (d_cruise > 0) ? d_cruise / vmax : 0;

    // 6. If not enough distance to reach vmax, adjust calculation
    if (d_cruise < 0) {
        // Only accelerate and decelerate, never reach vmax
        double d_half = (distance - brake_distance > 0) ? (distance - brake_distance) : (distance / 2.0);
        double v_peak = sqrt(2 * accel * d_half);
        t_accel = v_peak / accel;
        t_decel = sqrt(2 * brake_distance / accel);
        t_cruise = 0;
    }

    return t_accel + t_cruise + t_decel;
}
    
int main() {
    double total_runtime = 0.0;
    double total_distance = 0.0;

    std::ofstream file("section_1.csv");
    file << "From,To,Distance(m),RunTime(s),AverageSpeed(km/h)\n";
    for (size_t i = 0; i < stations.size() - 1; ++i) {
        double distance = stations[i+1].distance; // if distance is segment length
        int civil_speed = std::min(stations[i].civil_speed, stations[i+1].civil_speed);
        double runtime = calculate_run_time(distance, civil_speed);
        double avg_speed = (runtime > 0) ? (distance / runtime) * 3.6 : 0; // km/h

        file << stations[i].station_name << ","
             << stations[i+1].station_name << ","
             << distance << ","
             << runtime << ","
             << avg_speed << "\n";

        total_runtime += runtime;
        total_distance += distance;
    }
    file << "#Total running distance:," << total_distance << "\n";
    file << "#Total run time (s):," << total_runtime << "\n";
    file << "#Average speed (km/h):," << (total_distance / total_runtime) * 3.6 << "\n";
    file.close();

    std::cout << "CSV file 'section_1.csv' created. Open it in Excel." << std::endl;
    return 0;
}
