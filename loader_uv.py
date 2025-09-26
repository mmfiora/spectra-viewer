import os
import pandas as pd

def load_spectra_file(path):
    # Read CSV or Excel without assuming header
    if path.endswith(".csv"):
        df = pd.read_csv(path, header=None)
    else:
        df = pd.read_excel(path, header=None)

    # Find the header row: first non-empty row
    header_row = None
    for idx, row in df.iterrows():
        if row.notna().sum() > 1:  # At least two non-empty cells (X and one Y)
            header_row = idx
            break

    if header_row is None:
        raise ValueError("No valid header row found in file.")

    # Read again using the detected header
    if path.endswith(".csv"):
        df = pd.read_csv(path, header=header_row)
    else:
        df = pd.read_excel(path, header=header_row)

    base_name = os.path.splitext(os.path.basename(path))[0]
    spectra = {}

    # First column is always wavelength (X)
    x = df.iloc[:, 0]

    # Loop over each Y column with the correct header
    for col in df.columns[1:]:
        label = f"{base_name}: {col}"
        spectra[label] = pd.DataFrame({
            df.columns[0]: x,
            col: df[col]
        }).dropna()

    return spectra
