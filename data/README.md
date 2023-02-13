# Read Me

This directory contains a couple of scripts that collects data and aggregates
them to be displayed by a frontend. The scripts are:

- `fetch_txs.py`: Fetches censored txs from the monitor in a certain time
  interval, e.g. the past 7 days.
- `fetch_blocks.py`: Fetches the blocks corresponding to the transactions
  fetched by `fetch_txs.py`.
- `fetch_relays.py`: Fetches the relays that relayed the blocks in a
  `blocks.json` file created by `fetch_blocks.py`. To this end, it scrapes the
  APIs of the relays defined in a `relay_apis.json` file.
- `fetch_validator_pubkeys.py`: Fetch the public keys for all validators from a
  consensus node.
- `create_builder_leaderboard.py`: Takes txs and blocks fetched with above two
  scripts and aggregates it into a builder leaderboard. Builders are identified
  by the fee recipient. Known builders are furnished with a name from the
  manually created `builders.json` file (based on https://www.mev.to/builders).
- `create_relay_leaderboard.py`: Similar to `create_builder_leaderboard.py`,
  but for relays.
