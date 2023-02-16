import fetch_txs
import fetch_blocks
import fetch_relays
import fetch_validator_pubkeys
import create_depositor_leaderboard
import create_builder_leaderboard
import create_relay_leaderboard


def main():
    fetch_txs.main()
    fetch_blocks.main()
    fetch_relays.main()
    fetch_validator_pubkeys.main()
    create_depositor_leaderboard.main()
    create_builder_leaderboard.main()
    create_relay_leaderboard.main()


if __name__ == "__main__":
    main()
