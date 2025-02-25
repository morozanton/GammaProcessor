from gamma_spectrum import GammaSpectrum, SpectrumProcessor
from misc import get_filenames
import os
import config
from plotter import Plotter

"""
(!) Edit the config.py file to use correct file paths
"""
print(config.logo)

processor = SpectrumProcessor()
plotter = Plotter()
spectra = []

iteration = 0
while True:
    print("\n[1] Load spectra"
          "[2] Sum spectra\n"
          "[3] Subtract background\n"
          "[4] Add channels/energies; remove header and footer\n"
          "[5] Plot spectra\n"
          "[q] Quit")
    command = input(": ").strip().lower()
    match command:
        case "1":
            # Sum all .Spe files in a specified directory
            directory = input("Path to a directory with .Spe files to sum: ").strip('"')
            if os.path.isdir(directory):
                filenames = get_filenames(directory, extension=".Spe")
                if filenames:
                    print(f"Found {len(filenames)} files to sum.")
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
        case "99":
            print("TEST MODE", end="-" * 10 + "\n")
            GammaSpectrum().load("D:\Anton\Desktop (D)\Shots_processing\Calibration\BigDet-MixSource.Spe")
        case "q":
            break
