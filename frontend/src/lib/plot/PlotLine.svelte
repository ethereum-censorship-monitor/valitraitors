<script>
  import AxisLine from './AxisLine.svelte';
  import Tick from './Tick.svelte';
  import TickLabel from './TickLabel.svelte';
  import Marker from './Marker.svelte';

  import { createEventDispatcher } from 'svelte';

  export let width;
  export let height;
  export let ticks = [];
  export let markers = [];

  const dispatch = createEventDispatcher();

  function handleMarkerEnter(marker) {
    dispatch('tooltipUpdate', marker);
  }

  function handleMarkerLeave(marker) {
    dispatch('tooltipUpdate', null);
  }
</script>

<g>
  <AxisLine {width} />
  {#each ticks as { x, isMajor, label }}
    <g transform="translate({x * width}, 0)">
      <Tick {isMajor} {height} />
      {#if isMajor}
        <g transform="translate(0, {-height * 0.9})">
          <TickLabel text={label} />
        </g>
      {/if}
    </g>
  {/each}
  {#each markers as marker}
    <g transform="translate({marker.x * width}, {-height * 0.5})">
      <Marker
        length={height * 1.4}
        on:mouseenter={(_) => handleMarkerEnter(marker)}
        on:mouseleave={(_) => handleMarkerLeave(marker)}
        txHash={marker.txHash}
      />
    </g>
  {/each}
</g>
