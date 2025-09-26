import os

import pandas as pd


def save_curves_to_csv(curves, filename):
    """Save all curves to a CSV file."""
    if not curves:
        return
    
    # Ensure filename has .csv extension
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    # Create output directory if needed
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    df_out = pd.DataFrame()
    for i, (label, df) in enumerate(curves.items()):
        if i == 0:
            df_out[df.columns[0]] = df.iloc[:, 0]
        df_out[label] = df.iloc[:, 1].values

    df_out.to_csv(filename, index=False)
    return filename
