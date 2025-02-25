from config import DetectorType
import config


class Detector:

    def __init__(self, detector_type: DetectorType):
        self.CHANNELS = 8191
        self.type = detector_type
        self.name = self.type.value
        self.bg_path = config.detectors[self.type]["bg_path"]
        self.bg_times = config.detectors[self.type]["bg_times"]
        self.intercept = config.detectors[self.type]["energy_calibration"]["intercept"]
        self.slope = config.detectors[self.type]["energy_calibration"]["slope"]
        self.energy_scale = [self.intercept + self.slope * channel for channel in range(self.CHANNELS)]

