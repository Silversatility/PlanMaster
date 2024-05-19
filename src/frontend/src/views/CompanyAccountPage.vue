<template>
  <div>
    <Header />
    <PageHeading text="Company Account" />
    <div class="container">
      <div>
        <div id="tabs" class="tab-container">
          <div class="tabs">
            <!-- <a v-on:click="activetab=3" v-bind:class="[ activetab === 3 ? 'active' : '' ]">Account Balance</a> -->
            <!-- <a v-on:click="activetab=4" v-bind:class="[ activetab === 4 ? 'active' : '' ]">Activities</a> -->
            <ul class="company-tabs nav nav-pills mb-3">
              <li
                role="presentation"
                class="pointer mr-3"
                :class="[activetab === 1 ? 'active' : '' ]"
              >
                <a @click="activetab=1">Company Details</a>
              </li>
              <li
                role="presentation"
                class="pointer mr-3"
                :class="[ activetab === 2 ? 'active' : '' ]"
              >
                <a @click="activetab=2">Subscription</a>
              </li>
              <li
                role="presentation"
                class="pointer mr-3"
                :class="[ activetab === 5 ? 'active' : '' ]"
              >
                <a @click="activetab=5">Scheduling</a>
              </li>
              <li
                role="presentation"
                class="pointer mr-3"
                :class="[ activetab === 6 ? 'active' : '' ]"
              >
                <a @click="activetab=6">General</a>
              </li>
            </ul>
            <div class="dropdown company-dropdown mb-4">
              <button
                class="btn btn-default dropdown-toggle"
                type="button"
                id="dropdownMenu1"
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="true"
              >
                Go to
                <span class="caret"></span>
              </button>
              <ul class="dropdown-menu" aria-labelledby="dropdownMenu1">
                <li :class="[activetab === 1 ? 'active' : '' ]">
                  <a @click="activetab=1">Company Details</a>
                </li>
                <li :class="[activetab === 2 ? 'active' : '' ]">
                  <a @click="activetab=2">Subscription</a>
                </li>
                <li :class="[activetab === 5 ? 'active' : '' ]">
                  <a @click="activetab=5">Scheduling</a>
                </li>
                <li :class="[activetab === 6 ? 'active' : '' ]">
                  <a @click="activetab=6">General</a>
                </li>
              </ul>
            </div>
          </div>
          <div class="content">
            <div v-if="activetab === 1" class="tabcontent">
              <CompanyDetailsForm />
            </div>
            <div v-if="activetab === 2" class="tabcontent">
              <CompanySubscriptionTab />
            </div>
            <!-- <div v-if="activetab === 3" class="tabcontent">
                            Content for Account Transactions and Balance
            </div>-->
            <!-- <div v-if="activetab === 4" class="tabcontent">
                            Content for Activities
            </div>-->
            <div v-if="activetab === 5" class="tabcontent">
              <SchedulingForm />
            </div>
            <div v-if="activetab === 6" class="tabcontent">
              <GeneralForm />
            </div>
          </div>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script>
// @ is an alias to /src
import Header from "@/components/Header.vue";
import PageHeading from "@/components/PageHeading.vue";
import Footer from "@/components/Footer.vue";
import CompanyDetailsForm from "./CompanyDetailsForm.vue";
import CompanySubscriptionTab from "./Company/SubscriptionTab.vue";
import SchedulingForm from "./SchedulingForm.vue";
import GeneralForm from "./GeneralForm.vue";

import { mapState, mapActions } from "vuex";
import _ from "lodash";

export default {
  name: "CompanyAccountPage",
  components: {
    Header,
    PageHeading,
    Footer,
    CompanyDetailsForm,
    CompanySubscriptionTab,
    SchedulingForm,
    GeneralForm
  },
  data: function() {
    return {
      activetab: 1
    };
  },
};
</script>
<style scoped lang="css">
.nav-pills > li.active > a,
.nav-pills > li.active > a:focus,
.nav-pills > li.active > a:hover {
  color: #000;
  background-color: #b8d2e8;
}

.nav-pills > li > a {
  background: #f0f4fb;
  color: #2c3e50;
  border: thin #d3dae5 solid;
}

.tab-container {
  margin: 0;
}

.main-fluid {
  padding-top: 0;
}

.company-dropdown {
  display: none;
}

.nav {
    padding-left: 0;
}

@media (max-width: 768px) {
  .company-tabs {
    display: none;
  }

  .company-dropdown {
    display: block;
  }
}
</style>
