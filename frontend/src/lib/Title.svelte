<script>
  import { onMount } from 'svelte';

  let isSafari = false;

  onMount(() => {
    isSafari = window.navigator.userAgent.indexOf('Safari') != -1;
  });
</script>

<a href="/">
  <h1
    class="font-heading italic text-6xl md:text-8xl font-bold text-center mt-12 mb-8 text-white underline decoration-8 decoration-cyan-500"
    class:underline-offset-8={isSafari}
  >
    Valitraitors
  </h1>
</a>
