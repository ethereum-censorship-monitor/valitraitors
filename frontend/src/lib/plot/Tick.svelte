<script>
  export let height;
  export let isMajor;
</script>

<line
  x1="0"
  x2="0"
  y1={isMajor ? -height / 3 : 0}
  y2={height / 2}
  stroke="white"
  stroke-width={isMajor ? 2 : 1}
/>
