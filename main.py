from gamma_spectrum import GammaSpectrum, SpectrumProcessor
from misc import get_filenames
import os
import config
from plotter import Plotter
import re

"""
(!) Edit the config.py file to use correct file paths
"""


def load_files(input_path: str) -> list | GammaSpectrum:
    if os.path.isdir(input_path):
        files = get_filenames(input_path, ".Spe", ".csv")
        if files:
            return processor.load_multiple_spectra(input_path)
    elif os.path.isfile(input_path):
        return GammaSpectrum().load(input_path)


print(config.logo)

processor = SpectrumProcessor()
plotter = Plotter()

iteration = 0
while True:
    if iteration == 0:
        spectra = [sp for sp in load_files(input("Path to a spectrum file/directory: ").strip('"'))]
    print(f"Loaded files: {[sp.name for sp in spectra]}")

    print("\n[1] Sum spectra\n"
          "[2] Subtract background\n"
          "[3] Add channels/energies; remove header and footer\n"
          "[4] Plot spectra\n"
          "[5] Load new spectra\n"
          "[q] Quit")
    command = input("---> ").strip().lower()
    match command:
        case "1":
            # Sum all .Spe files in a specified directory
            if any(sp.file_extension == ".Spe" for sp in spectra):
                valid_spectra = [sp for sp in spectra if sp.file_extension == ".Spe"]
                print(f"The following files will be summed: ")
                for sp in valid_spectra:
                    print(f"{sp.name}{sp.file_extension}")

                shot_name = re.match(r"Shot_\d+", valid_spectra[0].name).group(0)
                detector = spectra[0].detector

                result = processor.sum_spectra(spectra, name_modifier=shot_name)
                out_path = config.save_paths["sum_spectra"][result.detector.type]
                prompt = input(f"Save {result.name} to {out_path}? [y/n]: ").strip().lower()
                if prompt == "y":
                    result.save_spe(os.path.join(out_path, result.name))
            else:
                print(f"No .Spe files found to sum.")

        case "2":
            path = input("Enter the path to the spectrum to subtract background from.\nOR\n"
                         "Enter a path to a directory to treat all .Spe files inside: ")
            spectra = processor.load_multiple_spectra(path)
            if spectra:
                filenames = [s.name for s in spectra]
                print(f"Background will be subtracted from {len(filenames)} files")
                for spectrum in spectra:
                    result = processor.subtract_background(spectrum=spectrum)

                    out_directory = config.save_paths["subtracted_bg"][result.detector.value]
                    out_path = os.path.join(out_directory, result.name)
                    result.save_raw(out_directory)
        case "3":
            path = input("Enter the path to the spectrum to process.\nOR\n"
                         "Enter a path to a directory to treat all .Spe files inside: ")
            spectra = processor.load_multiple_spectra(path)
            if spectra:
                filenames = [s.name for s in spectra]
                print(f"{len(filenames)} files will be processed.")
                use_energy_scale = input("Output energy scale? [y/n]: ").strip().lower()
                for spectrum in spectra:
                    out_directory = config.save_paths["raw_files"][spectrum.detector.type]
                    spectrum.save_raw(out_directory=out_directory, output_energies=use_energy_scale == "y")
        case "4":
            n_spectra = int(input("How many spectra to plot?: ").strip())
            spectra = []
            for i in range(n_spectra):
                path = input(f"Spectrum {i + 1} path: ")
                spectra.append(GammaSpectrum().load(path.strip('"')))

            plotter.scatter(*spectra)
        case "5":
            spectra = [sp for sp in load_files(input("Path to a spectrum file/directory: ").strip('"'))]
        case "q":
            break
    iteration += 1
