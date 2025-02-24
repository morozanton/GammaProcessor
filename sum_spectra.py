import os
import sys
import argparse
import re

"""
Usage:
python sum_range.py "input_path" --output "output_path" --start "start_range" --end "end_range"
--output "output_path": Where to save the summed spectrum
--start "start_range": Starting spectrum
--end "end_range": End spectrum
"""


def parse_file(path: str) -> (list, list):
    with open(path, 'r') as file:
        lines = file.readlines()
    counts = [int(line.strip()) for line in lines[HEADER_LEN:FILE_LEN - FOOTER_LEN]]
    times = [int(time) for time in lines[9].split()]
    return counts, times


parser = argparse.ArgumentParser()
parser.add_argument("input_path", type=str, help="Path to the folder with files to sum")
parser.add_argument("--output", type=str, help="Path to the folder to save the result")
parser.add_argument("--start", type=int, help="Start index of files")
parser.add_argument("--end", type=int, help="End index of files")
parser.add_argument("--a", type=bool, default=False, help="Sum all .Spe files in the directory")

args = parser.parse_args()
folder_path = args.input_path

files = [f for f in os.listdir(folder_path) if
         os.path.isfile(os.path.join(folder_path, f)) and f.startswith("Shot") and f.endswith(".Spe")]
detector_name = re.search(r"BigDet|SmallDet", folder_path).group(0)

full_range = [int(f.split()[-1][:-4]) for f in files]
if len(full_range) < 2:
    raise ValueError("Wrong input directory or wrong input filename")

start_range = args.start if args.start else full_range[0]
end_range = args.end if args.end else full_range[-1]

SHOT_NAME = files[0].split()[0]

if args.a:
    output_ending = f"SUM_Shots{1}"
else:
    output_ending = f"\SumSpectra{detector_name}{SHOT_NAME}-{start_range:03d}_to_{end_range:03d}.Spe"

output_file = args.output + output_ending if args.output else args.input_path + output_ending

FILE_LEN = 8220
HEADER_LEN = 12
FOOTER_LEN = 17

lines_to_sum = FILE_LEN - HEADER_LEN - FOOTER_LEN
first_file = True

if os.path.exists(folder_path):
    sum_counts = [0] * (FILE_LEN - FOOTER_LEN - HEADER_LEN)
    sum_times = [0, 0]

    file_range = files if args.a else range(start_range, end_range + 1)

    for n, i in enumerate(file_range):
        file_name = i if args.a else f'{SHOT_NAME} {i:03d}.Spe'
        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path):
            if n == 0:
                with open(file_path) as f:
                    lines = f.readlines()
                header = lines[:HEADER_LEN]
                footer = lines[-FOOTER_LEN + 2:]
            file_counts, file_times = parse_file(file_path)
            sum_counts = [sum(count) for count in zip(sum_counts, file_counts)]
            sum_times = [sum(time) for time in zip(sum_times, file_times)]
        else:
            print(f"File '{file_name}' not found.")

    if any(sum_counts):
        header[9] = f'{sum_times[0]} {sum_times[1]}\n'
        if args.output:
            os.makedirs(args.output, exist_ok=True)

        with open(output_file, 'w') as output:
            output.writelines(header)
            output.writelines(["{:8d}\n".format(l) for l in sum_counts])
            output.writelines(footer)

        print(f"Results written to '{output_file}'")
    else:
        print("No '.SPE' files found in the specified range.")
else:
    print(f"The folder '{folder_path}' does not exist.")
