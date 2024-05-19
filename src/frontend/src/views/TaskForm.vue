<template>
  <div>
    <Header />

    <PageHeading :text="headingText">
      <ButtonHeadingCommon :buttons="commonButtons"/>
    </PageHeading>

    <modal
      name="addRoleModal"
      width="50%"
      height="50%">
          <div class="modal-content" style="border-radius: 0; height:100%">
            <div class="modal-header">
              <button type="button" class="close"  @click="$modal.hide('addRoleModal')">&times;</button>
              <h4 class="modal-title"><strong>{{addRoleModal.title}}</strong></h4>
              <p class="modal-title">By pressing enter, you will invite the user to CrewBoss.</p>
            </div>
            <div class="modal-body">

              <article class="row top-form-article">
                <div class="col-md-12">
                  <div class="row">
                    <div class="col-sm-4">
                      <label class="required-label">First Name:</label>
                    </div>
                    <div class="col-sm-8">
                      <input
                        type="text"
                        name="first_name"
                        v-model="newRole.user.first_name"
                        class="form-control" />
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
                        v-model="newRole.user.last_name"
                        class="form-control" />
                    </div>
                  </div>
                </div>
                <div class="col-md-12">
                  <div class="row">
                    <div class="col-sm-4">
                      <label class="required-label">Email Address:</label>
                    </div>
                    <div class="col-sm-8">
                      <input
                        type="email"
                        name="email"
                        required
                        v-model="newRole.user.email"
                        class="form-control" />
                    </div>
                  </div>
                </div>
                <div class="col-md-12">
                  <div class="row">
                    <div class="col-sm-4">
                      <label>Mobile Number:</label>
                    </div>
                    <div class="col-sm-8">
                      <input
                        type="text"
                        name="mobile_number"
                        required
                        v-model="newRole.user.mobile_number"
                        class="form-control" />
                    </div>
                  </div>
                </div>
                <div v-if="(currentUser.active_role.company_type == 'General Contractor' && newRole.subcontractor) || (currentUser.active_role.company_type == 'Subcontractor' && newRole.builder)" class="col-md-12">
                  <div class="row">
                    <div class="col-sm-4">
                      <label>Company:</label>
                    </div>
                    <div class="col-sm-8">
                      <input
                        type="text"
                        name="company_name"
                        required
                        v-model="newRole.company_name"
                        class="form-control" />
                    </div>
                  </div>
                </div>
              </article>

            </div>
            <div class="modal-footer" style="position: absolute; bottom:0; right:0; width: 100%">
              <button type="button" class="btn btn-default" @click="$modal.hide('addRoleModal')">Close</button>
              <button type="button" class="btn btn-success" @click="sendCreateRole">Send</button>
            </div>
          </div>
    </modal>
    <main class="container-fluid main-fluid add-job-fluid">
      <div class="container">
        <article class="top-form-article task-editor-form">
          <div id="IsCompleted" class="row">
            <div class="col-sm-12 text-left">
              <label>
                <input
                  type="checkbox"
                  name="isCompleted"
                  v-model="newTask.is_completed"
                  class="cb-checkbox"
                  style="vertical-align: middle;" /> Completed?
              </label>
            </div>
          </div>
          <div id="NameAndCategories" class="row">
            <div class="col-md-5 col-sm-6 mb-4">
              <label>Task Name:</label>
              <multiselect
                required
                v-model="newTask.name"
                class="form-control"
                :taggable="true"
                :class="{error: errors.has('taskName')}"
                :options="taskNames"
                @search-change="filterTaskNames"
                @tag="addTaskName"
                placeholder="Select one or type your own"
                tag-placeholder="Use new task name"
                :internal-search="false">
              </multiselect>
              <span class="required-label"></span>
            </div>
          </div>

          <section id="LocationAndOwner" class="row">
            <div class="col-md-5 col-sm-6 mb-4">
              <label>Job Address:</label>
              <multiselect
                v-model="newJobData"
                v-bind:options="jobs"
                label="location"
                class="form-control"
                :taggable="true"
                :placeholder="jobPlaceholder"
                tag-placeholder="Please enter to create a Job"
                @select="setNewJobData"
                @tag="handleJobTag"
              />
                <span class="required-label"></span>
            </div>
            <div class="col-md-7 col-sm-6">
              <div class="row">
                <div class="col-sm-6">
                  <label>General Contractor:</label>
                  <p class="task-details-p">
                     {{owner}}
                  </p>
                </div>
                <div class="col-sm-6">
                  <label>Author:</label>
                  <p class="task-details-p">
                     {{ task.id ? newTask.author_display : currentUser.user.full_name }}
                  </p>
                </div>
              </div>
            </div>
          </section>

          <div id="RolesAndScheduling" class="row space-row">
            <div id="Roles" class="col-md-5 col-sm-6">
              <label class="category-label">Roles: <span v-if="! newJobData" style="font-weight: normal; font-size: 13px; color: red;">*You need to select a job first to pick roles</span></label>

              <div class="row">
                <div class="col-sm-4">
                  <label>Builder:</label>
                </div>
                <div class="col-sm-8">
                  <v-select
                    taggable
                    :disabled="!newJobData"
                    v-model="newBuilderData"
                    v-bind:options="builders"
                    label="user_full_name"
                    class="form-control"
                    :on-change="maybeSetCustomBuilder">
                  </v-select>
                </div>
              </div>

              <div class="row">
                <div class="col-sm-4">
                  <label>Subcontractor:</label>
                </div>
                <div class="col-sm-8">
                  <v-select
                    taggable
                    :disabled="!newJobData"
                    v-model="newCrewLeaderData"
                    v-bind:options="crewLeaders"
                    label="user_full_name"
                    class="form-control"
                    :on-change="maybeSetCustomCrewLeader">
                  </v-select>
                </div>
              </div>

              <div class="row">
                <div class="col-sm-4">
                  <label>Crew / Flex:</label>
                </div>
                <div class="col-sm-8">
                  <v-select
                    taggable
                    :disabled="!newJobData"
                    v-model="newSuperintendentData"
                    v-bind:options="superintendents"
                    label="user_full_name"
                    class="form-control"
                    :on-change="maybeSetCustomSuperintendent">
                  </v-select>
                </div>
              </div>

            </div>
            <div id="Scheduling" class="col-md-7 col-sm-6">
              <label class="category-label">Scheduling:</label>
              <div id="Dates" class="row">
                <div class="col-xs-6">
                  <div class="row">
                    <div class="col-md-6">
                      <label>Start Date:</label>
                    </div>
                    <div class="col-md-6">
                      <datepicker
                        :disabledDates = "{
                          days: nonWorkingDays
                        }"
                        @input="computeDurationInDays"
                        v-model="newTask.start_date"
                        name="start_date"
                        format="MM/dd/yyyy"
                        input-class="fill-vdp"
                        use-utc
                      />
                    </div>
                  </div>
                </div>
                <div class="col-xs-6">
                  <div class="row">
                    <div class="col-md-6">
                      <label>Daily Start Time:</label>
                    </div>
                    <div class="col-md-6">
                      <timepicker
                        class=""
                        format="hh:mm A"
                        :minute-interval="15"
                        hide-clear-button
                        v-model="startTime"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div id="Times" class="row">
                <div class="col-xs-6">
                  <div class="row">
                    <div class="col-md-6">
                      <label>End Date:</label>
                    </div>
                    <div class="col-md-6">
                      <datepicker
                        :disabledDates = "{
                          to: beforeStartDate,
                          days: nonWorkingDays
                        }"
                        @input="computeDurationInDays"
                        v-model="newTask.end_date"
                        name="end_date"
                        format="MM/dd/yyyy"
                        input-class="fill-vdp"
                        use-utc
                      />
                    </div>
                  </div>
                </div>
                <div class="col-xs-6">
                  <div class="row">
                    <div class="col-md-6">
                      <label>Daily End Time:</label>
                    </div>
                    <div class="col-md-6">
                      <timepicker
                        class=""
                        format="hh:mm A"
                        :minute-interval="15"
                        hide-clear-button
                        v-model="endTime"
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div id="Duration" class="row">
                <div class="col-xs-6">
                  <div class="row">
                    <div class="col-md-6">
                      <label>Duration In Working Days:</label>
                    </div>
                    <div class="col-md-6">
                      <input
                        @change="computeEndDate"
                        v-model.number="durationInDays"
                        type="number"
                        class="form-control"
                      >
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="row">
            <div class="form-group col-xs-12">
              <label class="cb-label bold">Note to Add</label>
              <textarea
                v-model="newTask.note_text"
                class="form-control  cb-textarea" rows="3"></textarea>
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
import Footer from "@/components/Footer.vue";
import ButtonHeadingCommon from "@/components/Button/HeadingCommon.vue";

