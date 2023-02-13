<script>
  export let length = 20;
  export let txHash = '';
</script>

<g on:mouseenter on:mouseleave class="cursor-pointer">
  <a xlink:href="https://etherscan.com/tx/{txHash}">
    <line x0="0" x1="0" y0="0" y1={length} class="stroke-cyan-600" stroke-width="1.5" />
    <g transform="translate(0, {length})">
      <g transform="scale(0.6)">
        <path
          d="M -11.232 24 A 4 3.744 90 0 0 11.232 24 C 11.232 16 0 13 0 0 C 0 13 -11.232 16 -11.232 24"
          stroke-width={1.5 / 0.6}
          class="fill-cyan-500 stroke-cyan-600"
        />
      </g>
    </g>
  </a>
</g>
