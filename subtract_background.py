import os
import pandas as pd
from reader import read_counts, get_Spe_files

# INPUT_PATH = input("Input path: ")
INPUT_PATH = r"D:\Anton\Desktop (D)\Shots_processing\Calibration"

HEADER_L = 12
FOOTER_L = 15

SM_BG_PATH = r"D:\Anton\Desktop (D)\Shots_processing\SmallDet-Background.Spe"
BIG_BG_PATH = r"D:\Anton\Desktop (D)\Shots_processing\BigDet-Background.Spe"

sm_bg_time = 62366
b_bg_time = 62372


def extract_counts_time(path) -> tuple[list, list, int]:
    with open(path, 'r') as f:
        lines = f.readlines()
    if len(lines) < max(HEADER_L, 10):  # Проверка на минимальное количество строк
        raise ValueError(f"Input file is too short or damaged")

    file_counts = [int(line.strip()) for line in lines[HEADER_L:-FOOTER_L]]
    file_channels = list(range(len(file_counts)))
    file_time = int(lines[9].split()[0])

    return file_channels, file_counts, file_time


def check_detector(filename: str) -> tuple[str, int, str]:
    filename_lower = filename.lower()

    if "bigdet" in filename_lower:
        print("Big Detector data")
        return BIG_BG_PATH, b_bg_time, r"D:\Anton\Desktop (D)\Shots_processing\BG_SUBTRACTED\BigDet"
    elif "smalldet" in filename_lower:
        print("Small Detector data")
        return SM_BG_PATH, sm_bg_time, r"D:\Anton\Desktop (D)\Shots_processing\BG_SUBTRACTED\SmallDet"
    else:
        response = input(f"{filename}: Could not determine the detector type automatically. "
                         f"\nWhich detector? [b/s]: ").strip().lower()
        if response == "b":
            return BIG_BG_PATH, b_bg_time, r"D:\Anton\Desktop (D)\Shots_processing\BG_SUBTRACTED\BigDet"
        elif response == "s":
            return SM_BG_PATH, sm_bg_time, r"D:\Anton\Desktop (D)\Shots_processing\BG_SUBTRACTED\SmallDet"


files = get_Spe_files(INPUT_PATH)
for file in files:
    print(f"Processing file: {file}")

    bg_path, bg_time, output_path = check_detector(file)
    bg_chan, bg_counts = read_counts(bg_path)
    spectrum_chan, spectrum_counts, spectrum_time = extract_counts_time(os.path.join(INPUT_PATH, file))

    time_scale = spectrum_time / bg_time
    counts_without_background = [max(0, (spec - bg * time_scale)) for spec, bg in zip(spectrum_counts, bg_counts)]

    df = pd.DataFrame({"Channel": spectrum_chan, "Counts": counts_without_background})

    os.makedirs(OUTPUT_PATH, exist_ok=True)
    out_filename = f"{file}_BG_SUBTRACTED.csv"
    out_path = os.path.join(OUTPUT_PATH, out_filename)

    df.to_csv(out_path, index=False)
    print(f"File saved: {out_path}")
