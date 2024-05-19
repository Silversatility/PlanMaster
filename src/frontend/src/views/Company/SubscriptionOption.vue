<template>
  <article class="subscription-card" :class="{ selected: selected }">
    <header class="subscription-header">
      <h1>{{ plan }}</h1>
      <h2>{{ priceString }}</h2>
    </header>
    <section class="subscription-details">
      <slot />
    </section>
    <footer class="subscription-footer">
      <button v-if="price > -1" :disabled="disableCheckout" class="btn upload-btn" v-on:click.prevent="stripeOpen()">Activate {{plan}} Plan</button>
      <button v-if="price < 0" :disabled="disableCheckout" class="btn upload-btn" v-on:click.prevent="contactForPricing()">Contact Us</button>
    </footer>
  </article>
</template>

<script>
import { mapState, mapActions } from "vuex";
export default {
  name: "CompanySubscriptionOption",
  props: {
    plan: {
      type: String,
      default: 'Custom Plan'
    },
    price: {
      type: Number,
      default: -1
    },
    schedule: {
      type: String,
      default: 'annual'
    },
    disableCheckout: {
      type: Boolean,
      default: false,
    },
    selected: {
      type: Boolean,
      default: false,
    },
    hasActivePlan: {
      type: Boolean,
      default: false,
    }
  },
  computed: {
    ...mapState([
      "currentUser",
      "user",
    ]),
    priceString(){
      if (this.price < 0){
        return 'Custom Price';
      }
      return this.schedule == 'monthly' ? `$${this.price}/month` : `$${this.price}/year`;
    },
    stripePlan(){
      return `${this.plan}_${this.schedule}`.toLowerCase();
    }
  },
  data: function(){
    return {
      stripeHandler: null
    }
  },
  methods: {
    ...mapActions([
      "createStripeCustomer",
      "subscribeCustomer",
      "getUserById",
    ]),
    stripeOpen(){
      this.stripeHandler.open({
        name: `CrewBoss ${this.plan} Plan`,
        description: this.priceString,
        amount: Math.ceil(this.price * 100),
      });
    },
    stripeSubmit(source, args){
      let user = this.currentUser.active_role.user.id;
      let plan = this.stripePlan;
      this.createStripeCustomer({ user: user, source: source.id })
        .then(() => {
          return this.subscribeCustomer({ user: user, plan: plan });
        })
        .then(() => {
          this.getUserById({ id: user }).then(() => {
            this.$toastr("info", "Successfully Activated", "info");
          })
        })
        .catch((errors) => {
          console.log(errors);
          this.toastrErrors(errors);
        });
    },
    contactForPricing(){
      window.open("https://crewbossconnect.com/#contacts", "_blank");
    }
  },
  mounted() {
    this.stripeHandler = StripeCheckout.configure({
      key: process.env.VUE_APP_STRIPE_PUBLIC_KEY,
      image: 'https://crewbossconnect.com/wp-content/themes/crewboss/assets/images/icon01@2x.png',
      locale: 'auto',
      zipCode: true,
      currency: 'USD',
      panelLabel: 'Activate',
      allowRememberMe: false,
      email: this.currentUser.active_role.user.email,
      source: this.stripeSubmit
    });
  }
}
</script>

<style lang="scss" scoped>
  .subscription-card {
    border: 3px solid #c5d0e3;
    background: #FFF;
    padding: 16px;
    z-index: 1;
    transition: all 500ms;
    cursor: pointer;
    &:hover {
      z-index: 2;
      transform: scale3d(1.1,1.1,1.1) translateY(-5px);
      box-shadow: 0 15px 30px 0px rgba(0,0,0,0.1);
    }
  }

  .subscription-card.selected {
    border: 3px solid #FFD700;
    background: #FAFAD2
  }

  .subscription-header {
    display: block;
    margin-bottom: 20px;
    text-align: center;
  }

  .subscription-details {
    display: block;
  }

  .subscription-footer {
    button {
      display: block;
      width: 100%;
      text-align: center;
    }
  }
</style>
