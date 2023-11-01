#ifndef BLUETOOTH_H
#define BLUETOOTH_H

#include <BluetoothSerial.h>

void initialize_bluetooth();
void connect_bluetooth();
void data_transfer(void *pvParameters);
void write_data();
void read_data(void *pvParameters);

#endif