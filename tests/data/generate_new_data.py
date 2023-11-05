import json
import random
from datetime import datetime, timedelta

AMOUNT = 500


def save_json_result(data: list):
    with open("tests/data/test_candles.json", "w") as json_file:
        json.dump(
            data,
            json_file,
            indent=4,
        )


def generate():
    data = []
    start = datetime.now()
    for i in range(AMOUNT):
        data.append(
            {
                "open": random.randint(0, 9000000),
                "high": random.randint(0, 9000000),
                "low": random.randint(0, 9000000),
                "close": random.randint(0, 9000000),
                "volume": random.randint(0, 10000),
                "timestamp": start + timedelta(minutes=i),
            },
        )

    save_json_result(data)


if __name__ == "__main__":
    generate()
