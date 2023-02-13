<script>
  export let heads = null;
  export let rows = [];
</script>

<div class="mx-auto max-w-screen-sm">
  <table class="table-fixed text-white mx-4 border-b border-white">
    {#if heads}
      <thead class="mb-4">
        <tr>
          {#each heads as head}
            <th class="w-1/4 align-top pb-2 border-b border-white">{head}</th>
          {/each}
        </tr>
      </thead>
    {/if}
    <tbody>
      {#each rows as row}
        <tr>
          {#each row as cell}
            <td class="text-center py-1">{cell}</td>
          {/each}
        </tr>
      {/each}
    </tbody>
  </table>
</div>
