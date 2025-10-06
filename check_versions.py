import sys
print("Python version:", sys.version)
try:
    import plotly
    print("Plotly version:", plotly.__version__)
except:
    print("Plotly: NOT INSTALLED")
    
try:
    import PyQt5.QtCore
    print("PyQt5 version:", PyQt5.QtCore.PYQT_VERSION_STR)
except:
    print("PyQt5: NOT INSTALLED")
