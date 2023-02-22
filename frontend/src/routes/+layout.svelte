<script>
  import '../app.css';
  import Title from '../lib/Title.svelte';
  import Footer from '../sections/Footer.svelte';
  import Card from '../assets/card.png';

  export let data;
</script>

<svelte:head>
  <title>Valitraitors</title>
  <meta name="description" content="Monitoring censorship in Ethereum." />
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="Valitraitors" />
  <meta name="twitter:image" content={Card} />
</svelte:head>

<div class="container mx-auto">
  <Title />
  <slot {data} />
  <Footer />
</div>
