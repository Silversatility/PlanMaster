<template>
  <div>
    <Header />
    <PageHeading text="Home" />
    <Footer />
  </div>
</template>

<script>
// @ is an alias to /src
import Header from "@/components/Header.vue";
import PageHeading from "@/components/PageHeading.vue";
import Footer from "@/components/Footer.vue";

export default {
    name: "Home",
    components: {
        Header,
        PageHeading,
        Footer
    }
};
</script>
