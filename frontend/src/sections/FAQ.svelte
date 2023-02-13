<script>
  import Heading from '../lib/Heading.svelte';
  import FAQEntry from '../lib/FAQEntry.svelte';
</script>

<Heading text="FAQ" />
<div class="max-w-screen-sm mx-auto ">
  <div class="flex flex-col space-y-4 mx-4">
    <FAQEntry>
      <span slot="question">What data am I looking at?</span>
      <p slot="answer">asdf fdsa asdf</p>
    </FAQEntry>
    <FAQEntry>
      <span slot="question">What's a miss?</span>
      <p slot="answer">asdf fdsa asdf</p>
    </FAQEntry>
    <FAQEntry>
      <span slot="question">How are misses detected?</span>
      <p slot="answer">asdf fdsa asdf</p>
    </FAQEntry>
    <FAQEntry>
      <span slot="question">Is Ethereum censored?</span>
      <p slot="answer">asdf fdsa asdf</p>
    </FAQEntry>
    <FAQEntry>
      <span slot="question">What kinds of transactions are usually censored?</span>
      <p slot="answer">asdf fdsa asdf</p>
    </FAQEntry>
    <FAQEntry>
      <span slot="question">What can we do about this?</span>
      <p slot="answer">asdf fdsa asdf</p>
    </FAQEntry>
  </div>
</div>
