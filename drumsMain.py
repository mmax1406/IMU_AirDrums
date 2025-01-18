import serial
import numpy as np
from drumsClass import IMUSensorData
import keyboard  # For keypress detection
import time
import rtmidi

# Set up the serial connection
ser = serial.Serial('COM4', 115200, timeout=0.1)  # Use a short timeout for non-blocking behavior

# Constants
SAMPLES_FOR_CALIBRATION = 1
ANGLE_TOLERANCE_heading = 30  # Degrees tolerance for drum hit
ANGLE_TOLERANCE_pitch = 10  # Degrees tolerance for drum hit
JERK_THRESHOLD = 2 # Threshold for jerk detection (adjust as needed)

# Initialize sensor objects
sensor1 = IMUSensorData(SAMPLES_FOR_CALIBRATION)
sensor2 = IMUSensorData(SAMPLES_FOR_CALIBRATION)

# Log the acc data for use and a time release mechanism
recordJerk = []
last_save_time = 0

# MIDI channel (0-15). Channel 10 is usually reserved for drums in General MIDI.
MIDI_CHANNEL = 9  # MIDI channels are 0-indexed, so 9 = Channel 10

# Initialize MIDI output
midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

# Open the first available port
if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("MyVirtualOutput")

# Function to send MIDI note
def send_midi_note(note, velocity=127, duration=0.2):
    # Send Note On message
    note_on = [0x90 + MIDI_CHANNEL, note, velocity]  # 0x90 = Note On
    midiout.send_message(note_on)

    # Wait for the duration of the note
    time.sleep(duration)

    # Send Note Off message
    note_off = [0x80 + MIDI_CHANNEL, note, 0]  # 0x80 = Note Off
    midiout.send_message(note_off)

# Load drum hit locations from file
try:
    with open("sensor_data.txt", "r") as f:
        lines = f.readlines()

    # Parse sensor 1 and sensor 2 data
    sensor1_data_start = lines.index("Sensor 1 Data:\n") + 1
    sensor2_data_start = lines.index("Sensor 2 Data:\n") + 1

    sensor1_hit_locations = [
        tuple(map(float, line.strip("()\n").split(", ")))
        for line in lines[sensor1_data_start:sensor2_data_start - 1]
        if line.strip()  # Ignore empty lines
    ]
    sensor2_hit_locations = [
        tuple(map(float, line.strip("()\n").split(", ")))
        for line in lines[sensor2_data_start:]
        if line.strip()  # Ignore empty lines
    ]

    print("Drum hit locations loaded.")
except FileNotFoundError:
    print("sensor_data.txt not found. Please ensure the file exists.")
    exit()

def is_within_hit_zone(sensor_heading, sensor_pitch, hit_locations, toleranceHeading, tolerancePitch):
    """
    Check if the current sensor angles are within the hit zone of any drum hit location.
    """
    for hit_heading, hit_pitch, _, drumType in hit_locations:
        if (
            abs(sensor_heading - hit_heading) <= toleranceHeading
            and abs(sensor_pitch - hit_pitch) <= tolerancePitch
        ):
            return drumType
    return 0

try:
    print("Listening for drum hits (Press Ctrl+C to exit)...")
    prev_accZ1 = prev_accZ2 = 0.0  # Previous acceleration values for jerk calculation

    while True:
        # Read a line of data from the serial port
        line = ser.readline().decode('utf-8').strip()
        if line:
            values = line.split()
            if len(values) == 8:  # Ensure there are exactly 8 values
                data = list(map(float, values))
                if not all(value == 0 for value in data):  # Ensure all values are non-zero
                    print('Reciving data')
                    heading1, roll1, pitch1, accZ1 = map(float, values[:4])
                    heading2, roll2, pitch2, accZ2 = map(float, values[4:])

                    # Update raw data
                    sensor1.update_raw_data(heading1, roll1, pitch1, accZ1)
                    sensor2.update_raw_data(heading2, roll2, pitch2, accZ2)

                    # if sensor1.calibration_counter < SAMPLES_FOR_CALIBRATION:
                    #     sensor1.calculate_offset()
                    #     sensor2.calculate_offset()
                    # else:
                    #     sensor1.process_data()
                    #     sensor2.process_data()
                    
                    # print(f"L: H: {sensor1.heading:.3f}, P: {sensor1.pitch:.3f}, "
                    #         f"R: H: {sensor2.heading:.3f}, P: {sensor2.pitch:.3f}")   

                    # Calculate jerk for each sensor
                    jerk1 = abs(accZ1 - prev_accZ1)
                    jerk2 = abs(accZ2 - prev_accZ2)

                    # Chek for hitting
                    hit1 = is_within_hit_zone(sensor1.heading, sensor1.pitch, sensor1_hit_locations, ANGLE_TOLERANCE_heading, ANGLE_TOLERANCE_pitch)
                    hit2 = is_within_hit_zone(sensor2.heading, sensor2.pitch, sensor2_hit_locations, ANGLE_TOLERANCE_heading, ANGLE_TOLERANCE_pitch)
                    
                    # Check if a drum hit occurs for sensor 1
                    if (
                        hit1 > 0 and jerk1 > JERK_THRESHOLD
                    ):
                        send_midi_note(hit1)
                        print("Drum hit detected for sensor 1!, drum " + str(hit1))

                    # Check if a drum hit occurs for sensor 2
                    if (
                        hit2 > 0 and jerk2 > JERK_THRESHOLD
                    ):
                        send_midi_note(hit2)
                        print("Drum hit detected for sensor 2!, drum " + str(hit2) )

                    # # Here i want to test the jerk values for the drum hits later on
                    # print(jerk2)
                    # recordJerk.append(jerk2)
                    # if keyboard.is_pressed('s'):
                    #     current_time = time.time()
                    #     if current_time - last_save_time > 3.0:
                    #         last_save_time = current_time  # Update the last save time
                    #         with open("hitTest.txt", "w") as f:
                    #             f.write("Sensor 1 Data:\n")
                    #             for data in recordJerk:
                    #                 f.write(f"{data}\n")
                    #         print("Data saved to hitTest.txt")

                    # Update previous acceleration values
                    prev_accZ1 = accZ1
                    prev_accZ2 = accZ2

except KeyboardInterrupt:
    print("\nExiting program.")
finally:
    ser.close()
    midiout.close_port()
    del midiout
    print("Serial port closed.")
