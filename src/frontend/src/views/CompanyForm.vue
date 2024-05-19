<template>
  <div>
    <Header />

    <PageHeading v-bind:text="headingText">
      <ButtonHeadingCommon :buttons="commonButtons"/>
    </PageHeading>

    <main class="container-fluid main-fluid add-job-fluid">
      <div class="container">
        <article class="top-form-article task-editor-form">
          <section id="Location" class="row">
            <div class="mb-4">
              <h3 class="cb-h3 bold">Company Details</h3>
            </div>
            <div class="col-md-3 mb-4">
              <label>Name:</label>
              <input
                v-model="newCompany.name"
                type="text"
                name="name"
                class="form-control"
              />
              <span class="required-label"></span>
            </div>
            <div class="col-md-3 col-sm-4 mb-4">
              <label>Billing Address:</label>
              <input
                v-model="newCompany.billing_address"
                type="text"
                name="billing_address"
                class="form-control"
              />
            </div>
            <div class="col-md-3 col-sm-4 mb-4">
              <label >Address Line 2:</label>
              <input
                v-model="newCompany.address_line_2"
                type="text"
                name="billing_address"
                class="form-control"
              />
            </div>
            <div class="col-md-3 col-sm-4 mb-4">
              <label>Zip Code:</label>
              <input
                v-model="newCompany.zip"
                type="zip"
                name="zip"
                class="form-control"
              />
            </div>
          </section>
          <section id="SubdivisionOwner" class="row">
            <div class="col-md-3">
              <label>City:</label>
              <input
                v-model="newCompany.city"
                type="text"
                name="city"
                class="form-control"
              />
            </div>
            <div class="col-md-3">
              <label>State:</label>
              <v-select
                v-model="newCompany.state"
                v-bind:options="states"
                label="display_name"
                index="value"
                class="form-control cb-input">
              </v-select>
              <span style="top: 5px;" class="required-label"></span>
            </div>
            <div class="col-md-3">
              <label>Type:</label>
              <v-select
                v-model="newCompany.type"
                :options="companyTypes"
                label="display_name"
                index="value"
                class="form-control cb-input">
              </v-select>
              <span style="top: 5px;" class="required-label"></span>
            </div>
          </section>
          <section id="DefaultContacts" class="row">
            <div class="mb-4">
              <h3 class="cb-h3 bold">Standard Working Hours</h3>
            </div>
            <div class="col-md-3">
              <label>Daily Start Time:</label>
              <timepicker
                class
                v-model="startOfDay"
                format="hh:mm a"
                :minute-interval="15"
                hide-clear-button
              />
            </div>
            <div class="col-md-3">
              <label>Daily End Time:</label>
              <timepicker
                class
                v-model="endOfDay"
                format="hh:mm a"
                :minute-interval="15"
                hide-clear-button
              />
            </div>
            <div class="col-md-3">
              <label>Reminder Time:</label>
              <timepicker
                v-model="reminderTime"
                format="hh:mm a"
                :minute-interval="15"
                hide-clear-button
              />
            </div>
          </section>
          <section class="row">
            <div class="mb-4">
              <h3 class="cb-h3 bold" style="">Standard Workdays</h3>
            </div>
            <div style="padding: 0 15px" class="days-wrap d-flex justify-content-between align-items-center flex-wrap mb-5">
              <div>
                <input v-model="newCompany.monday" type="checkbox" class="cb-checkbox mr-2" />
                <label class="cb-label">Monday</label>
              </div>
              <div>
                <input v-model="newCompany.tuesday" type="checkbox" class="cb-checkbox mr-2" />
                <label class="cb-label">Tuesday</label>
              </div>
              <div>
                <input v-model="newCompany.wednesday" type="checkbox" class="cb-checkbox mr-2" />
                <label class="cb-label">Wednesday</label>
              </div>
              <div>
                <input v-model="newCompany.thursday" type="checkbox" class="cb-checkbox mr-2" />
                <label class="cb-label">Thursday</label>
              </div>
              <div>
                <input v-model="newCompany.friday" type="checkbox" class="cb-checkbox mr-2" />
                <label class="cb-label">Friday</label>
              </div>
              <div>
                <input v-model="newCompany.saturday" type="checkbox" class="cb-checkbox mr-2" />
                <label class="cb-label">Saturday</label>
              </div>
              <div>
                <input v-model="newCompany.sunday" type="checkbox" class="cb-checkbox mr-2" />
                <label class="cb-label">Sunday</label>
              </div>
            </div>
          </section>
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
    name: "CompanyForm",
    components: {
        Header,
        PageHeading,
        ButtonHeadingCommon,
        Footer
    },
    data: function() {
        return {
            newCompany: {
                company_name: null,
                billing_address: '',
                address_line_2: '',
                zip: '',
                city: '',
                state: '',
                type: 1,
                start_of_day: "00:00:00",
                end_of_day: "00:00:00",
                reminder_time: "00:00:00",
            },
            companyTypes: [
              { display_name: 'General Contractor', value: 1 },
              { display_name: 'Subcontractor', value: 2 },
            ],
            commonButtons: [
              { name: 'Cancel', type: 'cancel' },
              { name: 'Save', type: 'save', action: 'event-save-company'}
            ]
        };
    },
    computed: {
        ...mapState(["loading", "role", "currentUser", 'states']),
        headingText: function() {
            if (this.$route.name === "add-company") {
                return "Add Company";
            } else {
                return "Update Company";
            }
        },
        startOfDay: {
          get() {
            return this.pickerTime(this.newCompany.start_of_day);
          },
          set(time) {
            this.newCompany.start_of_day = this.crewbossTime(time);
          },
        },
        endOfDay: {
          get() {
            return this.pickerTime(this.newCompany.end_of_day);
          },
          set(time) {
            this.newCompany.end_of_day = this.crewbossTime(time);
          },
        },
        reminderTime: {
          get() {
            return this.pickerTime(this.newCompany.reminder_time);
          },
          set(time) {
            this.newCompany.reminder_time = this.crewbossTime(time);
          },
        },
    },
    methods: {
        ...mapActions(["getAllStates", 'createCompany']),
        resetLocalState: function() {

        },
        submitCompanyForm: function() {
          this.createCompany(this.newCompany)
            .then(() => {
              this.$router.push({ name: "companyroles" });
            })
            .catch((errors) => {
              this.toastrErrors(errors);
            })
        },
        cancel: function() {
            this.$router.push({ name: "companyroles" });
        },
        pickerTime(time) {
          if (time) {
            time = time.split(":");
            return {
              hh: (time[0] % 12).toString().padStart(2, "0"),
              mm: time[1],
              a: time[0] / 12 > 1 ? "pm" : "am"
            };
          }
          return time;
        },
        crewbossTime(time) {
          let hour = time.a == "am" ? time.hh : parseInt(time.hh) + 12;
          if (Number.isNaN(hour)) {
            return "00:00:00";
          }
          return `${hour}:${time.mm}:00`;
        },
        initialize: function() {
          this.getAllStates()
        },
    },
    created() {
      this.initialize();
      this.$root.$on('event-save-company', this.submitCompanyForm);
    },
    destroyed() {
      this.$root.$off('event-save-company');
    }
};
</script>

<style lang="scss" scoped>
.bottom-row {
  margin-bottom: 120px;
}

.cb-input {
  margin-bottom: 0 !important;
}

.required-label-email-or-mobile {
  position: relative;
  top: -15px;
}
.required-label {
  position: relative;
  top: -5px;
}
</style>
5
