"""
Test different Plotly embedding methods with QWebEngineView
Run in Windows: python test_qwebengine.py
"""
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
import numpy as np
import pandas as pd
from plotter import plot_spectra

wavelength = np.linspace(400, 700, 100)
intensity = np.sin((wavelength - 400) / 50) + 1
df = pd.DataFrame({'Wavelength': wavelength, 'Intensity': intensity})
curves = {'Test': df}

app = QApplication(sys.argv)
window = QWidget()
layout = QVBoxLayout()

web_view = QWebEngineView()
web_view.setMinimumSize(800, 600)

def test_method_1():
    print("Testing: include_plotlyjs=True (embedded)")
    fig = plot_spectra(curves, y_label='Test')
    html = fig.to_html(include_plotlyjs=True)
    web_view.setHtml(html)
    print(f"HTML size: {len(html)} bytes")

def test_method_2():
    print("Testing: include_plotlyjs='cdn' (CDN)")
    fig = plot_spectra(curves, y_label='Test')
    html = fig.to_html(include_plotlyjs='cdn')
    web_view.setHtml(html)
    print(f"HTML size: {len(html)} bytes")

btn1 = QPushButton("Test Embedded (True)")
btn1.clicked.connect(test_method_1)

btn2 = QPushButton("Test CDN")
btn2.clicked.connect(test_method_2)

layout.addWidget(btn1)
layout.addWidget(btn2)
layout.addWidget(web_view)

window.setLayout(layout)
window.setWindowTitle("Plotly QWebEngineView Test")
window.resize(900, 700)
window.show()

# Auto-test embedded method
test_method_1()

sys.exit(app.exec_())
