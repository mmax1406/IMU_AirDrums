import serial
import numpy as np
from drumsClass import IMUSensorData
import keyboard  # For keypress detection
import time
import rtmidi

# Set up the serial connection
ser = serial.Serial('COM3', 115200, timeout=0.05)  # Use a short timeout for non-blocking behavior

# Constants
SAMPLES_FOR_CALIBRATION = 100
HIT_THRESHOLD = -8 # Threshold for pitch rate detection (adjust as needed)
last_save_time1 = 0 # For a time debounce mechanism
last_save_time2 = 0 # For a time debounce mechanism
debounceTime = 0.1 # Time delay one theres no hit detection

# For data logging
NumOfSamplesRecord = 3000
countRecord = 0
MaDataSensor1 = []
MaDataSensor2 = []
printCounter = False

# Initialize sensor objects
sensor1 = IMUSensorData(SAMPLES_FOR_CALIBRATION)
sensor2 = IMUSensorData(SAMPLES_FOR_CALIBRATION)

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

def send_midi_note(note, velocity=127, duration=0.05):
    # Function to send MIDI note
    # Send Note On message
    note_on = [0x90 + MIDI_CHANNEL, note, velocity]  # 0x90 = Note On
    midiout.send_message(note_on)

    # Wait for the duration of the note
    time.sleep(duration)

    # Send Note Off message
    note_off = [0x80 + MIDI_CHANNEL, note, 0]  # 0x80 = Note Off
    midiout.send_message(note_off)

def is_within_hit_zone(sensor_heading, sensor_pitch):
    # Check if the current sensor angles are within the hit zone of any drum hit location.
    note = 0
    if sensor_heading<0 and sensor_pitch>45:
        note = 51
    elif sensor_heading>0 and sensor_pitch>45:
        note = 49
    elif sensor_heading<-25:
        note = 41
    elif sensor_heading>-25 and sensor_heading<25:
        note = 38
    elif sensor_heading > 25:
        note = 42
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

                    # Process sensor 1
                    if Calib1 == 0:
                        print('Sensor 1 No good')
 
                    if Calib2 == 0:
                        print('Sensor 2 No good')

                    if Calib1>0:
                        sensor1.process_data(w1, x1, y1, z1)
                        # Chek for hitting
                        hit1 = is_within_hit_zone(sensor1.heading, sensor1.pitch)
                        # Check if a drum hit occurs for sensor 1 and send MIDI if so 
                        if (
                            hit1 > 0 and sensor1.omegaP <= HIT_THRESHOLD and (time.time()-last_save_time1)>debounceTime
                        ):
                            send_midi_note(hit1)
                            last_save_time1 = time.time()

                    if Calib2>0:
                        sensor2.process_data(w2, x2, y2, z2)
                        # Chek for hitting
                        hit2 = is_within_hit_zone(sensor2.heading, sensor2.pitch)
                        # Check if a drum hit occurs for sensor 2 and send MIDI if so 
                        if (
                            hit2 > 0 and sensor2.omegaP <= HIT_THRESHOLD and (time.time()-last_save_time2)>debounceTime
                        ):
                            send_midi_note(hit2)
                            last_save_time2 = time.time()


                    print(f"L: H: {sensor1.heading:.3f}, P: {sensor1.pitch:.3f}, "
                            f"R: H: {sensor2.heading:.3f}, P: {sensor2.pitch:.3f}") 

                    if keyboard.is_pressed('c'): # Calibrate them drums upon keboard press
                        sensor1.calibration_counter = 0.0
                        sensor2.calibration_counter = 0.0
                        
                    if keyboard.is_pressed('r') or printCounter: # Calibrate them drums upon keboard press
                        if countRecord<NumOfSamplesRecord:
                            MaDataSensor1.append((w1, x1, y1, z1, Calib1, sensor1.heading, sensor1.pitch, time.time()))
                            MaDataSensor2.append((w1, x1, y1, z1, Calib1, sensor1.heading, sensor1.pitch, time.time()))
                            printCounter = True
                        else:
                            with open("sensor_data1.txt", "w") as f:
                                f.write("Sensor 1 Data:\n")
                                for data in MaDataSensor1:
                                    f.write(",".join(map(str, data)) + "\n")
                            # with open("sensor_data2.txt", "w") as f:
                            #     for data in MaDataSensor2:
                            #         f.write(",".join(map(str, data)) + "\n")
                            print("Data saved to sensor_data.txt")
                            printCounter = False
                            break
                        countRecord += 1

except KeyboardInterrupt:
    print("\nExiting program.")
finally:
    ser.close()
    midiout.close_port()
    del midiout
    print("Serial port closed.")
