<template>
  <div>
    <Header />

    <PageHeading text="User Details">
      <ButtonHeadingCommon :buttons="commonButtons"/>
    </PageHeading>
    <main class="container-fluid main-fluid add-job-fluid">
      <div class="container">
        <article class="row form-article">
          <div class="col-md-12">
            <h3 class="task-details-title bold">
              Full Name: {{user.first_name}} {{user.last_name}}
            </h3>
          </div>
          <div class="col-md-4 col-sm-6">
            <p class="task-details-p">
              <span class="task-details-label bold">Email:</span>
              <span class="task-details-value">
                <i v-if="user.email" :class="renderNotificationStatus(user, 'email')"></i>
                {{user.email}}
              </span>
            </p>
          </div>
          <div class="col-md-4 col-sm-6">
            <p class="task-details-p">
              <span class="task-details-label bold">Mobile:</span>
              <span class="task-details-value">
                <i v-if="user.mobile_number_display" :class="renderNotificationStatus(user, 'text')"></i>
                {{user.mobile_number_display}}
              </span>
            </p>
          </div>
          <div class="col-md-4 col-sm-6">
            <p class="task-details-p">
              <span class="task-details-label bold">User Types:</span>
              <span class="task-details-value">{{role.company == currentUser.active_role.company ? role.user_types_display : role.user_types_other_display}}</span>
            </p>
          </div>
          <div class="col-md-4 col-sm-6" v-if="role.company != currentUser.active_role.company">
            <p class="task-details-p">
              <span class="task-details-label bold">Company:</span>
              <span class="task-details-value">{{role.company_name}}</span>
            </p>
          </div>
          <div class="col-md-4 col-sm-6">
            <p class="task-details-p">
              <span class="task-details-label bold">
                CrewBoss Access?
                <i class="fa fa-question-circle" data-toggle="tooltip" title="Grant this user access to CrewBoss Portal?"></i>
              </span>
              <span class="task-details-value">
                <i v-if="user.is_active" class="fa fa-check-circle cb-check-circle" aria-hidden="true"></i>
                <i v-else class="fa fa-ban cb-ban-icon" aria-hidden="true"></i>
              </span>
            </p>
          </div>
          <div class="col-md-4 col-sm-6">
            <p class="task-details-p">
              <span class="task-details-label-200px bold">
                Related Tasks Access?
                <i class="fa fa-question-circle" data-toggle="tooltip" title="Can this user see all tasks under their jobs?"></i>
              </span>
              <span class="task-details-value">
                <i v-if="role.can_see_full_job" class="fa fa-check-circle cb-check-circle" aria-hidden="true"></i>
                <i v-else class="fa fa-ban cb-ban-icon" aria-hidden="true"></i>
              </span>
            </p>
          </div>
          <div class="col-md-4 col-sm-6">
            <p class="task-details-p">
            </p>
          </div>
        </article>

        <span v-if="false">
        <article v-if="user.user_type == 'contractor-admin' || user.user_type == 'crew-leader'" class="row form-article">
            <div class="col-md-2">
                <h3 class="cb-h3 text-uppercase bold">Crew Staff:</h3>
            </div>
            <div class="col-md-10">
                <div class="clearfix">
                    <button class="btn upload-btn pull-right" v-on:click="addCrewStaff()">
                      <i class="fa fa-plus-circle" aria-hidden="true"></i>Add Crew Staff
                    </button>
                </div>
                <div class="table-responsive">
                  <table class="table table-bordered add-job-table">
                    <thead>
                      <tr>
                        <th>Company</th>
                        <th>Name</th>
                        <th>Email Address</th>
                        <th>User Types</th>
                        <th>Mobile Number</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="crew_staff in user.crew_staff" v-bind:key="crew_staff.id">
                        <td>{{crew_staff.company_name}}</td>
                        <td><router-link v-bind:to="{name: 'update-crew-staff', params: {id: crew_staff.user.id}}">{{crew_staff.user.first_name}} {{crew_staff.user.last_name}}</router-link></td>
                        <td>{{crew_staff.user.email}}</td>
                        <td>{{crew_staff.user.user_type_display}}</td>
                        <td>{{crew_staff.user.mobile_number_display}}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
            </div>
        </article>
        </span>

        <article id="UserJobs" class="row form-article">
          <h3 class="cb-h3 bold">Jobs:</h3>
          <Table
            ref="jobsTable"
            :fetch="getJobs"
            :items="jobs"
            :count="jobsCount"
            :pageSize="jobsPageSize"
            :pageIndex="jobsPageIndex"
            :numPages="jobsNumPages"
            :keywords="jobsKeywords"
            :ordering="jobsOrdering"
            :initialOrdering="jobsInitialOrdering"
            :headers="jobsHeaders"
          >
            <tr v-for="job in jobs" v-bind:key="job.id">
              <td><router-link v-bind:to="{name: 'job-detail', params: {id: job.id}}">{{job.street_address}}</router-link></td>
              <td>{{job.subdivision_name}}</td>
              <td>#{{job.lot_number}}</td>
              <td>{{job.owner_name}}</td>
              <td>
                <span class="participant-status B">
                  {{job.builder_name}}
                </span>
                <span class="participant-status SC">
                  {{job.subcontractor_name}}
                </span>
                <span class="participant-status CR">
                  {{job.superintendent_name}}
                </span>
              </td>
              <td>
                <span class="table-action-buttons">
                  <a v-if="!job.is_archived && permission.isAdmin(currentUser)" @click="confirmArchiveOrHideJob(job)" href="#">
                    <i class="text-success fa fa-archive" aria-hidden="true"></i>
                  </a>
                  <a v-if="job.is_archived && permission.isAdmin(currentUser)" @click="confirmUnarchiveOrHideJob(job)" href="#">
                    <i class="text-success fa fa-undo" aria-hidden="true"></i>
                  </a>
                  <ButtonTableAction
                    icon="view"
                    @click.native.prevent="goToJobView(job)"
                  />
                  <ButtonTableAction
                    v-if="currentUser.active_role.company === job.owner || currentUser.active_role.company === job.created_by"
                    icon="edit"
                    @click.native.prevent="goToJobEdit(job)"
                  />
                  <ButtonTableAction
                    v-if="currentUser.active_role.company === job.owner || currentUser.active_role.company === job.created_by"
                    icon="delete"
                    @click.native.prevent="confirmDeleteJob(job)"
                  />
                </span>
              </td>
            </tr>
          </Table>
        </article>

        <article id="UserTasks" class="row form-article">
          <h3 class="cb-h3 bold">Tasks:</h3>
          <Table
            ref="tasksTable"
            :fetch="getTasks"
            :items="tasks"
            :count="tasksCount"
            :pageSize="tasksPageSize"
            :pageIndex="tasksPageIndex"
            :numPages="tasksNumPages"
            :keywords="tasksKeywords"
            :ordering="tasksOrdering"
            :initialOrdering="tasksInitialOrdering"
            :headers="tasksHeaders"
          >
            <tr v-for="task in tasks" v-bind:key="task.id">
              <td>
                <router-link v-bind:to="{name: 'task-detail', params: {id: task.id}}" :class="task | statusDisplay">
                  {{task.name}}
                </router-link>
              </td>
              <td>{{task.start_date | date("MM/DD/YYYY", false)}}</td>
              <td>{{task.end_date | date("MM/DD/YYYY", false)}}</td>
              <td>
                <span
                  v-for="participant in task.participant_statuses"
                  :class="`participant-status ${participant.status} ${participant.label}`"
                  >
                  {{getParticipantName(task, participant.label)}}
                </span>
              </td>
              <td>
                <span class="table-action-buttons">
                  <ButtonTableAction
                    icon="view"
                    @click.native.prevent="goToTaskView(task)"
                  />
                  <ButtonTableAction
                    icon="edit"
                    @click.native.prevent="goToTaskEdit(task)"
                  />
                  <ButtonTableAction
                    icon="delete"
                    @click.native.prevent="confirmDeleteTask(task)"
                  />
                </span>
              </td>
            </tr>
          </Table>
        </article>
        <article id="UserTasks" class="row form-article">
          <h3 class="cb-h3 bold">Login Attempts:</h3>
          <Table
            ref="loginAttemptsTable"
            :fetch="getLoginAttempts"
            :items="loginAttempts"
            :count="loginAttemptsCount"
            :pageSize="loginAttemptsPageSize"
            :pageIndex="loginAttemptsPageIndex"
            :numPages="loginAttemptsNumPages"
            :keywords="loginAttemptsKeywords"
            :ordering="loginAttemptsOrdering"
            :initialOrdering="loginAttemptsInitialOrdering"
            :headers="loginAttemptsHeaders"
          >
            <tr v-for="loginAttempt in loginAttempts" v-bind:key="loginAttempt.id">
              <td>{{loginAttempt.date | date("MM/DD/YYYY", false)}}</td>
              <td>{{loginAttempt.ip_address}}</td>
              <td>{{loginAttempt.location}}</td>
              <td>
                {{ loginAttempt.is_succesful ? 'Success' : 'Failed' }}
              </td>
            </tr>
          </Table>
        </article>
      </div>
    </main>
    <Footer />
    <v-dialog />
  </div>
