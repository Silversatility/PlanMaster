<template>
  <article
    @click="goToTask(id)"
    class="task d-flex justify-content-between align-items-center pointer mb-3"
  >
    <div class="d-flex align-items-center">
      <span class="left-strip mr-3"></span>
      <div>
        <span class="lot task-span mb-1">{{showBy === true ? lotNumber : address}}, {{ subdivision }}</span>
        <span class="desc task-span">{{taskDesc}}</span>
      </div>
    </div>
    <i class="arrows fa fa-chevron-right pointer"></i>
  </article>
</template>

<script>
export default {
  name: "Task",
  props: {
    lotNumber: String,
    address: String,
    subdivision: String,
    taskDesc: String,
    id: Number,
    showBy: Boolean
  },

  methods: {
    goToTask(taskId) {
      this.$router.push({ name: "task-detail", params: { id: taskId } });
    }
  },
  components: {}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/assets/styles/Dashboard/task.scss";
</style>
