<template>
  <div>
    <Header />

    <PageHeading text="Settings">
      <ButtonHeadingCommon :buttons="commonButtons"/>
    </PageHeading>

    <main class="container-fluid main-fluid add-job-fluid">
      <div class="container">
        <article class="row top-form-article">
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-4">
                <label>Default Calendar Filter:</label>
              </div>
              <div class="col-sm-8">
                <select
                  name="default_calendar_filter"
                  v-model="newCrewLeaderSettings.default_calendar_filter"
                  required
                  v-validate="'required'"
                  class="form-control cb-input">
                  <option value="3">Builder</option>
                  <option value="1">Subcontractor</option>
                  <option value="2">Crew / Flex</option>
                  <option value="4">Job</option>
                </select>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-4">
                <label>Default Page Size:</label>
              </div>
              <div class="col-sm-8">
                <select
                  name="page_size"
                  v-model="newCrewLeaderSettings.page_size"
                  class="form-control cb-input">
                  <option value="5">5</option>
                  <option value="10">10</option>
                  <option value="25">25</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                </select>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
            </div>
          </div>
        </article>
        <article class="row top-form-article">
          <div class="col-md-6">
            <div class="checkbox">
              <label>
                <input
                  type="checkbox"
                  name="enable_text_notifications"
                  v-model="newCrewLeaderSettings.enable_text_notifications"
                  class="cb-checkbox" /> Enable Text Notifications
              </label>
            </div>
            <div class="checkbox">
              <label>
                <input
                  type="checkbox"
                  name="enable_email_notifications"
                  v-model="newCrewLeaderSettings.enable_email_notifications"
                  class="cb-checkbox" /> Enable Email Notifications
              </label>
            </div>
          </div>
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
            </div>
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
import ButtonHeadingCommon from "@/components/Button/HeadingCommon.vue";
import Footer from "@/components/Footer.vue";

import { mapState, mapActions } from "vuex";

export default {
    name: "SettingsPage",
    components: {
        Header,
        PageHeading,
        ButtonHeadingCommon,
        Footer
    },
    data: function() {
        return {
          newCrewLeaderSettings: {
            enable_text_notifications: false,
            enable_email_notifications: false,
            default_calendar_filter: "",
            page_size: "",
          },
          required: true,
          commonButtons: [
            { name: 'Cancel', type: 'cancel' },
            { name: 'Save', type: 'save', action: 'event-save-settings'}
          ]
        };
    },
    computed: {
      ...mapState(["crewLeaderSettings"])
    },
    methods: {
      ...mapActions(["getCrewLeaderSettings", "updateCrewLeader"]),
      submitSettingsForm: function() {
          this.$validator.validateAll().then(valid => {
            if (!valid) {
                return;
            }
            let crewLeader = this.newCrewLeaderSettings;
            this.updateCrewLeader(crewLeader)
                .then(() => {
                    this.$toastr("info", "Settings updated", "info");
                    this.$router.push({
                        name: "calendar",
                    });
                })
                .catch((errors) => {
                    this.toastrErrors(errors);
                });
          });
      },
      goBack: function() {
        this.$router.go(-1);
      }
    },
    created() {
      this.$root.$on('event-save-settings', this.submitSettingsForm);
      let self = this;
      this.getCrewLeaderSettings()
          .then(data => {
            self.newCrewLeaderSettings = {
              id: self.crewLeaderSettings.id,
              default_calendar_filter: self.crewLeaderSettings.default_calendar_filter,
              page_size: self.crewLeaderSettings.page_size,
              enable_text_notifications: self.crewLeaderSettings.enable_text_notifications,
              enable_email_notifications: self.crewLeaderSettings.enable_email_notifications,
            }
          })
    },
    destroyed() {
      this.$root.$off('event-save-settings');
    }
};
</script>
