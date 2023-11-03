# This source code might not be used if raspberry pi OS do that automatically

import ntplib
import time

# Synchronize the system time with an NTP server
def sync_time_with_ntp_server(ntp_server='pool.ntp.org'):
    try:
        c = ntplib.NTPClient()
        response = c.request(ntp_server)
        current_time = response.tx_time
        
        # Set the system time to the synchronized time
        time.localtime(time.mktime(time.localtime(current_time)))
        print("Time synchronized with NTP server: ", time.strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        print("Failed to sync time:", str(e))