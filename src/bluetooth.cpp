#include "bluetooth.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <list>

bool is_initialized = false;
bool is_connected = false;
BluetoothSerial SerialBT;

// Serial Read / Write Settings
std::list<String> read_buffer;
std::list<String> write_buffer;
int timeout_ms = 2000;
int async_sleep_time = 500;
int rw_timer = 100;
bool semaphore = 0;


void initialize_bluetooth() {
    Serial.begin(115200);
    SerialBT.begin(115200);
    // Create semaphore to hold async function to wait for another async function

    connect_bluetooth();

    // Start async function for bluetooth continuous data transfer
    xTaskCreate(data_transfer, "DataTransfer", 2048, NULL, 5, NULL);
    // Main Menu
}

void connect_bluetooth() {
    while(!SerialBT.available()) {
        if (SerialBT.connected()) {
            is_connected = true;
            SerialBT.println("BT_CONNECT_START");
        }
        delay(100);
    }
    // Main program logic starts here
    // Program should get initialization data confirm message
    String received_data = SerialBT.readStringUntil('\n');
    if (received_data == "BT_CONNECTED") {
        is_initialized = true;
        return;
    }
    else {
        // Unexpected serial data
        exit(1);
    }
}

void data_transfer(void *pvParameters) {
    while (true) {
        while (is_connected) {
            // Write data
            write_data();

            // Read data (with Timeout)
            xTaskCreate(read_data, "ReadData", 2048, NULL, 5, NULL);
            
            // Halt task until ReadData is complete
            while (semaphore == 0)
            {
                vTaskDelay(pdMS_TO_TICKS(rw_timer));
            }

            vTaskDelay(pdMS_TO_TICKS(async_sleep_time));
            semaphore = 0;
        }
        // If Bluetooth is disconnected, attempt to reconnect automatically
        connect_bluetooth();
    }
    vTaskDelete(NULL);
}

void write_data() {
    // Nothing to send in write buffer
    if (write_buffer.size() <= 0) {
        SerialBT.println("BT_CONNECTION_CHECK");
    }
    else {
        String command = write_buffer.front();
        write_buffer.pop_front();
        SerialBT.println(command);
    }
}

void read_data(void *pvParameters) {
    // Get the current tick count
    TickType_t start_time = xTaskGetTickCount();
    while (true) {
        // Read data function
        if (SerialBT.available()) {
            String received_data = SerialBT.readStringUntil('\n');
            // Filter out check signal
            if (received_data != "BT_CONNECTION_IDLE") {
                read_buffer.push_back(received_data);
            }
            semaphore = 1;
            vTaskDelete(NULL);
            return;
        }

        // Check if the timeout has occured
        if ((xTaskGetTickCount() - start_time) * portTICK_PERIOD_MS >= timeout_ms) {
            // printf("TimeoutError: BT_CONNECTION_LOST");
            is_connected = false;
            semaphore = 1;
            vTaskDelete(NULL);
            return;
        }

        // Wait before begin next read trial
        vTaskDelay(pdMS_TO_TICKS(rw_timer));
    }
}