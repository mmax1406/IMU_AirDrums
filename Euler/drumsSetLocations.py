import serial
import keyboard  # For keypress detection
from drumsClass import IMUSensorData
import time  # For debounce timing

# Set up the serial connection
ser = serial.Serial('COM4', 115200, timeout=0.1)  # Use a short timeout for non-blocking behavior

# Constants
SAMPLES_FOR_CALIBRATION = 100

# Initialize sensor objects
sensor1 = IMUSensorData(SAMPLES_FOR_CALIBRATION)
sensor2 = IMUSensorData(SAMPLES_FOR_CALIBRATION)

# Initialize arrays to store recorded data
recorded_sensor1 = []
recorded_sensor2 = []

# For the clicking
last_save_time = 0.0
dTime = 1.0

try:   
    print("Receiving data (Press Ctrl+C to exit)...")
    while True:
        # Read a line of data from the serial port
        line = ser.readline().decode('utf-8').strip()
        if line:
            values = line.split()
            if len(values) == 8:  # Ensure there are exactly 8 values
                data = list(map(float, values))
                if not all(value == 0 for value in data):  # Ensure all values are non-zero
                    
                    heading1, roll1, pitch1, omegaP1 = map(float, values[:4])
                    heading2, roll2, pitch2, omegaP2 = map(float, values[4:])
                    
                    # Update raw data
                    sensor1.update_raw_data(heading1, roll1, pitch1, omegaP1)
                    sensor2.update_raw_data(heading2, roll2, pitch2, omegaP2)

                    # if sensor1.calibration_counter < SAMPLES_FOR_CALIBRATION:
                    #     sensor1.calculate_offset()
                    #     sensor2.calculate_offset()
                    # else:
                    #     sensor1.process_data()
                    #     sensor2.process_data()

                    print(f"L: H: {sensor1.heading:.3f}, P: {sensor1.pitch:.3f}, "
                            f"R: H: {sensor2.heading:.3f}, P: {sensor2.pitch:.3f}")                   

                    
                    # Record data if keys are pressed
                    if keyboard.is_pressed('l'):
                        current_time = time.time()
                        if current_time - last_save_time > dTime:
                            last_save_time = current_time  # Update the last save time
                            recorded_sensor1.append((sensor1.heading, sensor1.pitch, sensor1.roll, 0))
                            print(f"Recorded sensor 1 data: {recorded_sensor1[-1]}")

                    if keyboard.is_pressed('r'):
                        current_time = time.time()
                        if current_time - last_save_time > dTime:
                            last_save_time = current_time  # Update the last save time
                            recorded_sensor2.append((sensor2.heading, sensor2.pitch, sensor2.roll, 0))
                            print(f"Recorded sensor 2 data: {recorded_sensor2[-1]}")

                    if keyboard.is_pressed('s'):
                        current_time = time.time()
                        if current_time - last_save_time > dTime:
                            last_save_time = current_time  # Update the last save time
                            with open("sensor_data.txt", "w") as f:
                                f.write("Sensor 1 Data:\n")
                                for data in recorded_sensor1:
                                    f.write(f"{data}\n")
                                f.write("\nSensor 2 Data:\n")
                                for data in recorded_sensor2:
                                    f.write(f"{data}\n")
                            print("Data saved to sensor_data.txt")

except KeyboardInterrupt:
    print("\nExiting program.")
finally:
    ser.close()
    print("Serial port closed.")
