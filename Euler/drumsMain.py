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
HIT_THRESHOLD = -3 # Threshold for jerk detection (adjust as needed)

# Initialize sensor objects
sensor1 = IMUSensorData(SAMPLES_FOR_CALIBRATION)
sensor2 = IMUSensorData(SAMPLES_FOR_CALIBRATION)

# Time debounce mechanism
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

def send_midi_note(note, velocity=127, duration=0.2):
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
    if sensor_heading<-45:
        note = 42
    elif sensor_heading>-45 and sensor_heading<45:
        note = 38
    elif sensor_heading > 45:
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
            if len(values) == 8:  # Ensure there are exactly 8 values
                data = list(map(float, values))
                if not all(value == 0 for value in data):  # Ensure all values are non-zero
                    print('Reciving data')
                    heading1, roll1, pitch1, omegaP1 = map(float, values[:4])
                    heading2, roll2, pitch2, omegaP2 = map(float, values[4:])

                    # Update raw data
                    sensor1.update_raw_data(heading1, roll1, pitch1, omegaP1)
                    sensor2.update_raw_data(heading2, roll2, pitch2, omegaP2)

                    if sensor1.calibration_counter < SAMPLES_FOR_CALIBRATION:
                        sensor1.calculate_offset()
                        sensor2.calculate_offset()
                    else:
                        sensor1.process_data()
                        sensor2.process_data()
                    
                    print(f"L: H: {sensor1.heading:.3f}, P: {sensor1.pitch:.3f}, "
                            f"R: H: {sensor2.heading:.3f}, P: {sensor2.pitch:.3f}")   

                    # Chek for hitting
                    hit1 = is_within_hit_zone(sensor1.heading, sensor1.pitch)
                    hit2 = is_within_hit_zone(sensor2.heading, sensor2.pitch)
                    
                    # Check if a drum hit occurs for sensor 1
                    if (
                        hit1 > 0 and omegaP1 < HIT_THRESHOLD
                    ):
                        send_midi_note(hit1)
                        print("Drum hit detected for sensor 1!, drum " + str(hit1))

                    # Check if a drum hit occurs for sensor 2
                    if (
                        hit2 > 0 and omegaP2 < HIT_THRESHOLD
                    ):
                        send_midi_note(hit2)
                        print("Drum hit detected for sensor 2!, drum " + str(hit2) )

except KeyboardInterrupt:
    print("\nExiting program.")
finally:
    ser.close()
    midiout.close_port()
    del midiout
    print("Serial port closed.")
