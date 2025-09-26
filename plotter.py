import plotly.graph_objs as go
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import numpy as np
import pandas as pd

def plot_spectra(curves, y_label="Absorbance (a.u.)"):
    """
    Plot multiple spectra using Plotly (for the app).
    curves: dict of {label: DataFrame}
    """
    fig = go.Figure()

    # Plot each curve
    for label, df in curves.items():
        fig.add_trace(go.Scatter(
            x=df.iloc[:, 0],
            y=df.iloc[:, 1],
            mode="lines",
            name=label
        ))

    # Layout configuration
    fig.update_layout(
        xaxis=dict(
            title="Wavelength (nm)",
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            zeroline=True,
            zerolinecolor="black",
            zerolinewidth=1,
            dtick=20  # ticks cada 20 nm en el gráfico interactivo
        ),
        yaxis=dict(
            title=y_label,
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            zeroline=True,
            zerolinecolor="black",
            zerolinewidth=1
        ),
        plot_bgcolor="white",
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="right",
            x=0.98,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1,
            font=dict(size=14)
        ),
        margin=dict(l=60, r=20, t=20, b=60)
    )

    return fig


def export_plot_as_jpg(curves, path, y_label="Absorbance (a.u.)"):
    """
    Export plot to JPG using Matplotlib with the legend inside the plot area.
    curves: dict of {label: DataFrame}
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot each curve with numeric conversion
    for label, df in curves.items():
        x = pd.to_numeric(df.iloc[:, 0], errors="coerce")
        y = pd.to_numeric(df.iloc[:, 1], errors="coerce")

        # Remove invalid rows
        mask = ~(x.isna() | y.isna())
        x = x[mask]
        y = y[mask]

        ax.plot(x, y, label=label)

    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel(y_label)
    ax.axhline(0, color="black", linestyle="--", linewidth=1)

    # Set X range from data
    x_min = min(np.nanmin(pd.to_numeric(df.iloc[:, 0], errors="coerce")) for df in curves.values())
    x_max = max(np.nanmax(pd.to_numeric(df.iloc[:, 0], errors="coerce")) for df in curves.values())
    ax.set_xlim(x_min, x_max)

    # Force rendering before applying ticks
    fig.canvas.draw()

    # X ticks every 20 nm
    ax.xaxis.set_major_locator(MultipleLocator(20))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))

    # Borders
    for spine in ax.spines.values():
        spine.set_edgecolor("black")
        spine.set_linewidth(1)

    # Legend inside the plot
    legend = ax.legend(
        loc="best",
        frameon=True,
        fancybox=False,
        edgecolor="black"
    )
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_alpha(0.8)

    # Save figure
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
