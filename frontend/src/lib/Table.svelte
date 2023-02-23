<script>
  export let heads = null;
  export let rows = [];
  export let defaultSortColumn = 0;

  let overrideSortColumn = null;
  $: sortColumn = overrideSortColumn !== null ? overrideSortColumn : defaultSortColumn;

  let sortedRows = [];
  $: sortedRows = [...rows].sort((a, b) => {
    const av = a[sortColumn].sortValue;
    const bv = b[sortColumn].sortValue;
    if (av < bv) {
      return -1;
    } else if (av > bv) {
      return 1;
    } else {
      return 0;
    }
  });

  function columnClickHandler(i) {
    if (overrideSortColumn === i) {
      overrideSortColumn = null;
    } else {
      overrideSortColumn = i;
    }
  }
</script>

<div class="mx-auto max-w-screen-sm">
  <div class="mx-4">
    <table class="table-fixed text-white w-full border-b border-white">
      {#if heads}
        <thead class="mb-4">
          <tr>
            {#each heads as head, i}
              <th class="w-1/4 align-top pb-2 border-b border-white">
                <span
                  class="cursor-pointer select-none"
                  class:underline={i === overrideSortColumn}
                  on:click={() => columnClickHandler(i)}>{head}</span
                >
              </th>
            {/each}
          </tr>
        </thead>
      {/if}
      <tbody>
        {#each sortedRows as row}
          <tr>
            {#each row as cell}
              <td class="text-center py-1">
                {#if cell.text != 'Lido'}
                  {cell.text}
                {:else}
                  Lido <sup>1</sup>
                {/if}
              </td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
