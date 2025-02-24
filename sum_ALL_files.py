from reader import get_all_files
import os

INPUT_DIRECTORY = "D:\Anton\Desktop (D)\Shots_processing\SUMS"
OUTPUT_DIRECTORY = INPUT_DIRECTORY

FILE_LEN = 8220
HEADER_LEN = 12
FOOTER_LEN = 15

files = get_all_files(INPUT_DIRECTORY)

sum_counts = [0] * (FILE_LEN - FOOTER_LEN - HEADER_LEN)
sum_times = [0, 0]

for n, f in enumerate(files):
    file_path = os.path.join(INPUT_DIRECTORY, f)
    with open(file_path) as file:
        lines = file.readlines()
    if n == 0:
        header = lines[:HEADER_LEN]
        footer = lines[-FOOTER_LEN:]
    file_counts = [int(l.strip()) for l in lines[HEADER_LEN:-FOOTER_LEN]]

    file_times = [int(time) for time in lines[9].split()]

    sum_counts = [sum(count) for count in zip(sum_counts, file_counts)]
    sum_times = [sum(time) for time in zip(sum_times, file_times)]

header[9] = f'{sum_times[0]} {sum_times[1]}\n'

output_filename = "Sum_all.Spe"
out = os.path.join(OUTPUT_DIRECTORY, output_filename)

with open(out, 'w') as output:
    output.writelines(header)
    output.writelines(["{:8d}\n".format(l) for l in sum_counts])
    output.writelines(footer)

print(f"Results written to '{out}'")
