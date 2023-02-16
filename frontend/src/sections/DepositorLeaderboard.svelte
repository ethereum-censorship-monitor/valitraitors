<script>
  import Heading from '../lib/Heading.svelte';
  import Table from '../lib/Table.svelte';
  import { formatPercentage } from '../lib/utils.js';

  export let data;

  let rows = [];
  $: {
    if (data) {
      rows = data.depositor_leaderboard.map((r) => [
        r.depositor,
        formatPercentage(r.market_share),
        r.num_misses,
        r.weighted_num_misses.toFixed(1)
      ]);
    } else {
      rows = [];
    }
  }
</script>

<Heading text="Pool Leaderboard" />

<Table heads={['Pool', 'Market Share', 'Misses', 'Weighted Misses']} {rows} />
