from enum import Enum
import os


class DetectorType(Enum):
    SMALL_DET = "SmallDet"
    BIG_DET = "BigDet"


SUPPORTED_FILE_EXTENSIONS = [".Spe", ".csv", ".json"]

detectors = {
    DetectorType.SMALL_DET: {"bg_path": r"data/SmallDet-Background.Spe",
                             "bg_times": [62366, 62370],
                             "energy_calibration": {"intercept": -0.01681401, "slope": 0.1859788}},
    DetectorType.BIG_DET: {"bg_path": r"data/BigDet-Background.Spe",
                           "bg_times": [62372, 62375],
                           "energy_calibration": {"intercept": 0.01901937, "slope": 0.1842347}}
}

spectra_files = {
    "footer_start": "$ROI",
    "header_end": "$DATA",
    # After this "header_end" line in .Spe files, there is one more extra line.
    # Don't forget to include this next line in the header
    "time_line": 9
}

save_root_path = r"./output"
processed_path = os.path.join(save_root_path, "processed")

save_paths = {
    "sums": {
        DetectorType.SMALL_DET: os.path.join(save_root_path, "sums", DetectorType.SMALL_DET.value),
        DetectorType.BIG_DET: os.path.join(save_root_path, "sums", DetectorType.BIG_DET.value)
    },
    "processed": {
        DetectorType.SMALL_DET: {
            "bg_subtracted": os.path.join(processed_path, DetectorType.SMALL_DET.value, "bg_subtracted"),
            "energy_scale": os.path.join(processed_path, DetectorType.SMALL_DET.value, "energy_scale"),
            "counts": os.path.join(processed_path, DetectorType.SMALL_DET.value, "counts"),
            "filtered": os.path.join(processed_path, DetectorType.SMALL_DET.value, "filtered"),
        },
        DetectorType.BIG_DET: {
            "bg_subtracted": os.path.join(processed_path, DetectorType.BIG_DET.value, "bg_subtracted"),
            "energy_scale": os.path.join(processed_path, DetectorType.BIG_DET.value, "energy_scale"),
            "counts": os.path.join(processed_path, DetectorType.BIG_DET.value, "counts"),
            "filtered": os.path.join(processed_path, DetectorType.BIG_DET.value, "filtered"),
        },
    },
}

logo = r"""  /\  /\/ _ \/ _ \___                         
 / /_/ / /_)/ /_\/ _ \                        
/ __  / ___/ /_\\  __/                        
\/ /_/\/   \____/\___|                        
                                              
                                              
 _ __  _ __ ___   ___ ___  ___ ___  ___  _ __ 
| '_ \| '__/ _ \ / __/ _ \/ __/ __|/ _ \| '__|
| |_) | | | (_) | (_|  __/\__ \__ \ (_) | |   
| .__/|_|  \___/ \___\___||___/___/\___/|_|   
|_| """
