# test BLE Scanning software
# jcs 6/8/2014

import blescan3
import sys

import bluetooth._bluetooth as bluez

def process_scans(self, scans, timestamps):
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
            for address, payload in scan.items():
                advertisement = {'ADDRESS': address, 'TIMESTAMP': timestamp}
                advertisement['NAME'] = payload[0]
                advertisement['MAC'] = payload[1]
                advertisement['UUID'] = payload[2]
                advertisement['MAJOR'] = payload[3]
                advertisement['MINOR'] = payload[4]
                advertisement['Uhh'] = payload[5]
                advertisement['RSSI'] = payload[6]
                advertisements.append(advertisement)
        # Format into DataFrame
        return  pd.DataFrame(advertisements,columns=['ADDRESS', 'TIMESTAMP', 
            'UUID', 'MAJOR', 'MINOR', 'TX POWER', 'RSSI'])

dev_id = 0
try:
    sock = bluez.hci_open_dev(dev_id)
    print("ble thread started")

except:
    print("error accessing bluetooth device...")
    sys.exit(1)

blescan3.hci_le_set_scan_parameters(sock)
blescan3.hci_enable_le_scan(sock)

while True:
    returnedList,results = blescan3.parse_events(sock, 10)
    print(results)
    print("----------")
    for beacon in returnedList:
        print(beacon)

    for beacon in results:

