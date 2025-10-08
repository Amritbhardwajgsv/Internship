#include<iostream>
#include<vector>
#include<string>
#include<functional>
#include<cmath>
#include<algorithm>
#include<fstream>
#include <iomanip>

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
    {"GAIMUKH", "LINE4", "METRO_6CAR", 0.0, 180, 180, 35},
    {"GOWNIWADA", "LINE4", "METRO_6CAR", 1502.229, 180, 30, 45},
    {"KASARVADVALI", "LINE4", "METRO_6CAR", 1385.394, 180, 30, 45},
    {"VIJAYGARDEN", "LINE4", "METRO_6CAR", 1024.036, 180, 30, 45},
    {"DONGARI PADA", "LINE4", "METRO_6CAR", 1198.778, 180, 30, 45},
    {"TIKUJI NI WADI", "LINE4", "METRO_6CAR", 1226.694, 180, 30, 45},
    {"MANPADA", "LINE4", "METRO_6CAR", 758.992, 180, 30, 45},
    {"KAPURBAWDI", "LINE4", "METRO_6CAR", 815.824, 180, 30,45},
    {"MAJIWADA", "LINE4", "METRO_6CAR", 1453.707, 180, 30, 45},
    {"CADBUARY JUNCTION", "LINE4", "METRO_6CAR", 824.707, 180, 180, 45}
};

// amde this function for caclulating runtime 

double calculate_run_time(double distance, int civil_speed) {
    const double brake_distance = 150.0; 
    const double buffer_distance = 50.0; // meters for buffer
    double vmax_kmph = (distance > 800) ? 35.0 : 30.0;
    vmax_kmph = std::min(vmax_kmph, (double)civil_speed);
    double vmax = vmax_kmph * 1000.0 / 3600.0; 

    // as mentioned to take the accelerating phase of the train as 1/8th of the distance
    double accelerating_distance = distance / 8.0;

    // 2. Acceleration needed to reach vmax in accelerating_distance: v^2 = 2*a*s => a = v^2/(2*s)
    double accel = vmax * vmax / (2.0 * accelerating_distance);

    // 3. Time to reach vmax: v = u + at => t = v/a
    double t_accel = vmax / accel;

    // 4. Deceleration phase: vmax to 0 over brake_distance (assume deceleration = accel for simplicity)
    double t_decel = sqrt(2 * (brake_distance+buffer_distance) / accel);

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
double safestheadwaysbetweeneachstation(double average_speed_in_thatsection, double distance_between_stations) {
    double safestheadway = 0;
    double buffer_distance = 50.0; // meters for buffer
    double brake_distance = 150.0; // meters for brake distance
    double top_speed = 0; // m/s
    if (distance_between_stations > 800) {
        top_speed = 35.0 * 1000.0 / 3600.0; // m/s
    } else {
        top_speed = 30.0 * 1000.0 / 3600.0; // m/s
    }
    safestheadway = (brake_distance + buffer_distance) / top_speed;
    return safestheadway;
}

double headwayofthissection(double runtime){
    double no_of_trains = 7;
    double headway = runtime / no_of_trains;
    return headway;
}

void generate_timetable() {
    std::ofstream timetable("timetable_5to6.csv");
    timetable << "Station,Arrival,Departure\n";

    // Start at 5:00:00
    int current_time_sec = 5 * 3600; // 5:00 AM in seconds
    std::string arrival, departure;

    // First station: departure only
    arrival = "--";
    int dwell_time = stations[0].dwell_time;
    departure = "05:00:00";
    timetable << stations[0].station_name << "," << arrival << "," << departure << "\n";

    // For each next station
    for (size_t i = 1; i < stations.size(); ++i) {
        double distance = stations[i].distance;
        int civil_speed = std::min(stations[i-1].civil_speed, stations[i].civil_speed);
        double runtime = calculate_run_time(distance, civil_speed);

        // Arrival time at this station
        current_time_sec += static_cast<int>(runtime);
        int arr_h = current_time_sec / 3600;
        int arr_m = (current_time_sec % 3600) / 60;
        int arr_s = current_time_sec % 60;
        std::ostringstream arr_ss;
        arr_ss << std::setw(2) << std::setfill('0') << arr_h << ":"
               << std::setw(2) << std::setfill('0') << arr_m << ":"
               << std::setw(2) << std::setfill('0') << arr_s;
        arrival = arr_ss.str();

        // Dwell time at this station
        dwell_time = stations[i].dwell_time;
        current_time_sec += dwell_time;

        // Departure time from this station
        int dep_h = current_time_sec / 3600;
        int dep_m = (current_time_sec % 3600) / 60;
        int dep_s = current_time_sec % 60;
        std::ostringstream dep_ss;
        dep_ss << std::setw(2) << std::setfill('0') << dep_h << ":"
               << std::setw(2) << std::setfill('0') << dep_m << ":"
               << std::setw(2) << std::setfill('0') << dep_s;
        departure = dep_ss.str();

        // Only write if arrival is before 6:00 AM
        if (current_time_sec <= 6 * 3600) {
            timetable << stations[i].station_name << "," << arrival << "," << departure << "\n";
        } else {
            // If arrival is before 6:00 but departure is after, still write
            if ((current_time_sec - dwell_time) < 6 * 3600) {
                timetable << stations[i].station_name << "," << arrival << "," << "--\n";
            }
            break;
        }
    }
    timetable.close();
    std::cout << "Timetable written to timetable_5to6.csv\n";
}

int main() {
    double total_runtime = 0.0;
    double total_distance = 0.0;
    double total_dwell_time = 0.0;

    std::ofstream file("section_3.csv");
    file << "From,To,Distance(m),RunTime(s),DwellTime(s),TotalSectionTime(s),AverageSpeed(km/h),SafeHeadway(s)\n";
    for (size_t i = 0; i < stations.size() - 1; ++i) {
        double distance = stations[i+1].distance;
        int civil_speed = std::min(stations[i].civil_speed, stations[i+1].civil_speed);
        double runtime = calculate_run_time(distance, civil_speed);

        // Use terminal dwell for first row, else arrival station dwell
        int dwell_time = (i == 0) ? stations[0].dwell_time : stations[i+1].dwell_time;

        double section_time = runtime + dwell_time;
        double avg_speed = (runtime > 0) ? (distance / runtime) * 3.6 : 0; // km/h
        double safe_headway = safestheadwaysbetweeneachstation(avg_speed, distance);

        file << stations[i].station_name << ","
             << stations[i+1].station_name << ","
             << distance << ","
             << runtime << ","
             << dwell_time << ","
             << section_time << ","
             << avg_speed << ","
             << safe_headway << "\n";

        total_runtime += runtime;
        total_distance += distance;
        total_dwell_time += dwell_time;
    }

    // Add dwell at the starting terminal (if not already included)
    total_dwell_time += stations[0].dwell_time;

    double overall_headway_min = ((total_runtime + total_dwell_time)*2) / 7.0 / 60.0;

    file << "#Total running distance:," << total_distance << "\n";
    file << "#Total run time (s):," << total_runtime << "\n";
    file << "#Total dwell time (s):," << total_dwell_time << "\n";
    file << "#Overall headway for 7 trains (min):," << overall_headway_min << "\n";
    file.close();

    std::cout << "Overall headway for 7 trains (min): " << overall_headway_min << std::endl;
    std::cout << "CSV file 'section_3.csv' created. Open it in Excel." << std::endl;

    generate_timetable();
    return 0;
}
