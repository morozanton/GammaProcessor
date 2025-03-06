import re
import numpy as np
import misc
import config
import csv
from config import DetectorType
from scipy.ndimage import gaussian_filter1d
from detector_manager import Detector
import os
import json


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

    def load(self, path: str, csv_delimiter=","):
        """
        Loads a new GammaSpectrum from a file depending on its extension and contents, pre-filling its properties
        :param csv_delimiter: column separator in the .csv file
        :param path: The path to the .Spe file
        :return:
        """
        delimiter = csv_delimiter
        self.name, self.file_extension = os.path.splitext(
            os.path.basename(path))
        if self.file_extension == ".json":
            with open(path) as f:
                file_contents = json.load(f)
            self.detector = Detector(misc.get_detector_from_filename(file_contents["metadata"]["detector"]))
            self.times = file_contents["metadata"]["spectrum_recording_times"]
            self.counts = file_contents["data"]["counts"]
            self.channels = file_contents["data"]["channels"]
            self.energies = file_contents["data"]["energies"]

        else:
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

            elif self.file_extension == ".csv":
                file_channels, file_counts = zip(*[line.split(delimiter) for line in lines])
                self.channels = list(map(float, file_channels))
                self.counts = list(map(float, file_counts))
            else:
                raise ValueError("Unsupported file format")

        if not self.energies and self.detector.energy_scale:
            self.fill_energies()

        return self

    def apply_filtering(self):
        def estimate_noise(spectrum):
            diffs = np.diff(spectrum)  # Разности соседних значений
            noise_level = np.median(np.abs(diffs)) / 0.6745  # Оценка стандартного отклонения шума
            return noise_level

        print(f"Initial noise level: {estimate_noise(self.counts):.2f}")
        print("Filtering data...")
        self.counts = list(gaussian_filter1d(self.counts, sigma=1))
        self.name += "_filtered"
        print(f"Resulting noise level: {estimate_noise(self.counts):.2f}")

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
        Replaces the data acquisition times in the GammaDetector's header (for .Spe files)
        :param new_times: Values for replacing the existing times
        """
        self.header[self.TIME_LINE] = f"{new_times[0]} {new_times[1]}"

    def save_spe(self, out_path: str) -> None:
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        with open(out_path, "w") as f:
            f.writelines(line + "\n" for line in self.header)
            f.writelines(line + "\n" for line in map(str, self.counts))
            f.writelines(line + "\n" for line in self.footer)

        print(f"File saved: {out_path}")

    def save_raw(self, out_directory: str, output_energies=False, filename_suffix="") -> None:
        data = self.energies if output_energies else self.channels
        name_suffix = f"{filename_suffix}.csv"
        out_filename = self.name + name_suffix
        out_path = os.path.join(out_directory, out_filename)
        if not os.path.exists(out_directory):
            os.makedirs(out_directory)
        with open(out_path, "w", newline='') as f:
            writer = csv.writer(f)
            for d, cnt in zip(data, self.counts):
                writer.writerow([d, cnt])

        print(f"File saved: {out_path}")

    def save_json(self, out_directory: str, filename_suffix=""):
        metadata = {
            "spectrum_name": self.name,
            "detector": self.detector.name,
            "spectrum_recording_times": self.times
        }
        data = {
            "counts": self.counts,
            "channels": self.channels,
            "energies": self.energies,
        }
        json_data = {
            "metadata": metadata,
            "data": data
        }

        name_suffix = f"{filename_suffix}.json"
        out_filename = self.name + name_suffix
        out_path = os.path.join(out_directory, out_filename)

        if not os.path.exists(out_directory):
            os.makedirs(out_directory)

        with open(out_path, "w") as f:
            json.dump(json_data, f, indent=4)

        print(f"File saved: {out_path}")


class SpectrumProcessor:
    @staticmethod
    def load_multiple_spectra(files: list) -> list[GammaSpectrum] | None:
        return [GammaSpectrum().load(os.path.join(filename)) for filename in files]

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
    def get_normalized_background(detector_type: DetectorType, spectrum_time: int | float) -> GammaSpectrum:
        """
        Normalizes the background for a given detector type to the given measurement time.
        """
        detector = Detector(detector_type)
        background_spectrum = GammaSpectrum().load(detector.bg_path)
        scaling_factor = spectrum_time / detector.bg_times[0]

        background_spectrum.counts = list(map(lambda c: c * scaling_factor, background_spectrum.counts))
        return background_spectrum

    @staticmethod
    def subtract_background(spectrum: GammaSpectrum, significance=0) -> GammaSpectrum:
        """
        Subtracts background from a GammaSpectrum based on the detector type
        :param significance: How to treat low numbers. If significance == 0, all counts below 0 are dropped.
        When significance == 3, values below 3 sigma are dropped
        :param spectrum: A GammaSpectrum to subtract the background from
        :return: The GammaSpectrum with subtracted background
        """

        detector = spectrum.detector
        background_spectrum = GammaSpectrum().load(detector.bg_path)

        result = GammaSpectrum()
        result.detector = detector
        result.channels = spectrum.channels

        scaling_factor = spectrum.times[0] / detector.bg_times[0]

        if significance:
            min_nonzero_bg = min(bg for bg in background_spectrum.counts if bg > 0)
            result.counts = []
            for bg, cnt in zip(background_spectrum.counts, spectrum.counts):
                bg_scaled = bg * scaling_factor if bg > 0 else min_nonzero_bg * scaling_factor
                threshold = np.sqrt(bg_scaled) + bg_scaled
                cnt_new = cnt - bg_scaled
                result.counts.append(cnt_new) if cnt_new > threshold else result.counts.append(0)
        else:
            result.counts = [spec - bg * scaling_factor if spec - bg * scaling_factor > 0 else 0 for spec, bg
                             in zip(spectrum.counts, background_spectrum.counts)]

        result.fill_energies()
        result.name = f"{spectrum.name}_NO_BG"
        if significance:
            result.name += f"_{significance}-sigma_significance"
        result.file_extension = ".csv"
        return result
