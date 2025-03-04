import os
from config import DetectorType
import numpy as np


def get_sigma(count):
    """Returns the standard deviation for a given count.
    As gamma peaks follow Poisson's distribution, the standard deviation is sqrt(n)"""
    return np.sqrt(count)


def get_detector_from_filename(filename: str) -> DetectorType | None:
    for dtype in DetectorType:
        if dtype.value in filename:
            return dtype
    print(f"\nUnable to derive the detector type from {filename}!")
    prompt = input("Specify manually [b/s] ---> ").strip().lower()
    if prompt == "b":
        return DetectorType.BIG_DET
    elif prompt == "s":
        return DetectorType.SMALL_DET
    else:
        raise ValueError("Unknown detector type")


def get_filenames(directory: str, *extension: str) -> list[str]:
    if extension:
        files = []
        for file in os.listdir(directory):
            if os.path.splitext(os.path.basename(file))[1].lower() in [ext.lower() for ext in extension]:
                files.append(file)
        return files
    return os.listdir(directory)
