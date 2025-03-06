import os
from config import DetectorType
import numpy as np
import re


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


def check_file_extension(path: str, *supported_extensions: str) -> bool:
    return os.path.splitext(os.path.basename(path))[1].lower() in [ext.lower() for ext in supported_extensions]


def get_filenames(directory: str, *extension: str) -> list[str]:
    if extension:
        files = []
        for file in os.listdir(directory):
            if check_file_extension(file, *extension):
                files.append(os.path.join(directory, file))
        return sorted(files, key=lambda x: int(re.search(r"\d+", x).group(0)))
    return os.listdir(directory)
