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
    LIDO_OPERATOR_PUBKEYS_PATH: str
    LIDO_OPERATOR_NAMES_PATH: str
    LIDO_LEADERBOARD_PATH: str

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
    operator_pubkeys = read_operator_pubkeys(config)
    operator_names = read_operator_names(config)

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
    operator_pubkeys = operator_pubkeys["operator_pubkeys"]

    operators = join_validator_index_with_operator(
        validator_pubkeys, operator_pubkeys, operator_names
    )
    misses_by_validator_index = count_misses_by_validator_index(txs, blocks)
    misses_by_operator = aggregate_misses_by_operator(
        misses_by_validator_index, validator_pubkeys, operator_names, operators
    )

    operator_market_shares = compute_operator_market_shares(
        blocks, validator_pubkeys, operator_names, operators
    )
    operator_leaderboard = create_operator_leaderboard(
        config,
        misses_by_operator,
        operator_market_shares,
        fetched_from,
        fetched_to,
    )
    write_operator_leaderboard(config, operator_leaderboard)


def read_txs(config):
    with open(config.TXS_PATH) as f:
        return json.load(f)


def read_blocks(config):
    with open(config.BLOCKS_PATH) as f:
        return json.load(f)


def read_validator_pubkeys(config):
    with open(config.VALIDATOR_PUBKEYS_PATH) as f:
        return json.load(f)


def read_operator_pubkeys(config):
    with open(config.LIDO_OPERATOR_PUBKEYS_PATH) as f:
        return json.load(f)


def read_operator_names(config):
    with open(config.LIDO_OPERATOR_NAMES_PATH) as f:
        return json.load(f)


def join_validator_index_with_operator(
    validator_pubkeys, operator_pubkeys, operator_names
):
    pubkey_to_operator_id = {
        pubkey: int(operator_index)
        for operator_index, pubkeys in operator_pubkeys.items()
        for pubkey in pubkeys
    }
    pubkey_to_operator_name = {
        pubkey: operator_names.get(str(operator_id), str(operator_id))
        for pubkey, operator_id in pubkey_to_operator_id.items()
    }
    validator_index_to_operator = {}
    for index, pubkey in validator_pubkeys.items():
        if pubkey in pubkey_to_operator_name:
            validator_index_to_operator[int(index)] = pubkey_to_operator_name[pubkey]
    return validator_index_to_operator


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
            counts[int(validator_index)] = counts.get(validator_index, 0) + 1
    return counts


def aggregate_misses_by_operator(
    misses_by_validator_index, validator_pubkeys, operator_names, operators
):
    misses_by_operator = {}
    for validator_index, count in misses_by_validator_index.items():
        try:
            operator_name = operators[int(validator_index)]
        except KeyError:
            pass
        else:
            misses_by_operator[operator_name] = (
                misses_by_operator.get(operator_name, 0) + count
            )
    for operator_name in operator_names.values():
        if operator_name not in misses_by_operator:
            misses_by_operator[operator_name] = 0
    return misses_by_operator


def compute_operator_market_shares(
    blocks, validator_pubkeys, operator_names, operators
):
    blocks_by_operator = {}
    num_missed = 0
    for block in blocks:
        if block["missed"]:
            num_missed += 1
            continue
        proposer_index = int(block["proposer_index"])
        if proposer_index not in operators:
            continue
        operator = operators[proposer_index]
        blocks_by_operator[operator] = blocks_by_operator.get(operator, 0) + 1

    for operator_name in operator_names.values():
        if operator_name not in blocks_by_operator:
            blocks_by_operator[operator_name] = 0

    shares = {
        operator: num_blocks / (len(blocks) - num_missed)
        for operator, num_blocks in blocks_by_operator.items()
    }
    return shares


def create_operator_leaderboard(
    config, num_misses_by_operator, operator_market_shares, fetched_from, fetched_to
):
    leaderboard_unordered = []
    for operator, count in num_misses_by_operator.items():
        share = operator_market_shares[operator]
        leaderboard_unordered.append(
            {
                "operator": operator,
                "num_misses": count,
                "market_share": share,
                "weighted_num_misses": count / share / 100,
            }
        )
    leaderboard = sorted(leaderboard_unordered, key=lambda r: -r["num_misses"])
    return {
        "fetched_from": fetched_from,
        "fetched_to": fetched_to,
        "lido_leaderboard": leaderboard,
    }


def write_operator_leaderboard(config, leaderboard):
    with open(config.LIDO_LEADERBOARD_PATH, "w") as f:
        json.dump(leaderboard, f)


if __name__ == "__main__":
    main()
