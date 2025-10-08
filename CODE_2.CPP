#include<iostream>
#include<vector>
#include<string>
#include<functional>
#include<cmath>
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

const vector<string> START_STATIONS = {"BHAKTI PARK METRO", "GANDHINAGAR", "CADBUARY JUNCTION", "GAIMUKH"};
const int TRAINS_PER_STATION = 2;
const int HEADWAY = 10; // 10 minutes
const int TERMINAL_TURNAROUND = 15; // 15 minutes
const int INTERMEDIATE_TURNAROUND = 1; // 1 minute

vector<station> stations = {
    {"BHAKTI PARK METRO", "LINE4", "METRO_6CAR", 1014.37, 180, 30, 45},
    // ... (all your station data exactly as you provided) ...
    {"GAIMUKH", "LINE4", "METRO_6CAR", -1.0, 180, 30, 45}
};

string format_time_manual(int total_minutes) {
    int hours = total_minutes / 60;
    int minutes = total_minutes % 60;
    char buffer[6];
    sprintf(buffer, "%02d:%02d", hours, minutes);
    return string(buffer);
}

vector<TimetableEntry> generate_24hour_timetable() {
    vector<TimetableEntry> timetable;
    const int FIRST_DEPARTURE = 5 * 60; // 5:00 AM
    const int LAST_DEPARTURE = 24 * 60; // Midnight
    const int NUM_TRAINS = 8; // BPM1, BPM2, GAD1, GAD1_DOWN, CAD1, CAD2_DOWN, GAI_1, GAI_2

    auto calculate_run_time = [](double distance) {
        double speed = (distance < 800.0) ? 30.0 : 35.0;
        return static_cast<int>((distance / speed) * 3.6 / 60); // in minutes
    };

    // Generate trains for each departure time
    for (int depart_time = FIRST_DEPARTURE; depart_time < LAST_DEPARTURE; depart_time += HEADWAY) {
        // BPM1 - Bhakti Park to Gaimukh (UP)
        generate_train(timetable, "BPM1", depart_time, "BHAKTI PARK METRO", "GAIMUKH", "UP", 
                      TERMINAL_TURNAROUND, calculate_run_time);

        // BPM2 - Bhakti Park to Gandhinagar (UP)
        generate_train(timetable, "BPM2", depart_time + HEADWAY, "BHAKTI PARK METRO", "GANDHINAGAR", "UP",
                      INTERMEDIATE_TURNAROUND, calculate_run_time);

        // GAD1 - Gandhinagar to Cadbury (UP)
        generate_train(timetable, "GAD1", depart_time, "GANDHINAGAR", "CADBUARY JUNCTION", "UP",
                      INTERMEDIATE_TURNAROUND, calculate_run_time);

        // GAD1_DOWN - Gandhinagar to Bhakti Park (DOWN)
        generate_train(timetable, "GAD1_DOWN", depart_time + HEADWAY, "GANDHINAGAR", "BHAKTI PARK METRO", "DOWN",
                      TERMINAL_TURNAROUND, calculate_run_time);

        // CAD1 - Cadbury to Gaimukh (UP)
        generate_train(timetable, "CAD1", depart_time, "CADBUARY JUNCTION", "GAIMUKH", "UP",
                      TERMINAL_TURNAROUND, calculate_run_time);

        // CAD2_DOWN - Cadbury to Bhakti Park (DOWN)
        generate_train(timetable, "CAD2_DOWN", depart_time + HEADWAY, "CADBUARY JUNCTION", "BHAKTI PARK METRO", "DOWN",
                      TERMINAL_TURNAROUND, calculate_run_time);

        // GAI_1 - Gaimukh to Cadbury (DOWN)
        generate_train(timetable, "GAI_1", depart_time, "GAIMUKH", "CADBUARY JUNCTION", "DOWN",
                      INTERMEDIATE_TURNAROUND, calculate_run_time);

        // GAI_2 - Gaimukh to Bhakti Park (DOWN)
        generate_train(timetable, "GAI_2", depart_time + HEADWAY, "GAIMUKH", "BHAKTI PARK METRO", "DOWN",
                      TERMINAL_TURNAROUND, calculate_run_time);
    }

    return timetable;
}

void generate_train(vector<TimetableEntry>& timetable, string train_id, int depart_time,
                   string start_stn, string end_stn, string direction,
                   int turnaround, function<int(double)> calc_runtime) {
    int current_time = depart_time;
    bool started = false;
    bool is_down = (direction == "DOWN");

    for (size_t j = 0; j < stations.size(); j++) {
        size_t idx = is_down ? stations.size() - 1 - j : j;
        
        if (stations[idx].station_name == start_stn) started = true;
        if (!started) continue;

        TimetableEntry entry;
        entry.train_id = train_id + "_" + format_time_manual(depart_time).substr(0,2) + 
                         format_time_manual(depart_time).substr(3,2);
        entry.arrival_time = format_time_manual(current_time);
        
        int dwell = (stations[idx].station_name == end_stn) ? turnaround : 
                   ((stations[idx].station_name == "GANDHINAGAR" || 
                     stations[idx].station_name == "CADBUARY JUNCTION") ? INTERMEDIATE_TURNAROUND : 1);
        
        current_time += dwell;
        entry.departure_time = format_time_manual(current_time);
        entry.station = stations[idx].station_name;
        entry.direction = direction;

        // Calculate next segment travel time
        if ((!is_down && idx+1 < stations.size()) || (is_down && idx > 0)) {
            size_t next_idx = is_down ? idx - 1 : idx + 1;
            double dist = abs(stations[next_idx].distance - stations[idx].distance);
            entry.top_speed_that_canbe_achieved = (dist < 800.0) ? 30.0 : 35.0;
            current_time += calc_runtime(dist);
        }

        timetable.push_back(entry);

        if (stations[idx].station_name == end_stn) break;
    }
}

int main() {
    vector<TimetableEntry> timetable = generate_24hour_timetable();
    
    // Print timetable
    for (const auto& entry : timetable) {
        cout << "Train " << entry.train_id << "\t" << entry.station 
             << "\tArr: " << entry.arrival_time 
             << "\tDep: " << entry.departure_time
             << "\tDir: " << entry.direction << endl;
    }
    
    return 0;
}