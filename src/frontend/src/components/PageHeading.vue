<template>
  <header class="container">
    <h1 class="page-title bold mr-3">{{text}}</h1>
    <div class="header-flex">
      <slot/>
    </div>
  </header>
</template>

<script>
export default {
    name: "PageHeading",
    props: {
        text: String
    }
};
</script>

<!-- "scoped" attribute limits CSS to this component only -->
<style lang="scss">
@import "@/assets/styles/helpers.scss";

  .header-flex {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 30px 0 15px 0;

    & > * {
      //margin: 0 10px;
    }

    & > :first-child {
      margin-left: 0;
    }

    & > :last-child {
      margin-right: 0;
    }

    input {
      text-overflow: ellipsis;
      padding-right: 3em;
      margin: 0;
      top: 0;
    }

  }

  @media (max-width: 768px) {
    .header-flex {
      flex-direction: column;
      margin-top: 15px;
      align-items: start;
      h1,
      button {
        margin: 0 auto;
      }
      input {
        margin: 10px 0;
        width: 100%;
      }
    }
  }
</style>
