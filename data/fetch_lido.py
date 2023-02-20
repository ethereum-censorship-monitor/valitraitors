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


NODE_OPERATOR_REGISTRY_ADDRESS = "0x55032650b14df07b85bf18a3a3ec8e0af2e028d5"
SIGNING_KEY_ADDED_TOPIC = (
    "0xc77a17d6b857abe6d6e6c37301621bc72c4dd52fa8830fb54dfa715c04911a89"
)
NODE_OPERATORS_REGISTRY_DEPLOY_BLOCK = 11473216
REORG_DELAY = 10


@dataclass
class Config:
    LIDO_OPERATOR_PUBKEYS_PATH: str
    EXECUTION_API_URL: str
    NUM_BLOCKS_PER_LOGS_REQUEST: int

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
    old_node_operators = read_node_operators(config)
    fetch_range = get_fetch_range(config, old_node_operators)
    new_node_operators = fetch_node_operators(config, fetch_range)
    all_node_operators = merge_node_operators(old_node_operators, new_node_operators)
    write_node_operators(
        config,
        {
            "operator_pubkeys": all_node_operators,
            "fetched_until_block": fetch_range[1],
        },
    )


def read_node_operators(config):
    try:
        with open(config.LIDO_OPERATOR_PUBKEYS_PATH) as f:
            return json.load(f)
    except IOError:
        return None


def write_node_operators(config, node_operators):
    with open(config.LIDO_OPERATOR_PUBKEYS_PATH, "w") as f:
        json.dump(node_operators, f)


def get_fetch_range(config, old_node_operators):
    if old_node_operators is None:
        from_block = NODE_OPERATORS_REGISTRY_DEPLOY_BLOCK
    else:
        from_block = old_node_operators["fetched_until_block"]
    to_block = get_current_block(config) + 1 - REORG_DELAY
    return (from_block, max(to_block, from_block))


def get_current_block(config):
    params = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1,
    }
    res = requests.post(config.EXECUTION_API_URL, json=params)
    res.raise_for_status()
    data = res.json()
    return int(data["result"], 16)


def fetch_node_operators(config, fetch_range):
    logs = fetch_signing_key_added_logs(config, fetch_range)
    operator_ids_to_pubkeys = {}
    for log in logs:
        operator_id, pubkey = parse_log(log)
        if operator_id not in operator_ids_to_pubkeys:
            operator_ids_to_pubkeys[operator_id] = set()
        operator_ids_to_pubkeys[operator_id].add(pubkey)
    return {
        operator_id: sorted(pubkeys)
        for operator_id, pubkeys in operator_ids_to_pubkeys.items()
    }


def parse_log(log):
    operator_id = parse_operator_id(log["topics"][1])
    pubkey = parse_pubkey(log["data"])
    return operator_id, pubkey


def parse_operator_id(operator_id):
    assert operator_id[:2] == "0x"
    operator_id_bytes = bytes.fromhex(operator_id[2:])
    return int.from_bytes(operator_id_bytes, "big")


def parse_pubkey(pubkey):
    assert pubkey[:2] == "0x"
    pubkey_bytes = bytes.fromhex(pubkey[2:])
    pubkey_without_selector = pubkey_bytes[32:]
    length = int.from_bytes(pubkey_without_selector[:32], "big")
    padded_pubkey = pubkey_without_selector[32:]
    unpadded_pubkey = padded_pubkey[:length]
    pubkey_hex = "0x" + unpadded_pubkey.hex()
    return pubkey_hex


def fetch_signing_key_added_logs(config, fetch_range):
    num_blocks = fetch_range[1] - fetch_range[0]
    print(
        f"fetching signing key logs in {num_blocks} blocks from {fetch_range[0]} to {fetch_range[1]}..."
    )
    logs = []
    for from_block in range(
        fetch_range[0], fetch_range[1], config.NUM_BLOCKS_PER_LOGS_REQUEST
    ):
        to_block = min(
            from_block + config.NUM_BLOCKS_PER_LOGS_REQUEST, fetch_range[1] - 1
        )
        params = {
            "jsonrpc": "2.0",
            "method": "eth_getLogs",
            "params": [
                {
                    "fromBlock": f"0x{from_block:x}",
                    "toBlock": f"0x{to_block:x}",
                    "address": NODE_OPERATOR_REGISTRY_ADDRESS,
                    "topics": [SIGNING_KEY_ADDED_TOPIC],
                }
            ],
            "id": 1,
        }
        res = requests.post(config.EXECUTION_API_URL, json=params)
        res.raise_for_status()
        data = res.json()
        if "error" in data:
            raise ValueError(
                f"request with params {params['params']} failed: {data['error']}"
            )
        logs.extend(data["result"])
        progress = (to_block - fetch_range[0]) / num_blocks
        print(f"{progress * 100:.1f}% (got {len(logs)} logs so far)")
        if len(logs) > 0:
            break
    return logs


def merge_node_operators(old_node_operators, new_node_operators):
    if old_node_operators is None:
        return new_node_operators
    return {**old_node_operators["operator_pubkeys"], **new_node_operators}


if __name__ == "__main__":
    main()
