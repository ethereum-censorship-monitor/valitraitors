<script>
  import { formatHash, formatNumber } from '../utils.js';

  export let x;
  export let y;
  export let marker;
</script>

<div
  class="absolute bg-cyan-500 border-cyan-700 border-2 rounded-md px-2 py-1 pointer-events-none mx-auto"
  style="left: {x}px; top: {y}px; transform: translate(-50%, 0); max-width: 12rem"
>
  <p class="text-sm">
    Tx {formatHash(marker.txHash)} missed {marker.numMisses} times in blocks {marker.blocks
      .map(formatNumber)
      .join(', ')}
  </p>
</div>
