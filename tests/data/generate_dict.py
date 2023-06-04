import csv


def generate_dict_from_csv():
    """Uses CSV to generate a dict be used as input fopr all other generation"""
    candles = []
    with open("tests/data/NASDAQ.csv", newline="") as original:
        data = csv.reader(original, delimiter=",")

        for row in data:
            if "open" in row[1]:
                continue
            candles.append(
                {
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": int(row[6]),
                }
            )
    return candles


if __name__ == "__main__":
    print(generate_dict_from_csv())
