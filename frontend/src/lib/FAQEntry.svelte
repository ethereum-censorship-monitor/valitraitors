<script>
  export let folded = true;

  function handleOnClick() {
    folded = !folded;
  }
</script>

<div>
  <div>
    <h3 class="text-lg font-bold text-white cursor-pointer" on:click={handleOnClick}>
      <span class="inline-block w-4">{folded ? '+' : '−'}</span>
      <slot name="question" />
    </h3>
  </div>
  {#if !folded}
    <div
      class="text-white mt-2 ml-5 prose prose-a:text-cyan-500 prose-a:no-underline hover:prose-a:underline"
    >
      <slot name="answer" />
    </div>
  {/if}
</div>
