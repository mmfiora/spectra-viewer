import sys

from PyQt5.QtWidgets import QApplication

from config import setup_qtwebengine_profile
from spectra_viewer_uv import SpectraViewer

setup_qtwebengine_profile("uv")

def main():
    """App entry point."""
    app = QApplication(sys.argv)
    viewer = SpectraViewer()  # Create an instance of the class
    viewer.show()             # Show the window
    sys.exit(app.exec_())     # Start Qt event loop

# This runs only if this file is executed directly
if __name__ == "__main__":
    main()


