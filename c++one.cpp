#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <algorithm>
#include <ctime>
#include <cmath>

using namespace std;

// Station data structure
struct Station {
    string name;
    string line;
    string type;
    double distance; // in meters
    int run_time;    // in seconds
    int dwell_time;  // in seconds
    int civil_speed; // in km/h
};

// Timetable entry
struct TimetableEntry {
    string train_id;
    string arrival_time;
    string departure_time;
    string station;
    string direction;
    double top_speed; // in km/h
};

// Configuration constants
const vector<string> START_STATIONS = {"BHAKTI PARK METRO", "GANDHINGAR", "CADBUARY JUNCTION", "GAIMUKH"};
const int TRAINS_PER_STATION = 2;
const int HEADWAY = 10 * 60; // 10 minutes in seconds
const int TURNAROUND_TIME = 15 * 60; // 15 minutes in seconds

// Station data
vector<Station> stations = {
    {"BHAKTI PARK METRO", "LINE4", "METRO_6CAR", 1014.37, 180, 30, 45},
    {"WADALA TT", "LINE4", "METRO_6CAR", 916.806, 180, 30, 45},
    {"ANIKNAGARBUSDEPOT", "LINE4", "METRO_6CAR", 1651.480, 180, 30, 45},
    {"SIDDHARTHCOLONY", "LINE4", "METRO_6CAR", 2421.413, 180, 30, 45},
    {"GARODIA NAGAR", "LINE4", "METRO_6CAR", 1662.149, 180, 30, 45},
    {"PANT NAGAR", "LINE4", "METRO_6CAR", 1148.172, 180, 30, 45},
    {"LAXMINAGAR", "LINE4", "METRO_6CAR", 952.884, 180, 30, 45},
    {"SHREYAS CINEMA", "LINE4", "METRO_6CAR", 745.313, 180, 30, 45},
    {"GODREJ COMPANY", "LINE4", "METRO_6CAR", 709.649, 180, 30, 45},
    {"VIKHROLI METRO", "LINE4", "METRO_6CAR", 1017.761, 180, 30, 45},
    {"SURYA NAGAR", "LINE4", "METRO_6CAR", 973.585, 180, 30, 45},
    {"GANDHINGAR", "LINE4", "METRO_6CAR", 747.000, 180, 30, 45},
    {"NAVAL HOUSING", "LINE4", "METRO_6CAR", 745.156, 180, 30, 45},
    {"BHANDUP MAHAPALIKA", "LINE4", "METRO_6CAR", 1039.865, 180, 30, 45},
    {"BHANDUP METRO", "LINE4", "METRO_6CAR", 797.654, 180, 30, 45},
    {"SHANGRILLA", "LINE4", "METRO_6CAR", 1454.303, 180, 30, 45},
    {"SONAPUR", "LINE4", "METRO_6CAR", 1124.344, 180, 30, 45},
    {"MULUND FIRE STATION", "LINE4", "METRO_6CAR", 1339.919, 180, 30, 45},
    {"MULUND NAKA", "LINE4", "METRO_6CAR", 1212.231, 180, 30, 45},
    {"TEEN HAATH NAKA", "LINE4", "METRO_6CAR", 784.465, 180, 30, 45},
    {"RTO THANE", "LINE4", "METRO_6CAR", 964.956, 180, 30, 45},
    {"MAHAPALIKAMARG", "LINE4", "METRO_6CAR", 795.993, 180, 30, 45},
    {"CADBUARY JUNCTION", "LINE4", "METRO_6CAR", 824.707, 180, 30, 45},
    {"MAJIWADA", "LINE4", "METRO_6CAR", 1445.707, 180, 30, 45},
    {"KAPURBAWDI", "LINE4", "METRO_6CAR", 815.824, 180, 30, 45},
    {"MANPADA", "LINE4", "METRO_6CAR", 758.992, 180, 30, 45},
    {"TIKUJI NI WADI", "LINE4", "METRO_6CAR", 1226.694, 180, 30, 45},
    {"DONGARI PADA", "LINE4", "METRO_6CAR", 1198.778, 180, 30, 45},
    {"VIJAYGARDEN", "LINE4", "METRO_6CAR", 1024.036, 180, 30, 45},
    {"KASARVADVALI", "LINE4", "METRO_6CAR", 1385.394, 180, 30, 45},
    {"GOWNIWADA", "LINE4", "METRO_6CAR", 1502.229, 180, 30, 45},
    {"GAIMUKH", "LINE4", "METRO_6CAR", -1.0, 180, 30, 45} // Using -1.0 for None
};

// Function to calculate speed in km/h
double calculate_speed(double distance, int run_time, int civil_speed) {
    if (distance < 0 || run_time == 0) {
        return -1.0; // Invalid value
    }
    double speed = (distance / run_time) * 3.6; // m/s to km/h
    return min(speed, static_cast<double>(civil_speed));
}

