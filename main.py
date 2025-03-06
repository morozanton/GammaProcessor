from gamma_spectrum import GammaSpectrum, SpectrumProcessor
from misc import get_filenames, check_file_extension
import os
import config
from plotter import Plotter
import re

"""
(!) Edit the config.py file to use correct file paths
"""


def get_files(message: str, path='') -> list:
    ATTEMPTS = 3
    for _ in range(ATTEMPTS):
        if not path:
            input_path = input(message).strip('"')
            if input_path == "s":
                return []
        else:
            input_path = path
        if os.path.isdir(input_path):
            files = get_filenames(input_path, *config.SUPPORTED_FILE_EXTENSIONS)
            if files:
                return files
            else:
                print(f"No supported files found in {input_path}")
        elif os.path.isfile(input_path):
            if check_file_extension(input_path, *config.SUPPORTED_FILE_EXTENSIONS):
                return [input_path]
            else:
                print(f"{input_path}: file format is unsupported")
    raise FileExistsError("Max number of attempts reached")


def sum_spectra(input_spectra: list[GammaSpectrum]) -> list[GammaSpectrum]:
    """
    Sum all .Spe files in a specified directory
    :param input_spectra:
    :return:
    """
    if any(sp.file_extension == ".Spe" for sp in input_spectra):
        valid_spectra = [sp for sp in input_spectra if sp.file_extension == ".Spe"]
        names = [sp.name for sp in valid_spectra]

        print(f"The files from {valid_spectra[0].name} to {valid_spectra[-1].name} will be summed")

        shot_names = {match.group() for name in names if (match := re.search(r"Shot_\d+", name))}
        sorted_names = sorted(shot_names, key=lambda x: int(x.split("_")[1]))
        if len(shot_names) > 1:
            shot_name = "+".join(sorted_names)
        elif len(shot_names) == 1:
            shot_name = sorted_names[0]
        else:
            shot_name = None

        result = processor.sum_spectra(spectra, name_modifier=shot_name)
        out_path = config.save_paths["sums"][result.detector.type]

        print(f"[y] - Save {result.name} to default directory\n"
              f"[n] - Continue without saving\n"
              f"'your_custom_path' - Save to the specified location")
        prompt = input(f"---> ").strip()

        if prompt == "y":
            result.save_spe(os.path.join(out_path, result.name + result.file_extension))
        elif os.path.isdir(prompt):
            result.save_spe(os.path.join(prompt, result.name + result.file_extension))
        else:
            pass
        return [result]
    else:
        print(f"No .Spe files found to sum.")


def subtract_background(input_spectra: list[GammaSpectrum], out_format="json") -> list[GammaSpectrum]:
    if input_spectra:
        processed_spectra = []
        print(f"Background will be subtracted from {len(input_spectra)} files")
        significance_prompt = int(input("Significance level: e.g. '3' for 3sigma significance "
                                        "(0 = preserve all nonzero counts): \n"
                                        "---> ").strip())

        for sp in input_spectra:
            result = processor.subtract_background(spectrum=sp, significance=significance_prompt)
            out_directory = config.save_paths["processed"][result.detector.type]["bg_subtracted"]
            if out_format == "json":
                result.save_json(out_directory)
            elif out_format in ["raw", "csv"]:
                result.save_raw(out_directory)
            processed_spectra.append(result)

        return processed_spectra


def select_output_format() -> str:
    prompt = input("Select the output file format:\n"
                   "[j] = .json\n"
                   "[c] = .csv\n"
                   "---> ").strip().lower()
    if prompt in ["j", "json", ".json"]:
        return "json"
    elif prompt in ["c", "csv", ".csv"]:
        return "csv"
    else:
        raise TypeError("Could not determine the output file format")


def add_energies_remove_headers(input_spectra: list[GammaSpectrum], out_format="json") -> list[GammaSpectrum]:
    if input_spectra:
        processed_spectra = []
        print(f"{len(input_spectra)} files will be processed.")
        use_energy_scale = input("Use energy scale?\n"
                                 "[y] output energy values for channels\n"
                                 "[n] output channel numbers\n"
                                 "---> ").strip().lower()

        for sp in input_spectra:
            if use_energy_scale == "y":
                out_directory = config.save_paths["processed"][sp.detector.type]["energy_scale"]
                suffix = "_energies"
            else:
                out_directory = config.save_paths["processed"][sp.detector.type]["counts"]
                suffix = "_counts"
            if out_format == "json":
                sp.save_json(out_directory=out_directory,
                             filename_suffix=suffix)
            elif out_format in ["raw", "csv"]:
                sp.save_raw(out_directory=out_directory, output_energies=use_energy_scale == "y",
                            filename_suffix=suffix)
            processed_spectra.append(sp)

        return processed_spectra


