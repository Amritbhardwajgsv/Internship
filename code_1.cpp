#include<iostream>
using namespace std;
#include<map>
#include<set>
#include <vector>
#include<cmath>
#include<fstream>
#include<string>

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

const vector<string> START_STATIONS = {"BHAKTI PARK METRO", "GANDHINAGAR", "CADBUARY JUNCTION", "GAIMUKH"};
const int TRAINS_PER_STATION = 2;
const int HEADWAY = 10 * 60; // 10 minutes in seconds
const int TURNAROUND_TIME = 15 * 60; //specified for metro line 4 to be 15 minutes

vector<station> stations = {
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
    {"GANDHINAGAR", "LINE4", "METRO_6CAR", 747.000, 180, 30, 45}, // Fixed from GANDHINGAR
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
    {"GAIMUKH", "LINE4", "METRO_6CAR", -1.0, 180, 30, 45}
};

double calculate_speed(double distance, int run_time, int civil_speed){
    double speed = (distance/run_time)*3.6;
    return (speed > civil_speed) ? civil_speed : speed;
}

string calculate_time(const string &time_str, int headway) {
    int minutes = 0;
    int hours = 0;
    bool colon_found = false;

    for (int i = 0; i < time_str.length(); i++) {
        if (time_str[i] == ':') {
            colon_found = true;
            continue;
        }
        if (!colon_found) {
            hours = hours * 10 + (time_str[i] - '0');
        } else {
            minutes = minutes * 10 + (time_str[i] - '0');
        }
    }

    int new_time = hours * 60 + minutes + headway;
    int new_hour = (new_time / 60) % 24;
    int new_minute = new_time % 60;

    string final_time;
    if (new_hour < 10) final_time += '0';
    final_time += to_string(new_hour / 10) + to_string(new_hour % 10);
    final_time += ':';
    if (new_minute < 10) final_time += '0';
    final_time += to_string(new_minute / 10) + to_string(new_minute % 10);

    return final_time;
}

string format_time_manual(int total_minutes) {
    int hours = total_minutes / 60;
    int minutes = total_minutes % 60;
    string time(5, ' ');
    time[0] = '0' + (hours / 10);
    time[1] = '0' + (hours % 10);
    time[2] = ':';
    time[3] = '0' + (minutes / 10);
    time[4] = '0' + (minutes % 10);
    return time;
}

