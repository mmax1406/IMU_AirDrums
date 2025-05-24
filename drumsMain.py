import serial
import numpy as np
from drumsClass import IMUSensorData
import keyboard  # For keypress detection
import time
import rtmidi
import os

# Set up the serial connection
ser = serial.Serial('COM5', 115200, timeout=0.05)  # Use a short timeout for non-blocking behavior

# Constants
SAMPLES_FOR_CALIBRATION = 100
HIT_THRESHOLD = -8 # Threshold for pitch rate detection (adjust as needed)
last_save_time1 = 0 # For a time debounce mechanism
last_save_time2 = 0 # For a time debounce mechanism
debounceTime = 0.1 # Time delay one theres no hit detection
hystersisAngle = 40

# For data logging
NumOfSamplesRecord = 1000
countRecord = 0
MaDataSensor1 = []
MaDataSensor2 = []
printFlag = False
windowSize = 5
hit1 = 0
hit2 = 0

# Initialize sensor objects
sensor1 = IMUSensorData(SAMPLES_FOR_CALIBRATION, windowSize)
sensor2 = IMUSensorData(SAMPLES_FOR_CALIBRATION, windowSize)

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

def save_data():
    """Handles saving the recorded data after user input."""
    folder = "records"
    os.makedirs(folder, exist_ok=True)  # Create the folder if it doesn't exist

    filename = input("Enter a filename (without extension): ")
    filepath1 = os.path.join(folder, f"{filename}_sensor1.txt")
    filepath2 = os.path.join(folder, f"{filename}_sensor2.txt")

    with open(filepath1, "w") as f:
        for data in MaDataSensor1:
            f.write(",".join(map(str, data)) + "\n")

    with open(filepath2, "w") as f:
        for data in MaDataSensor2:
            f.write(",".join(map(str, data)) + "\n")

    print(f"Data saved in {folder} as {filename}_sensor1.txt and {filename}_sensor2.txt")

def send_midi_notes(notes, velocity=127, duration=0.05):
    # Function to send MIDI note
    for note in notes:
        if note>0:
            # Send Note On message
            note_on = [0x90 + MIDI_CHANNEL, note, velocity]  # 0x90 = Note On
            midiout.send_message(note_on)

    # Wait for the duration of the note
    time.sleep(duration)

    for note in notes:
        if note>0:
            # Send Note Off message
            note_off = [0x80 + MIDI_CHANNEL, note, 0]  # 0x80 = Note Off
            midiout.send_message(note_off)

def is_within_hit_zone(sensor_heading, sensor_pitch):
    # Basic hystersis idea
    if sensor_pitch>55:
        hystersisAngle = 30
    else:
        hystersisAngle = 40
    # Check if the current sensor angles are within the hit zone of any drum hit location. (Maybe add HYSTERSIS HERE?)
    note = 0
    if sensor_pitch<hystersisAngle:
        if sensor_heading<-25:
            note = 41
        elif sensor_heading>-25 and sensor_heading<25:
            note = 38
        elif sensor_heading > 25:
            note = 42    
    else:
        if sensor_heading<0:
            note = 51
        elif sensor_heading>0:
            note = 49

    return note

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
                    w1, x1, y1, z1, Calib1 = map(float, values[:5])
                    w2, x2, y2, z2, Calib2 = map(float, values[5:])

                    # Flag according to sensor's dara sheet that check whether its ok
                    if Calib1 == 0:
                        print('Sensor 1 No good')
                    if Calib2 == 0:
                        print('Sensor 2 No good')

                    # Deccide if an air drum was hit
                    if Calib1>0:
                        sensor1.process_data(w1, x1, y1, z1)                    
                        # Check if a drum hit occurs for sensor 1
                        if (sensor1.accP <= HIT_THRESHOLD and (time.time()-last_save_time1)>debounceTime):
                            hit1 = is_within_hit_zone(sensor1.heading, sensor1.pitch)
                            last_save_time1 = time.time()
                        else:
                            hit1 = 0    
                    if Calib2>0:
                        sensor2.process_data(w2, x2, y2, z2)
                        # Chek for hitting
                        hit2 = is_within_hit_zone(sensor2.heading, sensor2.pitch)
                        # Check if a drum hit occurs for sensor 2 
                        if (sensor2.accP <= HIT_THRESHOLD and (time.time()-last_save_time2)>debounceTime):
                            hit2 = is_within_hit_zone(sensor2.heading, sensor2.pitch)
                            last_save_time2 = time.time()
                        else:
                            hit2 = 0

                    # If at least one drum was hit than send the MIDI signal
                    if hit1 != 0 or hit2 != 0:
                        send_midi_notes([hit1, hit2])

                    # Print the angles for fun
                    print(f"L: H: {sensor1.heading:.3f}, P: {sensor1.pitch:.3f}, "
                            f"R: H: {sensor2.heading:.3f}, P: {sensor2.pitch:.3f}") 

                    # Some keyboard options for user
                    if keyboard.is_pressed('c'): # Calibrate them drums upon keboard press (I think i have mistake in the Average calculator)
                        sensor1.calibration_counter = 0.0
                        sensor2.calibration_counter = 0.0
                        
                    if keyboard.is_pressed('r') or printFlag: # Calibrate them drums upon keboard press
                        if printFlag == False:
                            print('Recording start')
                        if countRecord<NumOfSamplesRecord:
                            MaDataSensor1.append((hit1, w1, x1, y1, z1, Calib1, sensor1.heading, sensor1.pitch, sensor1.omegaP, sensor1.accP, time.time()))
                            MaDataSensor2.append((hit2, w2, x2, y2, z2, Calib2, sensor2.heading, sensor2.pitch, sensor1.omegaP, sensor1.accP, time.time()))
                            printFlag = True
                        else:
                            print("Recording finished. Enter filename to save.")
                            save_data()
                            printFlag = False  # Stop recording
                            countRecord = 0  # Reset counter
                            MaDataSensor1.clear()  # Clear previous data
                            MaDataSensor2.clear()
                        countRecord += 1

except KeyboardInterrupt:
    print("\nExiting program.")
finally:
    ser.close()
    midiout.close_port()
    del midiout
    print("Serial port closed.")
