import pandas as pd

def load_data():

    return pd.read_csv(
        "scan_history.csv",
        header=None
    )