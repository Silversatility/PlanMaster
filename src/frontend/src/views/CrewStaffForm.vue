<template>
  <div>
    <Header />
    <PageHeading v-bind:text="headingText()" />
    <main class="container-fluid main-fluid add-job-fluid">
      <div class="container">
        <article class="row top-form-article">
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-4">
                <label>First Name:</label>
              </div>
              <div class="col-sm-8">
                <input
                  type="text"
                  name="first_name"
                  v-model="newUser.first_name"
                  class="form-control cb-input" />
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-4">
                <label>Last Name:</label>
              </div>
              <div class="col-sm-8">
                <input
                  type="text"
                  name="last_name"
                  v-model="newUser.last_name"
                  class="form-control cb-input" />
              </div>
            </div>
          </div>
        </article>
        <article class="row">
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-4">
                <label>Contact Email:</label>
              </div>
              <div class="col-sm-8">
                <input
                  type="email"
                  name="email"
                  required
                  v-model="newUser.email"
                  v-bind:class="{error: errors.has('email')}"
                  class="form-control cb-input" />
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-4">
                <label>Contact Phone:</label>
              </div>
              <div class="col-sm-8">
                <input
                  type="text"
                  name="mobile_number"
                  required
                  v-model="newUser.mobile_number"
                  v-bind:class="{error: errors.has('mobile_number')}"
                  class="form-control cb-input" />
              </div>
            </div>
          </div>
        </article>
        <article class="row">
          <div class="col-md-6">
          </div>
          <div class="col-md-6">
            <section class="btn-section">
              <button class="btn cb-cancel cb-btn" v-on:click="cancel()">Cancel</button>
              <button class="btn cb-save-add cb-btn" v-on:click="submitUserForm()">Save and Add Another</button>
              <button class="btn cb-save cb-btn" v-on:click="submitUserForm()">Save</button>
            </section>
          </div>
        </article>
      </div>
    </main>
    <Footer />
  </div>
</template>

<script>
// @ is an alias to /src
import Header from "@/components/Header.vue";
import PageHeading from "@/components/PageHeading.vue";
import Footer from "@/components/Footer.vue";

import { mapState, mapActions } from "vuex";

export default {
    name: "CrewStaffForm",
    components: {
        Header,
        PageHeading,
        Footer
    },
    data: function() {
        return {
            newUser: {
                email: "",
                mobile_number: "",
                first_name: "",
                last_name: "",
                is_active: false,
                enable_text_notifications: false,
                enable_email_notifications: false,
                user_type: "crew-staff",
                company_name: "",
                crew_leader_for_staff: null
            },
            required: true,
            email: true
        };
    },
    computed: {
        ...mapState(["loading", "user", "crewLeaders"])
    },
    methods: {
        ...mapActions(["getUserById", "updateUser", "addUser"]),
        headingText: function() {
            if (this.$route.name === "add-crew-staff") {
                return "Add Crew Staff";
            } else {
                return "Update Crew Staff";
            }
        },
        resetLocalState: function() {
            this.newUser = {
                email: "",
                mobile_number: "",
                first_name: "",
                last_name: "",
                is_active: true,
                enable_text_notifications: false,
                enable_email_notifications: false,
                user_type: "crew-staff",
                company_name: "",
                crew_leader_for_staff: null
            };
        },
        submitUserForm: function() {
            this.$validator.validateAll().then(valid => {
                if (!valid) {
                    return;
                }
                if (this.newUser.id) {
                    this.update(this.newUser);
                } else {
                    this.add(this.newUser);
                }
            });
        },
        add: function(user) {
            this.addUser(user)
                .then(() => {
                    this.$toastr("info", "Crew Staff added", "info");
                    this.$router.push({
                        name: "user-detail",
                        params: { id: this.newUser.crew_leader_for_staff }
                    });
                    this.resetLocalState();
                    this.$nextTick(() => {
                        this.errors.clear();
                    });
                })
                .catch((errors) => {
                    this.toastrErrors(errors);
                });
        },
        update: function(user) {
            this.updateUser(user)
                .then(() => {
                    this.$toastr("info", "Crew Staff updated", "info");
                    this.$router.push({
                        name: "user-detail",
                        params: { id: this.newUser.crew_leader_for_staff }
                    });
                })
                .catch((errors) => {
                    this.toastrErrors(errors);
                });
        },
        cancel: function() {
            this.$router.push({
                name: "user-detail",
                params: { id: this.newUser.crew_leader_for_staff }
            });
        }
    },
    created() {
        // this.$store.subscribe((mutation, state) => {
        //     if (mutation.type == "getUserByIdSuccess") {
        //         this.newUser = {
        //             id: this.user.id,
        //             email: state.user.email,
        //             mobile_number: state.user.mobile_number,
        //             first_name: state.user.first_name,
        //             last_name: state.user.last_name,
        //             is_active: state.user.is_active,
        //             user_type: state.user.user_type,
        //             company_name: state.user.company_name
        //         }
        //     }
        // });
        let self = this;
        if (this.$route.name == "update-crew-staff") {
            this.getUserById({ id: this.$route.params.id })
                .then((data) => {
                    self.newUser = {
                        id: this.user.id,
                        email: this.user.email,
                        mobile_number: this.user.mobile_number,
                        first_name: this.user.first_name,
                        last_name: this.user.last_name,
                        is_active: this.user.is_active,
                        user_type: this.user.user_type,
                        company_name: this.user.company_name,
                        crew_leader_for_staff: this.user.crew_leader_for_staff
                    }
                })
                .catch(() => {
                    this.$router.push({
                        name: "user-detail",
                        params: { id: this.newUser.crew_leader_for_staff }
                    });
                });
        } else {
            this.newUser.crew_leader_for_staff = this.$route.query.crew_leader;
        }
    }
};
</script>
