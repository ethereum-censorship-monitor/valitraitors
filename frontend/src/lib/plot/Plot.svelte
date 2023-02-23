<script>
  import PlotLine from './PlotLine.svelte';
  import Tooltip from './Tooltip.svelte';

  export let t0 = 0;
  export let t1 = 0;
  export let txs = [];

  let width = 0;

  const timePerLine = 24 * 60 * 60;
  const tickSpacing = 2 * 60 * 60;
  const majorTickInterval = 3;
  $: numLines = (t1 - t0) / timePerLine;

  let ticks = null;
  $: {
    ticks = Array.from(Array(numLines), () => []);

    let tickRefDate = new Date(t0 * 1000);
    tickRefDate.setUTCHours(0, 0, 0, 0);
    let tickRefTimestamp = Math.floor(tickRefDate.getTime() / 1000);

    let tickIndex = -1;
    for (let t = tickRefTimestamp; t < t1; t += tickSpacing) {
      tickIndex += 1;
      if (t < t0) {
        continue;
      }
      let lineAndX = timestampToLineAndX(t);

      let tick;
      if (tickIndex % majorTickInterval == 0) {
        let isNewDay =
          new Date(t * 1000).getUTCDate() !=
          new Date((t - majorTickInterval * tickSpacing) * 1000).getUTCDate();
        tick = {
          x: lineAndX.x,
          isMajor: true,
          label: formatTickLabel(t, isNewDay)
        };
      } else {
        tick = { x: lineAndX.x, isMajor: false };
      }
      ticks[lineAndX.line].push(tick);
    }
    ticks = ticks;
  }

  let markers = null;
  $: {
    markers = Array.from(Array(numLines), () => []);
    for (const tx of txs) {
      const proposalTime = tx.misses[0].proposal_time;
      const lineAndX = timestampToLineAndX(proposalTime);
      markers[lineAndX.line].push({
        x: lineAndX.x,
        txHash: tx.tx_hash,
        numMisses: tx.num_misses,
        blocks: tx.misses.map((b) => b.block_number)
      });
    }
    markers = markers;
  }

  let lineHeight = 20;
  let lineSpacing = 70;
  let marginLeft = 50;
  let marginRight = 50;
  let marginTop = 50;
  let marginBottom = 40;

  $: lineWidth = width - marginLeft - marginRight;
  $: height = numLines * lineHeight + (numLines - 1) * lineSpacing + marginTop + marginBottom;

  let toolTipPosition = null;
  let toolTipMarker = null;
  $: showToolTip = toolTipPosition !== null;
  let toolTipOffset = 50;

  function timestampToLineAndX(t) {
    if (t < t0 || t > t1) {
      return null;
    }
    let line = Math.floor((t - t0) / timePerLine);
    let lineStart = t0 + line * timePerLine;
    let x = (t - lineStart) / timePerLine;
    return {
      line: line,
      x: x
    };
  }

  function formatTickLabel(t, isNewDay) {
    let d = new Date(t * 1000);
    if (isNewDay) {
      return (
        d.getUTCFullYear() +
        '-' +
        String(d.getUTCMonth() + 1).padStart(2, '0') +
        '-' +
        String(d.getUTCDate()).padStart(2, '0')
      );
    } else {
      let hours = d.getUTCHours();
      let minutes = d.getUTCMinutes();
      return String(hours).padStart(2, '0') + ':' + String(minutes).padStart(2, '0');
    }
  }

  function handleToolTipUpdate(update, line) {
    if (update.detail) {
      toolTipPosition = [
        update.detail.x * lineWidth + marginLeft,
        line * (lineHeight + lineSpacing) + marginTop + toolTipOffset
      ];
      toolTipMarker = update.detail;
    } else {
      toolTipPosition = null;
    }
  }
</script>

<div class="relative">
  <div class="w-full h-0" bind:clientWidth={width} />
  <svg
    class="w-full overflow-visible"
    style="height: {height}px"
    viewBox="0 0 {width} {height}"
    preserveAspectRatio="xMidYMin"
  >
    <g transform="translate({marginLeft}, {marginTop})">
      {#each Array(numLines) as _, i}
        <g transform="translate(0, {i * (lineHeight + lineSpacing)})">
          <PlotLine
            width={lineWidth}
            height={lineHeight}
            ticks={ticks ? ticks[i] : []}
            markers={markers ? markers[i] : []}
            on:tooltipUpdate={(e) => handleToolTipUpdate(e, i)}
          />
        </g>
      {/each}
    </g>
  </svg>
  {#if showToolTip}
    <Tooltip x={toolTipPosition[0]} y={toolTipPosition[1]} marker={toolTipMarker} />
  {/if}
</div>
