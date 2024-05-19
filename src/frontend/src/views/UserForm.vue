<template>
  <div>
    <Header />

    <PageHeading v-bind:text="headingText">
      <ButtonHeadingCommon :buttons="commonButtons"/>
    </PageHeading>

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
                  required
                  v-model="newRole.user.first_name"
                  v-bind:class="{error: errors.has('first_name')}"
                  class="form-control cb-input"
                  @change="filterCompanies" />
                  <span class="required-label"></span>
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
                  required
                  v-model="newRole.user.last_name"
                  v-bind:class="{error: errors.has('last_name')}"
                  class="form-control cb-input"
                  @change="filterCompanies" />
                  <span class="required-label"></span>
              </div>
            </div>
          </div>
        </article>
        <article class="row">
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-3">
                <label>Email Address:</label>
              </div>
              <div class="col-sm-1 notification-checkbox">
                <label class="cb-label block">
                  <i :class="newRole.user.enable_email_notifications ? 'fa fa-bell' : 'fa fa-bell-o'"></i>
                </label>
                <input
                  type="checkbox"
                  name="is_active"
                  v-model="newRole.user.enable_email_notifications"
                  class="cb-checkbox add-contact-checkbox" />
              </div>
              <div class="col-sm-8">
                <input
                  type="email"
                  name="email"
                  required
                  v-model="newRole.user.email"
                  v-bind:class="{error: errors.has('email')}"
                  class="form-control cb-input"
                  @change="filterCompanies" />
                  <span class="required-label-email-or-mobile"></span>
              </div>

            </div>
          </div>
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-3">
                <label>Mobile Number:</label>
              </div>
              <div class="col-sm-1 notification-checkbox">
                <label class="cb-label block">
                  <i :class="newRole.user.enable_text_notifications ? 'fa fa-bell' : 'fa fa-bell-o'"></i>
                </label>
                <input
                  type="checkbox"
                  name="is_active"
                  v-model="newRole.user.enable_text_notifications"
                  class="cb-checkbox add-contact-checkbox" />
              </div>
              <div class="col-sm-8">
                <input
                  type="text"
                  name="mobile_number"
                  required
                  v-model="newRole.user.mobile_number"
                  v-bind:class="{error: errors.has('mobile_number')}"
                  class="form-control cb-input"
                  @change="filterCompanies" />
                  <span class="required-label-email-or-mobile"></span>
              </div>
            </div>
          </div>
        </article>
        <hr>
        <article class="row">
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-12">
                <label>Relationship with {{currentUser.active_role.company_name}}:</label>
              </div>
              <div class="col-sm-12">
                <ul class="list-inline">
                  <li>
                    <input
                      type="radio"
                      name="is_employed"
                      :value="true"
                      v-model="newRole.is_employed"
                      class="cb-checkbox"
                      :disabled="$route.params.id"
                      @change="clearRoles" />
                    Employed
                  </li>
                  <li>
                    <input
                      type="radio"
                      name="is_employed"
                      :value="false"
                      v-model="newRole.is_employed"
                      class="cb-checkbox"
                      :disabled="$route.params.id"
                      @change="clearRoles" />
                    Hired via Other Company
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </article>
        <article class="row" v-if="newRole.is_employed && (!$route.params.id || newRoleCompany == currentUser.active_role.company)">
          <div class="col-md-12">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-4">
                <label>CrewBoss Access:</label>
              </div>
              <div class="col-sm-8">
                <ul class="list-inline">
                  <li>
                    <div class="checkbox">
                      <label>
                        <input
                          type="checkbox"
                          name="is_active"
                          v-model="newRole.user.is_active"
                          class="cb-checkbox" /> Grant this user access to CrewBoss Portal?
                      </label>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </article>
        <article class="row" v-if="currentUser.active_role.is_admin">
          <div class="col-md-12">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-4">
                <label>Related Tasks Access:</label>
              </div>
              <div class="col-sm-8">
                <ul class="list-inline">
                  <li>
                    <div class="checkbox">
                      <label>
                        <input
                          type="checkbox"
                          name="is_active"
                          v-model="newRole.can_see_full_job"
                          class="cb-checkbox" /> Can this user see all tasks under their jobs?
                      </label>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </article>
        <article class="row bottom-row" v-if="newRole.is_employed && (!$route.params.id || newRoleCompany == currentUser.active_role.company)">
          <div class="col-md-6">
            <label class="required-label">Roles:</label>
            <div class="checkbox">
              <label>
                <input
                  type="checkbox"
                  name="is_admin"
                  v-model="newRole.is_admin"
                  class="cb-checkbox" /> Company Admin?
              </label>
            </div>
            <div class="checkbox" v-if="currentUser.active_role.company_type == 'General Contractor'">
              <label>
                <input
                  type="checkbox"
                  name="is_builder"
                  v-model="newRole.is_builder"
                  class="cb-checkbox" /> Builder?
              </label>
            </div>
            <div class="checkbox" v-if="currentUser.active_role.company_type == 'Subcontractor'">
              <label>
                <input
                  type="checkbox"
                  name="is_crew_leader"
                  v-model="newRole.is_crew_leader"
                  class="cb-checkbox" /> Subcontractor?
              </label>
            </div>
            <div class="checkbox">
              <label>
                <input
                  type="checkbox"
                  name="is_superintendent"
                  v-model="newRole.is_superintendent"
                  class="cb-checkbox" /> Crew / Flex?
              </label>
            </div>
            <div class="checkbox">
              <label>
                <input
                  type="checkbox"
                  name="is_contact"
                  v-model="newRole.is_contact"
                  class="cb-checkbox" /> Contact?
              </label>
            </div>
          </div>
        </article>
        <article class="row" v-if="!newRole.is_employed">
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-4">
                <label>Company Name:</label>
              </div>
              <div class="col-sm-8">
                <multiselect
                  required
                  v-model="newRoleCompany"
                  class="form-control"
                  label="name"
                  track-by="id"
                  :taggable="true"
                  :disabled="$route.params.id"
                  :class="{error: errors.has('company_name')}"
                  :options="matchedCompanies"
                  @search-change="searchCompanies"
                  @tag="addCompany"
                  @select="selectCompany"
                  placeholder="Search or add new company"
                  tag-placeholder="Add new company"
                  :internal-search="false">
                  <template slot="option" slot-scope="props">
                    <h5><b>{{ props.option.name }}</b></h5>
                    {{ props.option.address }}
                  </template>
                </multiselect>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="row cb-add-task-inputs">
              <div class="col-sm-4">
                <label>State:</label>
              </div>
              <div class="col-sm-8">
                <multiselect
                  :disabled="newRoleCompany.id"
                  v-model="newRoleCompany.state_data"
                  v-bind:options="states"
                  label="display_name"
                  class="form-control">
                  <template slot="option" slot-scope="props">
                    {{ props.option.display_name }}
                  </template>
                </multiselect>
                <span class="required-label"></span>
              </div>
            </div>
          </div>
        </article>
        <article class="row bottom-row" v-if="!newRole.is_employed">
          <div class="col-md-6">
            <label class="required-label">Roles:</label>
            <div class="checkbox" v-if="currentUser.active_role.company_type != 'General Contractor'">
              <label>
                <input
                  disabled
                  type="checkbox"
                  name="is_builder"
                  v-model="newRole.is_builder"
                  class="cb-checkbox" /> Builder?
              </label>
            </div>
            <div class="checkbox" v-if="currentUser.active_role.company_type != 'Subcontractor'">
              <label>
                <input
                disabled
                  type="checkbox"
                  name="is_crew_leader"
                  v-model="newRole.is_crew_leader"
                  class="cb-checkbox" /> Subcontractor?
              </label>
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
    name: "AddRolePage",
    components: {
        Header,
        PageHeading,
        ButtonHeadingCommon,
        Footer
    },
    data: function() {
        return {
            newRole: {
                company_id: null,
                company_name: "",
                company_state: "",
                user: {
                    email: "",
                    mobile_number: "",
                    first_name: "",
                    last_name: "",
                    is_active: true,
                    enable_text_notifications: false,
                    enable_email_notifications: false,
                },
                is_admin: false,
                is_builder: false,
                is_crew_leader: false,
                is_superintendent: false,
                is_contact: false,
                is_employed: true,
            },
            newRoleCompany: {id: null, name: "", state: ""},
            required: true,
            email: true,
            commonButtons: [
              { name: 'Cancel', type: 'cancel' },
              { name: 'Save', type: 'save', action: 'event-save-user'}
            ]
        };
    },
    computed: {
        ...mapState(["loading", "role", "crewLeaders", "currentUser", "matchedCompanies", "states"]),
        headingText: function() {
            if (this.$route.name === "add-user") {
                return "Invite User";
            } else {
                return "Update User";
            }
        },
    },
    methods: {
        ...mapActions(["getRoleById", "updateRole", "addRole", "getAllCrewLeaders", "getMatchedCompanies", "getAllStates"]),
        resetLocalState: function() {
            this.newRole = {
                company_id: null,
                company_name: "",
                company_state: "",
                user: {
                    email: "",
                    mobile_number: "",
                    first_name: "",
                    last_name: "",
                    is_active: true,
                    enable_text_notifications: false,
                    enable_email_notifications: false,
                },
                is_admin: false,
                is_crew_leader: false,
                is_superintendent: false,
                is_contact: false,
                is_employed: true,
            };
        },
        submitRoleForm: function() {
            this.$validator.validateAll().then(valid => {
                if (!valid) {
                    return;
                }
                if (!this.newRole.user.first_name) {
                  this.$toastr("error", "First name field may not be blank", "error");
                  return;
                }
                if (!this.newRole.user.last_name) {
                  this.$toastr("error", "Last name field may not be blank", "error");
                  return;
                }
                if (!this.newRole.is_employed && !this.newRoleCompany) {
                  this.$toastr("error", "Company name field may not be blank", "error");
                  return;
                }
                if (!this.newRole.is_employed && !this.newRoleCompany.id && !this.newRoleCompany.state_data) {
                  this.$toastr("error", "State field may not be blank", "error");
                  return;
                }
                let hasRole = this.newRole.is_admin ||
                              this.newRole.is_builder ||
                              this.newRole.is_crew_leader ||
                              this.newRole.is_superintendent ||
                              this.newRole.is_contact;
                if (!hasRole){
                  this.$toastr("error", "You must select at least 1 role", "error");
                  return;
                }
                let user = {...this.newRole};
                user.company_id = this.newRoleCompany.id;
                user.company_name = this.newRoleCompany.name;
                user.company_state = this.newRoleCompany.state_data && this.newRoleCompany.state_data.value;
                if (this.$route.name == "update-user") {
                    user.id = this.$route.params.id;
                    this.update(user);
                } else {
                    this.add(user);
                }
            });
        },
        clearRoles: function() {
          if (this.newRole.is_employed) {
            if (this.currentUser.active_role.company_type == 'General Contractor') {
              this.newRole.is_admin = false;
              this.newRole.is_crew_leader = false;
            } else if (this.currentUser.active_role.company_type == 'Subcontractor') {
              this.newRole.is_admin = false;
              this.newRole.is_builder = false;
            }
          } else {
            this.newRole.is_admin = true;
            this.newRole.is_superintendent = false;
            this.newRole.is_contact = false;
            if (this.currentUser.active_role.company_type == 'General Contractor') {
              this.newRole.is_crew_leader = true;
              this.newRole.is_builder = false;
            } else if (this.currentUser.active_role.company_type == 'Subcontractor') {
              this.newRole.is_builder = true;
              this.newRole.is_crew_leader = false;
            }
          }
        },
        add: function(user) {
            this.addRole(user)
                .then(() => {
                    this.$toastr("info", "User added", "info");
                    this.$router.go(-1);
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
            this.updateRole(user)
                .then(() => {
                    this.$toastr("info", "User updated", "info");
                    this.$router.push({
                        name: "user-detail",
                        params: { id: this.$route.params.id }
                    });
                })
                .catch((errors) => {
                    this.toastrErrors(errors);
                });
        },
        cancel: function() {
            this.$router.push({ name: "users" });
        },
        selectCompany: function(company) {
            company.state_data = this.states.reduce(function(agg, cur) {
                return company.state == cur.value ? cur : agg;
            }, null);
        },
        searchCompanies: function(query) {
            this.getMatchedCompanies({
                search: query,
                email: this.newRole.user.email,
                mobile_number: this.newRole.user.mobile_number,
            });
        },
        filterCompanies: function () {
            this.getMatchedCompanies({
                first_name: this.newRole.user.first_name,
                last_name: this.newRole.user.last_name,
                email: this.newRole.user.email,
                mobile_number: this.newRole.user.mobile_number,
            });
        },
        addCompany (companyName) {
            const company = {id: null, name: companyName, state: null};
            this.newRoleCompany = company;
        }
    },
    created() {
      this.$root.$on('event-save-user', this.submitRoleForm);
        // this.$store.subscribe((mutation, state) => {
        //     if (mutation.type == "getRoleByIdSuccess") {
        //         this.newRole = {
        //             id: this.user.id,
        //             email: state.user.email,
        //             mobile_number: state.user.mobile_number,
        //             first_name: state.user.first_name,
        //             last_name: state.user.last_name,
        //             is_active: state.user.is_active,
        //             user_type: state.user.user_type
        //         }
        //     }
        // });
        let self = this;
        if (this.$route.name == "update-user") {
            this.getRoleById({ id: this.$route.params.id })
                .then((data) => {
                    self.newRole = {
                        user: this.role.user,
                        is_admin: this.role.is_admin,
                        is_builder: this.role.is_builder,
                        is_crew_leader: this.role.is_crew_leader,
                        is_superintendent: this.role.is_superintendent,
                        is_contact: this.role.is_contact,
                        is_employed: this.role.is_employed,
                        can_see_full_job: this.role.can_see_full_job,
                    }
                    self.newRoleCompany = this.role.company;
                })
                .catch(() => {
                    // this.$router.push({ name: "users" });
                });
        } else {
            this.getAllCrewLeaders({});
            this.getAllStates();
        }
    },
    destroyed() {
      this.$root.$off('event-save-user');
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
  top: -15px;
}

.notification-checkbox {
  line-height: 10px;
}
</style>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
