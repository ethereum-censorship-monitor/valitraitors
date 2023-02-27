<script>
  import Heading from '../lib/Heading.svelte';
  import Table from '../lib/Table.svelte';
  import { formatPercentage } from '../lib/utils.js';

  export let data;

  let rows = [];
  $: {
    if (data) {
      rows = data.relay_leaderboard.map((r) => [
        { text: r.relay, sortValue: r.relay },
        { text: formatPercentage(r.market_share), sortValue: -r.market_share },
        { text: r.num_misses.toFixed(0), sortValue: -r.num_misses },
        { text: r.weighted_num_misses.toFixed(1), sortValue: -r.weighted_num_misses }
      ]);
    } else {
      rows = [];
    }
  }
</script>

<Heading text="Relay Leaderboard" />

<div class="mx-auto max-w-screen-sm">
  <p class="text-white mx-4 mb-8">
    Relays do not engage in transaction selection directly. However, if a builder proposes a block
    that includes an unwanted transaction, the relay can reject that whole block.
  </p>
</div>
<Table
  heads={['Relay', 'Market Share', 'Misses', 'Weighted Misses']}
  defaultSortColumn={2}
  {rows}
/>
