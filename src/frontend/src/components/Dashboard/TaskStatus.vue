<template>
  <article class="d-flex justify-content-between align-items-center">
    <h4 class="status d-flex align-items-center">
      <span class="mr-3">{{status}}</span>
      <i class="fa fa-circle mr-3 mobile"></i>
      <span class="mobile">{{numberOfTasks}}</span>
    </h4>
    <span class="show-more pointer mobile" @click="$emit('removeHeightLimit')"  v-show="numberOfTasks > 2">
      Show {{showMore === true ? "Less" : "More"}}
      <i class="arrows fa fa-chevron-up pointer ml-2" :class="{rotateArrow: !showMore}"></i>
    </span>
  </article>
</template>

<script>
export default {
  name: "TaskStatus",
  props: {
    status: String,
    numberOfTasks: Number,
    showMore: Boolean
  },

  components: {}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/assets/styles/Dashboard/task-status.scss";
</style>
