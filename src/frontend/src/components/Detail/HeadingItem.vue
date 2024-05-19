<template>
  <div class="row task-details-row">
    <span class="task-details-label bold w-auto block">{{titleText}}</span>
       <slot />
  </div>
</template>

<script>
  export default {
    name: "DetailHeadingItem",
    props: {
      titleText: String
    }
  }
</script>
