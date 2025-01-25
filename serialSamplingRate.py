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

prevTime = 0.0
averageTime = 0.0
count = 0.0

try:
    print("Listening for drum hits (Press Ctrl+C to exit)...")
    prev_accZ1 = prev_accZ2 = 0.0  # Previous acceleration values for jerk calculation

    while True:
        # Read a line of data from the serial port
        line = ser.readline().decode('utf-8').strip()
        if line:
            values = line.split()
            if len(values) == 10:  # Ensure there are exactly 8 values
                data = list(map(float, values))
                if not all(value == 0 for value in data):  # Ensure all values are non-zero
                    w1, x1, y1, z1, omegaP1 = map(float, values[:5])
                    w2, x2, y2, z2, omegaP2 = map(float, values[5:])

                    # Update raw data
                    sensor1.process_data(w1, x1, y1, z1, omegaP1)
                    sensor2.process_data(w2, x2, y2, z2, omegaP2)

                    gotData = time.time()
                    dt = gotData - prevTime
                    prevTime = gotData

                    f = 1/dt
                    count += 1
                    averageTime = averageTime + (f - averageTime) / count

                    print(averageTime)

                    
except KeyboardInterrupt:
    print("\nExiting program.")
finally:
    ser.close()
    print("Serial port closed.")
