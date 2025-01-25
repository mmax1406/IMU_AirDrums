import serial
import numpy as np
from drumsClass import IMUSensorData
import keyboard  # For keypress detection
import time
import rtmidi

# Set up the serial connection
ser = serial.Serial('COM4', 115200, timeout=0.1)  # Use a short timeout for non-blocking behavior

# Constants
SAMPLES_FOR_CALIBRATION = 100
HIT_THRESHOLD = -3 # Threshold for pitch rate detection (adjust as needed)
last_save_time = 0 # For a time debounce mechanism

# Initialize sensor objects
sensor1 = IMUSensorData(SAMPLES_FOR_CALIBRATION)
sensor2 = IMUSensorData(SAMPLES_FOR_CALIBRATION)

MaDataSensor1 = []
MaDataSensor2 = []
NumOfSamples = 5000
count = 0

try:
    print("Listening for drum hits (Press Ctrl+C to exit)...")
    prev_accZ1 = prev_accZ2 = 0.0  # Previous acceleration values for jerk calculation

    while True:
        # Read a line of data from the serial port
        line = ser.readline().decode('utf-8').strip()
        if line:
            values = line.split()
            if len(values) == 12:  # Ensure there are exactly 8 values
                data = list(map(float, values))
                if not all(value == 0 for value in data):  # Ensure all values are non-zero
                    w1, x1, y1, z1, omegaP1, Calib1 = map(float, values[:6])
                    w2, x2, y2, z2, omegaP2, Calib2 = map(float, values[6:])

                    if Calib1 == 0:
                        print('Sensor 1 No good')
 
                    if Calib2 == 0:
                        print('Sensor 2 No good')

                    if Calib1>0 and Calib2>0:
                        print(f"{count} | L: H: {sensor1.heading:.3f}, P: {sensor1.pitch:.3f}, "
                                f"R: H: {sensor2.heading:.3f}, P: {sensor2.pitch:.3f}") 

                        # Update raw data
                        sensor1.process_data(w1, x1, y1, z1, omegaP1)
                        sensor2.process_data(w2, x2, y2, z2, omegaP2)

                        if count<NumOfSamples:
                            MaDataSensor1.append((w1, x1, y1, z1, omegaP1, Calib1, sensor1.heading, sensor1.pitch))
                            MaDataSensor2.append((w1, x1, y1, z1, omegaP2, Calib1, sensor1.heading, sensor1.pitch))
                        else:
                            with open("sensor_data1.txt", "w") as f:
                                f.write("Sensor 1 Data:\n")
                                for data in MaDataSensor1:
                                    f.write(",".join(map(str, data)) + "\n")
                            with open("sensor_data2.txt", "w") as f:
                                for data in MaDataSensor2:
                                    f.write(",".join(map(str, data)) + "\n")
                            print("Data saved to sensor_data.txt")
                            break
                        count += 1
finally:
    ser.close()
    print("Serial port closed.")
