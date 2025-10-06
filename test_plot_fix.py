"""
Test script to verify Plotly plotting works with embedded JavaScript.
Run this in Windows PowerShell: python test_plot_fix.py
"""

import numpy as np
import pandas as pd

print("Testing plot generation...")

wavelength = np.linspace(400, 700, 100)
intensity = np.sin((wavelength - 400) / 50) + 1
df = pd.DataFrame({'Wavelength': wavelength, 'Intensity': intensity})

from plotter import plot_spectra
curves = {'Test Curve': df}
fig = plot_spectra(curves, y_label='Test Intensity')

print("\nGenerating HTML with embedded Plotly...")
html = fig.to_html(include_plotlyjs=True)

print(f"✓ HTML generated successfully ({len(html)} characters)")
print(f"✓ Plotly embedded: {'Yes' if len(html) > 500000 else 'No (might be CDN)'}")

with open('test_plot_output.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✓ Test plot saved to: test_plot_output.html")
print("  Open this file in your web browser to verify it works")
print("\nIf the HTML file displays correctly in your browser,")
print("the issue is with PyQt5's QWebEngineView, not the plotting.")
