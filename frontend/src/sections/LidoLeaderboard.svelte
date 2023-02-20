<script>
  import Heading from '../lib/Heading.svelte';
  import Table from '../lib/Table.svelte';
  import { formatPercentage } from '../lib/utils.js';

  export let data;

  let rows = [];
  $: {
    if (data) {
      rows = data.lido_leaderboard.map((r) => [
        { text: r.operator, sortValue: r.operator },
        { text: formatPercentage(r.market_share), sortValue: -r.market_share },
        { text: r.num_misses.toFixed(0), sortValue: -r.num_misses },
        { text: r.weighted_num_misses.toFixed(1), sortValue: -r.weighted_num_misses }
      ]);
    } else {
      rows = [];
    }
  }
</script>

<Heading text="Lido Node Operator Leaderboard" />

<div class="mx-auto max-w-screen-sm text-justify">
  <p class="text-white mx-4 mb-8">
    Lido is the biggest staking pool. They don't run validators themselves, but outsource this job
    to a set of external entities. This table compares these node operators.
  </p>
</div>
<Table
  heads={['Operator', 'Market Share', 'Misses', 'Weighted Misses']}
  defaultSortColumn={2}
  {rows}
/>
