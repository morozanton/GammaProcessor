import os

from config import DetectorType


def get_detector_from_filename(filename: str) -> DetectorType | None:
    for dtype in DetectorType:
        if dtype.value in filename:
            return dtype
    print(f"Unable to derive the detector type from {filename}")
    return None


def get_filenames(directory: str, extension: str = None) -> list[str]:
    if extension:
        return [file for file in os.listdir(directory) if file.lower().endswith(extension.lower())]
    return os.listdir(directory)
