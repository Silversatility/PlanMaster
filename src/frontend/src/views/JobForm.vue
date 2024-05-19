<template>
  <div>
    <Header />
    <PageHeading v-bind:text="headingText">
      <ButtonHeadingCommon :buttons="commonButtons"/>
    </PageHeading>

    <modal
      name="inviteBuilderModal"
      width="50%"
      height="50%"
    >
          <div class="modal-content" style="border-radius: 0; height:100%">
            <div class="modal-header">
              <button type="button" class="close"  @click="$modal.hide('inviteBuilderModal')">&times;</button>
              <h4 class="modal-title"><strong>Create General Contractor</strong></h4>
              <p class="modal-title">By pressing send, you will create a new General Contractor and a Builder under it.</p>
            </div>
            <div class="modal-body">
              <article class="row top-form-article">
                <div class="col-md-12">
                  <div class="row">
                    <div class="col-sm-4">
                      <label class="required-label">Company Name:</label>
                    </div>
                    <div class="col-sm-8">
                      <input
                        type="text"
                        name="company_name"
                        class="form-control"
                        v-model="inviteBuilderModal.company_name"
                      />
                    </div>
                  </div>
                </div>
                <div class="col-md-12">
                  <div class="row">
                    <div class="col-sm-4">
                      <label class="required-label">First Name:</label>
                    </div>
                    <div class="col-sm-8">
                      <input
                        type="text"
                        name="first_name"
                        class="form-control"
                        v-model="inviteBuilderModal.first_name"
                      />
                    </div>
                  </div>
                </div>
                <div class="col-md-12">
                  <div class="row">
                    <div class="col-sm-4">
                      <label class="required-label">Last Name:</label>
                    </div>
                    <div class="col-sm-8">
                      <input
                        type="text"
                        name="last_name"
                        class="form-control"
                        v-model="inviteBuilderModal.last_name"
                      />
                    </div>
                  </div>
                </div>

                <div class="col-md-12">
                  <div style="margin: 15px 0px;"><span style="color: red; font-weight: bold;">* Either email or phone number is required</span></div>
                  <div class="row">
                    <div class="col-sm-4">
                      <label>Email Address: <span style="color: red">*</span></label>
                      <br>
                    </div>
                    <div class="col-sm-8">
                      <input
                        type="email"
                        name="email"
                        class="form-control"
                        v-model="inviteBuilderModal.email"
                      />
                    </div>
                  </div>
                </div>
                <div class="col-md-12">
                  <div class="row">
                    <div class="col-sm-4">
                      <label>Mobile Number: <span style="color: red">*</span></label>
                    </div>
                    <div class="col-sm-8">
                      <input
                        type="text"
                        name="mobile_number"
                        class="form-control"
                        v-model="inviteBuilderModal.mobile_number"
                      />
                    </div>
                  </div>
                </div>
              </article>
            </div>
            <div class="modal-footer" style="position: absolute; bottom:0; right:0; width: 100%">
              <button type="button" class="btn btn-default" @click="$modal.hide('inviteBuilderModal')">Close</button>
              <button type="button" class="btn btn-success" @click="handleAddRole">Send</button>
            </div>
          </div>
    </modal>

    <main class="container-fluid main-fluid add-job-fluid">
      <div class="container">
        <article class="top-form-article task-editor-form">
          <section id="Owner" class="row">
            <div class="col-md-6 mb-4">
              <label>General Contractor</label>
              <multiselect
                v-model="newJob.owner"
                v-bind:options="companiesWithSelf"
                label="name"
                :disabled="currentUser.active_role.company_type == 'General Contractor'"
                class="form-control"
                :tag-placeholder="(this.currentUser.active_role.company_type == 'Subcontractor') ? 'Add new general contractor' : null"
                :taggable="true"
                @tag="handleGeneralContractorTag"
                @select="selectCompany"
              />
              <span class="required-label"></span>
            </div>
            <div class="col-md-6 mb-4">
              <label>Street Address:</label>
              <input
                v-if="this.currentUser.active_role.company_type == 'General Contractor'"
                type="text"
                name="street_address"
                v-model="newJob.street_address"
                class="form-control"
              />
              <multiselect
                v-if="this.currentUser.active_role.company_type == 'Subcontractor'"
                required
                v-model="newJobExisting"
                label="street_address"
                class="form-control"
                track-by="id"
                :taggable="true"
                :disabled="!newJob.owner"
                :options="matchedJobsWithSelf"
                @search-change="searchJobs"
                @tag="addJobExisting"
                @select="selectJob"
                placeholder="Search or add new job"
                tag-placeholder="Add new job"
                :internal-search="false">
                <template slot="option" slot-scope="props">
                  <h5><b>{{ props.option.street_address }}</b></h5>
                  {{ props.option.lot_number ? '#' + props.option.lot_number + ', ' : '' }}{{ props.option.subdivision_name }}
                </template>
              </multiselect>
            </div>
          </section>
          <section id="Location" class="row">
            <div class="col-md-4 col-sm-4 mb-4">
              <label>City:</label>
              <input
                type="text"
                name="city"
                v-model="newJob.city"
                class="form-control"
                :disabled="!newJob.owner || (! newJob.id && newJobExisting && newJobExisting.id)"
              />
              <span class="required-label"></span>
            </div>
            <div class="col-md-4 col-sm-4 mb-4">
              <label >State:</label>
              <multiselect
                ref="state"
                v-model="newJob.state"
                v-bind:options="states"
                label="display_name"
                class="form-control"
                :disabled="!newJob.owner || (! newJob.id && newJobExisting && newJobExisting.id)">
                <template slot="option" slot-scope="props">
                  {{props.option.display_name}}
                </template>
              </multiselect>
              <span class="required-label"></span>
            </div>
            <div class="col-md-4 col-sm-4 mb-4">
              <label>Zip Code:</label>
              <input
                type="zip"
                name="zip"
                v-model="newJob.zip"
                class="form-control"
                :disabled="!newJob.owner || (! newJob.id && newJobExisting && newJobExisting.id)"
              />
              <span class="required-label"></span>
            </div>
          </section>
          <section id="SubdivisionOwner" class="row">
            <div class="col-md-4">
              <label>Lot Number:</label>
              <input
                type="text"
                name="lot_number"
                v-model="newJob.lot_number"
                class="form-control"
                :disabled="!newJob.owner || (! newJob.id && newJobExisting && newJobExisting.id)"
              />
            </div>
            <div class="col-md-4">
              <label>Subdivision:</label>
              <multiselect
                :taggable="true"
                track-by="id"
                v-model="newJob.subdivision"
                v-bind:options="subdivisions"
                label="name"
                class="form-control"
                @tag="addSubdivision"
                placeholder="Search or add new subdivision"
                tag-placeholder="Add new subdivision"
                :select-on-tab="true"
                :select-on-search-blur="true"
                :disabled="!newJob.owner || (! newJob.id && newJobExisting && newJobExisting.id)"
              />
            </div>
          </section>

          <section id="DefaultContacts" class="row">
            <div class="col-md-6">
              <label class="category-label">Default Contacts:</label>
              <div class="row" v-if="currentUser.active_role.company_type == 'General Contractor'">
                <div class="col-md-4">
                  <label>Builder</label>
                </div>
                <div class="col-md-8">
                  <multiselect
                    v-model="newJob.builder"
                    v-bind:options="builders"
                    label="user_full_name"
                    class="form-control"
                    :disabled="!newJob.owner || (! newJob.id && newJobExisting && newJobExisting.id)">
                  </multiselect>
                </div>
              </div>

              <div class="row" v-if="currentUser.active_role.company_type == 'Subcontractor'">
                <div class="col-md-4">
                  <label>Subcontractor</label>
                </div>
                <div class="col-md-8">
                  <multiselect
                    v-model="newJob.subcontractor"
                    v-bind:options="crewLeaders"
                    label="user_full_name"
                    class="form-control"
                    :disabled="!newJob.owner || (! newJob.id && newJobExisting && newJobExisting.id)">
                  </multiselect>
                </div>
              </div>

              <div class="row">
                <div class="col-md-4">
                  <label>Crew / Flex</label>
                </div>
                <div class="col-md-8">
                  <multiselect
                    v-model="newJob.superintendent"
                    v-bind:options="superintendents"
                    label="user_full_name"
                    class="form-control"
                    :disabled="!newJob.owner || (! newJob.id && newJobExisting && newJobExisting.id)">
                  </multiselect>
                </div>
              </div>
            </div>
          </section>

          <section id="Notes" class="row">
            <div class="col-xs-12">
              <label>Note to Add:</label>
              <textarea
                v-model="newJob.note_text"
                class="form-control cb-textarea" rows="3">
              </textarea>
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
  name: "Home",
  components: {
    Header,
    PageHeading,
    ButtonHeadingCommon,
    Footer
  },
  data: function() {
    return {
      params: {},
      inviteBuilderModal: {
        company_name: null,
        first_name: null,
        last_name: null,
        email: null,
        mobile_number: null,
      },
      newJob: {
        street_address: "",
        city: "",
        state: null,
        zip: "",
        subdivision: null,
        lot_number: "",
        builder: null,
        subcontractor: null,
        superintendent: null,
        created_by: null,
        owner: null,
        note_text: ""
      },
      matchedJobsWithSelf: [],
      companiesWithSelf: [],
      newJobExisting: null,
      required: true,
      commonButtons: [
        { name: 'Cancel', type: 'cancel', action: 'event-cancel-job'},
        { name: 'Save', type: 'save', action: 'event-save-job'}
      ]
    };
  },
  computed: {
    ...mapState([
      "loading",
      "job",
      "states",
      "subdivisions",
      "companies",
      "builders",
      "crewLeaders",
      "superintendents",
      "currentUser",
      "matchedJobs",
    ]),
    headingText: function() {
      if (this.$route.name === "add-job") {
        return "Add Job";
      } else {
        return "Update Job";
      }
    },
  },
  methods: {
    ...mapActions([
      "getAllSubdivisions",
      "getAllBuilders",
      "getAllCrewLeaders",
      "getAllSuperintendents",
      "getAllCompanies",
      "getAllStates",
      "getJobById",
      "updateJob",
      "addJob",
      "addRole",
      "getMatchedJobs"
    ]),
    filterBuilders: function() {
      return this.getAllBuilders({ company: this.newJob.owner.id, onlyInvited: true })
    },
    submitJobForm: function() {
      if (this.errors.any()) {
        return;
      }
      let self = this;
      let job = {
        ...this.newJob,
        existing: this.newJobExisting && this.newJobExisting.id,
        state: this.newJob.state && this.newJob.state.value,
        subdivision: this.newJob.subdivision && this.newJob.subdivision.id,
        builder: this.newJob.builder && this.newJob.builder.id,
        subcontractor: this.newJob.subcontractor && this.newJob.subcontractor.id,
        superintendent: this.newJob.superintendent && this.newJob.superintendent.id,
        created_by: this.currentUser.active_role.company,
        owner: this.newJob.owner && this.newJob.owner.id
      };
      if (this.newJob.subdivision && !this.newJob.subdivision.id) {
        job.custom_subdivision = this.newJob.subdivision.name || this.newJob.subdivision;
      }
      if (this.newJob.id) {
        this.update(job);
      } else {
        this.add(job);
      }
    },
    add: function(job) {
      let self = this;
      this.addJob(job)
        .then(function(data) {
          self.newJob = {
            street_address: "",
            city: "",
            state: null,
            zip: "",
            subdivision: null,
            lot_number: "",
            builder: null,
            subcontractor: null,
            superintendent: null,
            owner: null,
            note_text: ""
          };
          self.newJobExisting = null;
          self.$toastr("info", "Job added", "info");
          if (self.$route.params.isfromTaskForm) {
            self.$router.push({
              name: "add-task",
              query: { job: data.id },
              params: { isFromJobForm: true }
            });
          } else {
            self.$router.push({
              name: "job-detail",
              params: { id: data.id }
            });
          }
        })
        .catch(function(errors) {
          self.toastrErrors(errors);
        });
    },
    update: function(job) {
      let self = this;
      delete job.created_by
      this.updateJob(job)
        .then(() => {
          self.$toastr("info", "Job updated", "info");
          self.$router.push({
            name: "job-detail",
            params: { id: self.$route.params.id }
          });
        })
        .catch(errors => {
          self.toastrErrors(errors);
        });
    },
    cancel() {
      if (this.$route.params.isfromTaskForm) {
        this.$router.push({
          name: "add-task",
          params: { isFromJobForm: true }
      });
      } else {
        this.$router.push({ name: "jobs" });
      }
    },
    searchJobs: function(query) {
      if (this.currentUser.active_role.company_type == 'General Contractor') {
        return
      }
      this.getMatchedJobs({ owner: this.newJob.owner.id, search: query })
        .then(() => {
          this.matchedJobsWithSelf = [...this.matchedJobs];
        })
    },
    selectCompany (selectedCompany) {
      this.getAllCrewLeaders({ company: selectedCompany.id, onlyInvited: true })
      this.getAllBuilders({ company: selectedCompany.id, onlyInvited: true })
      this.getAllSuperintendents({ company: selectedCompany.id, onlyInvited: true })
      this.getMatchedJobs({ owner: selectedCompany.id })
        .then(() => {
          this.matchedJobsWithSelf = [...this.matchedJobs];
        })
    },
    addSubdivision (name) {
      this.newJob.subdivision = {id: null, name: name};
    },
    addJobExisting (street_address) {
      this.newJobExisting = {id: null, street_address: street_address};
      this.newJob.street_address = street_address;
    },
    selectJob (selectedOption) {
      this.newJobExisting = selectedOption;
      this.newJob.street_address = selectedOption.street_address;
      if (selectedOption.id) {
        this.newJob.city = selectedOption.city;
        this.newJob.state = selectedOption.state;
        this.newJob.zip = selectedOption.zip;
        this.newJob.subdivision = selectedOption.subdivision;
        this.newJob.lot_number = selectedOption.lot_number;
        this.newJob.builder = selectedOption.builder;
        this.newJob.subcontractor = selectedOption.subcontractor;
        this.newJob.superintendent = selectedOption.superintendent;

        const self = this;
        this.newJob.state = this.states.find(state => self.newJob.state == state.value);
        this.newJob.subdivision = this.subdivisions.find(subdivision => self.newJob.subdivision == subdivision.id);
        this.newJob.builder = this.builders.find(builder => self.newJob.builder == builder.id);
        this.newJob.subcontractor = this.crewLeaders.find(subcontractor => self.newJob.subcontractor == subcontractor.id);
        this.newJob.superintendent = this.superintendents.find(superintendent => self.newJob.superintendent == superintendent.id);
      }
    },
    handleAddRole () {
      const data = {}
      data.user = {
        first_name: this.inviteBuilderModal.first_name,
        last_name: this.inviteBuilderModal.last_name,
        email: this.inviteBuilderModal.email,
        mobile_number: this.inviteBuilderModal.mobile_number,
      }
      data.is_employed = false
      data.company_name = this.inviteBuilderModal.company_name

      this.addRole(data)
        .then((data) => {
          this.getAllCompanies({ type: 1 })
            .then(() => {
              this.companiesWithSelf = [...this.companies];  // Spread to clone the array
              this.companiesWithSelf.unshift(
                {
                  id: this.currentUser.active_role.company,
                  name: `${this.currentUser.active_role.company_name} (self)`,
                }
              );
              this.newJob.owner = this.companies.find((company) => (company.id == data.company))
              this.filterBuilders()
                .then(() => {
                  this.newJob.builder = this.builders.find((builder) => (builder.company == data.company))
                })
            });
          this.$modal.hide('inviteBuilderModal')
        })
        .catch((data) => {
          this.toastrErrors(data);
        })
    },
    handleGeneralContractorTag (searchQuery) {
      if (this.currentUser.active_role.company_type != 'Subcontractor') {
        return
      }
      this.$modal.show('inviteBuilderModal');
      this.inviteBuilderModal.company_name = searchQuery;
    }
  },
  created() {
    this.$root.$on('event-cancel-job', this.cancel);
    this.$root.$on('event-save-job', this.submitJobForm);

    let self = this;
    if (this.$route.name == "update-job") {
      this.getJobById({ id: this.$route.params.id })
        .then(data => {
          this.newJob = {
            id: this.job.id,
            street_address: this.job.street_address,
            city: this.job.city,
            state: this.job.state,
            zip: this.job.zip,
            subdivision: this.job.subdivision,
            lot_number: this.job.lot_number,
            builder: this.job.builder,
            subcontractor: this.job.subcontractor,
            superintendent: this.job.superintendent,
            owner: this.job.owner,
            note_text: ""
          };
          this.getAllStates().then(function() {
            self.newJob.state = self.states.reduce(function(
              newJobState,
              state
            ) {
              if (self.newJob.state == state.value) {
                return state;
              } else {
                return newJobState;
              }
            },
            null);
          });
          this.getAllSuperintendents({onlyInvited: true}).then(function() {
            self.newJob.superintendent = self.superintendents.reduce(function(newJobSuperintendent, superintendent) {
              if (self.newJob.superintendent == superintendent.id) {
                return superintendent;
              } else {
                return newJobSuperintendent;
              }
            },
            null);
          });
          const ownerId = self.$route.query.owner || self.newJob.owner;
          this.getAllSubdivisions({ company: ownerId }).then(function() {
            self.newJob.subdivision = self.subdivisions.reduce(function(
              newJobSubdivision,
              subdivision
            ) {
              if (self.newJob.subdivision == subdivision.id) {
                return subdivision;
              } else {
                return newJobSubdivision;
              }
            },
            null);
          });
          this.getAllBuilders({ company: ownerId, onlyInvited: true }).then(() => {
            this.newJob.builder = this.builders.find((builder) => this.newJob.builder == builder.id)
          });
          this.getAllCrewLeaders({ company: ownerId, onlyInvited: true }).then(() => {
            this.newJob.subcontractor = this.crewLeaders.find((subcontractor) => this.newJob.subcontractor == subcontractor.id)
          });
          this.getAllCompanies({ type: 1})
            .then(() => {
              this.companiesWithSelf = [...this.companies];  // Spread to clone the array
              if (this.currentUser.active_role.company_type == 'General Contractor') {

              } else {
                this.companiesWithSelf.unshift(
                  {
                    id: this.currentUser.active_role.company,
                    name: `${this.currentUser.active_role.company_name} (self)`,
                  }
                );
              }
              this.newJob.owner = this.companiesWithSelf.find((company) => ownerId == company.id);
            })
            .catch((error) => {
              console.log(error)
              this.$router.push({ name: "jobs" });
            });
            this.newJobExisting = { ...this.job }
        })
        .catch(data => {
          this.$router.push({ name: "jobs" });
        });
    } else {
      this.params = this.$route.params;
      this.getAllStates();
      this.getAllSubdivisions({});
      this.getAllSuperintendents({ onlyInvited: true });
      this.getAllCrewLeaders({ onlyInvited: true });
      // this.getAllBuilders({});
      const self = this;
      this.getAllCompanies({ type: 1 })
        .then(() => {
          this.companiesWithSelf = [...this.companies];  // Spread to clone the array
          if (this.currentUser.active_role.company_type == 'General Contractor') {
            const companyId = self.currentUser.active_role.company;
            this.newJob.owner = this.companiesWithSelf.find((company) => companyId == company.id);
            self.filterBuilders();
          } else {
            this.companiesWithSelf.unshift(
              {
                id: this.currentUser.active_role.company,
                name: `${this.currentUser.active_role.company_name} (self)`,
              }
            );
          }
        });
      if (this.$route.params.street_address) {
        this.addJobExisting(this.$route.params.street_address);
      }
    }
  },
  destroyed() {
    this.$root.$off('event-cancel-job');
    this.$root.$off('event-save-job');
  }
};
</script>

<style lang="scss" scoped>
.top-form-article {
    margin-bottom: 133px;
}
</style>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
