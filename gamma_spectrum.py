import re
import numpy as np
import misc
import config
import csv
from config import DetectorType
from detector_manager import Detector
import os


class GammaSpectrum:
    """
    A GammaSpectrum object used for spectrum processing
    """
    TIME_LINE = config.spectra_files["time_line"]

    HEADER_END = config.spectra_files["header_end"]
    FOOTER_START = config.spectra_files["footer_start"]

    def __init__(self):
        self.name = None
        self.detector = None
        self.header = None
        self.footer = None
        self.times = None
        self.counts = None
        self.length = None
        self.channels = None
        self.energies = None
        self.file_extension = None
        self.header_end_index = None
        self.footer_start_index = None

    def load(self, path: str):
        """
        Loads a new GammaSpectrum from an .Spe file, pre-filling its properties
        :param delimiter:
        :param path: The path to the .Spe file
        :return:
        """
        CSV_DELIMITER = ","

        self.name, self.file_extension = os.path.splitext(
            os.path.basename(path))

        self.detector = Detector(misc.get_detector_from_filename(path))

        with open(path) as f:
            lines = f.read().splitlines()

        if self.file_extension == ".Spe":
            self.header_end_index = next((i for i, line in enumerate(lines) if
                                          self.HEADER_END in line)) + 2
            # +2 Because there is one more extra header line after the $Data line
            # plus the $Data line should also be incuded
            self.footer_start_index = next((i for i, line in enumerate(lines[::-1]) if
                                            self.FOOTER_START in line)) + 1
            # +1 because the $ROI line should also be included

            self.header = lines[:self.header_end_index]
            self.footer = lines[-self.footer_start_index:]

            self.times = list(map(int, lines[self.TIME_LINE].split()))

            self.counts = [int(line) for line in lines[self.header_end_index:-self.footer_start_index]]
            self.length = len(self.counts)
            self.fill_channels()
        else:
            if self.file_extension == ".csv":
                file_channels, file_counts = zip(*[line.split(CSV_DELIMITER) for line in lines])
                self.channels = list(map(float, file_channels))
                self.counts = list(map(float, file_counts))
        if self.detector.energy_scale:
            self.fill_energies()
        return self

    def fill_channels(self):
        """
        Fills the spectrum channels
        :return:
        """
        self.channels = list(range(len(self.counts)))

    def fill_energies(self):
        self.energies = self.detector.energy_scale[:self.length]

    def update_times(self, new_times: list) -> None:
        """
        Replaces the data acquisition times in the GammaDetector's header
        :param new_times: Values for replacing the existing times
        """
        self.header[self.TIME_LINE] = f"{new_times[0]} {new_times[1]}"

    def save_spe(self, out_path: str) -> None:
        with open(out_path, "w") as f:
            f.writelines(line + "\n" for line in self.header)
            f.writelines(line + "\n" for line in map(str, self.counts))
            f.writelines(line + "\n" for line in self.footer)
        print(f"File saved: {out_path}")

    def save_raw(self, out_directory: str, output_energies=False) -> None:
        data = self.energies if output_energies else self.channels
        data_type = "_energies" if output_energies else ""
        name_suffix = f"{data_type}_RAW.csv"
        out_filename = self.name + name_suffix
        out_path = os.path.join(out_directory, out_filename)
        with open(out_path, "w", newline='') as f:
            writer = csv.writer(f)
            for d, cnt in zip(data, self.counts):
                writer.writerow([d, cnt])

        print(f"File saved: {out_path}")


class SpectrumProcessor:
    @staticmethod
    def load_multiple_spectra(path) -> list[GammaSpectrum] | None:
        spectra = []
        path = path.strip('"')

        if os.path.isdir(path):
            for filename in misc.get_filenames(path, ".Spe", ".csv"):
                spectra.append(GammaSpectrum().load(os.path.join(path, filename)))
        elif os.path.isfile(path):
            spectra.append(GammaSpectrum().load(path))
        else:
            print(f"No .Spe or .csv files found in {path}")
            return None
        return spectra

    @staticmethod
    def sum_spectra(spectra: list[GammaSpectrum], name_modifier: str) -> GammaSpectrum:
        """
        Sums spectra counts and times from the list and returns the resulting spectrum
        :param spectra: The spectra to sum
        :param name_modifier: The resulting file will be saved as
        "SumSpectra{detector}{name_modifier}-{name_prefix}_to_{name_suffix}.Spe"
        :return: A new GammaSpectrum consisting of the summed up counts
        """

        def get_file_number(file) -> str:
            return re.search(r"(\d{3})", file).group(1)

        result = GammaSpectrum()
        for i, spectrum in enumerate(spectra):
            if i == 0:
                result.header = spectrum.header
                result.footer = spectrum.footer
                result.detector = spectrum.detector
                name_prefix = get_file_number(spectrum.name)
                result.counts = spectrum.counts
                result.times = spectrum.times
            else:
                result.counts = np.add(np.array(result.counts), np.array(spectrum.counts))
                result.times = np.add(np.array(result.times), np.array(spectrum.times))

            if i == len(spectra) - 1:
                result.update_times(result.times)
                name_suffix = get_file_number(spectrum.name)
                result.name = f"SumSpectra{result.detector.name}{name_modifier}-{name_prefix}_to_{name_suffix}"
                result.file_extension = ".Spe"
        result.fill_channels()
        return result

    @staticmethod
    def subtract_background(spectrum: GammaSpectrum) -> GammaSpectrum:
        """
        Subtracts background from a GammaSpectrum based on the detector type
        :param spectrum: A GammaSpectrum to subtract the background from
        :param detector_type: a DetectorType to select a corresponding background spectrum
        :return: The GammaSpectrum with subtracted background
        """
        detector = spectrum.detector
        background_spectrum = GammaSpectrum().load(detector.bg_path)

        result = GammaSpectrum()
        result.detector = detector
        result.channels = spectrum.channels

        scaling_factor = spectrum.times[0] / detector.bg_times[0]

        result.counts = [max(0, (spec - bg * scaling_factor)) for spec, bg in
                         zip(spectrum.counts, background_spectrum.counts)]
        result.fill_energies()
        result.name = f"{spectrum.name}_BG_SUBTRACTED"
        result.file_extension = ".csv"
        return result
