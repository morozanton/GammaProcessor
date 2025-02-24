import os
from reader import read_counts, get_Spe_files, get_all_files


def make_raw_files(files, in_path, out_path, energy=False) -> None:
    """
    Reads spectra and creates plain text files (data only, no header/footer)
    :param files: a list of files to record
    :param in_path: input folder
    :param out_path: where to save the files
    :param detector: detector name: "Big" or "Small"
    :param energy: convert channel to energy based on detector calibration
    :return: None; saves the new files in out_path
    """
    print(f"\nProcessing files from {files[0]} to {files[-1]} ({len(files)} total)")
    for filename in files:
        path = os.path.join(in_path, filename)


        file_content = read_counts(path)
        if file_content:
            x_data, counts = file_content
            # Output energy instead of channels

            text_data = [f"{str(ch)} {str(co)}\n" for ch, co in zip(x_data, counts)]
            out_filename = filename[:-4] + "_RAW.txt"
            output = os.path.join(out_path, out_filename)
            os.makedirs(out_path, exist_ok=True)
            with open(output, 'w') as out:
                out.writelines(text_data)
            print(f'{out_filename} created successfully.')


def write_area_file(output_path, output_filename, data):
    os.makedirs(output_path, exist_ok=True)
    full_path = os.path.join(output_path, output_filename)
    with open(full_path, "w") as out:
        out.writelines(data)



if __name__ == "__main__":

    # detector_name = input("Which detector? [b/s]: ").strip().lower()
    # match detector_name:
    #     case "b":
    #         detector_name = "Big"
    #     case "s":
    #         detector_name = "Small"
    #     case _:
    #         raise ValueError("Wrong detector name")

    INPUT_DIRECTORY = "D:\Anton\Desktop (D)\Shots_processing\Calibration"
    OUTPUT_DIRECTORY = "D:\Anton\Desktop (D)\Shots_processing\Calibration\RAW"
    # INPUT_DIRECTORY = f"D:\Anton\Desktop (D)\Shots_processing\SUMS\{detector_name}Det"
    # OUTPUT_DIRECTORY = f"D:\Anton\Desktop (D)\Shots_processing\RAW\{detector_name}Det"

    # filenames = ["SumSpectraSmallDetShot_26-000_to_017.Spe"]

    # filenames = get_Spe_files(INPUT_DIRECTORY)

    filenames = get_all_files(INPUT_DIRECTORY)

    make_raw_files(filenames, in_path=INPUT_DIRECTORY, out_path=OUTPUT_DIRECTORY)
