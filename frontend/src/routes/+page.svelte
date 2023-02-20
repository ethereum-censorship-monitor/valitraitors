<script>
  import '../app.css';
  import Intro from '../sections/Intro.svelte';
  import DepositorLeaderboard from '../sections/DepositorLeaderboard.svelte';
  import BuilderLeaderboard from '../sections/BuilderLeaderboard.svelte';
  import RelayLeaderboard from '../sections/RelayLeaderboard.svelte';
  import Timeline from '../sections/Timeline.svelte';
  import FAQ from '../sections/FAQ.svelte';

  export let data;
</script>

<Intro />
<Timeline txs={data.txs} />
<DepositorLeaderboard data={data.depositorLeaderboard} />
<BuilderLeaderboard data={data.builderLeaderboard} />
<RelayLeaderboard data={data.relayLeaderboard} />
<FAQ />
