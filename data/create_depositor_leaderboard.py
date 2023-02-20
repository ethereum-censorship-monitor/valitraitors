from dotenv import load_dotenv

load_dotenv()

from dataclasses import dataclass, fields
import os
import json


@dataclass
class Config:
    TXS_PATH: str
    BLOCKS_PATH: str
    VALIDATOR_PUBKEYS_PATH: str
    DEPOSITORS_PATH: str
    DEPOSITOR_LEADERBOARD_PATH: str
    MIN_DEPOSITOR_MARKET_SHARE: float

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
    blocks = read_blocks(config)
    validator_pubkeys = read_validator_pubkeys(config)
    depositors = read_depositors(config)

    if (txs["fetched_from"], txs["fetched_to"]) != (
        blocks["fetched_from"],
        blocks["fetched_to"],
    ):
        raise ValueError("blocks and txs time range mismatch")

    fetched_from = txs["fetched_from"]
    fetched_to = txs["fetched_to"]
    txs = txs["txs"]
    blocks = blocks["blocks"]
    validator_pubkeys = validator_pubkeys["pubkeys"]

    misses_by_validator_index = count_misses_by_validator_index(txs, blocks)
    misses_by_depositor = aggregate_misses_by_depositor(
        misses_by_validator_index, validator_pubkeys, depositors
    )

    depositor_market_shares = compute_depositor_market_shares(
        blocks, validator_pubkeys, depositors
    )
    depositor_leaderboard = create_depositor_leaderboard(
        config, misses_by_depositor, depositor_market_shares, fetched_from, fetched_to
    )
    write_depositor_leaderboard(config, depositor_leaderboard)


def read_txs(config):
    with open(config.TXS_PATH) as f:
        return json.load(f)


def read_blocks(config):
    with open(config.BLOCKS_PATH) as f:
        return json.load(f)


def read_validator_pubkeys(config):
    with open(config.VALIDATOR_PUBKEYS_PATH) as f:
        return json.load(f)


def read_depositors(config):
    with open(config.DEPOSITORS_PATH) as f:
        return json.load(f)


def count_misses_by_validator_index(txs, blocks):
    validator_index_by_block_hash = {
        block["block_hash"]: block["proposer_index"] for block in blocks
    }

    counts = {}
    for tx in txs:
        for block in tx["misses"]:
            block_hash = block["block_hash"]
            if block_hash not in validator_index_by_block_hash:
                # this may happen since a tx might have misses outside of the
                # time range (only one of the misses needs to be in the time
                # range for a tx to pass the filter)
                continue
            validator_index = validator_index_by_block_hash[block["block_hash"]]
            counts[validator_index] = counts.get(validator_index, 0) + 1
    return counts


def aggregate_misses_by_depositor(
    misses_by_validator_index, validator_pubkeys, depositors
):
    validator_index_to_depositor = {}
    for index, pubkey in validator_pubkeys.items():
        if pubkey in depositors:
            validator_index_to_depositor[int(index)] = depositors[pubkey]

    misses_by_depositor = {}
    for validator_index, count in misses_by_validator_index.items():
        try:
            depositor = validator_index_to_depositor[validator_index]
        except KeyError:
            pass
        else:
            misses_by_depositor[depositor] = (
                misses_by_depositor.get(depositor, 0) + count
            )

    return misses_by_depositor


def compute_depositor_market_shares(blocks, validator_pubkeys, depositors):
    blocks_by_depositor = {}
    num_missed = 0
    for block in blocks:
        if block["missed"]:
            num_missed += 1
            continue
        proposer_index = int(block["proposer_index"])
        if str(proposer_index) not in validator_pubkeys:
            continue
        proposer_pubkey = validator_pubkeys[str(proposer_index)]
        if proposer_pubkey not in depositors:
            continue
        depositor = depositors[proposer_pubkey]
        blocks_by_depositor[depositor] = blocks_by_depositor.get(depositor, 0) + 1

    shares = {
        depositor: num_blocks / (len(blocks) - num_missed)
        for depositor, num_blocks in blocks_by_depositor.items()
    }
    return shares


def create_depositor_leaderboard(
    config, misses_by_depositor, depositor_market_shares, fetched_from, fetched_to
):
    leaderboard_unordered = []
    for depositor, count in misses_by_depositor.items():
        share = depositor_market_shares[depositor]
        if share >= config.MIN_DEPOSITOR_MARKET_SHARE:
            leaderboard_unordered.append(
                {
                    "depositor": depositor,
                    "num_misses": count,
                    "market_share": share,
                    "weighted_num_misses": count / share / 100,
                }
            )
    leaderboard = sorted(leaderboard_unordered, key=lambda r: -r["num_misses"])
    return {
        "fetched_from": fetched_from,
        "fetched_to": fetched_to,
        "depositor_leaderboard": leaderboard,
    }


def write_depositor_leaderboard(config, leaderboard):
    with open(config.DEPOSITOR_LEADERBOARD_PATH, "w") as f:
        json.dump(leaderboard, f)


if __name__ == "__main__":
    main()
