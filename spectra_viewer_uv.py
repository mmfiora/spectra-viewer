from base_spectra_viewer import BaseSpectraViewer
from loader_uv import load_spectra_file


class SpectraViewer(BaseSpectraViewer):
    def __init__(self):
        super().__init__(
            title="Spectra Viewer (UV)",
            y_label="Absorbance (a.u.)",
            loader_func=load_spectra_file,
            file_filter="Data files (*.csv *.xls *.xlsx)"
        )



