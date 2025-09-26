import os
import pandas as pd
import re
import io

def load_fluo_file(path):
    """
    Load a fluorescence file (.txt or .csv) and return a dictionary {name: dataframe}.
    Each dataframe contains two columns: Wavelength and Intensity.
    Supports:
    1. Original .txt files with metadata (X Y pairs for multiple curves).
    2. CSVs saved from the app (one X column + multiple Y columns).
    """
    base_name = os.path.splitext(os.path.basename(path))[0]

    # --- CASE 1: CSV (exported from app) ---
    if path.endswith(".csv"):
        df = pd.read_csv(path)
        spectra = {}
        x = df.iloc[:, 0]

        for col in df.columns[1:]:
            label = f"{base_name}: {col}"
            spectra[label] = pd.DataFrame({
                df.columns[0]: x,
                col: df[col]
            }).dropna()

        return spectra

    # --- CASE 2: TXT (original format with metadata) ---
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find the header line that starts with "X"
    header_idx = next(i for i, line in enumerate(lines) if line.strip().startswith("X"))

    # Extract curve names from the line just before the "X Y" header
    label_line = re.split(r'\s{2,}|\t+', lines[header_idx - 1].strip())
    header_line = lines[header_idx].strip().split()
    num_curves = header_line.count("X")

    if len(label_line) < 2 * num_curves:
        raise ValueError("Number of labels does not match the number of detected curves")

    names = label_line[::2]  # Take only names (ignore Y labels or codes)

    # Read numeric data
    df = pd.read_csv(io.StringIO(''.join(lines[header_idx + 1:])), sep=r'\s+', header=None)

    spectra = {}
    for i, name in enumerate(names):
        x_idx, y_idx = 2 * i, 2 * i + 1
        if y_idx >= df.shape[1]:
            continue
        x = df.iloc[:, x_idx]
        y = df.iloc[:, y_idx]
        label = f"{base_name}: {name.strip()}"
        spectra[label] = pd.DataFrame({"Wavelength": x, "Intensity": y}).dropna()

    return spectra

