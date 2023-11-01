/* Smart Bluetooth Speaker with Matrix Display & Gesture Sensor
by Team 01 Ishikawa Kosen
*/

// Main Program and State Manager for Bluetooth Speaker

#include <Arduino.h>

#include "main.h"
#include "bluetooth.h"

enum State {
  INITIAL,
  SLEEP,
  CLOCK
};

enum State state = INITIAL;

void setup() {

  //initialize_display();
  initialize_bluetooth();

}

void loop() {

}