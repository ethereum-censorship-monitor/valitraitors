from dotenv import load_dotenv

load_dotenv()

import os
import json
import itertools
from datetime import datetime, timezone, timedelta
import urllib.parse
import requests
from dataclasses import dataclass, fields
import time


@dataclass
class Config:
    ECM_API_URL: str
    DELAY: int
    MIN_NUM_MISSES: int
    PROPAGATION_TIME: int
    TXS_PATH: str
    INTERVAL: int

    @classmethod
    def load(cls):
        values = {}
        for field in fields(cls):
            value = os.getenv(field.name)
            if value is None:
                raise ValueError(f"environment variable {field.name} is not specified")
            values[field.name] = field.type(value)
        return cls(**values)


def main():
    config = Config.load()
    interval_to = now() - config.DELAY
    interval_from = interval_to - config.INTERVAL

    last_output = read_last_output(config)

    if last_output is not None:
        last_fetched_from = last_output["fetched_from"]
        last_fetched_to = last_output["fetched_to"]
        if not (
            last_fetched_from <= last_fetched_from
            or last_fetched_from <= interval_from
            or last_fetched_to <= interval_to
        ):
            raise ValueError("unexpected last fetch range")
        fetch_from = max(interval_from, last_fetched_to)
        fetch_to = interval_to

        old_txs = last_output["txs"]
    else:
        fetch_from = interval_from
        fetch_to = interval_to
        old_txs = []

    new_txs = fetch_txs(config, fetch_from, fetch_to)
    txs = filter_txs(merge_txs(new_txs, old_txs), interval_from)
    output = {
        "fetched_from": interval_from,
        "fetched_to": interval_to,
        "txs": txs,
        "propagation_time": config.PROPAGATION_TIME,
        "min_num_misses": config.MIN_NUM_MISSES,
    }
    write_output(config, output)


def read_last_output(config):
    try:
        with open(config.TXS_PATH) as f:
            return json.load(f)
    except IOError:
        return None


def write_output(config, output):
    with open(config.TXS_PATH, "w") as f:
        json.dump(output, f)


def now():
    return int(time.time())


def get_timestamp_from_query_bound(b):
    return int(str(b).split(",")[0])


def get_datetime_from_query_bound(b):
    t = get_timestamp_from_query_bound(b)
    return datetime.utcfromtimestamp(t)


def cmp_query_bounds(b1, b2):
    t1 = get_timestamp_from_query_bound(b1)
    t2 = get_timestamp_from_query_bound(b2)
    if t1 < t2:
        return -1
    elif t1 > t2:
        return 1
    else:
        return 0


def fetch_txs(config, fetch_from, fetch_to):
    fetch_from_datetime = get_datetime_from_query_bound(fetch_from)
    fetch_to_datetime = get_datetime_from_query_bound(fetch_to)
    fetch_interval = fetch_to_datetime - fetch_from_datetime
    if fetch_interval <= timedelta():
        return []

    url = urllib.parse.urljoin(config.ECM_API_URL, "/v0/txs")
    txs = []
    print(
        f"fetching txs in {fetch_interval} from {fetch_from_datetime} to {fetch_to_datetime}..."
    )
    while True:
        res = requests.get(
            url,
            params={
                "min_num_misses": config.MIN_NUM_MISSES,
                "propagation_time": config.PROPAGATION_TIME,
                "from": fetch_from,
                "to": fetch_to,
            },
        )
        res.raise_for_status()
        data = res.json()
        txs.extend(data["items"])

        if data["complete"]:
            break
        next_fetch_from = data["to"]
        next_fetch_from_datetime = get_datetime_from_query_bound(next_fetch_from)
        if next_fetch_from == fetch_from:
            raise ValueError(
                f"fetching stopped making progress at {next_fetch_from_datetime}"
            )
        progress = 1 - (fetch_to_datetime - next_fetch_from_datetime) / fetch_interval
        fetch_from = next_fetch_from
        print(f"{progress * 100:.1f}% ({len(txs)} txs)...")
    print(f"fetched {len(txs)} txs")
    return txs


def merge_txs(txs1, txs2):
    txs = []
    hashes = set()
    for tx in itertools.chain(txs1, txs2):
        if tx["tx_hash"] in hashes:
            continue
        txs.append(tx)
        hashes.add(tx["tx_hash"])
    return txs


def filter_txs(txs, low_cutoff):
    return [tx for tx in txs if tx["misses"][0]["proposal_time"] >= low_cutoff]


if __name__ == "__main__":
    main()
