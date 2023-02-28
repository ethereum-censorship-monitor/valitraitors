<script>
  import Heading from '../lib/Heading.svelte';
  import FAQEntry from '../lib/FAQEntry.svelte';
</script>

<Heading text="FAQ" />
<div class="max-w-screen-sm mx-auto ">
  <div class="flex flex-col space-y-4 mx-4">
    <FAQEntry>
      <span slot="question">What data am I looking at?</span>
      <div slot="answer">
        <p>
          Whenever a transaction is not included in a block even though it should have, this website
          marks down a "miss". Individual blocks can contain many misses and a single transaction
          can be missed in many blocks.
        </p>

        <p>
          The timeline shows transactions with three or more misses to be reasonably certain
          something fishy is going on. The leaderboards attribute these misses to various entities
          who each can be considered responsible in different respects.
        </p>
      </div>
    </FAQEntry>
    <FAQEntry>
      <span slot="question">
        Which criteria are used to determine if a transaction should have been included?
      </span>
      <div slot="answer">
        <p>
          This website considers all transactions includable in a block if they are present in the
          mempool at proposal time, unless one or more of the following criteria is met:
        </p>
        <ul>
          <li>
            The transaction only recently appeared and thus some nodes in the network might not had
            the chance to observe it yet.
          </li>
          <li>
            The block is full, i.e., the amount of gas used in the block plus the transaction's gas
            limit would exceed the block's gas limit.
          </li>
          <li>
            The maximum base fee the transaction offers to pay is lower than the block's required
            base fee.
          </li>
          <li>
            The maximum tip per gas the transaction offers to pay is smaller than the median tip
            paid by all transactions in the block.
          </li>
          <li>
            The transaction was replaced by another one, i.e., the block contains a transaction
            signed by the same sender.
          </li>
          <li>The transaction nonce is incorrect.</li>
        </ul>
      </div>
    </FAQEntry>
    <FAQEntry>
      <span slot="question">How are misses detected?</span>
      <div slot="answer">
        <p>
          The work behind the scenes is carried out by the Ethereum Censorship Monitor. This tool
          connects to multiple Ethereum nodes and relentlessly records all miss events it can find.
          Checkout the source code and a readme with more information on
          <a href="https://github.com/ethereum-censorship-monitor/ethereum-censorship-monitor"
            >Github</a
          >.
        </p>
        <p>
          Note that the mempool is fundamentally subjective, i.e., different observers may see
          slightly different sets of transactions. The Ethereum Censorship Monitor deals with this
          by getting a look from different vantage points in the network and merging the views.
          While this is generally working well, there still might be cases of disagreement about the
          validity of some misses.
        </p>
      </div>
    </FAQEntry>
    <FAQEntry>
      <span slot="question">What are "weighted misses"?</span>
      <div slot="answer">
        <p>
          Entities which produce more blocks will in general have more misses even if they follow
          the exact transaction inclusion rules as a smaller entity. To account for this, the
          various leaderboards have a column "weighted misses" which is the number of misses divided
          by the market share in percentage points. For instance, if there is one entity with a 60%
          market share and 50 misses next to another with only 10% market share but 20 misses, the
          second one would lead in the weighted misses category by 2.0 to 1.2.
        </p>
      </div>
    </FAQEntry>
    <FAQEntry>
      <span slot="question">How accurate is the data?</span>
      <div slot="answer">
        <p>
          The mempool is by its nature subjective: Different nodes in the network see different
          transactions. It's therefore possible that the monitor classifies a not-included
          transaction as a miss, even though the block producer hasn't seen it. To account for this,
          we give transactions ample time to propagate before considering them as missable and only
          show transactions that have been missed in at least three blocks. In other words, we
          accept many false negatives in order to have a low false positive rate. In even other
          words, monitor is quite lenient.
        </p>

        <p>
          Of course, there is always the possibility of a bug. If you find something suspicious,
          please let us know by opening an issue in our <a
            href="https://github.com/ethereum-censorship-monitor/ethereum-censorship-monitor"
            >Github repository</a
          >.
        </p>
      </div>
    </FAQEntry>
    <FAQEntry>
      <span slot="question">Is Ethereum censored?</span>
      <div slot="answer">
        <p>
          As this site shows, some validators, builders, relays and other entities are censoring
          Ethereum transactions. This does however not necessarily mean that Ethereum as a whole is
          censored. Fortunately, the protocol is resilient enough to still be able to include
          undesirable-to-some transactions, albeit with a delay. However, this does not mean that
          some network participants aren't censoring and that it isn't concerning.
        </p>
      </div>
    </FAQEntry>
    <FAQEntry>
      <span slot="question">What can we do about this?</span>
      <div slot="answer">
        <p>
          If you're an entity involved in block production, be it a validator, relay, or builder,
          don't censor transactions. In addition, consider refusing to cooperate with other entities
          that do. For instance, as a validator, only allowlist non-censoring relays. As a relay,
          reject blocks from builders that are known to censor. As a user, leave staking pools that
          are not committed to censorship resistance or pressure them to change their stance.
        </p>
        <p>
          Besides these social solutions, there are a few changes to the protocol that would
          increase censorship resistance. These include CR or inclusion lists as well as more
          fundamental changes like
          <a href="https://ethresear.ch/t/shutterized-beacon-chain/12249">"shutterizing"</a>
          Ethereum.
        </p>
      </div>
    </FAQEntry>
  </div>
</div>
