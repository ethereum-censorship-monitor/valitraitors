from dotenv import load_dotenv

load_dotenv()

from dataclasses import dataclass, fields
import os
import json


@dataclass
class Config:
    TXS_PATH: str
    RELAYS_PATH: str
    RELAY_LEADERBOARD_PATH: str
    MIN_RELAY_MARKET_SHARE: float

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
    relays = read_relays(config)

    if (txs["fetched_from"], txs["fetched_to"]) != (
        relays["fetched_from"],
        relays["fetched_to"],
    ):
        raise ValueError("txs and relays time range mismatch")

    fetched_from = txs["fetched_from"]
    fetched_to = txs["fetched_to"]
    txs = txs["txs"]
    relays = relays["relays"]

    misses_by_relay = count_misses_by_relay(txs, relays)
    relay_market_shares = compute_relay_market_shares(relays)

    relay_leaderboard = create_relay_leaderboard(
        config, misses_by_relay, relay_market_shares, fetched_from, fetched_to
    )
    write_relay_leaderboard(config, relay_leaderboard)


def read_txs(config):
    with open(config.TXS_PATH) as f:
        return json.load(f)


def read_relays(config):
    with open(config.RELAYS_PATH) as f:
        return json.load(f)


def count_misses_by_relay(txs, relays):
    counts = {}
    for tx in txs:
        for block in tx["misses"]:
            try:
                relay = relays[str(block["slot"])]
                counts[relay] = counts.get(relay, 0) + 1
            except KeyError:
                pass
    return counts


def compute_relay_market_shares(relays):
    counts = {}
    for _, relay in relays.items():
        counts[relay] = counts.get(relay, 0) + 1
    return {relay: count / len(relays) for relay, count in counts.items()}


def create_relay_leaderboard(
    config, misses_by_relay, relay_market_shares, fetched_from, fetched_to
):
    leaderboard_unordered = []
    for relay, count in misses_by_relay.items():
        share = relay_market_shares[relay]
        if share >= config.MIN_RELAY_MARKET_SHARE:
            leaderboard_unordered.append(
                {
                    "relay": relay,
                    "num_misses": count,
                    "market_share": share,
                    "weighted_num_misses": count / share / 100,
                }
            )
    leaderboard = sorted(leaderboard_unordered, key=lambda r: -r["num_misses"])
    return {
        "fetched_from": fetched_from,
        "fetched_to": fetched_to,
        "relay_leaderboard": leaderboard,
    }


def write_relay_leaderboard(config, leaderboard):
    with open(config.RELAY_LEADERBOARD_PATH, "w") as f:
        json.dump(leaderboard, f)


if __name__ == "__main__":
    main()