vector<TimetableEntry> generate_timetable() {
    vector<TimetableEntry> timetable;
    const int BASE_TIME = 5 * 60;
    const int HEADWAY = 10;
    const int TERMINAL_TURNAROUND = 15 * 60;
    const int INTERMEDIATE_TURNAROUND = 60;

    auto calculate_run_time = [](double distance) {
        return static_cast<int>((distance / ((distance < 800.0) ? 30.0 : 35.0)) * 3.6);
    };

    // 1. Bhakti Park to Gaimukh (BPM1 at 5:00)
    string train_id = "BPM1";
    int current_time = BASE_TIME;
    bool started = false;
    
    for (size_t j = 0; j < stations.size(); j++) {
        if (stations[j].station_name == "BHAKTI PARK METRO") started = true;
        if (started) {
            TimetableEntry entry;
            entry.train_id = train_id;
            entry.arrival_time = format_time_manual(current_time);
            
            int dwell = (stations[j].station_name == "GANDHINAGAR" || 
                         stations[j].station_name == "CADBUARY JUNCTION") 
                         ? INTERMEDIATE_TURNAROUND : 30;
            
            current_time += dwell;
            entry.departure_time = format_time_manual(current_time);
            entry.station = stations[j].station_name;
            entry.direction = "UP";
            
            if (j + 1 < stations.size()) {
                double dist = stations[j+1].distance - stations[j].distance;
                entry.top_speed_that_canbe_achieved = (dist < 800.0) ? 30.0 : 35.0;
                current_time += calculate_run_time(dist);
            }
            
            timetable.push_back(entry);
            
            if (stations[j].station_name == "GAIMUKH") {
                current_time += TERMINAL_TURNAROUND;
                break;
            }
        }
    }

    // 2. Bhakti Park to Gandhinagar (BPM2 at 5:10)
    train_id = "BPM2";
    current_time = BASE_TIME + HEADWAY;
    started = false;
    
    for (size_t j = 0; j < stations.size(); j++) {
        if (stations[j].station_name == "BHAKTI PARK METRO") started = true;
        if (started) {
            TimetableEntry entry;
            entry.train_id = train_id;
            entry.arrival_time = format_time_manual(current_time);
            
            int dwell = (stations[j].station_name == "GANDHINAGAR") 
                         ? INTERMEDIATE_TURNAROUND : 30;
            
            current_time += dwell;
            entry.departure_time = format_time_manual(current_time);
            entry.station = stations[j].station_name;
            entry.direction = "UP";
            
            if (j + 1 < stations.size()) {
                double dist = stations[j+1].distance - stations[j].distance;
                entry.top_speed_that_canbe_achieved = (dist < 800.0) ? 30.0 : 35.0;
                current_time += calculate_run_time(dist);
            }
            
            timetable.push_back(entry);
            
            if (stations[j].station_name == "GANDHINAGAR") {
                current_time += INTERMEDIATE_TURNAROUND;
                break;
            }
        }
    }

    // 3. Gandhinagar to Cadbury (GAD1 at 5:00)
    train_id = "GAD1";
    current_time = BASE_TIME;
    started = false;    
    
    for (size_t j = 0; j < stations.size(); j++) {
        if (stations[j].station_name == "GANDHINAGAR") started = true;
        if (started) {
            TimetableEntry entry;
            entry.train_id = train_id;
            entry.arrival_time = format_time_manual(current_time);
            
            int dwell = (stations[j].station_name == "CADBUARY JUNCTION") 
                         ? INTERMEDIATE_TURNAROUND : 30;
            
            current_time += dwell;
            entry.departure_time = format_time_manual(current_time);
            entry.station = stations[j].station_name;
            entry.direction = "UP";
            
            if (j + 1 < stations.size()) {
                double dist = stations[j+1].distance - stations[j].distance;
                entry.top_speed_that_canbe_achieved = (dist < 800.0) ? 30.0 : 35.0;
                current_time += calculate_run_time(dist);
            }
            
            timetable.push_back(entry);
            
            if (stations[j].station_name == "CADBUARY JUNCTION") {
                current_time += INTERMEDIATE_TURNAROUND;
                break;
            }
        }
    }

    // 4. Gandhinagar to Bhakti Park (GAD1_DOWN at 5:10)
    train_id = "GAD1_DOWN";
    current_time = BASE_TIME + HEADWAY;
    started = false;

    for (int j = stations.size() - 1; j >= 0; j--) {
        if (stations[j].station_name == "GANDHINAGAR") started = true;
        if (started) {
            TimetableEntry entry;
            entry.train_id = train_id;
            entry.arrival_time = format_time_manual(current_time);

            int dwell = (stations[j].station_name == "BHAKTI PARK METRO") 
                         ? TERMINAL_TURNAROUND : 30;

            current_time += dwell;
            entry.departure_time = format_time_manual(current_time);
            entry.station = stations[j].station_name;
            entry.direction = "DOWN";

            if (j > 0) {
                double dist = stations[j].distance - stations[j-1].distance;
                entry.top_speed_that_canbe_achieved = (dist < 800.0) ? 30.0 : 35.0;
                current_time += calculate_run_time(abs(dist));
            }

            timetable.push_back(entry);

            if (stations[j].station_name == "BHAKTI PARK METRO") {
                current_time += TERMINAL_TURNAROUND;
                break;
            }
        }
    }

    // 5. Cadbury to Gaimukh (CAD1 at 5:00)
    train_id = "CAD1";
    current_time = BASE_TIME;
    started = false;
    
    for (size_t j = 0; j < stations.size(); j++) {
        if (stations[j].station_name == "CADBUARY JUNCTION") started = true;
        if (started) {
            TimetableEntry entry;
            entry.train_id = train_id;
            entry.arrival_time = format_time_manual(current_time);
            
            int dwell = (stations[j].station_name == "GAIMUKH") 
                         ? TERMINAL_TURNAROUND : 30;
            
            current_time += dwell;
            entry.departure_time = format_time_manual(current_time);
            entry.station = stations[j].station_name;
            entry.direction = "UP";
            
            if (j + 1 < stations.size()) {
                double dist = stations[j+1].distance - stations[j].distance;
                entry.top_speed_that_canbe_achieved = (dist < 800.0) ? 30.0 : 35.0;
                current_time += calculate_run_time(dist);
            }
            
            timetable.push_back(entry);
            
            if (stations[j].station_name == "GAIMUKH") {
                current_time += TERMINAL_TURNAROUND;
                break;
            }
        }
    }

    // 6. Cadbury to Bhakti Park (CAD2_DOWN at 5:10)
    train_id = "CAD2_DOWN";
    current_time = BASE_TIME + HEADWAY;
    started = false;
    
    for (int j = stations.size() - 1; j >= 0; j--) {
        if (stations[j].station_name == "CADBUARY JUNCTION") started = true;
        if (started) {
            TimetableEntry entry;
            entry.train_id = train_id;
            entry.arrival_time = format_time_manual(current_time);
            
            int dwell = (stations[j].station_name == "BHAKTI PARK METRO") 
                         ? TERMINAL_TURNAROUND : 30;
            
            current_time += dwell;
            entry.departure_time = format_time_manual(current_time);
            entry.station = stations[j].station_name;
            entry.direction = "DOWN";
            
            if (j > 0) {
                double dist = stations[j].distance - stations[j-1].distance;
                entry.top_speed_that_canbe_achieved = (dist < 800.0) ? 30.0 : 35.0;
                current_time += calculate_run_time(abs(dist));
            }
            
            timetable.push_back(entry);
            
            if (stations[j].station_name == "BHAKTI PARK METRO") {
                current_time += TERMINAL_TURNAROUND;
                break;
            }
        }
    }

    // 7. Gaimukh to Cadbury (GAI_1 at 5:00)
    train_id = "GAI_1";
    current_time = BASE_TIME;
    started = false;
    
    for (int j = stations.size() - 1; j >= 0; j--) {
        if (stations[j].station_name == "GAIMUKH") started = true;
        if (started) {
            TimetableEntry entry;
            entry.train_id = train_id;
            entry.arrival_time = format_time_manual(current_time);
            
            int dwell = (stations[j].station_name == "CADBUARY JUNCTION") 
                         ? INTERMEDIATE_TURNAROUND : 30;
            
            current_time += dwell;
            entry.departure_time = format_time_manual(current_time);
            entry.station = stations[j].station_name;
            entry.direction = "DOWN";
            
            if (j > 0) {
                double dist = stations[j].distance - stations[j-1].distance;
                entry.top_speed_that_canbe_achieved = (dist < 800.0) ? 30.0 : 35.0;
                current_time += calculate_run_time(abs(dist));
            }
            
            timetable.push_back(entry);
            
            if (stations[j].station_name == "CADBUARY JUNCTION") {
                current_time += INTERMEDIATE_TURNAROUND;
                break;
            }
        }
    }

    // 8. Gaimukh to Bhakti Park (GAI_2 at 5:10)
    train_id = "GAI_2";
    current_time = BASE_TIME + HEADWAY;
    started = false;
    
    for (int j = stations.size() - 1; j >= 0; j--) {
        if (stations[j].station_name == "GAIMUKH") started = true;
        if (started) {
            TimetableEntry entry;
            entry.train_id = train_id;
            entry.arrival_time = format_time_manual(current_time);
            
            int dwell = (stations[j].station_name == "BHAKTI PARK METRO") 
                         ? TERMINAL_TURNAROUND : 30;
            
            current_time += dwell;
            entry.departure_time = format_time_manual(current_time);
            entry.station = stations[j].station_name;
            entry.direction = "DOWN";
            
            if (j > 0) {
                double dist = stations[j].distance - stations[j-1].distance;
                entry.top_speed_that_canbe_achieved = (dist < 800.0) ? 30.0 : 35.0;
                current_time += calculate_run_time(abs(dist));
            }
            
            timetable.push_back(entry);
            
            if (stations[j].station_name == "BHAKTI PARK METRO") {
                current_time += TERMINAL_TURNAROUND;
                break;
            }
        }
    }

    return timetable;
}

int main() {
    vector<TimetableEntry> timetable = generate_timetable();
    // Print or process the timetable as needed
    for (const auto& entry : timetable) {
        cout << "Train ID: " << entry.train_id
             << ", Arrival: " << entry.arrival_time
             << ", Departure: " << entry.departure_time
             << ", Station: " << entry.station
             << ", Direction: " << entry.direction
             << ", Top Speed: " << entry.top_speed_that_canbe_achieved
             << endl;
    }
    // Save to file if needed
    ofstream file("timetable.txt");
    if (file.is_open()) {
        for (const auto& entry : timetable) {
            file << "Train ID: " << entry.train_id
                 << ", Arrival: " << entry.arrival_time
                 << ", Departure: " << entry.departure_time
                 << ", Station: " << entry.station
                 << ", Direction: " << entry.direction
                 << ", Top Speed: " << entry.top_speed_that_canbe_achieved
                 << endl;
        }
        file.close();
    } else {
        cout << "Unable to open file";
    }
    return 0;
}