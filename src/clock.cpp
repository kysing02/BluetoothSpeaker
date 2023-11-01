#include "display.h"
#include "clock.h"
#include <WiFi.h>

/*TODO: This clock program only uses display.h function directly without animation / styling.
    This code will eventually make use of own custom class or add styling here.*/

int prevss = 0;
int prevmm = 0;
int prevhh = 0;

struct tm timeinfo;

void initialize_clock() {
    // Initialize clock by getting time information from connection through Bluetooth
}
void display_clock() {
    
}