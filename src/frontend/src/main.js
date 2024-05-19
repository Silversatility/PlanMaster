import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store/";

import axios from "axios";
import VueAxios from "vue-axios";

import VeeValidate from "vee-validate";
import VueCookie from "vue-cookie";

import VueToastr from "@deveodk/vue-toastr";
import "@deveodk/vue-toastr/dist/@deveodk/vue-toastr.css";

import vSelect from "vue-select";
import Multiselect from 'vue-multiselect'
import Datepicker from "vuejs-datepicker";
import VueTimepicker from "vue2-timepicker";

import VueDateFilter from "./filters/date";
import VueStatusFilter from "./filters/status";

import VModal from "vue-js-modal";
import "./registerServiceWorker";
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.headers.post["Content-Type"] = "application/json";
//axios.defaults.baseURL = "https://stage.crewboss.app";
axios.interceptors.response.use(
  function(response) {
    return response;
  },
  function(error) {
    if (error.response) {
      const response = error.response;
      if (
        response.status === 401 ||
        response.data.detail === "Authentication credentials were not provided."
      ) {
        store
          .dispatch("logout")
          .then(() => {
            location.href = "/";
          })
          .catch(() => {
            location.href = "/";
          });
      } else if (response.status === 503) {
        store
          .dispatch("logout")
          .then(() => {
            location.href = "/";
          })
          .catch(() => {
            location.href = "/";
          });
      }
    }
    return Promise.reject(error);
  }
);

Vue.use(VueAxios, axios);

Vue.use(VeeValidate);
Vue.use(VueCookie);

Vue.use(VueToastr, {
  defaultPosition: "toast-top-center",
  defaultType: "info",
  defaultTimeout: 3000
});

Vue.component("v-select", vSelect);
Vue.component("multiselect", Multiselect);
Vue.component("datepicker", Datepicker);
Vue.component("timepicker", VueTimepicker);

Vue.use(VueDateFilter);
Vue.use(VueStatusFilter);

Vue.use(VModal, { dialog: true });

Vue.mixin({
  methods: {
    trueHardReload: function() {
      navigator.serviceWorker.getRegistration().then(function(reg) {
        if (reg) {
          reg.unregister().then(function() { window.location.reload(true); });
        } else {
           window.location.reload(true);
        }
      })
    },
    toastrErrors: function(errors) {
      let message = "";
      for (var key in errors) {
        let value = errors[key];
        message += key + " " + (Array.isArray(value) ? value.join(", ") : value) + "\n";
      }
      if (!this.$toastr) {
        console.error("this.$toastr function is not available.");
        return;
      }
      this.$toastr("error", message, "error");
    },
    mxDeepCopy: function(obj) {
      return JSON.parse(JSON.stringify(obj));
    }
  }
});

Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount("#app");
