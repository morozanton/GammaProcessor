import numpy as np
import os

HEADER_L = 12
FOOTER_L = 15


def get_Spe_files(directory):
    """Get all Shot*.Spe files in the directory"""
    # return [f for f in os.listdir(directory) if
    #         os.path.isfile(os.path.join(directory, f)) and f.startswith("Shot") and f.endswith(".Spe")]
    return [f for f in os.listdir(directory) if
            os.path.isfile(os.path.join(directory, f)) and f.endswith(".Spe")]


def get_all_files(directory):
    """Get all files in a directory"""
    return [f for f in os.listdir(directory)]


def read_counts(path: str) -> (list, list):
    """
    :param path: file to read the counts from
    :return: channels, counts
    """
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        counts = [int(l.strip()) for l in lines[HEADER_L:-FOOTER_L]]
        channels = np.arange(len(counts))
        return channels, counts

    except PermissionError:
        print(f"Could not process {path}. Skipping it...")
        return None
