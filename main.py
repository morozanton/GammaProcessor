from gamma_spectrum import GammaSpectrum, SpectrumProcessor
from misc import get_filenames
import os
import config
from plotter import Plotter
import re

"""
(!) Edit the config.py file to use correct file paths
"""


def load_files(message: str) -> list | GammaSpectrum:
    input_path = input(message).strip('"')
    if os.path.isdir(input_path):
        files = get_filenames(input_path, ".Spe", ".csv")
        if files:
            return processor.load_multiple_spectra(input_path)
    elif os.path.isfile(input_path):
        return [GammaSpectrum().load(input_path)]


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
        out_path = config.save_paths["sum_spectra"][result.detector.type]
        prompt = input(f"Save {result.name} to {out_path}? [y/n]: ").strip().lower()
        if prompt == "y":
            result.save_spe(os.path.join(out_path, f"{result.name}{result.file_extension}"))
        return [result]
    else:
        print(f"No .Spe files found to sum.")


def subtract_background(input_spectra: list[GammaSpectrum]) -> list[GammaSpectrum]:
    if input_spectra:
        processed_spectra = []
        print(f"Background will be subtracted from {len(input_spectra)} files")
        for spectrum in input_spectra:
            result = processor.subtract_background(spectrum=spectrum)
            out_directory = config.save_paths["subtracted_bg"][result.detector.type]
            # out_path = os.path.join(out_directory, result.name)
            result.save_raw(out_directory)
            processed_spectra.append(result)
        return processed_spectra


def add_energies_remove_headers(input_spectra: list[GammaSpectrum]) -> None:
    if input_spectra:
        print(f"{len(input_spectra)} files will be processed.")
        use_energy_scale = input("Output energy scale? [y/n]: ").strip().lower()
        for spectrum in input_spectra:
            out_directory = config.save_paths["raw_files"][spectrum.detector.type]
            spectrum.save_raw(out_directory=out_directory, output_energies=use_energy_scale == "y")


print(config.logo)

processor = SpectrumProcessor()
plotter = Plotter()

iteration = 0
while True:
    if iteration == 0:
        print()
        spectra = load_files(message="Path to a spectrum file/directory: ")

    print(f"\nCurrent files:")
    print("-" * 30)
    for i, sp in enumerate(spectra):
        print(f"{i + 1}. {sp.name}")
    print("-" * 30)
    print("[1] Bulk processing: sum spectra + subtract background + add energy scale\n"
          "[2] Sum spectra\n"
          "[3] Subtract background\n"
          "[4] Add channels/energies; remove header and footer\n"
          "[5] Plot spectra\n"
          "[6] Load NEW spectra\n"
          "[7] Load ADDITIONAL spectra\n"
          "[q] Quit")
    command = input("---> ").strip().lower()
    match command:
        case "1":
            add_energies_remove_headers(subtract_background(sum_spectra(spectra)))
            spectra = load_files(message="\nAll files are processed. Load new files to process?"
                                         "\nPath to a spectrum file/directory: ")
        case "2":
            spectra = sum_spectra(spectra)
        case "3":
            spectra = subtract_background(spectra)
        case "4":
            add_energies_remove_headers(spectra)
            spectra = load_files(message="\nAll files are processed. Load new files to process?"
                                         "\nPath to a spectrum file/directory: ")
        case "5":
            n_spectra = int(input("How many spectra to plot?: ").strip())
            spectra = []
            for i in range(n_spectra):
                path = input(f"Spectrum {i + 1} path: ")
                spectra.append(GammaSpectrum().load(path.strip('"')))

            plotter.scatter(*spectra)
        case "6":
            spectra = load_files(message="Path to a spectrum file/directory: ")
        case "7":
            spectra.extend(
                load_files(message="Path to an additional spectrum file/directory: "))

        case "99":
            # Sum up ALL files for ALL shots from a given detector
            root = "D:\Anton\Desktop (D)\Shots\Small_Det"
            dirs = os.listdir(root)
            for direct in dirs:
                direct = os.path.join(root, direct, "Messungen")
                spectra = load_files(direct)
                if spectra:
                    valid_spectra = [sp for sp in spectra if sp.file_extension == ".Spe"]
                    print(f"The following files will be summed: ")
                    print(f"{valid_spectra[0].name}{valid_spectra[0].file_extension}")
                    print("to")
                    print(f"{valid_spectra[-1].name}{valid_spectra[-1].file_extension}")
                    shot_name = re.match(r"Shot_\d+", valid_spectra[0].name).group(0)
                    detector = spectra[0].detector

                    result = processor.sum_spectra(spectra, name_modifier=shot_name)
                    out_path = config.save_paths["sum_spectra"][result.detector.type]
                    result.save_spe(os.path.join(out_path, result.name))
                    print(f"{result.name} saved at {out_path}")
        case "q":
            break
        case _:
            continue
    iteration += 1
