import axios from "axios";

export default {
    createStripeCustomer({ commit }, { user, source }) {
      commit("createStripeCustomerRequest");
      let payload = JSON.stringify({ user, source });
      return axios
          .post("/api/v1/create-stripe-customer/", payload)
          .then(function(response) {
              commit("createStripeCustomerSuccess", response.data);
              return response;
          })
          .catch(function(error) {
              commit("createStripeCustomerFailure", error);
              throw error;
          });
    },
    subscribeCustomer({ commit }, { user, plan }) {
      commit("subscribeCustomerRequest");
      let payload = JSON.stringify({ user, plan });
      return axios
          .post("/api/v1/subscribe-customer/", payload)
          .then(function(response) {
              commit("subscribeCustomerSuccess", response.data);
              return response;
          })
          .catch(function(error) {
              commit("subscribeCustomerFailure", error);
              throw error;
          });
    },
}
