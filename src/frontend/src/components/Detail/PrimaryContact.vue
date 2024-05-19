<template>
  <div class="primary-role-list">
    <div class="role">
      {{titleText}}:
    </div>
    <div class="contact">
      <slot/>
    </div>
  </div>
</template>

<script>
  export default {
    name: "DetailPrimaryContact",
    props: {
      titleText: String,
      contact: String
    }
  }
</script>

<style scoped>
  .primary-role-list {
    max-width: 300px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
</style>
