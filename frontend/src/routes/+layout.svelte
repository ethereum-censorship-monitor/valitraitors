<script>
  import '../app.css';
  import Title from '../lib/Title.svelte';
  import Footer from '../sections/Footer.svelte';

  export let data;
</script>

<svelte:head>
  <title>Valitraitors</title>
  <meta name="description" content="Monitoring censorship in Ethereum." />
</svelte:head>

<div class="container mx-auto">
  <Title />
  <slot {data} />
  <Footer />
</div>
