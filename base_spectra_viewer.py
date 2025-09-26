from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QLabel, QMessageBox, QFileDialog, 
                             QInputDialog, QSizePolicy)
from PyQt5.QtWebEngineWidgets import QWebEngineView

from plotter import plot_spectra, export_plot_as_jpg
from curve_tools import (normalize_curve, add_offset, subtract_curves, 
                         find_fluorescence_peaks_adaptive, diagnose_missing_peak, 
                         find_peaks_in_region, find_fluorescence_peaks_force_detect,
                         find_peaks_and_shoulders_combined, find_shoulders_and_inflections,
                         find_shoulder_in_region, find_true_shoulders_excluding_peaks)
from file_tools import save_curves_to_csv
from config import DEFAULT_WINDOW_SIZE, DEFAULT_PLOT_SIZE
from peak_analysis_dialog import SimplePeakTable


class BaseSpectraViewer(QWidget):
    def __init__(self, title, y_label, loader_func, file_filter=""):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(*DEFAULT_WINDOW_SIZE)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.y_label = y_label
        self.loader_func = loader_func
        self.file_filter = file_filter
        self.available_columns = {}
        self.plotted_curves = {}
        self.peak_data = {}  # Store peak analysis results for each curve
        self.peak_dialogs = {}  # Store open peak dialog windows
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        main_layout = QHBoxLayout(self)
        left_panel = QVBoxLayout()

        # Load files
        self.load_btn = QPushButton("Load Files")
        self.load_btn.clicked.connect(self.load_file)
        left_panel.addWidget(self.load_btn)

        # Loaded columns
        left_panel.addWidget(QLabel("Loaded Columns"))
        self.column_list = QListWidget()
        self.column_list.setSelectionMode(QListWidget.MultiSelection)
        left_panel.addWidget(self.column_list)

        # Delete columns button
        self.delete_column_btn = QPushButton("Delete Selected Columns")
        self.delete_column_btn.clicked.connect(self.delete_selected_columns)
        left_panel.addWidget(self.delete_column_btn)

        # Plot selected columns button
        self.plot_btn = QPushButton("Plot Selected Columns")
        self.plot_btn.clicked.connect(self.plot_selected_columns)
        left_panel.addWidget(self.plot_btn)

        # Plotted curves
        left_panel.addWidget(QLabel("Plotted Curves"))
        self.curve_list = QListWidget()
        self.curve_list.setSelectionMode(QListWidget.MultiSelection)
        left_panel.addWidget(self.curve_list)

        # Normalize button
        self.norm_btn = QPushButton("Normalize")
        self.norm_btn.clicked.connect(self.normalize_selected_curves)
        left_panel.addWidget(self.norm_btn)

        # Offset button
        self.offset_btn = QPushButton("Add Offset")
        self.offset_btn.clicked.connect(self.add_offset_to_curves)
        left_panel.addWidget(self.offset_btn)

        # Subtract curves
        self.subtract_btn = QPushButton("Subtract A - k·B")
        self.subtract_btn.clicked.connect(self.subtract_curves_action)
        left_panel.addWidget(self.subtract_btn)

        # Peak analysis (only for fluorescence)
        self.peak_analysis_btn = QPushButton("Peak Analysis")
        self.peak_analysis_btn.clicked.connect(self.analyze_peaks_action)
        left_panel.addWidget(self.peak_analysis_btn)
        # Hide by default, show only for fluorescence viewer
        self.peak_analysis_btn.setVisible(False)

        # Rename curves
        self.rename_curve_btn = QPushButton("Rename Curve")
        self.rename_curve_btn.clicked.connect(self.rename_curve)
        left_panel.addWidget(self.rename_curve_btn)

        # Delete curves
        self.delete_curve_btn = QPushButton("Delete Selected Curves")
        self.delete_curve_btn.clicked.connect(self.delete_selected_curves)
        left_panel.addWidget(self.delete_curve_btn)

        # Save curves
        self.save_csv_btn = QPushButton("Save Curves (CSV)")
        self.save_csv_btn.clicked.connect(self.save_all_curves)
        left_panel.addWidget(self.save_csv_btn)

        # Save plot
        self.save_jpg_btn = QPushButton("Save Plot (JPG)")
        self.save_jpg_btn.clicked.connect(self.save_plot_as_jpg)
        left_panel.addWidget(self.save_jpg_btn)

        # Clear all curves
        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.clicked.connect(self.clear_all_curves)
        left_panel.addWidget(self.clear_all_btn)

        main_layout.addLayout(left_panel, stretch=1)

        # Plot area
        self.plot_view = QWebEngineView()
        self.plot_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_view.setMinimumSize(*DEFAULT_PLOT_SIZE)
        main_layout.addWidget(self.plot_view, stretch=3)

    def _get_selected_curves(self):
        """
        Returns selected curves from plotted curves list,
        falling back to loaded columns if none selected in plotted curves.
        """
        selected = [item.text() for item in self.curve_list.selectedItems()]
        if not selected:
            selected = [item.text() for item in self.column_list.selectedItems()]
        return selected

    def _validate_numeric_input(self, value, min_val=-1e6, max_val=1e6):
        """Validate numeric input within reasonable bounds."""
        try:
            num_val = float(value)
            if not (min_val <= num_val <= max_val):
                raise ValueError(f"Value must be between {min_val} and {max_val}")
            return num_val
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid numeric value: {e}")

    def load_file(self):
        """Load spectral data file."""
        file_filter = self.file_filter or "Data Files (*.*)"
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", file_filter)
        if not path:
            return
        
        try:
            spectra = self.loader_func(path)
            for label, df in spectra.items():
                if label not in self.available_columns:
                    self.available_columns[label] = df
                    self.column_list.addItem(label)
        except Exception as e:
            QMessageBox.critical(self, "Error Loading File", 
                               f"Failed to load file '{path}':\n{str(e)}")

    def plot_selected_columns(self):
        """Plot selected columns from loaded data."""
        selected = [item.text() for item in self.column_list.selectedItems()]
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select columns to plot.")
            return
        
        for label in selected:
            if label not in self.plotted_curves:
                self.plotted_curves[label] = self.available_columns[label]
                self.curve_list.addItem(label)
        self.update_plot()

    def update_plot(self):
        """Update the plot display."""
        if not self.plotted_curves:
            self.plot_view.setHtml("<h3 style='text-align:center;'>No curves plotted</h3>")
            return
        
        try:
            # Filter peak data to only include curves that are currently plotted
            current_peak_data = {name: peaks for name, peaks in self.peak_data.items() 
                               if name in self.plotted_curves}
            
            fig = plot_spectra(self.plotted_curves, y_label=self.y_label, peak_data=current_peak_data)
            self.plot_view.setHtml(fig.to_html(include_plotlyjs="cdn"))
        except Exception as e:
            QMessageBox.critical(self, "Plot Error", f"Failed to generate plot:\n{str(e)}")

    def delete_selected_columns(self):
        """Delete selected columns from both loaded and plotted data."""
        selected = [item.text() for item in self.column_list.selectedItems()]
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select columns to delete.")
            return
        
        for label in selected:
            if label in self.available_columns:
                del self.available_columns[label]
            if label in self.plotted_curves:
                del self.plotted_curves[label]
                self._remove_item_from_list(self.curve_list, label)
            self._remove_item_from_list(self.column_list, label)
        self.update_plot()

    def delete_selected_curves(self):
        """Delete selected curves from plot."""
        selected = [item.text() for item in self.curve_list.selectedItems()]
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select curves to delete.")
            return
        
        for label in selected:
            if label in self.plotted_curves:
                del self.plotted_curves[label]
                # Also remove peak data and close peak dialog if open
                if label in self.peak_data:
                    del self.peak_data[label]
                if label in self.peak_dialogs:
                    self.peak_dialogs[label].close()
                    del self.peak_dialogs[label]
                self._remove_item_from_list(self.curve_list, label)
        self.update_plot()

    def clear_all_curves(self):
        """Clear all data and plots."""
        # Close all peak dialogs
        for dialog in self.peak_dialogs.values():
            dialog.close()
        
        self.plotted_curves.clear()
        self.curve_list.clear()
        self.available_columns.clear()
        self.column_list.clear()
        self.peak_data.clear()
        self.peak_dialogs.clear()
        self.update_plot()

    def normalize_selected_curves(self):
        """Normalize selected curves."""
        selected = self._get_selected_curves()
        if not selected:
            QMessageBox.information(self, "No Selection", 
                                  "Select curves to normalize (from Plotted or Loaded Columns).")
            return
        
        value, ok = QInputDialog.getDouble(self, "Normalization", 
                                         "Enter normalization value (0 = use max):", 
                                         0.0, 0, 1e6, 4)
        if not ok:
            return
        
        try:
            self._validate_numeric_input(value, 0, 1e6)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return
        
        for label in selected:
            df = self.available_columns.get(label, self.plotted_curves.get(label))
            if df is None:
                continue
            
            try:
                if value == 0:
                    df_new = normalize_curve(df)
                    new_label = f"{label} (norm by max)"
                else:
                    df_new = df.copy()
                    df_new.iloc[:, 1] = df_new.iloc[:, 1] / value
                    new_label = f"{label} (norm)"
                
                self.plotted_curves[new_label] = df_new
                self.curve_list.addItem(new_label)
            except Exception as e:
                QMessageBox.warning(self, "Normalization Error", 
                                  f"Failed to normalize '{label}':\n{str(e)}")
        
        self.update_plot()

    def add_offset_to_curves(self):
        """Add offset to selected curves."""
        selected = self._get_selected_curves()
        if not selected:
            QMessageBox.information(self, "No Selection", 
                                  "Select curves to add offset (from Plotted or Loaded Columns).")
            return
        
        offset, ok = QInputDialog.getDouble(self, "Offset", "Enter offset value:", 
                                          0.0, -1000, 1000, 4)
        if not ok:
            return
        
        try:
            self._validate_numeric_input(offset, -1000, 1000)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return
        
        for label in selected:
            df = self.available_columns.get(label, self.plotted_curves.get(label))
            if df is None:
                continue
            
            try:
                df_new = add_offset(df, offset)
                new_label = f"{label} (+{offset})"
                self.plotted_curves[new_label] = df_new
                self.curve_list.addItem(new_label)
            except Exception as e:
                QMessageBox.warning(self, "Offset Error", 
                                  f"Failed to add offset to '{label}':\n{str(e)}")
        
        self.update_plot()

    def subtract_curves_action(self):
        """Subtract two selected curves."""
        selected = self._get_selected_curves()
        if len(selected) != 2:
            QMessageBox.warning(self, "Invalid Selection", 
                              "Select exactly 2 curves (from Plotted or Loaded Columns) to subtract.")
            return
        
        factor, ok = QInputDialog.getDouble(self, "Factor", 
                                          "Enter multiplication factor for curve B:", 
                                          1.0, -1000, 1000, 4)
        if not ok:
            return
        
        try:
            self._validate_numeric_input(factor, -1000, 1000)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return
        
        curve_a, curve_b = selected
        df_a = self.available_columns.get(curve_a, self.plotted_curves.get(curve_a))
        df_b = self.available_columns.get(curve_b, self.plotted_curves.get(curve_b))
        
        try:
            df_new = subtract_curves(df_a, df_b, factor)
            new_label = f"{curve_a} - {factor}·{curve_b}"
            self.plotted_curves[new_label] = df_new
            self.curve_list.addItem(new_label)
            self.update_plot()
        except Exception as e:
            QMessageBox.critical(self, "Subtraction Error", 
                               f"Failed to subtract curves:\n{str(e)}")

    def analyze_peaks_action(self):
        """Analyze peaks in selected fluorescence curves."""
        selected = self._get_selected_curves()
        if not selected:
            QMessageBox.information(self, "No Selection", 
                                  "Select curves to analyze peaks (from Plotted or Loaded Columns).")
            return
        
        if len(selected) > 1:
            QMessageBox.information(self, "Multiple Selection", 
                                  "Please select only one curve at a time for peak analysis.")
            return
        
        curve_name = selected[0]
        df = self.available_columns.get(curve_name, self.plotted_curves.get(curve_name))
        
        if df is None:
            QMessageBox.warning(self, "Data Error", f"Could not find data for curve '{curve_name}'")
            return
        
        try:
            # Perform combined peak and shoulder analysis (all called "peaks")
            print("🔍 Analyzing peaks (including shoulders)...")
            peak_results = find_peaks_and_shoulders_combined(df, max_total_peaks=3)
            
            # Mostrar información unificada
            print(f"📊 Found {peak_results['num_peaks_found']} peaks total")
            print(f"   - Traditional peaks: {peak_results.get('traditional_peaks_count', 0)}")
            print(f"   - Shoulder peaks: {peak_results.get('shoulder_peaks_count', 0)}")
            
            # Mostrar todos los picos (unificados)
            if peak_results.get('all_peaks'):
                print("📋 All peaks by wavelength:")
                for peak in peak_results['all_peaks']:
                    detection_type = peak.get('detection_type', 'unknown')
                    type_indicator = "(traditional)" if detection_type == 'traditional_peak' else "(shoulder)" if detection_type == 'shoulder_peak' else ""
                    print(f"   🔸 Peak {peak['display_id']}: {peak['wavelength']:.1f} nm, {peak['intensity']:.2f} a.u. {type_indicator}")
            
            # Store peak data for plotting
            self.peak_data[curve_name] = peak_results
            
            # Close existing dialog if open
            if curve_name in self.peak_dialogs:
                self.peak_dialogs[curve_name].close()
            
            # Create and show simple peak table
            dialog = SimplePeakTable(peak_results, curve_name, self)
            
            # Connect signal to update plot when peaks are removed
            dialog.peak_removed.connect(lambda: self._on_peak_removed(curve_name))
            
            # Store dialog reference and show
            self.peak_dialogs[curve_name] = dialog
            dialog.show()
            
            # Update plot to show peak markers
            self.update_plot()
            
        except Exception as e:
            QMessageBox.critical(self, "Peak Analysis Error", 
                               f"Failed to analyze peaks in '{curve_name}':\n{str(e)}")
    
    def _on_peak_removed(self, curve_name):
        """Handle peak removal by updating the plot."""
        if curve_name in self.peak_dialogs:
            # Update peak data from the dialog
            dialog = self.peak_dialogs[curve_name]
            self.peak_data[curve_name] = dialog.peak_results
            
            # Update plot
            self.update_plot()

    def rename_curve(self):
        """Rename a selected curve."""
        selected = self.curve_list.selectedItems()
        if len(selected) != 1:
            QMessageBox.warning(self, "Invalid Selection", 
                              "Select exactly one curve to rename.")
            return
        
        old_label = selected[0].text()
        new_label, ok = QInputDialog.getText(self, "Rename Curve", 
                                           "New name:", text=old_label)
        if ok and new_label and new_label != old_label:
            if new_label in self.plotted_curves:
                QMessageBox.warning(self, "Name Conflict", 
                                  f"A curve named '{new_label}' already exists.")
                return
            
            self.plotted_curves[new_label] = self.plotted_curves.pop(old_label)
            selected[0].setText(new_label)
            self.update_plot()

    def save_all_curves(self):
        """Save all plotted curves to CSV."""
        if not self.plotted_curves:
            QMessageBox.information(self, "No Data", "No curves to save.")
            return
        
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV files (*.csv)")
        if not path:
            return
        
        try:
            save_curves_to_csv(self.plotted_curves, path)
            QMessageBox.information(self, "Success", "CSV file saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save CSV:\n{str(e)}")

    def save_plot_as_jpg(self):
        """Save current plot as JPG image."""
        if not self.plotted_curves:
            QMessageBox.information(self, "No Plot", "No plot to save.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "JPG files (*.jpg)")
        if not path:
            return

        try:
            # Filter peak data to only include curves that are currently plotted
            current_peak_data = {name: peaks for name, peaks in self.peak_data.items() 
                               if name in self.plotted_curves}
            
            export_plot_as_jpg(self.plotted_curves, path, y_label=self.y_label, peak_data=current_peak_data)
            QMessageBox.information(self, "Success", "Plot saved successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save plot:\n{str(e)}")

    def _remove_item_from_list(self, list_widget, label):
        """Remove an item from a QListWidget by label."""
        for i in range(list_widget.count()):
            if list_widget.item(i).text() == label:
                list_widget.takeItem(i)
                break