#include<iostream>
#include<iomanip>
#include<sstream>
using namespace std;
int  main(){
    int num_train=5;
    int headway=3*60;
    for(int t=0;t<num_train;t++){
         ostringstream oss;
        oss << "t" << setw(3) << setfill('0') << (t + 1);
        string arrival=add_minutes()

    }
}