import numpy as np

class IMUSensorData:
    def __init__(self, samples_for_calibration, FilterAlpha=0.05):
        self.heading = 0.0
        self.w = 0.0
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        
        self.local_forward = np.array([0, 0, 1])
        self.heading = 0.0
        self.pitch = 0.0
        self.FiltHeading = 0.0
        self.FiltPitch = 0.0
        self.omegaP = 0.0
        self.accP = 0.0
        
        self.offset_heading = 0.0
        self.offset_pitch = 0.0
        
        self.calibration_counter = 0
        self.samples_for_calibration = samples_for_calibration
        self.FilterAlpha = FilterAlpha

    def filterData(self):
        self.FiltHeading = self.FiltHeading*(1-self.FilterAlpha) + self.heading*self.FilterAlpha
        self.FiltPitch = self.FiltPitch*(1-self.FilterAlpha) + self.pitch*self.FilterAlpha

    def adjust_zero_point(self, angle, zero_point):
        relative_angle = (angle - zero_point + 180) % 360 - 180
        return relative_angle

    def update_raw_data(self, w, x, y, z):
        # The angles as recived
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def calculate_offset(self):
        self.calibration_counter += 1
        self.offset_heading = self.offset_heading + (self.heading - self.offset_heading) / self.samples_for_calibration
        self.offset_pitch = self.offset_pitch + (self.pitch - self.offset_pitch) / self.samples_for_calibration

    def apply_offset(self):
        self.heading -= self.offset_heading
        self.pitch -= self.offset_pitch
        
    def quaternion_to_polar(self):
        """
        Convert quaternion orientation to a polar direction vector.
        
        Args:
            qw, qx, qy, qz: Quaternion components.
        
        Returns:
            azimuth: Angle in the X-Y plane (yaw) in degrees.
            elevation: Vertical angle from the X-Y plane (pitch) in degrees.
        """
        qx, qy, qz, qw = self.x, self.y, self.z, self.w
        # Quaternion rotation matrix
        R = np.array([
            [1 - 2*(qy**2 + qz**2), 2*(qx*qy - qw*qz), 2*(qx*qz + qw*qy)],
            [2*(qx*qy + qw*qz), 1 - 2*(qx**2 + qz**2), 2*(qy*qz - qw*qx)],
            [2*(qx*qz - qw*qy), 2*(qy*qz + qw*qx), 1 - 2*(qx**2 + qy**2)]
        ])
        
        # Rotate the forward vector into the global frame
        global_forward = R @ self.local_forward

        # Compute polar coordinates
        x, y, z = global_forward
        azimuth = np.degrees(np.arctan2(y, x))  # Yaw: angle in the X-Y plane
        elevation = np.degrees(np.arcsin(z / np.linalg.norm(global_forward)))  # Pitch: vertical angle

        return azimuth, elevation

    def process_data(self, w, x, y, z):
        # Update Raw data
        self.update_raw_data(w, x, y, z)
        # Get the polar angles and save them
        azimuth, elevation = self.quaternion_to_polar()
        self.heading = azimuth
        self.accP = self.omegaP - (elevation - self.pitch) #Calc accleration of pitch
        self.omegaP = elevation - self.pitch  #Calc rate of pitch
        self.pitch = elevation #Calc pitch       

        # Either calibrate or apply the calibration
        if self.calibration_counter > self.samples_for_calibration:
            self.heading = self.adjust_zero_point(self.heading, self.offset_heading)
            self.pitch = self.adjust_zero_point(self.pitch, self.offset_pitch)
            self.filterData()
        else:
            self.calculate_offset()