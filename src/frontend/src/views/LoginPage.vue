<template>
  <div class="login-backdrop">
    <main class="scroll-container">
      <div class="login-container">
        <section class="login">
          <img src="/dist/assets/images/login-logo.png" class="login-logo" alt="Logo">
          <form class="login-form" novalidate v-on:submit.prevent="submitLoginForm" v-show="currentForm==='login'">
            <div>
              <input
              type="text"
              name="email_or_mobile_number"
              class="login-input"
              v-validate="'required'"
              required
              v-model="email_or_mobile_number"
              placeholder="EMAIL OR MOBILE NUMBER" />
            </div>
            <div>
              <input
              type="password"
              name="password"
              class="login-input"
              v-validate="'required'"
              v-bind:class="{error: errors.has('password')}"
              required
              v-model="password"
              placeholder="PASSWORD" />
            </div>
            <a href="#" class="forgot-password" v-on:click.prevent="toggleForm()">Forgot Password</a>
            <button type="submit" class="text-uppercase btn login-btn">Login</button>
          </form>
          <article class="forgot-password-section" v-show="currentForm=='passwordReset'">
            <p>Please enter your email here and we will send you a link to reset your password</p>
            <div>
              <input
              type="email"
              name="email"
              class="login-input"
              v-validate="'required|email'"
              v-bind:class="{error: errors.has('email')}"
              required
              v-model="email"
              placeholder="EMAIL" />
            </div>
            <button class="text-uppercase btn login-btn" v-on:click="submitResetForm">Submit</button>
            <a href="#" class="go-back" v-on:click.prevent="toggleForm()"><i class="fa fa-chevron-left go-back--fa" aria-hidden="true"></i>go back</a>
          </article>
        </section>
      </div>

      <footer class="container login-footer">
        <p class="copy text-center">Copyright © 2019 <a target="_blank" href="https://crewbossconnect.com/">crewbossconnect.com</a> - All Rights Reserved</p>
        <ul class="attribution-list">
          <li>
            <a target="_blank" href="https://crewbossconnect.com/terms-of-use/" class="login-ul--a">Terms of Use</a>
          </li>
          <li>
            <a target="_blank" href="https://crewbossconnect.com/privacy-policy/" class="login-ul--a">Privacy Policy</a>
          </li>
          <li>
            <a href="mailto:gary@crewbossconnect.com" class="login-ul--a">Contact</a>
          </li>
        </ul>
      </footer>
    </main>
  </div>
</template>

<script>
import { mapState, mapActions } from "vuex";
import axios from "axios";

export default {
    name: "LoginPage",
    components: {},
    data: function() {
        return {
            email: "",
            email_or_mobile_number: "",
            password: "",
            currentForm: "login"
        };
    },
    computed: {
        ...mapState(["currentUser"])
    },
    methods: {
        ...mapActions(["login", "forgotPassword"]),
        submitLoginForm: function() {
            if (this.errors.any()) {
                return;
            }
            let self = this;
            axios
              .get('https://api.ipify.org')
              .then(response => {
                 self.login({ email_or_mobile_number: self.email_or_mobile_number, password: self.password, ip_address: response.data })
                  .then((response) => {})
                  .catch(function(errors) {
                      if (errors.response.data.is_locked_out) {
                        self.$toastr("error", errors.response.data.error, "error");
                      } else {
                        self.$toastr("error", "Login Failed!", "error");
                      }
                      self.password = '';
                  });
              })
              .catch(function(errors) {
                self.login({ email_or_mobile_number: self.email_or_mobile_number, password: self.password })
                 .catch(function(errors) {
                     if (errors.response.data.is_locked_out) {
                       self.$toastr("error", errors.response.data.error, "error");
                     } else {
                       self.$toastr("error", "Login Failed!", "error");
                     }
                     self.password = '';
                 });
              });
        },
        submitResetForm: function() {
            if (this.errors.items[0].field === 'email') {
                return;
            }
            let self = this;
            self.forgotPassword({ email: self.email })
                .then(function() {
                    self.$toastr("info", "Check your email inbox", "info");
                    self.email = ''
                })
                .catch(function() {
                    self.$toastr("error", "Password reset failed", "error");
                    self.email = ''
                });
        },
        toggleForm: function() {
            this.currentForm =
                this.currentForm === "login" ? "passwordReset" : "login";
        }
    },
    watch: {
        currentUser: function(user) {
            if (user.session_key) {
                this.$router.push({ name: "home" });
            }
        }
    }
};
</script>
