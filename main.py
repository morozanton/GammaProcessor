from gamma_spectrum import GammaSpectrum, SpectrumProcessor
from misc import get_filenames
import os
import config

"""
(!) Edit the config.py file to use correct file paths
"""
print(config.logo)

processor = SpectrumProcessor()

while True:
    print("\n[1] Sum spectra\n"
          "[2] Subtract background\n"
          "[3] Clear header and footer\n"
          "[q] Quit")
    command = input(": ").strip().lower()
    match command:
        case "1":
            # Sum all .Spe files in a specified directory
            directory = input("Path to a directory with .Spe files to sum: ").strip('"')
            if os.path.isdir(directory):
                filenames = get_filenames(directory, extension=".Spe")
                if filenames:
                    print(f"{len(filenames)} .Spe files to sum.")
                    spectra = processor.load_multiple_spectra(directory)

                    shot_name = filenames[0].split()[0]
                    detector = spectra[0].detector

                    result = processor.sum_spectra(spectra, name_modifier=shot_name)
                    out_path = config.save_paths["sum_spectra"][result.detector.value]
                    prompt = input(f"Save {result.name} to {out_path}? [y/n]: ").strip().lower()
                    if prompt == "y":
                        result.save_spe(os.path.join(out_path, result.name))
                else:
                    print(f"No .Spe files found in {directory}")
            else:
                print(directory, "is not a directory")
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
                print(f"Headers and footers will be cleaned from {len(filenames)} files:")

                for spectrum in spectra:
                    out_directory = config.save_paths["raw_files"][spectrum.detector.value]
                    spectrum.save_raw(out_directory=out_directory)

        case "q":
            break
