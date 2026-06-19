import csv
from datetime import datetime

def save_scan(threat, risk, text):

    with open(
        "scan_history.csv",
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                datetime.now(),
                threat,
                risk,
                text
            ]
        )