def filter_spectra(input_spectra: list[GammaSpectrum], out_format="json") -> list[GammaSpectrum]:
    if input_spectra:
        processed_spectra = []

        for sp in input_spectra:
            out_directory = config.save_paths["processed"][sp.detector.type]["filtered"]
            sp.apply_filtering()
            processed_spectra.append(sp)
            if out_format == "json":
                sp.save_json(out_directory=out_directory)
            elif out_format in ["raw", "csv"]:
                sp.save_raw(out_directory=out_directory, output_energies=True)

        return processed_spectra


def convert_format(input_spectra: list[GammaSpectrum], output_format: str, save_path=config.processed_path):
    for sp in input_spectra:
        if output_format == "json":
            sp.save_json(save_path)
        elif output_format == "csv":
            sp.save_raw(save_path, output_energies=sp.energies is not None)
        print(f"{sp.name} saved")
    print(f"All files saved in {save_path}")


print(config.logo)

processor = SpectrumProcessor()
plotter = Plotter()

iteration = 0
while True:
    if iteration == 0:
        print()
        spectra = processor.load_multiple_spectra(get_files(message="Path to a spectrum file/directory: "))

    print(f"\nCurrent files:")
    print("-" * 30)
    for i, spectrum in enumerate(spectra):
        print(f"{i + 1}. {spectrum.name}")
    print("-" * 30)
    print("[1] Bulk processing: sum spectra + subtract background + add energy scale\n"
          "[2] Sum spectra\n"
          "[3] Subtract background\n"
          "[4] Add channels/energies; remove header and footer\n"
          "[5] Apply Gauss signal filtering\n"
          "[6] Plot spectra\n"
          "\n[n] Load NEW spectra\n"
          "[a] Load ADDITIONAL spectra\n"
          "\n[f] Convert the spectrum file format\n"
          "\n[q] Quit")
    command = input("---> ").strip().lower()
    match command:
        case "1":
            add_energies_remove_headers(subtract_background(sum_spectra(spectra)))
            spectra = processor.load_multiple_spectra(
                get_files(message="\nAll files are processed. Load new files to process?"
                                  "\nPath to a spectrum file/directory: "))

        case "2":
            spectra = sum_spectra(spectra)

        case "3":
            out_format = select_output_format()
            spectra = subtract_background(spectra, out_format=out_format)

        case "4":
            out_format = select_output_format()
            spectra = add_energies_remove_headers(spectra, out_format=out_format)

        case "5":
            out_format = select_output_format()
            spectra = filter_spectra(spectra, out_format=out_format)

        case "6":
            plot_background = input("Also plot background? [y/n]: ").strip().lower() == "y"
            plotter.plot_spectrum(*spectra, plot_background=plot_background, background_significance=3)

        case "n":
            spectra = processor.load_multiple_spectra(get_files(message="Path to a spectrum file/directory: "))

        case "a":
            spectra.extend(processor.load_multiple_spectra(get_files(
                message="Path to an additional spectrum file/directory: "
            )))

        case "f":
            out_format = select_output_format()
            convert_format(spectra, out_format)

        case "999":
            # Sum up ALL files for ALL shots from a given detector
            print("Summing all spectra for each of the shots separately")
            det_name = input("Big/Small detector?: ").strip()
            root = rf"D:\Anton\Desktop (D)\Shots\{det_name}_Det"

            dirs = os.listdir(root)

            for direct in dirs:
                direct = os.path.join(root, direct, "Messungen")
                try:
                    spectra = processor.load_multiple_spectra(get_files(message="Path to a spectrum file/directory: "))
                except FileExistsError:
                    continue

                if spectra:
                    valid_spectra = [sp for sp in spectra if sp.file_extension == ".Spe"]
                    print(f"The following files will be summed: ")
                    print(
                        f"{valid_spectra[0].name}{valid_spectra[0].file_extension} "
                        f"to {valid_spectra[-1].name}{valid_spectra[-1].file_extension}")
                    print()
                    shot = re.match(r"Shot_\d+", valid_spectra[0].name).group(0)
                    detector = spectra[0].detector

                    result = processor.sum_spectra(spectra, name_modifier=shot)
                    out_path = config.save_paths["sums"][result.detector.type]
                    result.save_spe(os.path.join(out_path, result.name + result.file_extension))
                    print(f"{result.name} saved at {out_path}")
        case "q":
            break
        case _:
            pass
    iteration += 1
