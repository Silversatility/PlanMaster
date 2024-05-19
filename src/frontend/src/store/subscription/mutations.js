export default {
  createStripeCustomerRequest(state) {
      state.loading = true;
  },
  createStripeCustomerSuccess(state) {
      state.loading = false;
  },
  createStripeCustomerFailure(state) {
      state.loading = false;
  },

  subscribeCustomerRequest(state) {
      state.loading = true;
  },
  subscribeCustomerSuccess(state) {
      state.loading = false;
  },
  subscribeCustomerFailure(state) {
      state.loading = false;
  },
}
