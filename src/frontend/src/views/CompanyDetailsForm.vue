<template>
  <div>
    <section class="container-fluid main-fluid cf-fluid">
      <div class="col-md-12">
        <h3 class="cb-h3 bold">Type: {{ newCompany.type_display }}</h3>
      </div>
      <div class="col-md-12">
        <h3 class="cb-h3 bold">Company Name</h3>
      </div>
      <div class="col-sm-12">
        <input
          type="text"
          class="form-control cb-input"
          v-model="newCompany.name"
          placeholder="Company Name" />
          <span class="required-label"></span>
      </div>
      <div class="col-md-12">
        <h3 class="cb-h3 bold">Billing Address</h3>
      </div>
      <div class="col-sm-12">
        <input
          type="text"
          class="form-control cb-input"
          v-model="newCompany.billing_address"
          placeholder="Billing Address" />
      </div>
      <div class="col-md-12">
        <h3 class="cb-h3 bold">Address Line 2</h3>
      </div>
      <div class="col-sm-12">
        <input
          type="text"
          class="form-control cb-input"
          v-model="newCompany.address_line_2"
          placeholder="Address Line 2" />
      </div>
      <div class="col-sm-4">
        <h3 class="cb-h3 bold">City</h3>
        <input
          type="text"
          class="form-control cb-input"
          v-model="newCompany.city"
          placeholder="City" />
      </div>
      <div class="col-sm-4">
        <h3 class="cb-h3 bold">State</h3>
        <v-select
          ref="state"
          v-model="newCompany.state"
          v-bind:options="states"
          label="display_name"
          class="form-control cb-input">
          <template slot="option" slot-scope="option">
            {{option.display_name}}
          </template>
        </v-select>
        <span class="required-label"></span>
      </div>
      <div class="col-sm-4">
        <h3 class="cb-h3 bold">Zip Code</h3>
        <input
          type="text"
          class="form-control cb-input"
          v-model="newCompany.zip"
          placeholder="Zip Code" />
      </div>
      <div class="col-sm-12">
        <button class="btn btn-common btn-primary" @click="saveCompanyDetails">OK</button>
        <button class="btn btn-common btn-default" @click="close">Close</button>
      </div>
    </section>
  </div>
</template>

<script>
// @ is an alias to /src


import { mapState, mapActions } from "vuex";
import _ from "lodash";

export default {
    name: "CompanyDetailsForm",
    components: {

    },
    data: function() {
      return {
        activetab: 1,
        newCompany: {
          name: '',
          billing_address: '',
          address_line_2: '',
          city: '',
          state: '',
          zip: '',
        },
      }
    },
     computed: {
      ...mapState([
        "loading",
        "states",
        "currentUser",
        "company",
      ])
    },
    watch: {
      company() {
        if (this.states.length > 0){
          this.reviseStateName();
        }
      }
    },
    methods: {
      ...mapActions([
        "getAllStates",
        "getCompanyById",
        "updateCompany",
      ]),
      saveCompanyDetails() {
        const self = this;
        const company = Object.assign(this.newCompany, {
          state: this.newCompany.state && this.newCompany.state.value,
        })
        this.updateCompany(company).then(() => {
          this.$toastr("info", "Company Account data has been saved", "info");
        }).catch(function(error) {
            if (Array.isArray(error)) {
              let message = "";
              for (var key in error) {
                  let value = error[key];
                  message +=
                      key +
                      " " +
                      (value.length ? value.join(", ") : value) +
                      "\n";
              }
              self.$toastr("error", message, "error");
            } else {
              self.$toastr("error", error.detail, "error");
            }
        });
      },
      reviseStateName() {
        this.newCompany.state = this.states.reduce((
          newCompanyState,
          state
        ) => {
          if (this.newCompany.state == state.value) {
            return state;
          } else {
            return newCompanyState;
          }
        },
        null);
      },
      close() {
        this.$router.push({ name: "home" });
      },
    },
    mounted() {
      const self = this;
      this.getCompanyById(this.currentUser.active_role.company)
        .then(() => {
          this.newCompany = this.company;
          this.getAllStates().then(function() {
            self.reviseStateName();
          });
        })
        .catch(() => {
          this.$router.push({ name: "home" });
        })
    }
};
</script>
<style scoped lang="css">
.cb-input {
    margin-bottom: 5px !important;
}

.main-fluid {
  margin-bottom: 120px;
}
</style>
