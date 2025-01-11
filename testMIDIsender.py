import rtmidi
import keyboard
import time

# MIDI note mapping
MIDI_NOTES = {
    "a": 42,  # Hi-hat
    "b": 38,  # Snare drum
    "c": 49,  # Cymbal
}

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

# Main function to listen for keypresses
def main():
    print("Press 'a' for hi-hat, 'b' for snare, 'c' for cymbal. Press 'q' to quit.")

    # Track which keys are currently being pressed
    active_keys = set()

    try:
        while True:
            for key, note in MIDI_NOTES.items():
                if keyboard.is_pressed(key) and key not in active_keys:
                    print(f"{key.upper()} pressed! Sending MIDI note {note}.")
                    send_midi_note(note)
                    active_keys.add(key)

                # Remove the key from active_keys when it's released
                if not keyboard.is_pressed(key) and key in active_keys:
                    active_keys.remove(key)

            if keyboard.is_pressed("q"):
                print("Quitting...")
                break
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        # Close the MIDI connection
        midiout.close_port()
        del midiout

if __name__ == "__main__":
    main()
