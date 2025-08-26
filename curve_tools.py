import pandas as pd
import numpy as np
def normalize_curve(df):
    """Return a normalized copy of a curve."""
    df_new = df.copy()
    df_new.iloc[:, 1] = df_new.iloc[:, 1] / df_new.iloc[:, 1].max()
    return df_new

def add_offset(df, offset):
    """Return a copy of a curve with an offset applied."""
    df_new = df.copy()
    df_new.iloc[:, 1] = df_new.iloc[:, 1] + offset
    return df_new

def subtract_curves(df1, df2, factor):
    try:
        # Get column names dynamically (first = X, second = Y)
        x_col_1, y_col_1 = df1.columns[0], df1.columns[1]
        x_col_2, y_col_2 = df2.columns[0], df2.columns[1]

        # Convert X to numeric
        x1 = pd.to_numeric(df1[x_col_1], errors="coerce").values
        x2 = pd.to_numeric(df2[x_col_2], errors="coerce").values

        # Check if X values match within tolerance
        if not np.allclose(x1, x2, rtol=1e-5, atol=1e-8):
            raise ValueError("X values do not match between curves.")

        # Subtract Y values
        result = pd.DataFrame({
            x_col_1: x1,
            y_col_1: df1[y_col_1] - factor * df2[y_col_2]
        })
        return result

    except Exception as e:
        raise RuntimeError(f"Subtraction failed: {e}")