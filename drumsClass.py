import math 

class IMUSensorData:
    def __init__(self, samples_for_calibration):
        self.heading = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.accZ = 0.0
        self.prev_heading = 0.0
        self.prev_pitch = 0.0
        self.prev_roll = 0.0
        self.offset_heading = 0.0
        self.offset_pitch = 0.0
        self.offset_roll = 0.0
        self.calibration_counter = 0
        self.samples_for_calibration = samples_for_calibration
        self.unwrap_heading_counter = 0
        self.unwrap_pitch_counter = 0

    def update_raw_data(self, heading, roll, pitch, accZ):
        # # All angler should be [-180 180]
        # self.heading = math.degrees(math.atan2(math.sin(math.radians(heading)),math.cos(math.radians(heading))))
        # self.roll = math.degrees(math.atan2(math.sin(math.radians(roll)),math.cos(math.radians(roll))))
        # self.pitch = math.degrees(math.atan2(math.sin(math.radians(pitch)),math.cos(math.radians(pitch))))
        # All angler should be [-180 180]
        self.heading = heading
        self.roll = roll
        self.pitch = pitch
        self.accZ = accZ

    def calculate_offset(self):
        self.offset_heading += self.heading
        self.offset_pitch += self.pitch
        self.offset_roll += self.roll
        self.calibration_counter += 1
        if self.calibration_counter == self.samples_for_calibration:
            self.offset_heading /= self.samples_for_calibration
            self.offset_pitch /= self.samples_for_calibration
            self.offset_roll /= self.samples_for_calibration

    def apply_offset(self):
        self.heading -= self.offset_heading
        self.pitch -= self.offset_pitch
        self.roll -= self.offset_roll

    def unwrap_angle(self, new_angle, prev_angle, wrap_threshold, unwrap_counter):
        delta = new_angle - prev_angle
        if delta > wrap_threshold:
            unwrap_counter -= 1
        elif delta < -wrap_threshold:
            unwrap_counter += 1
        unwrapped_angle = new_angle + (unwrap_counter * 2 * wrap_threshold)
        return unwrapped_angle, unwrap_counter

    def process_data(self):
        # if self.calibration_counter >= self.samples_for_calibration:
        #     # self.apply_offset()

        #     # We want to record the last wraped angle to the previous angle later on
        #     tmpPitch = self.pitch
        #     tmpHeading = self.heading
        #     tmpRoll = self.roll

        #     # # Unwrap angles
        #     # self.pitch, self.unwrap_pitch_counter = self.unwrap_angle(
        #     #     self.pitch, self.prev_pitch, 180, self.unwrap_pitch_counter
        #     # )
        #     # self.heading, self.unwrap_heading_counter = self.unwrap_angle(
        #     #     self.heading, self.prev_heading, 180, self.unwrap_heading_counter
        #     # )

        # # Update previous values
        # self.prev_heading = tmpHeading
        # self.prev_pitch = tmpPitch
        # self.prev_roll = tmpRoll
        
        self.prev_heading = 0
        self.prev_pitch = 0
        self.prev_roll = 0