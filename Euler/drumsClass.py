import math 

class IMUSensorData:
    def __init__(self, samples_for_calibration):
        self.heading = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.omegaP = 0.0
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

    def adjust_zero_point(self, angle, zero_point):
        # Adjust angle to make it relative to the given zero point.
        relative_angle = angle - zero_point
        # Handle wrapping to keep angles in the range of -180 to 180
        if relative_angle > 180:
            relative_angle -= 360
        elif relative_angle < -180:
            relative_angle += 360
        return relative_angle

    def update_raw_data(self, heading, roll, pitch, omegaP):
        # The angles as recived
        self.heading = heading
        self.roll = roll
        self.pitch = pitch
        self.omegaP = omegaP

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

    def process_data(self):
        if self.calibration_counter >= self.samples_for_calibration:
            # self.apply_offset()
            self.heading = self.adjust_zero_point(self.heading, self.offset_heading)
            self.roll = self.adjust_zero_point(self.roll, self.offset_roll)
            self.pitch = self.adjust_zero_point(self.pitch, self.offset_pitch)