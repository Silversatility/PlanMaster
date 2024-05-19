<template>
  <router-view />
</template>

<style lang="scss">
input.error,
textarea.error,
select.error {
  border: 1px solid #ff0000 !important;
}

.v-select.searchable .dropdown-toggle {
  max-height: 100%;
  border: none;
  overflow: hidden;
}

.v-select .selected-tag {
  margin: 4px 1px 0 0 !important;
  padding: 1px 0 !important;
}

.v-select .dropdown-toggle .clear {
  line-height: 1.75 !important;
}
</style>
