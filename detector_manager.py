from config import DetectorType
import config


class Detector:

    def __init__(self, detector_type: DetectorType):
        self.type = detector_type
        self.bg_path = config.detectors[self.type]["bg_path"]
        self.bg_times = config.detectors[self.type]["bg_times"]

    # TODO: add calibration handling
