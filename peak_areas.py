import os

import matplotlib.pyplot as plt

from reader import read_counts, get_Spe_files
from file_processing import write_area_file
from scipy.optimize import curve_fit
import numpy as np

TIME_STEP = 300  # Time per one measurement file in seconds


def gauss(x, a, x0, sigma):
    return a * np.exp(-((x - x0) / sigma) ** 2)


def gauss_fit(path, channel_start, channel_end):
    """
    :param channel_end:
    :param channel_start:
    :param path:
    :return: amplitude, center, width
    """
    x, y = get_peak_data(path, channel_start, channel_end)

    # Initial gauss parameters: amplitude, center, fwhm?
    p0 = [max(y), np.mean(x), (channel_end - channel_start) / 4]
    try:
        return curve_fit(f=gauss, xdata=x, ydata=y, p0=p0)[0]
    except RuntimeError:
        print(f"Unable to fit file {path}\nSkipping to next")
        return None, None, None


def get_peak(data, l_chan, r_chan, params):
    x_range = np.arange(l_chan, r_chan)
    average = (data[r_chan] + data[l_chan]) / 2
    peak_y = [max(gauss(x, *params), average) for x in x_range]

    return x_range, peak_y


def get_peak_data(path, channel_start, channel_end) -> (list, list):
    channels, counts = read_counts(path)
    return channels[channel_start:channel_end + 1], counts[channel_start:channel_end + 1]


def sum_peaks_rough(path, channel_start, channel_end):
    """
    Sun counts over the peak for all files in directory
    :param path:
    :param channel_start:
    :param channel_end:
    :return:
    """
    if channel_start >= channel_end:
        raise ValueError("channel_start should be LESS than channel_end")

    peak_sums = []
    for f in get_Spe_files(path):
        file_path = os.path.join(path, f)
        f_counts = get_peak_data(file_path, channel_start, channel_end)
        peak_sums.append(sum(f_counts))

    print("TIME\tSUM")
    print("-" * 15)
    for i, s in enumerate(peak_sums):
        print(f"{TIME_STEP * (i + 1)} \t{s}")


def get_gauss_areas(path, channel_start, channel_end) -> (list, list):
    areas = []
    times = []
    for i, f in enumerate(get_Spe_files(path)):
        file_path = os.path.join(path, f)
        a, x0, sigma = gauss_fit(file_path, channel_start, channel_end)
        if a and x0 and sigma:
            area = a * sigma * np.sqrt(np.pi)
        else:
            area = None
        if area:
            areas.append(area)
            times.append((i + 1) * TIME_STEP)

    return times, areas


if __name__ == "__main__":
    CHANNEL_START = 2700
    CHANNEL_END = 2790
    OUTPUT_DIRECTORY = "D:\Anton\Desktop (D)\Shots_processing\AREAS_FITTED"
    directory = "D:\Anton\Desktop (D)\Shots\Small_Det\SmallDet_Shot_14\Messungen"

    out_filename = directory.split("\\")[-2] + f"_areas_channel{CHANNEL_START}to{CHANNEL_END}.txt"

    times, areas = get_gauss_areas(directory, CHANNEL_START, CHANNEL_END)

    THRESHOLD = 50
    # ---------------data cleaning-----------------------
    clean_areas = []
    clean_times = []
    for i in range(1, len(areas) - 1):
        if areas[i - 1] - areas[i] < THRESHOLD and areas[i] - areas[i + 1] < THRESHOLD:
            clean_areas.append(areas[i])
            clean_times.append(times[i])
    times = clean_times
    areas = clean_areas

    data_to_write = [f"{t}\t{a}\n" for t, a in zip(times, areas)]

    write_area_file(OUTPUT_DIRECTORY, out_filename, data_to_write)
    print("\nDone.")

    plt.scatter(times, areas, label="Input Data", color="red")
    plt.xlabel("Time (sec)")
    plt.ylabel("Area")
    plt.yscale("log")
    plt.legend()
    plt.show()
