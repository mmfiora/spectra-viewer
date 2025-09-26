from base_spectra_viewer import BaseSpectraViewer
from loader_fluo import load_fluo_file


class SpectraViewerFluo(BaseSpectraViewer):
    def __init__(self):
        super().__init__(
            title="Spectra Viewer (Fluorescence)",
            y_label="Fluorescence (a.u.)",
            loader_func=load_fluo_file,
            file_filter="Data Files (*.txt *.csv)"
        )
        # Enable peak analysis for fluorescence spectra
        self.peak_analysis_btn.setVisible(True)
