import serial
import numpy as np

# Set up the serial connection
# Replace 'COM4' with the correct port for your Arduino
ser = serial.Serial('COM4', 115200, timeout=0.1)  # Use a short timeout for non-blocking behavior

# Main thingsd for the user to change
samples_for_calibration = 100


# Define variables to store the received data
roll1, pitch1, heading1, accZ1 = 0.0, 0.0, 0.0, 0.0
roll2, pitch2, heading2, accZ2 = 0.0, 0.0, 0.0, 0.0
# Varibales to store old Data
roll1prev, pitch1prev, heading1prev, accZ1prev = 0.0, 0.0, 0.0, 0.0
roll2prev, pitch2prev, heading2prev, accZ2prev = 0.0, 0.0, 0.0, 0.0
# Handle offsets
rollOffset1, pitchOffset1, headingOffset1, accZ1 = 0.0, 0.0, 0.0, 0.0
rollOffset2, pitchOffset2, headingOffset2, accZ2 = 0.0, 0.0, 0.0, 0.0
# Calibration 
calibrationCounter = 0
unwrapCounter = 0 #Wont happen probably but i need this to go below and above a single circle

# Function to unwrap angles
def unwrap_stream(new_angle, prev_angle, wrap_threshold, unwrapCounter):
    angle = 0
    delta = new_angle - prev_angle
    if delta>wrap_threshold:
        angle = new_angle-2*wrap_threshold
    elif delta<-wrap_threshold:
        angle = new_angle+2*wrap_threshold
    else:
        angle = new_angle
    return angle, unwrapCounter

try:
    print("Receiving data (Press Ctrl+C to exit)...")
    while True:
        # Read a line of data from the serial port
        line = ser.readline().decode('utf-8').strip()
        if line:
            # Split the line into individual values
            values = line.split()
            if len(values) == 8:  # Ensure there are exactly 8 values
                heading1, roll1, pitch1, accZ1 = map(float, values[:4]) 
                heading2, roll2, pitch2, accZ2 = map(float, values[4:])

                # if calibrationCounter>0:
                #     # Unwrap the angles only after the first code itteration
                #     pitch1 = unwrap_stream(pitch1, pitch1prev, 90)
                #     heading1 = unwrap_stream(heading1, heading1prev, 180)
                #     pitch2 = unwrap_stream(pitch2, pitch2prev, 90)
                #     heading2 = unwrap_stream(heading2, heading2prev, 180)

                # Print the received values
                print(f"{heading1}, {pitch1}, {heading2}, {pitch2}")

                if calibrationCounter < samples_for_calibration:
                    # Calculate the offset at the beginning
                    rollOffset1 += roll1
                    pitchOffset1 += pitch1
                    headingOffset1 += heading1
                    rollOffset2 += roll2
                    pitchOffset2 += pitch2
                    headingOffset2 += heading2
                    calibrationCounter += 1
                    if calibrationCounter == samples_for_calibration:
                        # Compute the average offset after 100 samples
                        rollOffset1 /= samples_for_calibration
                        pitchOffset1 /= samples_for_calibration
                        headingOffset1 /= samples_for_calibration
                        rollOffset2 /= samples_for_calibration
                        pitchOffset2 /= samples_for_calibration
                        headingOffset2 /= samples_for_calibration
                # else:
                #     # Remove the offset
                #     roll1 -= rollOffset1
                #     pitch1 -= pitchOffset1
                #     heading1 -= headingOffset1
                #     roll2 -= rollOffset2
                #     pitch2 -= pitchOffset2
                #     heading2 -= headingOffset2

                heading1prev = heading1
                roll1prev = roll1 
                pitch1prev = pitch1
                accZ1prev = accZ1
                heading2prev = heading2
                roll2prev = roll2
                pitch2prev = pitch2 
                accZ1prev = accZ2

except KeyboardInterrupt:
    print("\nExiting program.")
finally:
    ser.close()
    print("Serial port closed.")
