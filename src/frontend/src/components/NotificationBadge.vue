<template>
  <span
    v-if="count > 0"
    class="notification-badge"
    :class="digit"
  >
    {{ count }}
  </span>
</template>

<script>
export default {
  name: "NotificationBadge",
  props: {
    count: Number
  },
  computed: {
    digit() {
      return `notification-digit-${this.count.toString().length}`;
    }
  }
}
</script>

<style lang="scss" scoped>
  $digit_map: (
    1: 1.6,
    2: 2.2,
    3: 2.8
  );
  @each $digit, $value in $digit_map {
    .notification-digit-#{$digit}{
        width: #{$value}em;
        height: #{$value}em;
        margin: -#{$value}em -#{$value * 0.4}em;
    }
  }
</style>
