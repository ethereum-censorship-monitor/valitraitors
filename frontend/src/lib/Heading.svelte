<script>
  export let text;

  $: id = text.replace(' ', '_');

  let hovering = false;

  function mouseEnterHandler(_) {
    hovering = true;
  }

  function mouseLeaveHandler(_) {
    hovering = false;
  }
</script>

<h2
  {id}
  class="font-heading text-3xl font-semibold text-center mt-16 mb-6 text-white"
  on:mouseenter={mouseEnterHandler}
  on:mouseleave={mouseLeaveHandler}
>
  <a href="#{id}">
    <span class="text-cyan-500"># </span>
    <span class="">{text}</span></a
  >
</h2>