</template>

<script>
// @ is an alias to /src
import Header from "@/components/Header.vue";
import PageHeading from "@/components/PageHeading.vue";
import ButtonHeadingCommon from "@/components/Button/HeadingCommon.vue";
import Table from "@/components/Table.vue";
import ButtonTableAction from '@/components/Button/TableAction.vue';
import Footer from "@/components/Footer.vue";
import { permission } from "../router-helper"

import bootstrap from "bootstrap3"; // eslint-disable-line no-unused-vars
import { mapState, mapActions } from "vuex";

export default {
    name: "RoleDetailPage",
    components: {
        Header,
        PageHeading,
        ButtonHeadingCommon,
        Table,
        ButtonTableAction,
        Footer
    },
    computed: {
        ...mapState([
          "loading",
          "role",
          "currentUser",
          "tasks",
          "tasksCount",
          "tasksPageSize",
          "tasksPageIndex",
          "tasksOrdering",
          "tasksNumPages",
          "jobs",
          "jobsCount",
          "jobsPageSize",
          "jobsPageIndex",
          "jobsOrdering",
          "jobsNumPages",
          "loginAttempts",
          "loginAttemptsOrdering",
          "loginAttemptsCount",
          "loginAttemptsPageIndex",
          "loginAttemptsNumPages",
          "loginAttemptsPageSize",
        ]),
        commonButtons() {
          if (!this.permission.isAdmin(this.currentUser)) {
              return [{ name: 'Go Back', type: 'return' }]
          }
          return [
            { name: 'Go Back', type: 'return' },
            this.role.company == this.currentUser.active_role.company ? { name: 'Delete', type: 'delete', action: 'event-delete-user'}: null,
            this.role.company == this.currentUser.active_role.company ? { name: 'Edit', type: 'edit', action: 'event-edit-user'} : null,
            { name: 'Reinvite User', type: 'reinvite', action: 'event-reinvite-user'},
          ]
        },
        user() {
          return this.role.user ? this.role.user : {};
        }
    },
    data: function(){
      return {
        permission,
        jobsKeywords: "",
        jobsInitialOrdering: "street_address",
        jobsHeaders: [
            {key: 'street_address', label: 'Job Address', sort: true},
            {key: 'subdivision__name', label: 'Subdivision', sort: true},
            {key: 'lot_number', label: 'Lot #', sort: true},
            {key: 'owner__name', label: 'General Contractor', sort: true},
            {key: 'default_contacts', label: 'Default Contacts', sort: false},
            {key: 'action', label: 'Action', sort: false}
        ],
        tasksKeywords: "",
        tasksInitialOrdering: "-start_date",
        tasksHeaders: [
            {key: 'name', label: 'Name', sort: true},
            {key: 'start_date', label: 'Start Date', sort: true},
            {key: 'end_date', label: 'End Date', sort: true},
            {key: 'participants', label: 'Participants', sort: false},
            {key: 'actions', label: 'Actions', sort: false}
        ],
        loginAttemptsKeywords: "",
        loginAttemptsInitialOrdering: "-date",
        loginAttemptsHeaders: [
            {key: 'date', label: 'Date', sort: false},
            {key: 'ip_address', label: 'IP Address', sort: false},
            {key: 'location', label: 'Location', sort: false},
            {key: 'is_succesful', label: 'Status', sort: false},
        ],
      }
    },
    methods: {
        ...mapActions([
          "getRoleById",
          "deleteRole",
          "reinviteRole",
          "getLoginAttemptsByUser",
          "getTasksByRole",
          "getJobsByRole",
        ]),
        reinviteUser() {
            this.reinviteRole(this.role)
                .then(() => {
                    this.$toastr("info", "User Reinvited!", "info");
                    this.$router.go(-1);
                })
                .catch((errors) => {
                    this.toastrErrors(errors);
                });
        },
        confirmDeleteRole: function() {
          this.$modal.show('dialog', {
            title: 'Confirm',
            text: 'Are you sure you want to delete this user?',
            buttons: [
                {
                    title: '<div class="btn cb-delete">Delete</div>',
                    handler: () => {
                      this.deleteRole({ id: this.$route.params.id })
                        .then(() => {
                            this.$router.push({ name: "users"})
                            this.$toastr("info", "User Deleted!", "Info");
                        })
                        .catch(function(error) {
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
                        });
                      this.$modal.hide('dialog');
                    }
                },
                {
                    title: 'Cancel',
                }
            ]
        });
        },
        goToUpdate: function() {
            this.$router.push({ name: "update-user", params: {id: this.$route.params.id} });
        },
        goToJobView: function(job) {
          this.$router.push({
            name: "job-detail",
            params: { id: job.id }
          });
        },
        goToJobEdit: function(job) {
          this.$router.push({
            name: "update-job",
            params: { id: job.id }
          });
        },
        confirmDeleteJob: function(job) {
          this.$modal.show('dialog', {
            title: 'Delete Job',
            text: `<p>Are you sure you want to delete this job?</p><b class="text-center block">${job.street_address}<br>${job.subdivision_name}<br>#${job.lot_number}</b>`,
            buttons: [
              {
                title: '<div class="btn cb-delete">Delete</div>',
                handler: () => {
                  this.deleteJob({ id: job.id })
                    .then(() => {
                      this.$refs.Table.doFetch();
                      this.$toastr("info", "Job Deleted!", "Info");
                    })
                    .catch((errors) => {
                      this.toastrErrors(errors);
                    });
                  this.$modal.hide('dialog');
                }
              },
              {
                title: 'Cancel',
              }
            ]
          });
        },
        confirmArchiveOrHideJob: function(job) {
          let self = this;
          this.$modal.show('dialog', {
              title: 'Confirm',
              text: 'Are you sure you want to mark this job as Archived or Hidden?',
              buttons: [
                  {
                      title: '<div class="btn cb-delete">Archive</div>',
                      handler: () => {
                          this.archiveOrHideJob({ id: job.id })
                          .then(() => {
                              this.$refs.Table.doFetch(1, this.filters);
                              this.$toastr("info", "Job marked as Archived or Hidden!", "Info");
                          })
                          .catch(function(error) {
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
                          });
                          this.$modal.hide('dialog');
                      }
                  },
                  {
                      title: 'Cancel',
                  }
              ]
          });
        },
        getJobs: function(params) {
          let data = {...params, role: this.$route.params.id};
          this.getJobsByRole(data);
        },
        goToTaskView: function(task) {
          this.$router.push({ name: "task-detail", params: { id: task.id } });
        },
        goToTaskEdit: function(task) {
          this.$router.push({ name: "update-task", params: { id: task.id } });
        },
        getTasks: function(params) {
          let data = {...params, role: this.$route.params.id};
          this.getTasksByRole(data);
        },
        getLoginAttempts: function(params) {
          let data = {...params, user: this.$route.params.id};
          this.getLoginAttemptsByUser(data);
        },
        getParticipantName: function(task, label){
          switch (label) {
            case 'B':
              return task.builder_name;
            case 'SC':
              return task.subcontractor_name;
            case 'CR':
              return task.superintendent_name;
            default:
              return '';
          }
        },
        addCrewStaff: function() {
            this.$router.push({
                name: "add-crew-staff",
                query: { crew_leader: this.$route.params.id }
            });
        },
        renderNotificationStatus: function(user, notification_type){
          return user[`enable_${notification_type}_notifications`] ? 'fa fa-bell text-success' : 'fa fa-bell-o text-danger';
        },
    },
    created() {
      this.getRoleById({ id: this.$route.params.id }).then(() => {
        this.getLoginAttemptsByUser({ user: this.role.user.id });
      })
      this.getTasksByRole({ role: this.$route.params.id });
      this.getJobsByRole({ role: this.$route.params.id });
      this.$root.$on('event-edit-user', this.goToUpdate);
      this.$root.$on('event-delete-user', this.confirmDeleteRole);
      this.$root.$on('event-reinvite-user', this.reinviteUser);
    },
    destroyed() {
      this.$root.$off('event-edit-user');
      this.$root.$off('event-delete-user');
      this.$root.$off('event-reinvite-user');
    }
};
</script>
