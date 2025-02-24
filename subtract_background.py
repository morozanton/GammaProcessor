import os
from reader import read_counts, get_Spe_files

# INPUT_PATH = "D:\Anton\Desktop (D)\Shots_processing\SUMS\SmallDet\SumSpectraSmallDetShot_21-000_to_174.Spe"
INPUT_PATH = "D:\Anton\Desktop (D)\Shots_processing\Calibration"


def extract_counts_time(path) -> (list, list, int):
    """
    :param path:
    :return: channels, counts, time
    """
    with open(path, 'r') as f:
        lines = f.readlines()

    file_counts = [int(line.strip()) for line in lines[HEADER_L:-FOOTER_L]]
    file_channels = [i for i in range(len(file_counts))]
    file_time = int(lines[9].split()[0])
    return file_channels, file_counts, file_time


def check_detector(filename: str) -> (str, str, str):
    while True:
        if "bigdet" in filename.lower():
            print("Big Detector data")
            bg_path = big_bg_path
            bg_time = b_bg_time
            OUTPUT_PATH = "D:\Anton\Desktop (D)\Shots_processing\BG_SUBTRACTED\BigDet"
            break
        elif "smalldet" in filename.lower():
            print("Small Detector data")
            bg_path = sm_bg_path
            bg_time = sm_bg_time
            OUTPUT_PATH = "D:\Anton\Desktop (D)\Shots_processing\BG_SUBTRACTED\SmallDet"
            break
        else:
            print("Could not figure out the detector.")
            response = input("Which detector? [b/s]: ").strip().lower()
            if response == "b":
                filename = "bigdet"
            elif response == "s":
                filename = "smalldet"
    return bg_path, bg_time, OUTPUT_PATH


HEADER_L = 12
FOOTER_L = 15

sm_bg_path = "D:\Anton\Desktop (D)\Shots_processing\SmallDet-Background.Spe"
big_bg_path = "D:\Anton\Desktop (D)\Shots_processing\BigDet-Background.Spe"

sm_bg_time = 62366
b_bg_time = 62372

files = get_Spe_files(INPUT_PATH)
for file in files:
    print(f"File: {file} ", end="")
    bg_path, bg_time, OUTPUT_PATH = check_detector(file)
    # detector = input("Which detector? [b/s]: ").strip().lower()
    # if detector == "b":
    #     bg_path = big_bg_path
    #     bg_time = b_bg_time
    #     OUTPUT_PATH = "D:\Anton\Desktop (D)\Shots_processing\BG_SUBTRACTED\BigDet"
    # elif detector == "s":
    #     bg_path = sm_bg_path
    #     bg_time = sm_bg_time
    #     OUTPUT_PATH = "D:\Anton\Desktop (D)\Shots_processing\BG_SUBTRACTED\SmallDet"
    # else:
    #     raise ValueError("Wrong input")

    bg_chan, bg_counts = read_counts(bg_path)
    spectrum_chan, spectrum_counts, spectrum_time = extract_counts_time(os.path.join(INPUT_PATH, file))

    time_scale = spectrum_time / bg_time

    counts_without_background = [max(0, (spec - bg * time_scale)) for spec, bg in zip(spectrum_counts, bg_counts)]

    # out_filename = INPUT_PATH.split("\\")[-1][:-4] + "_BG_SUBTRACTED.txt"
    out_filename = file + "_BG_SUBTRACTED.txt"
    out_path = os.path.join(OUTPUT_PATH, out_filename)

    with open(out_path, 'w') as out:
        out.writelines([f"{chan}\t{cnt}\n" for chan, cnt in zip(spectrum_chan, counts_without_background)])
    print(f"File saved: {out_path}")