import { mapState, mapActions } from "vuex";
import { permission } from "../router-helper";

import moment from "moment";

export default {
  name: "AddTask",
  components: {
    Header,
    PageHeading,
    Footer,
    ButtonHeadingCommon
  },
  data: function() {
    return {
      permission,
      nonWorkingDays: [],
      durationInDays: 1,
      newRole: {
        user: {
          first_name: "",
          last_name: "",
          email: "",
        },
        employed: true,
      },
      addRoleModal: {
        title: "",
      },
      newTask: {
        _alsoSendNotifications: false,
        is_completed: false,
        name: "",
        category: null,
        category_data: null,
        subcategory: null,
        job: null,
        subcontractor: null,
        superintendent: null,
        job: null,
        builder: null,
        start_date: moment().toDate(),
        end_date: moment().toDate(),
        start_time: "09:00:00",
        end_time: "17:00:00",
        note_text: "",
      },
      required: true,
      commonButtons: [
        { name: 'Cancel', type: 'cancel' },
        { name: 'Save', type: 'save', action: 'event-save-task'},
        { name: 'Save and Send', type: 'save', action: 'event-save-and-send-task'},
      ],
      newJobData: null,
      newCrewLeaderData: null,
      newSuperintendentData: null,
      newBuilderData: null,
      newCategory: null,
      newSubcategory: null,
      firstLoad: true,
      beforeStartDate: null,
    };
  },
  computed: {
    ...mapState([
      "loading",
      "categories",
      "subcategories",
      "jobs",
      "crewLeaders",
      "superintendents",
      "builders",
      "task",
      "tasks",
      "taskNames",
      "contractor",
      "currentUser",
    ]),
    headingText: function() {
      if (this.$route.name === "add-task") {
        return "Add Task";
      } else {
        return "Update Task";
      }
    },
    owner: function(){
      return this.newJobData ? this.newJobData.owner_name : '';
    },
    startTime: {
      get() {
        return this.pickerTime(this.newTask.start_time);
      },
      set(time){
        this.newTask.start_time = this.crewbossTime(time);
      }
    },
    endTime: {
      get() {
        return this.pickerTime(this.newTask.end_time);
      },
      set(time){
        this.newTask.end_time = this.crewbossTime(time);
      }
    },
    jobPlaceholder: function() {
      return permission.isAdmin(this.currentUser) ? 'Select one or type your own' : 'Select one';
    }
  },
  methods: {
    ...mapActions([
      "getAllCategories",
      "getAllSubcategories",
      "getAllJobs",
      "getAllCrewLeaders",
      "getAllSuperintendents",
      "getAllBuilders",
      "getCompanyById",
      "getTaskById",
      "getTaskNames",
      "updateTask",
      "addTask",
      "resetTask",
      "inviteRole",
      "persistTaskForm",
    ]),
    computeDurationInDays() {
      if (this.newTask.start_date) {
        this.beforeStartDate = moment.utc(this.newTask.start_date).toDate();
      } else {
        this.beforeStartDate = null;
      }

      if (! this.newTask.end_date) {
        return
      } else if (moment.utc(this.newTask.end_date) < moment.utc(this.newTask.start_date)) {
        this.newTask.end_date = this.newTask.start_date;
      }

      // if (!this.newTask.job_data) {
      //   this.durationInDays = moment.utc(this.newTask.end_date).diff(moment.utc(this.newTask.start_date), 'days') + 1;
      //   return
      // }
      const companyId = this.newTask.job_data ? this.newTask.job_data.owner : this.currentUser.active_role.company
      this.$http.get(
        '/api/v1/task/compute-duration-in-days/',
        { params: {
            company_id: companyId,
            end_date: moment(this.newTask.end_date).format('YYYY-MM-DD'),
            start_date: moment(this.newTask.start_date).format('YYYY-MM-DD'),
          }
        }
      )
        .then((response) => {
          this.durationInDays = parseInt(response.data);
        })
    },
    computeEndDate() {
      const durationInDays = parseInt(this.durationInDays)
      // if (isNaN(durationInDays) || !this.newTask.job_data) return
      if (isNaN(durationInDays)) return;
      const companyId = this.newTask.job_data ? this.newTask.job_data.owner : this.currentUser.active_role.company;
      this.$http.get(
        '/api/v1/task/compute-end-date/',
        { params: {
            company_id: companyId,
            duration_in_days: durationInDays,
            start_date: moment(this.newTask.start_date).format('YYYY-MM-DD'),
          }
        }
      )
        .then((response) => {
          this.newTask.end_date = response.data;
        })
    },
    pickerTime(time){
      time = time.split(':');
      return {
        hh: time[0]%12,
        mm: time[1],
        A: time[0]/12 > 1 ? 'PM' : 'AM'
      }
    },
    crewbossTime(time){
      let hour = time.A == 'AM' ? time.hh : parseInt(time.hh) + 12;
      if (Number.isNaN(hour)){
        return "00:00:00";
      }
      return `${hour}:${time.mm}:00`;
    },

    doGetAllRoles() {
      let filters = {
        job: this.newTask.job_data && this.newTask.job_data.id,
      };
      this.getAllCrewLeaders(filters);
      this.getAllSuperintendents(filters);
      this.getAllBuilders(filters);
    },

    setNewJobData(value) {
      this.newJobData = value;
      this.newTask.job_data = value;
      if (value) {
        if (this.firstLoad || this.$route.name == "add-task") {
          this.doGetAllRoles();
          if(value.superintendent_data) {
            value.superintendent_data['user_full_name'] = value.superintendent_data.user.full_name;
          }
          this.newSuperintendentData = value.superintendent_data;
          if(value.builder_data) {
            value.builder_data['user_full_name'] = value.builder_data.user.full_name;
          }
          if(value.subcontractor_data) {
            value.subcontractor_data['user_full_name'] = value.subcontractor_data.user.full_name;
          }
          this.newBuilderData = value.builder_data;
        }
        else {
          this.firstLoad = false;
        }
      }

      this._setNonWorkingDays();
      this._maybeClearDates();
      this.computeDurationInDays();
    },

    setNewCategory(value) {
      this.newCategory = value;
      this.newTask.category_data = value;
      if (value && value.id) {
        this.getAllSubcategories({ categoryId: value.id }).then(() => {
          if (!this.newSubcategory || !this.subcategories.map(subcat => subcat.id).includes(this.newSubcategory.id)) {
            this.setNewSubcategory(this.subcategories[0]);
          }
        });
      } else {
        this.setNewSubcategory(null);
      }
    },

    setNewSubcategory(value) {
      this.newSubcategory = value;
      this.newTask.subcategory_data = value;
    },

    _maybeClearDates() {
      if (this.nonWorkingDays.includes(parseInt(moment(this.newTask.end_date).format('d')))) {
        this.newTask.start_date = null;
        this.newTask.end_date = null;
        this.durationInDays = null;
        this.$toastr("info", "Start/End Dates were cleared because they're outside the current job's working days.", "info");
      } else if (this.nonWorkingDays.includes(parseInt(moment(this.newTask.start_date).format('d')))) {
        this.newTask.start_date = null;
        this.newTask.end_date = null;
        this.durationInDays = null;
        this.$toastr("info", "Start/End Dates were cleared because they're outside the current job's working days.", "info");
      }
    },

    _setNonWorkingDays() {
        if (this.newJobData) {
          this.nonWorkingDays = this.newJobData.owner_non_working_days_in_day_of_week;
        } else {
          this.nonWorkingDays = this.currentUser.active_role.company_non_working_days_in_day_of_week;
        }
    },

    filterTaskNames: _.debounce(function(query) {
        this.getTaskNames({ search: query });
    }, 1000),
    addTaskName(name) {
      this.newTask.name = name;
    },

    maybeSetCustomBuilder(value, context) {
      this.newBuilderData = value;

      if (typeof(value) == "number") {
        // This happens when pre-populating the form
        return
      }
      if (value !== null && !value.id) {
        this.addRoleModal.title = "Invite as Builder";
        let names = value.user_full_name.trim().split(' ');
        if (names.length == 2) {
            this.newRole.user.first_name = names[0];
            this.newRole.user.last_name = names[1];
        } else {
            this.newRole.user.first_name = names.join(' ');
        }
        this.newRole.is_builder = true;
        this.newRole.builder = true;
        this.$modal.show("addRoleModal");
      } else {
        // this.newTask.builder = value;
      }
    },
    maybeSetCustomCrewLeader(value, context) {
      this.newCrewLeaderData = value;

      if (typeof(value) == "number") {
        // This happens when pre-populating the form
        return
      }
      if (value !== null && !value.id) {
        this.addRoleModal.title = "Invite as Subcontractor";
        let names = value.user_full_name.trim().split(' ');
        if (names.length == 2) {
            this.newRole.user.first_name = names[0];
            this.newRole.user.last_name = names[1];
        } else {
            this.newRole.user.first_name = names.join(' ');
        }
        this.newRole.is_crew_leader = true;
        this.newRole.subcontractor = true;
        this.$modal.show("addRoleModal");
      } else {
        // this.newTask.subcontractor_name = value;
      }
    },
    maybeSetCustomSuperintendent(value, context) {
      this.newSuperintendentData = value;

      if (typeof(value) == "number") {
        // This happens when pre-populating the form
        return
      }
      if (value !== null && !value.id) {
        this.addRoleModal.title = "Invite as Crew / Flex";
        let names = value.user_full_name.trim().split(' ');
        if (names.length == 2) {
            this.newRole.user.first_name = names[0];
            this.newRole.user.last_name = names[1];
        } else {
            this.newRole.user.first_name = names.join(' ');
        }
        this.newRole.is_superintendent = true;
        this.$modal.show("addRoleModal");
      } else {
        // this.newTask.superintendent = value;
      }
    },

    sendCreateRole() {
      if (! this.newRole.user.first_name || ! this.newRole.user.last_name || ! this.newRole.user.email) {
        this.$toastr("error", "Missing fields", "error");
        return;
      }
      this.inviteRole(this.newRole)
        .then((data) => {
          this.$toastr("success", "Invite sent successfully", "success");
          this.$modal.hide('addRoleModal');
          if(this.newRole.subcontractor) {
              this.newCrewLeaderData = this.newTask.subcontractor = data;
              this.newTask.subcontractor.user_full_name = `${this.newTask.subcontractor.user.first_name} ${this.newTask.subcontractor.user.last_name}`;
          } else if(this.newRole.is_superintendent) {
              this.newSuperintendentData = this.newTask.superintendent = data;
              this.newTask.superintendent.user_full_name = `${this.newTask.superintendent.user.first_name} ${this.newTask.superintendent.user.last_name}`;
          } else if(this.newRole.builder) {
              this.newBuilderData = this.newTask.builder = data;
              this.newTask.builder.user_full_name = `${this.newTask.builder.user.first_name} ${this.newTask.builder.user.last_name}`;
          }
        })
        .catch((errors) => {
          this.toastrErrors(errors);
        });
    },
    handleJobTag(name) {
      if (permission.isAdmin(this.currentUser)) {
        this.persistTaskForm({ task: this.newTask });
        this.$router.push({
          name: "add-job",
          params: {
            isfromTaskForm: true,
            street_address: name,
          }
        });
      } else {
        this.$toastr("error", "You are not allowed to create job", "error");
      }
    },
    submitAndSendTaskForm() {
      this.newTask._alsoSendNotifications = true
      this.submitTaskForm()
    },
    submitTaskForm() {
      if (this.errors.any()) {
        return;
      }

      let task = {
        _alsoSendNotifications: this.newTask._alsoSendNotifications,
        is_completed: this.newTask.is_completed,
        name: this.newTask.name,
        job: this.newJobData && this.newJobData.id,
        subcontractor: this.newCrewLeaderData && this.newCrewLeaderData.id,
        superintendent: this.newSuperintendentData && this.newSuperintendentData.id,
        builder: this.newBuilderData && this.newBuilderData.id,
        category: this.newTask.category_data && this.newTask.category_data.id,
        subcategory: this.newTask.subcategory_data && this.newTask.subcategory_data.id,
        start_date:
          this.newTask.start_date &&
          moment.utc(this.newTask.start_date).format("YYYY-MM-DD"),
        end_date:
          this.newTask.end_date &&
          moment.utc(this.newTask.end_date).format("YYYY-MM-DD"),
        start_time: this.newTask.start_time,
        end_time: this.newTask.end_time,
        note_text: this.newTask.note_text,
        duration: this.durationInDays,
      }

      if (this.newTask.category_data && !this.newTask.category_data.id) {
        task['custom_category'] = this.newTask.category_data.name || this.newTask.category_data;
      }
      if (this.newTask.subcategory_data && !this.newTask.subcategory_data.id) {
        task['custom_subcategory'] = this.newTask.subcategory_data.name || this.newTask.subcategory_data;
      }

      if (this.task.id) {
        this.update(task);
      } else {
        this.add(task);
      }
    },
    add: function(task) {
      this.addTask(task)
        .then((data) => {
          this.$toastr("info", "Task added", "info");
          if (
            data.notification_messages &&
            data.notification_messages.successful.roles.emails.length &&
            data.notification_messages.successful.roles.mobile_numbers.length
          ) {
            let successMessage = `
            <h5>Emails</h5>
            ${data.notification_messages.successful.roles.emails.join('<br>')}
            <h5>SMS</h5>
            ${data.notification_messages.successful.roles.mobile_numbers.join('<br>')}
            `
            this.$toastr("success", successMessage , "Notifications sent!");
          }
          if (
            data.notification_messages &&
            data.notification_messages.has_error
          ) {
            let errorMessage = `
            <h5>Emails</h5>
            ${data.notification_messages.unsuccessful.roles.emails.join('<br>')}
            <h5>SMS</h5>
            ${data.notification_messages.unsuccessful.roles.mobile_numbers.join('<br>')}
            `
            this.$toastr("error", errorMessage , "Notifications not sent!");
          }

          this.$router.push({
            name: "calendar",
            params: { id: data.id, isNewTask: true }
          });
        })
        .catch(errors => {
          this.newTask._alsoSendNotifications = false
          this.toastrErrors(errors);
        });
    },
    update: function(task) {
      task['id'] = this.task.id;

      this.updateTask(task)
        .then((data) => {
          this.$toastr("info", "Task updated", "info");
          if (
            data.notification_messages &&
            data.notification_messages.successful.roles.emails.length &&
            data.notification_messages.successful.roles.mobile_numbers.length
          ) {
            let successMessage = `
            <h5>Emails</h5>
            ${data.notification_messages.successful.roles.emails.join('<br>')}
            <h5>SMS</h5>
            ${data.notification_messages.successful.roles.mobile_numbers.join('<br>')}
            `
            this.$toastr("success", successMessage , "Notifications sent!");
          }
          if (
            data.notification_messages &&
            data.notification_messages.has_error
          ) {
            let errorMessage = `
            <h5>Emails</h5>
            ${data.notification_messages.unsuccessful.roles.emails.join('<br>')}
            <h5>SMS</h5>
            ${data.notification_messages.unsuccessful.roles.mobile_numbers.join('<br>')}
            `
            this.$toastr("error", errorMessage , "Notifications not sent!");
          }
          this.$router.push({
            name: "task-detail",
            params: { id: this.$route.params.id }
          });
        })
        .catch(errors => {
          this.newTask._alsoSendNotifications = false
          this.toastrErrors(errors);
        });
    },
    initialize: function(){
      const roleData = !this.currentUser.active_role.is_admin ? { role: this.currentUser.active_role.id } : '';
      if (this.$route.name == "update-task") {
        this.firstLoad = false;
        this.getTaskById({ id: this.$route.params.id })
          .then(() => {
            this.newTask = this.mxDeepCopy(this.task);
            this.newTask['category_data'] = (this.task.category) ?
            {
              id: this.task.category,
              name: this.task.category_name
            } :
            null;

            this.newCategory = this.newTask.category_data;

            this.newTask['subcategory_data'] = (this.task.subcategory) ?
            {
              id: this.task.subcategory,
              name: this.task.subcategory_name
            } :
            null;

            this.newSubcategory = this.newTask.subcategory_data;

            this.newJobData = this.newTask.job_data;
            if (this.newTask.subcontractor_data) {
              this.newTask.subcontractor_data['user_full_name'] = this.newTask.subcontractor_data.user.full_name;
              this.newCrewLeaderData = this.newTask.subcontractor_data;
            }
            if (this.newTask.superintendent_data) {
              this.newTask.superintendent_data['user_full_name'] = this.newTask.superintendent_data.user.full_name;
              this.newSuperintendentData = this.newTask.superintendent_data;
            }
            if (this.newTask.builder_data) {
              this.newTask.builder_data['user_full_name'] = this.newTask.builder_data.user.full_name;
              this.newBuilderData = this.newTask.builder_data;
            }
            if (this.newTask.subcontractor_data) {
              this.newTask.subcontractor_data['user_full_name'] = this.newTask.subcontractor_data.user.full_name;
              this.newCrewLeaderData = this.newTask.subcontractor_data;
            }
            this.getAllCategories();
            this.getAllJobs().then(() => {
              this.doGetAllRoles();
            });
          })
          .catch(() => {
            this.$router.push({ name: "tasks" });
          });
      } else {
        if (this.$route.params.isFromJobForm) {
          this.newTask = this.task;
        } else {
          this.resetTask();
        }
        this.getTaskNames({});
        this.getAllCategories();
        this.getAllJobs().then(() => {
          if (this.$route.query.job) {
            this.newJobData = this.jobs.reduce((acc, cur) => (cur.id == this.$route.query.job) ? cur : acc, null);
            if(this.newJobData) {
                if(this.newJobData.superintendent_data) {
                  this.newJobData.superintendent_data['user_full_name'] = this.newJobData.superintendent_data.user.full_name;
                  this.newSuperintendentData = this.newJobData.superintendent_data;
                }
                if(this.newJobData.builder_data) {
                  this.newJobData.builder_data['user_full_name'] = this.newJobData.builder_data.user.full_name;
                  this.newBuilderData = this.newJobData.builder_data;
                }
                if(this.newJobData.subcontractor_data) {
                  this.newJobData.subcontractor_data['user_full_name'] = this.newJobData.subcontractor_data.user.full_name;
                  this.newCrewLeaderData = this.newJobData.subcontractor_data;
                }
            }
          }
          this.doGetAllRoles();
        });
        if (this.$route.params.isFromJobForm) {
          this.newTask.name = this.$route.params.data.task_name;
          this.newCategory = this.$route.params.data.category;
          this.newTask.category_data = this.$route.params.category;
          if (this.$route.params.data.category && this.$route.params.data.category.id) {
            this.getAllSubcategories({ categoryId: this.$route.params.data.category.id }).then(() => {
              if (!this.newSubcategory || !this.subcategories.map(subcat => subcat.id).includes(this.newSubcategory.id)) {
                this.setNewSubcategory(this.subcategories[0]);
              }
            });
          } else {
            this.setNewSubcategory(null);
          }
          this.setNewJobData(this.$route.params.job_data);
        }
      }

      if (this.$route.query.start_date) {
        this.newTask['start_date'] = this.$route.query.start_date;
      }
      if (this.$route.query.end_date) {
        this.newTask['end_date'] = this.$route.query.end_date;
      }
      this._setNonWorkingDays();
    }
  },
  created() {
    this.initialize();
    this.$root.$on('event-save-task', this.submitTaskForm);
    this.$root.$on('event-save-and-send-task', this.submitAndSendTaskForm);
  },
  destroyed() {
    this.$root.$off('event-save-task');
    this.$root.$off('event-save-and-send-task');
  }
};
</script>

