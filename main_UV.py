import os, sys, pathlib

BASE = pathlib.Path(__file__).resolve().parent
PROFILE_DIR = BASE / ".qtwebengine" / "uv"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# 1) Ubicación de perfiles (cache + storage) para esta app
os.environ["QTWEBENGINE_PROFILE_STORAGE"] = str(PROFILE_DIR)

# 2) (Opcional) Flags de Chromium para evitar shader cache en disco
#   - Útil si el problema persiste con GPUCache
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu-shader-disk-cache"


import sys
from PyQt5.QtWidgets import QApplication
from spectra_viewer_uv import SpectraViewer  # Class that manages the UI

def main():
    """App entry point."""
    app = QApplication(sys.argv)
    viewer = SpectraViewer()  # Create an instance of the class
    viewer.show()             # Show the window
    sys.exit(app.exec_())     # Start Qt event loop

# This runs only if this file is executed directly
if __name__ == "__main__":
    main()
