<script>
  import Heading from '../lib/Heading.svelte';
  import Plot from '../lib/plot/Plot.svelte';

  export let txs = null;
  let t0;
  let t1;
  let min_num_misses;
  $: {
    if (txs) {
      t0 = txs['fetched_from'];
      t1 = txs['fetched_to'];
      min_num_misses = txs['min_num_misses'];
    } else {
      t0 = 0;
      t1 = 0;
      min_num_misses = 0;
    }
  }
</script>

<Heading text="Recently Censored Transactions" />
<div>
  <Plot {t0} {t1} txs={txs.txs} />
  <p class="text-white text-center text-sm">
    Only transactions with {min_num_misses} or more misses are shown.
  </p>
</div>
