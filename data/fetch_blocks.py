from dotenv import load_dotenv

load_dotenv()

from dataclasses import dataclass, fields
import os
import json
import urllib.parse
import requests


GENESIS_TIME = 1606824023


@dataclass
class Config:
    TXS_PATH: str
    BLOCKS_PATH: str
    CONSENSUS_API_URL: str

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

    txs = read_txs(config)
    last_blocks = read_blocks(config)

    if txs is None:
        delete_blocks(config)
        return

    t0 = txs["fetched_from"]
    t1 = txs["fetched_to"]
    blocks = fetch_blocks(config, t0, t1, last_blocks)
    write_blocks(
        config,
        {
            "fetched_from": t0,
            "fetched_to": t1,
            "blocks": blocks,
        },
    )


def read_txs(config):
    try:
        with open(config.TXS_PATH) as f:
            return json.load(f)
    except IOError:
        return None


def read_blocks(config):
    try:
        with open(config.BLOCKS_PATH) as f:
            return json.load(f)
    except IOError:
        return None


def delete_blocks(config):
    try:
        os.remove(config.BLOCKS_PATH)
    except FileNotFoundError:
        pass


def write_blocks(config, blocks):
    with open(config.BLOCKS_PATH, "w") as f:
        json.dump(blocks, f)


def fetch_blocks(config, t0, t1, last_blocks):
    s0 = time_to_slot_ceil(t0)
    s1 = time_to_slot_floor(t1)

    if last_blocks is not None:
        last_blocks_by_slot = {block["slot"]: block for block in last_blocks["blocks"]}
    else:
        last_blocks_by_slot = {}

    slots = list(range(s0, s1 + 1))
    blocks_by_slot = {}
    uncached_slots = []
    for slot in slots:
        if slot in last_blocks_by_slot:
            blocks_by_slot[slot] = last_blocks_by_slot[slot]
        else:
            uncached_slots.append(slot)

    print(
        f"looking for blocks for between {s0} and {s1}, {len(blocks_by_slot)} cached, {len(uncached_slots)} to fetch"
    )
    for i, slot in enumerate(uncached_slots):
        print(f"fetching block for slot {slot} ({i / len(uncached_slots) * 100:.1f}%)")
        res = fetch_block_by_slot(config, slot)
        if res is not None:
            msg = res["data"]["message"]
            exec = msg["body"]["execution_payload"]
            block = {
                "slot": slot,
                "missed": False,
                "block_number": int(exec["block_number"]),
                "block_hash": exec["block_hash"],
                "fee_recipient": exec["fee_recipient"],
            }
        else:
            block = {
                "slot": slot,
                "missed": True,
                "block_number": None,
                "block_hash": None,
                "fee_recipient": None,
            }
        blocks_by_slot[slot] = block
    print("done")

    blocks = sorted(blocks_by_slot.values(), key=lambda b: b["slot"])
    return blocks


def time_to_slot_floor(t):
    return (t - GENESIS_TIME) // 12


def time_to_slot_ceil(t):
    return ((t - GENESIS_TIME) + 12 - 1) // 12


def fetch_block_by_slot(config, slot):
    url = urllib.parse.urljoin(
        config.CONSENSUS_API_URL, f"/eth/v2/beacon/blocks/{slot}"
    )
    res = requests.get(url)
    if res.status_code == 404:
        return None
    else:
        res.raise_for_status()
        return res.json()


if __name__ == "__main__":
    main()
