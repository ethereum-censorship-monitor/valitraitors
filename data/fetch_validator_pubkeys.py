from dotenv import load_dotenv

load_dotenv()

from dataclasses import dataclass, fields
import os
import json
import copy
import urllib.parse
import requests


@dataclass
class Config:
    CONSENSUS_API_URL: str
    VALIDATOR_PUBKEYS_PATH: str
    NUM_VALIDATORS_PER_REQUEST: int

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

    old_pubkeys = read_pubkeys(config)
    pubkeys = fetch_pubkeys(config, old_pubkeys)
    write_pubkeys(config, pubkeys)


def read_pubkeys(config):
    try:
        with open(config.VALIDATOR_PUBKEYS_PATH) as f:
            return json.load(f)
    except IOError:
        return None


def write_pubkeys(config, pubkeys):
    with open(config.VALIDATOR_PUBKEYS_PATH, "w") as f:
        json.dump(pubkeys, f)


def fetch_pubkeys(config, old_pubkeys):
    slot = fetch_current_slot(config)
    if old_pubkeys is not None:
        if slot <= old_pubkeys["fetched_at_slot"]:
            raise ValueError("old pubkeys have been fetched in the future")
        old_pubkeys = old_pubkeys["pubkeys"]
    else:
        old_pubkeys = {}
    next_validator_index = max(old_pubkeys.keys(), default=0)
    new_pubkeys = fetch_pubkeys_from(config, slot, next_validator_index)
    return {
        "fetched_at_slot": slot,
        "pubkeys": {
            **old_pubkeys,
            **new_pubkeys,
        },
    }


def fetch_current_slot(config):
    url = urllib.parse.urljoin(config.CONSENSUS_API_URL, "/eth/v1/beacon/headers/head")
    res = requests.get(url)
    res.raise_for_status()
    data = res.json()
    return data["data"]["header"]["message"]["slot"]


def fetch_pubkeys_from(config, slot, validator_index):
    url = urllib.parse.urljoin(
        config.CONSENSUS_API_URL, f"/eth/v1/beacon/states/{slot}/validators"
    )
    pubkeys = {}
    i = validator_index
    while True:
        indices = list(range(i, i + config.NUM_VALIDATORS_PER_REQUEST))
        print(f"requesting validators from index {indices[0]} to {indices[-1]}")
        params = {
            "id": indices,
        }
        res = requests.get(url, params)
        res.raise_for_status()
        data = res.json()
        for v in data["data"]:
            pubkeys[int(v["index"])] = v["validator"]["pubkey"]
        if len(data["data"]) < len(indices):
            break
        i = max(pubkeys.keys()) + 1
    print(
        f"fetched validators from index {min(pubkeys.keys())} to {max(pubkeys.keys())}"
    )
    return pubkeys


if __name__ == "__main__":
    main()
