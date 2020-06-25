# test BLE Scanning software
# jcs 6/8/2014

import blescan3
import sys
import time
import bluetooth._bluetooth as bluez
import pandas as pd
from pathlib import Path
from datetime import datetime
from itertools import zip_longest

## GLOBAL VARS
timeout = 30

def getDistance(measuredPower, RSSI, environment): # https://iotandelectronics.wordpress.com/2016/10/07/how-to-calculate-distance-from-the-rssi-value-of-the-ble-beacon/
    # environment MUST be between 2-4
    return 10 ** ( ( measuredPower - RSSI )/( 10 * environment ) ) 


def process_scans(scans, timestamps):
        """Process collection of received beacon advertisement scans.
        
        Organize collection of received beacon advertisement scans according 
        to address, payload, and measurements.

        Args:
            scans (list): Received beacon advertisement scans. Each element 
                contains all advertisements received from one scan. Elements 
                are in temporal order.
            timestamps (list): Timestamps associated with each scan.
            
        Returns:
            Advertisements organized in a pandas.DataFrame by address first, 
            timestamp second, and then remainder of advertisement payload, 
            e.g., UUID, major, minor, etc.
        """
        # Collect all advertisements
        advertisements = []
        for (scan, timestamp) in zip_longest(scans, timestamps):
            for payload in scan:
                advertisement = {'TIMESTAMP': timestamp}
                advertisement['NAME'] = payload[0]
                advertisement['MAC'] = payload[1]
                advertisement['UUID'] = payload[2]
                advertisement['MAJOR'] = payload[3]
                advertisement['MINOR'] = payload[4]
                advertisement['MAYBE TX POWER'] = payload[5][0]
                advertisement['RSSI'] = payload[6][0]
                advertisement['DISTANCE in feet'] = getDistance(-69, payload[6][0], 2)
                advertisements.append(advertisement)
        # Format into DataFrame
        return  pd.DataFrame(advertisements,columns=['TIMESTAMP', 
            'NAME', 'MAC', 'UUID', 'MAJOR', 'MINOR', 'MAYBE TX POWER', 'RSSI', 'DISTANCE in feet'])

dev_id = 0


try:
    sock = bluez.hci_open_dev(dev_id)
    print("ble thread started")

except:
    print("error accessing bluetooth device...")
    sys.exit(1)

blescan3.hci_le_set_scan_parameters(sock)
blescan3.hci_enable_le_scan(sock)


# initialize csv
scan_prefix = "scan"
scan_file = Path(f"{scan_prefix}_{datetime.now():%Y%m%dT%H%M%S}.csv")

value = 'key_control'

# Initialize control file
control_file = Path(value).resolve()
control_file.touch()
control_file.chmod(0o777)
with control_file.open(mode='w') as f:
    f.write("1")

control_file_handle = None

with open(control_file, 'w') as f:
    f.write("1")

control_file_handle = control_file.open(mode='r+')

timestamps = []
scans = []
scan_count = 0
start_time = time.monotonic()

run = True
while run:

    # off(0) or on(1)
    control_file_handle.seek(0)
    control_flag = control_file_handle.read()

    if (time.monotonic()-start_time) > timeout:
        run = False
        print('done')

    if control_flag == "0":
        run = False
        print('done')
    if control_flag == "1":
        timestamps.append(datetime.now())
        returnedList, results = blescan3.parse_events(sock, 10)
        print(results)
        print("----------")
        '''
        for beacon in returnedList:
            print(beacon)
        '''
        scans.append(results)
    if control_flag == "2":
        continue

advertisements = process_scans(scans, timestamps)
#advertisements = filter_advertisements(advertisements)
advertisements.to_csv(scan_file, index_label='SCAN')
if control_file_handle is not None:
    control_file_handle.close()
control_file.unlink()
