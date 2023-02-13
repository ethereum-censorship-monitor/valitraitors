import fs from 'fs';

export async function load({ params }) {
  const txsPath = import.meta.env.VITE_TXS_PATH;
  const txsBuffer = await fs.promises.readFile(txsPath);
  const txs = JSON.parse(txsBuffer);

  const builderLeaderboardPath = import.meta.env.VITE_BUILDER_LEADERBOARD_PATH;
  const builderLeaderboardBuffer = await fs.promises.readFile(builderLeaderboardPath);
  const builderLeaderboard = JSON.parse(builderLeaderboardBuffer);

  const relayLeaderboardPath = import.meta.env.VITE_RELAY_LEADERBOARD_PATH;
  const relayLeaderboardBuffer = await fs.promises.readFile(relayLeaderboardPath);
  const relayLeaderboard = JSON.parse(relayLeaderboardBuffer);

  if (
    txs.fetched_from != builderLeaderboard.fetched_from ||
    txs.fetched_from != relayLeaderboard.fetched_from ||
    txs.fetched_to != builderLeaderboard.fetched_to ||
    txs.fetched_to != relayLeaderboard.fetched_to
  ) {
    console.error('fetched from mismatch in data files');
  }

  return {
    txs: txs,
    builderLeaderboard: builderLeaderboard,
    relayLeaderboard: relayLeaderboard
  };
}
