<script>
  import Heading from '../lib/Heading.svelte';
  import Table from '../lib/Table.svelte';
  import { formatPercentage } from '../lib/utils.js';

  export let data;

  let rows = [];
  $: {
    rows = data.relay_leaderboard.map((r) => [
      r.relay,
      formatPercentage(r.market_share),
      r.num_misses,
      r.weighted_num_misses.toFixed(1)
    ]);
  }
</script>

<Heading text="Relay Leaderboard" />

<div class="mx-auto max-w-screen-sm">
  <p class="text-white mx-4 mb-8">
    Note that relays do not engage in transaction selection directly, so they should not be
    considered responsible for misses in their blocks.
  </p>
</div>
<Table heads={['Relay', 'Market Share', 'Misses', 'Weighted Misses']} {rows} />
