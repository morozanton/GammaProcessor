import matplotlib.pyplot as plt
from gamma_spectrum import GammaSpectrum


class Plotter:

    @staticmethod
    def scatter(*spectra: GammaSpectrum, energy_scale=False, **kwargs):
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