<style lang="scss">
  $input-height: 50px;
  $padding-x: 12px;
  .task-editor-form {
    margin-bottom: 133px;

    label {
      line-height: 1;
      margin-bottom: 10px;
    }
    .category-label {
      font-size: 1.1em;
      margin: 14px 0;
    }
    .task-details-p {
      line-height: 50px;
      margin: 0;
    }
    .space-row {
      margin-top: 20px;
    }
    .dropdown,
    .vdp-datepicker,
    .time-picker input.display-time,
    input {
      height: $input-height;
      border: thin #c5d0e3 solid;
      border-radius: 0;
      background: #FFF;
      margin-bottom: 10px;
      font-family: "montserratlight", sans-serif;
    }
    .vdp-datepicker {
      padding: 0;
      input {
        padding: 15px $padding-x;
        margin: 0;
        width: 100%;
        height: 100%;
        border: 0;
      }
    }
    .time-picker {
      width: 100%;
      input.display-time {
        width: 100%;
        padding: 6px $padding-x;
      }
      .dropdown {
        top: 80%;
        .select-list {
          width: 100%;
          height: 100%;
        }
      }
    }
    .v-select {
      .vs__selected-options {
        width: 85%;
        height: $input-height;
        overflow: hidden;
      }
      .selected-tag {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        display: block;
        padding: 3px 0 !important;
      }
      .vs__selected-options
      .selected-tag,
      input[type=search] {
        height: auto;
        width: 100%;
        position: absolute;
        top: 0;
        left: 0;
      }
      input[type=search]:focus {
        padding: 0;
        width: 100%;
      }
    }

    @media (max-width: 767px){
      .space-row {
        margin-top: 0;
      }
    }
  }
</style>
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
