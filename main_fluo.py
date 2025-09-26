import sys

from PyQt5.QtWidgets import QApplication

from config import setup_qtwebengine_profile
from spectra_viewer_fluo import SpectraViewerFluo

setup_qtwebengine_profile("fluo")

def main():
    app = QApplication(sys.argv)
    viewer = SpectraViewerFluo()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
