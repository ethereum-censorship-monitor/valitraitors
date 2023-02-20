import fs from 'fs';
import { env } from '$env/dynamic/private';

async function loadJsonAtPath(path) {
  if (!path) {
    return null;
  }

  let buffer;
  try {
    buffer = await fs.promises.readFile(path);
  } catch (e) {
    console.error('failed to load file at ' + path + ': ' + e.toString());
    return null;
  }

  let data;
  try {
    data = JSON.parse(buffer);
  } catch (e) {
    console.error('failed to parse json at ' + path + ': ' + e.toString());
    return null;
  }
  return data;
}

export async function load({ params }) {
  const txs = await loadJsonAtPath(env.TXS_PATH);
  const depositorLeaderboard = await loadJsonAtPath(env.DEPOSITOR_LEADERBOARD_PATH);
  const builderLeaderboard = await loadJsonAtPath(env.BUILDER_LEADERBOARD_PATH);
  const relayLeaderboard = await loadJsonAtPath(env.RELAY_LEADERBOARD_PATH);
  const lidoLeaderboard = await loadJsonAtPath(env.LIDO_LEADERBOARD_PATH);

  return {
    txs: txs,
    depositorLeaderboard: depositorLeaderboard,
    builderLeaderboard: builderLeaderboard,
    relayLeaderboard: relayLeaderboard,
    lidoLeaderboard: lidoLeaderboard
  };
}
