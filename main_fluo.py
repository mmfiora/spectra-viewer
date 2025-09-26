import os, sys, pathlib
BASE = pathlib.Path(__file__).resolve().parent
PROFILE_DIR = BASE / ".qtwebengine" / "fluo"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

os.environ["QTWEBENGINE_PROFILE_STORAGE"] = str(PROFILE_DIR)
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu-shader-disk-cache"
# os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-gpu-shader-disk-cache"

import sys
from PyQt5.QtWidgets import QApplication
from spectra_viewer_fluo import SpectraViewerFluo

def main():
    app = QApplication(sys.argv)
    viewer = SpectraViewerFluo()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
