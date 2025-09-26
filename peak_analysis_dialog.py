from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QLabel, QMessageBox,
                             QHeaderView, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
import pandas as pd


class SimplePeakTable(QDialog):
    peak_removed = pyqtSignal(int)  # Signal to emit when a peak is removed
    
    def __init__(self, peak_results, curve_name, parent=None):
        super().__init__(parent)
        self.peak_results = peak_results
        self.curve_name = curve_name
        self.setWindowTitle(f"Peaks - {curve_name}")
        self.setModal(False)  # Non-modal so user can interact with plot
        self.resize(400, 300)
        
        self._setup_ui()
        self._populate_data()
    
    def _setup_ui(self):
        """Setup the simplified dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(f"<h3>First 3 Peaks: {self.curve_name}</h3>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Simple peaks table
        self.peaks_table = QTableWidget()
        self.peaks_table.setColumnCount(4)
        self.peaks_table.setHorizontalHeaderLabels(["Peak #", "Wavelength (nm)", "Intensity (a.u.)", "Remove"])
        self.peaks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.peaks_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.clicked.connect(self._export_to_csv)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def _populate_data(self):
        """Populate the simple peaks table."""
        peaks = self.peak_results.get('all_peaks', [])
        
        self.peaks_table.setRowCount(len(peaks))
        for i, peak in enumerate(peaks):
            # Peak number
            self.peaks_table.setItem(i, 0, QTableWidgetItem(str(peak['index'])))
            
            # Wavelength
            self.peaks_table.setItem(i, 1, QTableWidgetItem(f"{peak['wavelength']:.1f}"))
            
            # Intensity
            self.peaks_table.setItem(i, 2, QTableWidgetItem(f"{peak['intensity']:.2f}"))
            
            # Remove button
            remove_btn = QPushButton("✕")
            remove_btn.setMaximumWidth(30)
            remove_btn.clicked.connect(lambda checked, idx=i: self._remove_peak(idx))
            self.peaks_table.setCellWidget(i, 3, remove_btn)
            
            # Highlight Peak 1 and Peak 3
            if peak['index'] == 1:  # Peak 1 (first by wavelength)
                for col in range(3):
                    item = self.peaks_table.item(i, col)
                    item.setBackground(QColor(144, 238, 144))  # Light green
            elif peak['index'] == 3:  # Peak 3 (third by wavelength)
                for col in range(3):
                    item = self.peaks_table.item(i, col)
                    item.setBackground(QColor(173, 216, 230))  # Light blue
    
    def _remove_peak(self, row_index):
        """Remove a peak from the table and emit signal."""
        if 0 <= row_index < len(self.peak_results.get('all_peaks', [])):
            # Get the peak data before removing
            peak = self.peak_results['all_peaks'][row_index]
            
            # Remove from results
            self.peak_results['all_peaks'].pop(row_index)
            self.peak_results['num_peaks_found'] = len(self.peak_results['all_peaks'])
            
            # Update Peak 1/Peak 3 references if needed
            self._update_peak_references()
            
            # Refresh table
            self._populate_data()
            
            # Emit signal to update plot
            self.peak_removed.emit(row_index)
    
    def _update_peak_references(self):
        """Update Peak 1 and Peak 3 references after removal."""
        peaks = self.peak_results.get('all_peaks', [])
        
        # Reset references
        self.peak_results['first_peak'] = None
        self.peak_results['third_peak'] = None
        
        # Update indices and references
        for i, peak in enumerate(peaks):
            peak['index'] = i + 1
            
            if i == 0:  # Peak 1 (first by wavelength)
                self.peak_results['first_peak'] = {
                    'wavelength': peak['wavelength'],
                    'intensity': peak['intensity'],
                    'position': 'peak_1'
                }
            elif i == 2:  # Peak 3 (third by wavelength)
                self.peak_results['third_peak'] = {
                    'wavelength': peak['wavelength'],
                    'intensity': peak['intensity'],
                    'position': 'peak_3'
                }
    
    def _export_to_csv(self):
        """Export peak data to CSV file."""
        from PyQt5.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Peak Data", 
            f"peaks_{self.curve_name}.csv", 
            "CSV files (*.csv)"
        )
        
        if not filename:
            return
        
        try:
            # Create DataFrame with all peaks
            peaks = self.peak_results.get('all_peaks', [])
            if not peaks:
                QMessageBox.information(self, "No Data", "No peaks to export.")
                return
            
            # Create DataFrame
            df = pd.DataFrame([
                {
                    'Peak_Number': peak['index'],
                    'Wavelength_nm': peak['wavelength'],
                    'Intensity_au': peak['intensity']
                }
                for peak in peaks
            ])
            
            df.to_csv(filename, index=False)
            QMessageBox.information(self, "Exported", f"Peak data saved to:\n{filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data:\n{str(e)}")