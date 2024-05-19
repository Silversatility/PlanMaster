<template>
  <section class="container-fluid cf-fluid company-account-page">
    <header class="d-flex justify-content-between align-items-center flex-wrap">
      <div>
        <label class="cb-label">Current Plan:</label>
        <span
          class="ml-3"
        >{{ user.active_plan_display ? user.active_plan_display : "Trial Plan" }}</span>
      </div>
      <div v-if="user.active_plan_display">
        <label>{{ user.has_autorenew ? "Renews" : "Expires" }}:</label>
        <span class="ml-3">{{ user.expiry_date }}</span>
      </div>
      <div>
        <label>Show Pricing for:</label>
        <select v-model="schedule" class="plan-select ml-3">
          <option v-for="(option,i) in options" :value="option.value" :key="i">{{ option.text }}</option>
        </select>
      </div>
    </header>

    <section class="row flex-align vertical between">
      <div class="col-md-4">
        <SubscriptionOption
          plan="Contractor"
          :price="plans.contractor[schedule]"
          :schedule="schedule"
          :selected="user.active_plan_prefix === 'contractor'"
          :disableCheckout="user.active_plan_display !== null && user.active_plan_display !== ''"
        >
          <p>The perfect solution for contractors who have many jobs with a single or few tasks each.</p>
          <p>As a contractor, you need to be able to manage multiple job sites while maintaining a good overview of the many tasks at hand. The Contractor plan has been designed specifically to allow you to make the most out of CrewBoss from your unique perspective.</p>
        </SubscriptionOption>
      </div>

      <div class="col-md-4">
        <SubscriptionOption
          plan="Builder"
          :price="plans.builder[schedule]"
          :schedule="schedule"
          :selected="user.active_plan_prefix === 'builder'"
          :disableCheckout="user.active_plan_display !== null && user.active_plan_display !== ''"
        >
          <p>The perfect solution for builders who have job sites with many tasks each.</p>
          <p>As a builder, you need to be able to manage your job sites while keeping an overall view of the planning behind each of your subcontractors and their respective tasks. The Builder plan has been designed to allow you to make the most of CrewBoss from your specific perspective.</p>
        </SubscriptionOption>
      </div>

      <div class="col-md-4">
        <SubscriptionOption
          plan="Enterprise"
          :selected="user.active_plan_prefix === 'enterprise'"
          :disableCheckout="user.active_plan_display !== null && user.active_plan_display !== ''"
        >
          <p>Combine the perfect solution for planning numerous jobs and tasks together.</p>
          <p>You are probably a builder or a subcontractor of size with specific needs to make CrewBoss work in harmony with your existing business structure.</p>
          <p>Please contact us for more information. We are eager to help you get the most out of CrewBoss.</p>
        </SubscriptionOption>
      </div>
    </section>
  </section>
</template>

<script>
import { mapState, mapActions } from "vuex";
import SubscriptionOption from "@/views/Company/SubscriptionOption.vue";

export default {
  name: "CompanyDetailsForm",
  components: {
    SubscriptionOption
  },
  data: function() {
    return {
      schedule: "monthly",
      options: [
        { text: "Monthly Plan", value: "monthly" },
        { text: "Annual Plan", value: "annual" }
      ],
      plans: {
        contractor: {
          monthly: 19.99,
          annual: 99.0
        },
        builder: {
          monthly: 29.99,
          annual: 99.0
        }
      }
    };
  },
  computed: {
    ...mapState(["currentUser", "user"])
  },
  methods: {
    ...mapActions(["getUserById"])
  },
  created() {
    this.getUserById({ id: this.currentUser.user.id });
  }
};
</script>

<style lang="scss" scoped>
.flex-align {
  display: flex;
  &.vertical {
    align-items: center;
  }
  &.between {
    justify-content: space-between;
  }
}

.company-account-page {
  padding: 30px;
  .flex-align {
    flex-wrap: wrap;
  }
  .subscription-card {
    margin: 15px 0;
  }

  .plan-select {
    height: 30px;
  }
}

@media (max-width: 768px) {
  .company-account-page {
    padding: 15px;
  }
}
</style>
