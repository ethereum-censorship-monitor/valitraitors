from dotenv import load_dotenv

load_dotenv()

from dataclasses import dataclass, fields
import os
import json
import urllib.parse
import requests


@dataclass
class Config:
    BLOCKS_PATH: str
    RELAY_APIS_PATH: str
    RELAYS_PATH: str

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

    blocks = read_blocks(config)
    old_relays = read_relays(config)
    relay_apis = read_relay_apis(config)

    relays = fetch_relays(
        blocks["blocks"],
        relay_apis,
        old_relays,
        blocks["fetched_from"],
        blocks["fetched_to"],
    )
    write_relays(config, relays)


def read_blocks(config):
    with open(config.BLOCKS_PATH) as f:
        return json.load(f)


def read_relays(config):
    try:
        with open(config.RELAYS_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def read_relay_apis(config):
    with open(config.RELAY_APIS_PATH) as f:
        return json.load(f)


def fetch_relays(blocks, relay_apis, old_relays, fetched_from, fetched_to):
    slots = [block["slot"] for block in blocks]
    relays = {}
    for slot in slots:
        if slot in (old_relays or []):
            relays[slot] = old_relays[slot]

    slots_to_fetch = [slot for slot in slots if slot not in relays]
    min_slot = min(slots_to_fetch)
    max_slot = max(slots_to_fetch)

    print(f"fetching slots for {len(relay_apis)} relays")
    for api in relay_apis:
        slots = fetch_slots_for_relay(api, min_slot, max_slot)
        for slot in slots:
            relays[slot] = api["name"]
    print("done")

    for slot in slots:
        if slot not in relays:
            relays[slot] = None

    return {
        "fetched_from": fetched_from,
        "fetched_to": fetched_to,
        "relays": relays,
    }


def fetch_slots_for_relay(relay, min_slot, max_slot):
    slots = []
    cursor = max_slot
    print(f'fetching slots by relay {relay["name"]} between {min_slot} and {max_slot}')
    while True:
        url_with_path = urllib.parse.urljoin(
            relay["url"], "/relay/v1/data/bidtraces/proposer_payload_delivered"
        )
        params = {
            "cursor": cursor,
        }
        print(
            f"requesting from slot {cursor} ({(max_slot - cursor) / (max_slot - min_slot) * 100:.1f}%)"
        )
        res = requests.get(url_with_path, params=params)
        res.raise_for_status()
        data = res.json()

        new_slots = [int(block["slot"]) for block in data]
        slots.extend([slot for slot in new_slots if min_slot <= slot <= max_slot])

        if len(new_slots) == 0 or min(new_slots) <= min_slot:
            break
        cursor = min(new_slots) - 1
    return sorted(set(slots))


def write_relays(config, relays):
    with open(config.RELAYS_PATH, "w") as f:
        json.dump(relays, f)


if __name__ == "__main__":
    main()