// Function to add seconds to a time string
string add_seconds_to_time(const string& time_str, int seconds) {
    tm tm = {};
    istringstream ss(time_str);
    ss >> get_time(&tm, "%H:%M");
    
    time_t time = mktime(&tm);
    time += seconds;
    
    tm = *localtime(&time);
    ostringstream oss;
    oss << put_time(&tm, "%H:%M");
    return oss.str();
}

// Function to compare time strings
bool is_time_less(const string& time1, const string& time2) {
    tm tm1 = {}, tm2 = {};
    istringstream ss1(time1), ss2(time2);
    ss1 >> get_time(&tm1, "%H:%M");
    ss2 >> get_time(&tm2, "%H:%M");
    
    return difftime(mktime(&tm1), mktime(&tm2)) < 0;
}

// Function to generate timetable
vector<TimetableEntry> generate_timetable() {
    vector<TimetableEntry> timetable;
    int base_minutes = 5 * 60; // 05:00 in minutes

    for (const auto& start_station : START_STATIONS) {
        size_t start_idx = 0;
        for (; start_idx < stations.size(); ++start_idx) {
            if (stations[start_idx].name == start_station) break;
        }

        for (int n = 0; n < TRAINS_PER_STATION; ++n) {
            string train_id = start_station.substr(0, 3);
            for (auto& c : train_id) c = toupper(c);
            train_id += to_string(n + 1);

            vector<Station> forward_seq;
            if (start_station == "GAIMUKH" || start_station == "CADBUARY JUNCTION") {
                forward_seq = vector<Station>(stations.begin(), stations.begin() + start_idx + 1);
                reverse(forward_seq.begin(), forward_seq.end());
            } else {
                forward_seq = vector<Station>(stations.begin() + start_idx, stations.end());
            }

            int current_minutes = base_minutes + n * HEADWAY;
            string direction = "forward";
            auto seq = forward_seq;

            while (current_minutes < 24 * 60) { // Until midnight
                // Journey in current direction
                for (const auto& s : seq) {
                    int arrival_min = current_minutes;
                    int departure_min = arrival_min + s.run_time + s.dwell_time;
                    double topspeed = calculate_speed(s.distance, s.run_time, s.civil_speed);

                    // Convert minutes to HH:MM
                    char arrbuf[6], depbuf[6];
                    snprintf(arrbuf, sizeof(arrbuf), "%02d:%02d", arrival_min / 60, arrival_min % 60);
                    snprintf(depbuf, sizeof(depbuf), "%02d:%02d", departure_min / 60, departure_min % 60);

                    timetable.push_back({
                        train_id,
                        arrbuf,
                        depbuf,
                        s.name,
                        direction,
                        topspeed
                    });

                    current_minutes = departure_min;
                }

                // Turnaround at terminal
                int arrival_min = current_minutes;
                int departure_min = arrival_min + TURNAROUND_TIME;
                char arrbuf[6], depbuf[6];
                snprintf(arrbuf, sizeof(arrbuf), "%02d:%02d", arrival_min / 60, arrival_min % 60);
                snprintf(depbuf, sizeof(depbuf), "%02d:%02d", departure_min / 60, departure_min % 60);

                timetable.push_back({
                    train_id,
                    arrbuf,
                    depbuf,
                    seq.back().name,
                    "turnaround",
                    -1.0
                });

                current_minutes = departure_min;

                // Reverse direction and sequence for next leg
                reverse(seq.begin(), seq.end());
                direction = (direction == "forward") ? "return" : "forward";
            }
        }
    }
    return timetable;
}

// Function to save timetable to CSV
void save_to_csv(const vector<TimetableEntry>& timetable, const string& filename) {
    ofstream file(filename);
    if (!file.is_open()) {
        cerr << "Error opening file: " << filename << endl;
        return;
    }
    
    file << "train_id,arrival_time,departure_time,station,direction,top_speed\n";
    for (const auto& entry : timetable) {
        file << entry.train_id << ","
             << entry.arrival_time << ","
             << entry.departure_time << ","
             << entry.station << ","
             << entry.direction << ",";
        if (entry.top_speed >= 0) {
            file << fixed << setprecision(2) << entry.top_speed;
        } else {
            file << "";
        }
        file << "\n";
    }
    
    file.close();
}

int main() {
    // Generate timetable
    vector<TimetableEntry> timetable = generate_timetable();
    
    // Save to CSV with new filename "cone.csv"
    save_to_csv(timetable, "cone.csv");
    
    cout << "Timetable generated and saved to cone.csv" << endl;
    
    // Note: The visualization part would require a C++ plotting library like Matplotlib-cpp
    // or exporting data for visualization in another tool.
    
    return 0;
}
