from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QMessageBox, QFileDialog, QInputDialog, QSizePolicy
from PyQt5.QtWebEngineWidgets import QWebEngineView
from loader_uv import load_spectra_file
from plotter import plot_spectra, export_plot_as_jpg
from curve_tools import normalize_curve, add_offset, subtract_curves
from file_tools import save_curves_to_csv

class SpectraViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spectra Viewer (UV)")
        self.resize(1200, 750)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.available_columns = {}
        self.plotted_curves = {}

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

        # Delete selected columns
        self.delete_column_btn = QPushButton("Delete Selected Columns")
        self.delete_column_btn.clicked.connect(self.delete_selected_columns)
        left_panel.addWidget(self.delete_column_btn)

        # Plot selected columns
        self.plot_btn = QPushButton("Plot Selected Columns")
        self.plot_btn.clicked.connect(self.plot_selected_columns)
        left_panel.addWidget(self.plot_btn)

        # Plotted curves
        left_panel.addWidget(QLabel("Plotted Curves"))
        self.curve_list = QListWidget()
        self.curve_list.setSelectionMode(QListWidget.MultiSelection)
        left_panel.addWidget(self.curve_list)

        # Delete selected curves
        self.delete_curve_btn = QPushButton("Delete Selected Curves")
        self.delete_curve_btn.clicked.connect(self.delete_selected_curves)
        left_panel.addWidget(self.delete_curve_btn)

        # Normalize
        self.norm_btn = QPushButton("Normalize")
        self.norm_btn.clicked.connect(self.normalize_selected_curves)
        left_panel.addWidget(self.norm_btn)

        # Add offset
        self.offset_btn = QPushButton("Add Offset")
        self.offset_btn.clicked.connect(self.add_offset_to_curves)
        left_panel.addWidget(self.offset_btn)

        # Subtract curves
        self.subtract_btn = QPushButton("Subtract A - k·B")
        self.subtract_btn.clicked.connect(self.subtract_curves_action)
        left_panel.addWidget(self.subtract_btn)

        # Rename curve
        self.rename_curve_btn = QPushButton("Rename Curve")
        self.rename_curve_btn.clicked.connect(self.rename_curve)
        left_panel.addWidget(self.rename_curve_btn)

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

        main_layout.addLayout(left_panel,stretch=1)

        # Plot area
        self.plot_view = QWebEngineView()
        self.plot_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_view.setMinimumSize(600, 400)
        main_layout.addWidget(self.plot_view, stretch=3)

    def _get_selected_curves(self):
        selected = [item.text() for item in self.curve_list.selectedItems()]
        if not selected:
            selected = [item.text() for item in self.column_list.selectedItems()]
        return selected

    def load_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Data files (*.csv *.xls *.xlsx)")
        if not path:
            return
        try:
            spectra = load_spectra_file(path)
            for label, df in spectra.items():
                if label not in self.available_columns:
                    self.available_columns[label] = df
                    self.column_list.addItem(label)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def plot_selected_columns(self):
        selected = [item.text() for item in self.column_list.selectedItems()]
        if not selected:
            return
        for label in selected:
            if label not in self.plotted_curves:
                self.plotted_curves[label] = self.available_columns[label]
                self.curve_list.addItem(label)
        self.update_plot()

    def update_plot(self):
        if not self.plotted_curves:
            self.plot_view.setHtml("<h3 style='text-align:center;'>No curves plotted</h3>")
            return
        fig = plot_spectra(self.plotted_curves, y_label="Absorbance (a.u.)")
        self.plot_view.setHtml(fig.to_html(include_plotlyjs="cdn"))

    def delete_selected_columns(self):
        selected = [item.text() for item in self.column_list.selectedItems()]
        for label in selected:
            if label in self.available_columns:
                del self.available_columns[label]
            if label in self.plotted_curves:
                del self.plotted_curves[label]
                self._remove_item_from_list(self.curve_list, label)
            self._remove_item_from_list(self.column_list, label)
        self.update_plot()

    def delete_selected_curves(self):
        selected = [item.text() for item in self.curve_list.selectedItems()]
        for label in selected:
            if label in self.plotted_curves:
                del self.plotted_curves[label]
                self._remove_item_from_list(self.curve_list, label)
        self.update_plot()

    def clear_all_curves(self):
        self.plotted_curves.clear()
        self.curve_list.clear()
        self.available_columns.clear()
        self.column_list.clear()
        self.update_plot()

    def normalize_selected_curves(self):
        selected = self._get_selected_curves()
        if not selected:
            QMessageBox.information(self, "Info", "Select curves to normalize (from Plotted or Loaded Columns).")
            return
        value, ok = QInputDialog.getDouble(self, "Normalization", "Enter normalization value (0 = use max):", 0.0, 0, 1e6, 4)
        if not ok:
            return
        for label in selected:
            df = self.available_columns.get(label, self.plotted_curves.get(label))
            if df is None:
                continue
            if value == 0:
                df_new = normalize_curve(df)
                new_label = f"{label} (norm by max)"
            else:
                df_new = df.copy()
                df_new.iloc[:, 1] = df_new.iloc[:, 1] / value
                new_label = f"{label} (norm)"
            self.plotted_curves[new_label] = df_new
            self.curve_list.addItem(new_label)
        self.update_plot()

    def add_offset_to_curves(self):
        selected = self._get_selected_curves()
        if not selected:
            QMessageBox.information(self, "Info", "Select curves to add offset (from Plotted or Loaded Columns).")
            return
        offset, ok = QInputDialog.getDouble(self, "Offset", "Enter offset value:", 0.0, -1000, 1000, 4)
        if not ok:
            return
        for label in selected:
            df = self.available_columns.get(label, self.plotted_curves.get(label))
            if df is None:
                continue
            df_new = add_offset(df, offset)
            new_label = f"{label} (+{offset})"
            self.plotted_curves[new_label] = df_new
            self.curve_list.addItem(new_label)
        self.update_plot()

    def subtract_curves_action(self):
        selected = self._get_selected_curves()
        if len(selected) != 2:
            QMessageBox.warning(self, "Warning", "Select exactly 2 curves (from Plotted or Loaded Columns) to subtract.")
            return
        factor, ok = QInputDialog.getDouble(self, "Factor", "Enter multiplication factor for curve B:", 1.0, -1000, 1000, 4)
        if not ok:
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
            QMessageBox.critical(self, "Error", str(e))

    def rename_curve(self):
        selected = self.curve_list.selectedItems()
        if len(selected) != 1:
            QMessageBox.warning(self, "Warning", "Select exactly one curve to rename.")
            return
        old_label = selected[0].text()
        new_label, ok = QInputDialog.getText(self, "Rename Curve", "New name:", text=old_label)
        if ok and new_label:
            self.plotted_curves[new_label] = self.plotted_curves.pop(old_label)
            selected[0].setText(new_label)
            self.update_plot()

    def save_all_curves(self):
        if not self.plotted_curves:
            QMessageBox.information(self, "Info", "No curves to save.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV files (*.csv)")
        if not path:
            return
        save_curves_to_csv(self.plotted_curves, path)
        QMessageBox.information(self, "Saved", "CSV file saved successfully.")

    def save_plot_as_jpg(self):
        if not self.plotted_curves:
            QMessageBox.information(self, "Info", "No plot to save.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "JPG files (*.jpg)")
        if not path:
            return

        # Exportar usando la función de plotter
        from plotter import export_plot_as_jpg
        export_plot_as_jpg(self.plotted_curves, path, y_label="Absorbance (a.u.)")

        QMessageBox.information(self, "Saved", "Plot saved successfully.")


    def _remove_item_from_list(self, list_widget, label):
        for i in range(list_widget.count()):
            if list_widget.item(i).text() == label:
                list_widget.takeItem(i)
                break



