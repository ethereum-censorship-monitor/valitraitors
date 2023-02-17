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
        old_relays["relays"] if old_relays is not None else {},
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
    all_slots = [block["slot"] for block in blocks]
    relays = {}
    for slot in all_slots:
        if str(slot) in old_relays:
            relays[str(slot)] = old_relays[str(slot)]
        else:
            relays[str(slot)] = set()

    slots_to_fetch = [slot for slot in all_slots if str(slot) not in old_relays]
    print(f"fetching {len(slots_to_fetch)} slots for {len(relay_apis)} relays")
    for api in relay_apis:
        slots = fetch_slots_for_relay(api, slots_to_fetch)
        for slot in slots:
            assert str(slot) in relays
            relays[str(slot)].add(api["name"])

    return {
        "fetched_from": fetched_from,
        "fetched_to": fetched_to,
        "relays": {s: sorted(rs) for s, rs in relays.items()},
    }


def fetch_slots_for_relay(relay, slots_to_fetch):
    all_slots_to_fetch = set(slots_to_fetch)
    remaining_slots_to_fetch = set(slots_to_fetch)
    fetched_slots = set()

    print(f'fetching {len(all_slots_to_fetch)} slots for relay {relay["name"]}')
    while len(remaining_slots_to_fetch) > 0:
        url_with_path = urllib.parse.urljoin(
            relay["url"], "/relay/v1/data/bidtraces/proposer_payload_delivered"
        )
        params = {
            "cursor": max(remaining_slots_to_fetch),
        }
        progress = 1 - (len(remaining_slots_to_fetch) / len(all_slots_to_fetch))
        print(f"requesting from slot {params['cursor']} ({progress * 100:.1f}%)")
        res = requests.get(url_with_path, params=params)
        res.raise_for_status()
        data = res.json()

        slots_by_relay = set(int(block["slot"]) for block in data)
        slot_range = set(range(min(slots_by_relay), params["cursor"] + 1))
        slots_not_by_relay = slot_range - slots_by_relay

        remaining_slots_to_fetch -= slot_range
        fetched_slots |= slots_by_relay

        if len(slots_by_relay) == 0 and len(remaining_slots_to_fetch) > 0:
            print(
                "empty response from relay {relay['url']}, but some slots still missing"
            )
            break
    return sorted(fetched_slots & all_slots_to_fetch)


def write_relays(config, relays):
    with open(config.RELAYS_PATH, "w") as f:
        json.dump(relays, f)


if __name__ == "__main__":
    main()
