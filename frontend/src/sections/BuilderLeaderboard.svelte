<script>
  import Heading from '../lib/Heading.svelte';
  import Table from '../lib/Table.svelte';
  import { formatPercentage } from '../lib/utils.js';

  export let data;

  let rows = [];
  $: {
    if (data) {
      rows = data.builder_leaderboard.map((r) => [
        { text: r.builder, sortValue: r.builder },
        { text: formatPercentage(r.market_share), sortValue: -r.market_share },
        { text: r.num_misses, sortValue: -r.num_misses },
        { text: r.weighted_num_misses.toFixed(1), sortValue: -r.weighted_num_misses }
      ]);
    } else {
      rows = [];
    }
  }
</script>

<Heading text="Builder Leaderboard" />

<div class="mx-auto max-w-screen-sm">
  <p class="text-white mx-4 mb-8">
    Builders draft blocks for validators and directly choose which transactions to include or
    exclude.
  </p>
</div>
<Table
  heads={['Builder', 'Market Share', 'Misses', 'Weighted Misses']}
  defaultSortColumn={2}
  {rows}
/>
