#include "bluetooth.h"

bool isInitialized = false;
BluetoothSerial SerialBT;

void initialize_bluetooth() {
    Serial.begin(115200);
    SerialBT.begin(115200);

    while(!isInitialized) {
        if (SerialBT.connected()) {
            if (!isInitialized) {
                SerialBT.println("INITIALIZED_FALSE");
                break;
            }
            else {
                SerialBT.println("INITIALIZED_TRUE");
                break;
            }
        }
        delay(100);
    }
    // Main program logic starts here
    char data = SerialBT.read();
}