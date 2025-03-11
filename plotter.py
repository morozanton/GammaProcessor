from config import DetectorType
from gamma_spectrum import GammaSpectrum, SpectrumProcessor
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go


class Plotter:
    colors = {DetectorType.BIG_DET: "#FF9D23",
              DetectorType.SMALL_DET: "#F93827"}

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

    @staticmethod
    def plot_spectrum(*spectra: GammaSpectrum, scale="energy", plot_background=False, background_significance=0,
                      xlim=None, ylim=None):
        if scale == "energy":
            fig = go.Figure()

            for spectrum in spectra:
                fig.add_trace(go.Scatter(
                    x=spectrum.energies,
                    y=spectrum.counts,
                    mode='lines',
                    name=spectrum.name,
                    line=dict(color=Plotter.colors[spectrum.detector.type]) if len(spectra) == 1 else None,
                    fill="tozeroy"
                ))

            if plot_background:
                spectrum_time = spectra[0].times[0] if len(spectra) == 1 and len(spectra[0].times) > 0 else float(
                    input("Spectrum measurement time is required for background plotting.\n"
                          "Enter the time (in sec.): ").strip())
                background_spectrum = SpectrumProcessor().get_normalized_background(spectra[0].detector.type,
                                                                                    spectrum_time)
                min_nonzero_bg = min(bg for bg in background_spectrum.counts if bg > 0)
                background_spectrum.counts = [bg if bg > 0 else min_nonzero_bg for bg in background_spectrum.counts]

                # Adding the normalized background line
                fig.add_trace(go.Scatter(
                    x=background_spectrum.energies,
                    y=background_spectrum.counts,
                    mode='lines',
                    name="Background",
                    line=dict(color="rgb(35,35,35)"),
                    fill="none"
                ))
                if background_significance:
                    # Adding the significance interval
                    fig.add_trace(go.Scatter(
                        x=background_spectrum.energies,
                        y=[x + background_significance * np.sqrt(x) for x in background_spectrum.counts],
                        mode='lines',
                        line=dict(color="grey"),
                        name="+3σ region",
                        fill="tozeroy"
                    ))

            fig.update_layout(
                xaxis=dict(
                    title="Energy (keV)",
                    title_font=dict(size=22),
                    tickfont=dict(size=18),
                    range=xlim
                ),
                yaxis=dict(
                    title="Counts",
                    title_font=dict(size=22),
                    tickfont=dict(size=18),
                    range=ylim
                ),
                legend=dict(
                    font=dict(size=22)
                )
            )

            fig.show(config={"toImageButtonOptions": {"filename": spectra[0].name}})
