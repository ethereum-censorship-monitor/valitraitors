<script>
  import Heading from '../lib/Heading.svelte';
  import Table from '../lib/Table.svelte';
  import Link from '../lib/Link.svelte';
  import { formatPercentage } from '../lib/utils.js';

  export let data;

  let rows = [];
  $: {
    if (data) {
      rows = data.depositor_leaderboard.map((r) => [
        { text: r.depositor, sortValue: r.depositor },
        { text: formatPercentage(r.market_share), sortValue: -r.market_share },
        { text: r.num_misses.toFixed(0), sortValue: -r.num_misses },
        { text: r.weighted_num_misses.toFixed(1), sortValue: -r.weighted_num_misses }
      ]);
    } else {
      rows = [];
    }
  }
</script>

<Heading text="Pool Leaderboard" />

<div class="mx-auto max-w-screen-sm text-justify">
  <p class="text-white mx-4 mb-8">
    Validators and by extensions pools are ultimately responsible for transaction selection. Many
    however choose to delegate this duty to builders.
  </p>
</div>
<Table heads={['Pool', 'Market Share', 'Misses', 'Weighted Misses']} defaultSortColumn={2} {rows} />
<div class="mx-auto max-w-screen-sm">
  <p class="text-white text-center text-sm mx-4 mt-4 mb-8">
    <sup>1</sup> See <Link href="/lido">here</Link> for a breakdown by Lido node operators.
  </p>
</div>
