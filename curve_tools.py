import numpy as np
import pandas as pd
from scipy.signal import savgol_filter


def normalize_curve(df):
    """Return a normalized copy of a curve."""
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None")
    
    if df.shape[1] < 2:
        raise ValueError("DataFrame must have at least 2 columns (X, Y)")
    
    df_new = df.copy()
    y_values = pd.to_numeric(df_new.iloc[:, 1], errors="coerce")
    
    if np.any(np.isnan(y_values)):
        raise ValueError("Y values contain non-numeric data")
    
    max_value = y_values.max()
    if max_value == 0:
        raise ValueError("Cannot normalize: maximum Y value is zero")
    
    df_new.iloc[:, 1] = y_values / max_value
    return df_new


def add_offset(df, offset):
    """Return a copy of a curve with an offset applied."""
    if df is None or df.empty:
        raise ValueError("Input DataFrame is empty or None")
    
    if df.shape[1] < 2:
        raise ValueError("DataFrame must have at least 2 columns (X, Y)")
    
    df_new = df.copy()
    y_values = pd.to_numeric(df_new.iloc[:, 1], errors="coerce")
    
    if np.any(np.isnan(y_values)):
        raise ValueError("Y values contain non-numeric data")
    
    df_new.iloc[:, 1] = y_values + offset
    return df_new

def subtract_curves(df1, df2, factor):
    """Subtract two curves with a multiplication factor applied to the second curve."""
    try:
        # Validate inputs
        if df1 is None or df2 is None:
            raise ValueError("Both curves must be provided")
        
        if df1.shape[1] < 2 or df2.shape[1] < 2:
            raise ValueError("Both curves must have at least 2 columns (X, Y)")
        
        # Get column names dynamically (first = X, second = Y)
        x_col_1, y_col_1 = df1.columns[0], df1.columns[1]
        x_col_2, y_col_2 = df2.columns[0], df2.columns[1]

        # Convert X to numeric
        x1 = pd.to_numeric(df1[x_col_1], errors="coerce").values
        x2 = pd.to_numeric(df2[x_col_2], errors="coerce").values

        # Remove NaN values
        if np.any(np.isnan(x1)) or np.any(np.isnan(x2)):
            raise ValueError("X values contain non-numeric data")
        
        # Check if curves have the same length
        if len(x1) != len(x2):
            raise ValueError(f"Curves have different lengths: {len(x1)} vs {len(x2)}")

        # Check if X values match within tolerance
        if not np.allclose(x1, x2, rtol=1e-5, atol=1e-8):
            raise ValueError("X values do not match between curves")

        # Convert Y values to numeric
        y1 = pd.to_numeric(df1[y_col_1], errors="coerce")
        y2 = pd.to_numeric(df2[y_col_2], errors="coerce")
        
        if np.any(np.isnan(y1)) or np.any(np.isnan(y2)):
            raise ValueError("Y values contain non-numeric data")

        # Subtract Y values
        result = pd.DataFrame({
            x_col_1: x1,
            y_col_1: y1 - factor * y2
        })
        return result

    except Exception as e:
        raise RuntimeError(f"Subtraction failed: {e}")










