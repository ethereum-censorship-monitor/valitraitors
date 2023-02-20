<script>
  import '../app.css';
  import Title from '../lib/Title.svelte';
  import Footer from '../sections/Footer.svelte';

  export let data;
</script>

<div class="container mx-auto">
  <Title />
  <slot {data} />
  <Footer />
</div>
