import fetch_txs
import fetch_blocks
import fetch_relays
import fetch_validator_pubkeys
import fetch_lido
import create_depositor_leaderboard
import create_builder_leaderboard
import create_relay_leaderboard
import create_lido_leaderboard


def main():
    print("fetching txs...")
    fetch_txs.main()
    print("fetching blocks...")
    fetch_blocks.main()
    print("fetching relays...")
    fetch_relays.main()
    print("fetching validator pubkeys...")
    fetch_validator_pubkeys.main()
    print("fetching lido...")
    fetch_lido.main()
    print("creating depositor leaderboard...")
    create_depositor_leaderboard.main()
    print("creating builder leaderboard...")
    create_builder_leaderboard.main()
    print("creating relay leaderboard...")
    create_relay_leaderboard.main()
    print("creating lido leaderboard...")
    create_lido_leaderboard.main()
    print("done.")


if __name__ == "__main__":
    main()
