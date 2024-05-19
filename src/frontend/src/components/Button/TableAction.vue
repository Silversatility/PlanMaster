<template>
    <a href="#">
      <i class="fa" :class="classType" aria-hidden="true"></i>
    </a>
</template>

<script>
export default {
  name: "ButtonTableAction",
  props: {
    icon: String
  },
  computed: {
    classType: function(){
      switch (this.icon){
        case 'view':
          return 'text-primary fa-eye';
        case 'edit':
          return 'text-primary fa-edit';
        case 'delete':
          return 'text-danger fa-trash';
        case 'delete disabled':
          return 'text-danger fa-trash disabled-link';
        case 'complete':
          return 'text-success fa-check-circle';
        case 'active':
          return 'text-success fa-check-circle';
        case 'archive':
          return 'text-success fa-archive';
        case 'remove':
          return 'text-success fa-remove';
        default:
          return '';
      }
    }
  }
}
</script>
