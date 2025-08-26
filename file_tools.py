import pandas as pd
import os

def save_curves_to_csv(curves, filename):
    """Save all curves to AppEspectros/csv or fallback to current dir."""
    folder = "csv"
    if os.path.exists("AppEspectros"):
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)
    else:
        path = filename  # Save in working directory

    if not curves:
        return

    df_out = pd.DataFrame()
    for i, (label, df) in enumerate(curves.items()):
        if i == 0:
            df_out[df.columns[0]] = df.iloc[:, 0]
        df_out[label] = df.iloc[:, 1].values

    df_out.to_csv(path, index=False)
    return path
