<template>
  <div class="heading-common-buttons">
    <button v-for="button in buttons"
      :class="buttonStyle(button.type)"
      v-on:click="buttonAction(button)"
      v-if="button"
    >
      {{button.name}}
    </button>
  </div>
</template>

<script>
export default {
  props: {
    buttons: {
      type: Array,
      default: [
        { type: 'return', name: 'Go Back', }
      ]
    }
  },
  methods: {
    goToPrevious: function() {
      this.$router.go(-1);
    },
    buttonStyle: function(type){
      let style = 'btn btn-common ';
      switch (type){
        case 'delete':
          return style + 'btn-danger';
        case 'accept':
        case 'save':
        case 'edit':
        case 'update':
          return style + 'btn-primary';
        case 'complete':
        case 'archive':
        case 'reinvite':
          return style + 'btn-success';
        case 'return':
        case 'cancel':
        default:
          return style + 'btn-default';

      }
    },
    buttonAction: function(button){
      if (button.type == 'return' || (button.type == 'cancel' && ! button.action)){
        return this.goToPrevious();
      }

      this.$root.$emit(button.action);
    }
  }
}
</script>

<style scoped lang="scss">
.heading-common-buttons {
  & > :first-child {
    margin-left: 0;
  }

  & > :last-child {
    margin-right: 0;
  }
}
@media (max-width: 768px) {
  .heading-common-buttons {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-top: 10px;
    .btn-common {
      min-width: 0;
    }
  }
}
</style>
