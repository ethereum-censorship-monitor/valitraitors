from dotenv import load_dotenv

load_dotenv()

from dataclasses import dataclass, fields
import os
import json


@dataclass
class Config:
    TXS_PATH: str
    BLOCKS_PATH: str
    BUILDERS_PATH: str
    BUILDER_LEADERBOARD_PATH: str
    MIN_BUILDER_MARKET_SHARE: float

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
    builders = read_builders(config)

    if (txs["fetched_from"], txs["fetched_to"]) != (
        blocks["fetched_from"],
        blocks["fetched_to"],
    ):
        raise ValueError("blocks and txs time range mismatch")

    fetched_from = txs["fetched_from"]
    fetched_to = txs["fetched_to"]
    txs = txs["txs"]
    blocks = blocks["blocks"]

    misses_by_fee_recipient = count_misses_by_fee_recipient(txs, blocks)
    misses_by_builder = aggregate_misses_by_builder(misses_by_fee_recipient, builders)
    builder_market_shares = compute_builder_market_share(blocks, builders)

    builder_leaderboard = create_builder_leaderboard(
        config, misses_by_builder, builder_market_shares, fetched_from, fetched_to
    )
    write_builder_leaderboard(config, builder_leaderboard)


def read_txs(config):
    with open(config.TXS_PATH) as f:
        return json.load(f)


def read_blocks(config):
    with open(config.BLOCKS_PATH) as f:
        return json.load(f)


def read_builders(config):
    with open(config.BUILDERS_PATH) as f:
        return json.load(f)


def count_misses_by_fee_recipient(txs, blocks):
    fee_recipient_by_block_hash = {
        block["block_hash"]: block["fee_recipient"] for block in blocks
    }

    counts = {}
    for tx in txs:
        for block in tx["misses"]:
            block_hash = block["block_hash"]
            if block_hash not in fee_recipient_by_block_hash:
                # this may happen since a tx might have misses outside of the
                # time range (only one of the misses needs to be in the time
                # range for a tx to pass the filter)
                continue
            fee_recipient = fee_recipient_by_block_hash[block["block_hash"]]
            counts[fee_recipient] = counts.get(fee_recipient, 0) + 1
    return counts


def aggregate_misses_by_builder(misses_by_fee_recipient, builders):
    fee_recipient_to_builder = {}
    for builder in builders:
        for fee_recipient in builder["fee_recipients"]:
            fee_recipient_to_builder[fee_recipient.lower()] = builder["name"]

    misses_by_builder = {}
    for fee_recipient, count in misses_by_fee_recipient.items():
        try:
            builder = fee_recipient_to_builder[fee_recipient]
        except KeyError:
            pass
        else:
            misses_by_builder[builder] = misses_by_builder.get(builder, 0) + count

    return misses_by_builder


def compute_builder_market_share(blocks, builders):
    fee_recipient_to_builder = {}
    for builder in builders:
        for fee_recipient in builder["fee_recipients"]:
            fee_recipient_to_builder[fee_recipient.lower()] = builder["name"]

    blocks_by_builder = {}
    for block in blocks:
        fee_recipient = block["fee_recipient"]
        builder = fee_recipient_to_builder.get(fee_recipient, fee_recipient)
        blocks_by_builder[builder] = blocks_by_builder.get(builder, 0) + 1

    shares = {
        builder: num_blocks / len(blocks)
        for builder, num_blocks in blocks_by_builder.items()
    }
    return shares


def create_builder_leaderboard(
    config, num_blocks_by_builder, builder_market_shares, fetched_from, fetched_to
):
    leaderboard_unordered = []
    for builder, count in num_blocks_by_builder.items():
        share = builder_market_shares[builder]
        if share >= config.MIN_BUILDER_MARKET_SHARE:
            leaderboard_unordered.append(
                {
                    "builder": builder,
                    "num_misses": count,
                    "market_share": share,
                    "weighted_num_misses": count / share / 100,
                }
            )
    leaderboard = sorted(leaderboard_unordered, key=lambda r: -r["num_misses"])
    return {
        "fetched_from": fetched_from,
        "fetched_to": fetched_to,
        "builder_leaderboard": leaderboard,
    }


def write_builder_leaderboard(config, leaderboard):
    with open(config.BUILDER_LEADERBOARD_PATH, "w") as f:
        json.dump(leaderboard, f)


if __name__ == "__main__":
    main()
