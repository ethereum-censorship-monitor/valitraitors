<script>
  import '../app.css';
  import Header from '../sections/Header.svelte';
  import BuilderLeaderboard from '../sections/BuilderLeaderboard.svelte';
  import RelayLeaderboard from '../sections/RelayLeaderboard.svelte';
  import Timeline from '../sections/Timeline.svelte';
  import FAQ from '../sections/FAQ.svelte';
  import Footer from '../sections/Footer.svelte';

  export let data;
</script>

<div class="container mx-auto">
  <Header />
  <Timeline txs={data.txs} />
  <BuilderLeaderboard data={data.builderLeaderboard} />
  <RelayLeaderboard data={data.relayLeaderboard} />
  <FAQ />
  <Footer />
</div>
