import matplotlib.pyplot as plt
from gamma_spectrum import GammaSpectrum
import numpy as np
import math


class Plotter:

    @staticmethod
    def plot(*spectra: GammaSpectrum, energy_scale=False, **kwargs):
        for spectrum in spectra:
            if energy_scale:
                x_data = spectrum.energies
                plt.xlabel("Energy (keV)")
            else:
                x_data = spectrum.channels
                plt.xlabel("Channel")

            plt.ylabel("Count")
            plt.scatter(x_data, spectrum.counts, label=spectrum.name, **kwargs)

        if 'xlim' in kwargs:
            plt.xlim(kwargs['xlim'])

        plt.legend()
        plt.show()


if __name__ == "__main__":
    import pandas as pd
    import matplotlib.pyplot as plt

    colors = {"red": "#F93827",
              "yellow": "#FFD65A",
              "orange": "#FF9D23",
              "green": "#16C47F",
              "blue": "4D96FF",
              "bigdet": "#FF9D23",
              "smalldet": "#F93827"
              }


    def plot_double_axes_with_annotations(columns, color):
        data = columns
        # Создание фигуры и осей
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax2 = ax1.twiny()  # Вторая ось X

        # Построение графиков
        ax1.plot(data["Channel"], data["Counts"], label="Channel vs Counts", color="white")
        ax2.plot(data["Energy"], data["Counts"], label="Energy vs Counts", color=color)

        # Настройки осей
        ax1.set_xlabel("Channel", fontsize=14)
        ax2.set_xlabel("Energy (keV)", fontsize=14)
        ax1.set_ylabel("Counts", fontsize=14)
        ax1.set_xlim(0)
        ax2.set_xlim(0)
        ax2.grid(alpha=0.5)
        ax1.grid(axis='y', alpha=0.5)

        annot_channels = []
        # Аннотации
        with open("./annotation_data.txt", 'r') as f:
            lines = f.readlines()
        annotations = []
        for line in lines:
            text, chan = line.split()
            annotations.append((text, float(chan)))

        for i, (text, ch) in enumerate(annotations):
            y_pos = data["Counts"][int(ch)]
            ax1.annotate(text,
                         xy=(ch, y_pos),
                         xytext=(ch, y_pos * 3),
                         verticalalignment='bottom',
                         horizontalalignment='center',
                         rotation=90,
                         fontsize=12,
                         color='black',
                         arrowprops=dict(arrowstyle='-', color="black", lw=1))
            #  arrowprops=dict(arrowstyle='->', color="black", lw=1, connectionstyle="angle,angleA=0,angleB=90"))
        plt.yscale("log")
        plt.ylim(3, 2e6)
        plt.show()

    def plot_with_annotations(columns, color):
        # Создание фигуры и осей
        plt.figure(figsize=(10, 6))

        # Построение графиков
        plt.plot(columns["Energy"], columns["Counts"], label="Channel vs Counts", color=color)

        plt.xlabel("Energy (keV)", fontsize=14)
        plt.ylabel("Counts", fontsize=14)

        # Annotations here
        with open("./annotation_data.txt", 'r') as f:
            lines = f.readlines()

        annotations = []
        for line in lines:
            text, chan = line.split()
            annotations.append((text, float(chan)))

        for text, ch in annotations:
            idx = (np.abs(columns["Energy"] - ch)).argmin()
            y_pos = columns["Counts"][idx]
            plt.annotate(text,
                         xy=(ch, y_pos),
                         xytext=(ch, 3 * y_pos),
                         verticalalignment='bottom',
                         horizontalalignment='center',
                         rotation=90,
                         fontsize=12,
                         color='black',
                         arrowprops=dict(arrowstyle='-', color="black", lw=1))
            #  arrowprops=dict(arrowstyle='->', color="black", lw=1, connectionstyle="angle,angleA=0,angleB=90"))

        text, ch, y_pos = ("214Pb+234U", 608.692, 19)
        plt.annotate(text,
                     xy=(ch, y_pos),
                     xytext=(ch + 30, 3 * y_pos),
                     verticalalignment='bottom',
                     horizontalalignment='center',
                     rotation=90,
                     fontsize=12,
                     color='black',
                     arrowprops=dict(arrowstyle='-', color="black", lw=1))
        plt.yscale("log")
        plt.xlim(0)
        plt.ylim(1, 600)
        plt.show()
    def simple_plot(path, color):
        data = read_csv(file_path, column_names=["Energy", "Count"])
        plt.plot(data["Energy"], data["Count"], color=graph_color, label="Energy calibration")
        plt.scatter(data["Energy"], data["Count"], color="black", label="Measured data")
        plt.xlabel("Channel number", fontsize=14)
        plt.ylabel("Energy (keV)", fontsize=14)
        plt.legend()
        plt.show()


    def read_csv(path, column_names, delimiter="\t"):
        return pd.read_csv(path, sep=delimiter, names=column_names)


    file_path = r"D:\Anton\Desktop (D)\Shots_processing\Calibration\RAW\SmallDet-MixSource-after_experiment_BG_SUBTRACTED_channels_AND_energies.csv"
    graph_color = colors["smalldet"]
    #data = read_csv(file_path, ["Energy", "Counts"], delimiter=",")

    plot_double_axes_with_annotations(read_csv(file_path, column_names=["Channel", "Counts", "Energy"]),
                                      color=graph_color)


    # simple_plot(file_path, graph_color)



    # plot_with_annotations(data, graph_color)
