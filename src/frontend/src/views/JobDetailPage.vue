<template>
  <div id="JobDetailPage">
    <Header/>
    <PageHeading text="Job Details">
      <ButtonHeadingCommon :buttons="commandButtons"/>
    </PageHeading>

    <main class="container-fluid main-fluid add-job-fluid">
      <div class="container">
        <article id="JobHeader" class="row form-article">
          <div class="col-sm-6">
            <div class="row task-details-row">
              <span class="task-details-label bold w-auto block">Job Address:</span>
              <h3 class="task-details-title bold">{{job.street_address}}</h3>

              <DetailPrimaryContact titleText="General Contractor">
                {{job.owner_name}}
              </DetailPrimaryContact>
            </div>
            <div class="row task-details-row task-details-roles">
              <span class="task-details-label bold w-auto block">Primary Contacts:</span>

              <DetailPrimaryContact titleText="Builder">
                {{job.builder_name}}
              </DetailPrimaryContact>

              <DetailPrimaryContact titleText="Subcontractor">
                {{job.subcontractor_name}}
              </DetailPrimaryContact>

              <DetailPrimaryContact titleText="Crew / Flex">
                {{job.superintendent_name}}
              </DetailPrimaryContact>

              <DetailPrimaryContact titleText="Created By">
                {{job.created_by_name}}
              </DetailPrimaryContact>

            </div>
          </div>

          <div class="col-md-6">
            <DetailHeadingItem titleText="Lot #">
              #{{job.lot_number}}
            </DetailHeadingItem>

            <DetailHeadingItem titleText="Subdivision">
              {{job.subdivision_name}}
            </DetailHeadingItem>

            <DetailHeadingItem titleText="Full Address">
              {{job.street_address}}
              <br>
              {{job.city}} {{job.state}} {{job.zip}}
            </DetailHeadingItem>
          </div>
        </article>

        <article id="JobRoleAccess" class="row form-article">
          <h3 class="cb-h3 bold">Roles:</h3>
          <div class="table-responsive">
            <table class="table table-bordered add-job-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Company</th>
                  <th class="action-column">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="role in jobRoles" v-bind:key="role.id">
                  <td>{{role.user.first_name}} {{role.user.last_name}}</td>
                  <td>{{role.user_types_other_display}}</td>
                  <td>{{role.company_name}}</td>
                  <td>
                    <!-- <DetailTableAction :actions="tableActions" /> -->
                    <span class="table-action-buttons">
                      <ButtonTableAction
                        v-if="job.created_by == currentUser.active_role.company || role.company == currentUser.active_role.company"
                        icon="delete"
                        @click.native.prevent="confirmRemoveRole(role)"
                      />
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="row add-contact">
            <div class="col-xs-12 col-sm-9">
              <label class="cb-label">Name</label>
              <v-select
                multiple
                v-model="sharedRoles"
                v-bind:options="unsharedRoles"
                label="user_full_name"
                placeholder="Select role to invite"
                class="form-control cb-input">
              </v-select>
            </div>
            <div class="col-xs-12 col-sm-3">
              <label class="cb-label hidden-label block">.</label>
              <button class="btn upload-btn pull-right" v-on:click="doAddRoles()">
                <i class="fa fa-plus-circle" aria-hidden="true"></i>
                Add Role
              </button>
            </div>
          </div>
        </article>

        <DetailNotes id="JobNotes" :notes="job.notes" category="job" />

        <DetailContacts
          id="DetailContacts"
          class="row form-article"
          :contacts="job.contacts"
          :roles="allRoles"
          category="job"
          titleText="Job Contacts"
        />

        <DetailDocuments :documents="job.documents" category="job" />
        <router-link
            v-bind:to="{name: 'add-task', query: {job: job.id}}"
            tag="button"
            class="btn upload-btn pull-right"
          >
            <i class="fa fa-plus-circle" aria-hidden="true"></i>Add Task
          </router-link>
        <article id="JobTasks" class="row form-article">
          <h3 class="cb-h3 bold">Tasks for this Job:</h3>
          <Table
            ref="tasksTable"
            :fetch="getTasks"
            :items="tasks"
            :count="tasksCount"
            :pageSize="tasksPageSize"
            :pageIndex="tasksPageIndex"
            :numPages="tasksNumPages"
            :keywords="keywords"
            :ordering="tasksOrdering"
            :initialOrdering="ordering"
            :headers="headers"
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
                    v-if="permission.hasTaskPermission(currentUser, task)"
                    icon="edit"
                    @click.native.prevent="goToTaskEdit(task)"
                  />
                  <ButtonTableAction
                    v-if="permission.hasTaskPermission(currentUser, task)"
                    icon="delete"
                    @click.native.prevent="confirmDeleteTask(task)"
                  />
                </span>
              </td>
            </tr>
          </Table>
        </article>

      </div>
      <Footer/>
      <v-dialog />
    </main>
  </div>
</template>

<script>
// @ is an alias to /src
import Header from "@/components/Header.vue";
import PageHeading from "@/components/PageHeading.vue";
import DetailPrimaryContact from "@/components/Detail/PrimaryContact.vue";
import DetailHeadingItem from "@/components/Detail/HeadingItem.vue";
import DetailNotes from "@/components/Detail/Notes.vue";
import DetailContacts from "@/components/Detail/Contacts.vue";
import DetailDocuments from "@/components/Detail/Documents.vue";
import Table from "@/components/Table.vue";
import ButtonTableAction from '@/components/Button/TableAction.vue';
import ButtonHeadingCommon from '@/components/Button/HeadingCommon.vue';
import Footer from "@/components/Footer.vue";
import { permission } from "../router-helper"

import { mapState, mapActions } from "vuex";
import moment from "moment";

import VueDropzone from 'vue2-dropzone';
import 'vue2-dropzone/dist/vue2Dropzone.min.css';

export default {
  name: "JobDetailPage",
  components: {
    Header,
    PageHeading,
    DetailPrimaryContact,
    DetailHeadingItem,
    DetailNotes,
    DetailContacts,
    DetailDocuments,
    Table,
    ButtonTableAction,
    ButtonHeadingCommon,
    Footer,
    VueDropzone,
  },
  data: function() {
    return {
      permission,
      addRoleModal: {
        title: "",
      },
      newRole: {
        user: {
          first_name: "",
          last_name: "",
          email: "",
        },
      },
      sharedTo: [],
      sharedRoles: [],
      headers: [
          {key: 'name', label: 'Name', sort: true},
          {key: 'start_date', label: 'Start Date', sort: true},
          {key: 'end_date', label: 'End Date', sort: true},
          {key: 'participants', label: 'Participants', sort: false},
          {key: 'actions', label: 'Actions', sort: false}
      ],
      keywords: "",
      ordering: "-start_date",
      jobRoles: [],
      unsharedRoles: [],
    };
  },
  computed: {
    ...mapState([
      'currentUser',
      "loading",
      "job",
      "allRoles",
      "tasks",
      "tasksCount",
      "tasksPageSize",
      "tasksPageIndex",
      "tasksOrdering",
      "tasksNumPages"
    ]),
    commandButtons() {
      if (
        ! (
          this.currentUser.active_role.company === this.job.owner ||
          this.currentUser.active_role.company === this.job.created_by
        )
      ) {
        return [{ name: 'Go Back', type: 'return' }]
      }
      let commonButtons = [
        { name: 'Go Back', type: 'return' },
        { name: 'Hide or Archive', type: 'archive', action: 'event-archive-or-hide-job'},
        { name: 'Delete', type: 'delete', action: 'event-delete-job'},
        { name: 'Edit', type: 'edit', action: 'event-edit-job'}
      ]
      if (!this.job.is_archived) {
        return commonButtons;
      } else {
        commonButtons[1].name = 'Active';
        commonButtons[1].action = 'event-unarchive-or-hide-job';
        return commonButtons;
      }
    }
  },
  methods: {
    ...mapActions([
        "getJobById",
        "deleteJob",
        "getAllRoles",
        "shareJobToCompany",
        "unshareJobToCompany",
        "shareJobToRole",
        "unshareJobToRole",
        "getTaskByJob",
        "deleteTask",
        "archiveOrHideJob",
        "unarchiveOrHideJob",
    ]),
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
    goToUpdate: function() {
      this.$router.push({
        name: "update-job",
        params: { id: this.$route.params.id }
      });
    },
    goToTaskView: function(task) {
      this.$router.push({
        name: "task-detail",
        params: { id: task.id }
      });
    },
    goToTaskEdit: function(task) {
      this.$router.push({
        name: "update-task",
        params: { id: task.id }
      });
    },
    confirmDeleteJob: function() {
      this.$modal.show('dialog', {
          title: 'Confirm',
          text: 'Are you sure you want to delete this job?',
          buttons: [
              {
                  title: '<div class="btn cb-delete">Delete</div>',
                  handler: () => {
                    this.deleteJob({ id: this.$route.params.id })
                      .then(() => {
                          this.$router.push({ name: "jobs"})
                          this.$toastr("info", "Job Deleted!", "Info");
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
    confirmDeleteTask: function(task) {
      let self = this;
      this.$modal.show('dialog', {
          title: 'Delete Task',
          text: `Are you sure you want to delete the <b>${task.name}</b> task?`,
          buttons: [
              {
                  title: '<div class="btn cb-delete">Delete</div>',
                  handler: () => {
                      this.deleteTask({ id: task.id })
                        .then(() => {
                            this.getTaskByJob({ job: this.$route.params.id });
                            this.$toastr("info", "Task Deleted!", "Info");
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
    confirmArchiveOrHideJob: function() {
        let self = this;
        this.$modal.show('dialog', {
            title: 'Confirm',
            text: 'Are you sure you want to mark this job as Archived or Hidden?',
            buttons: [
                {
                    title: '<div class="btn cb-delete">Archive</div>',
                    handler: () => {
                        this.archiveOrHideJob({ id: this.$route.params.id })
                        .then(() => {
                            this.$router.push({ name: "jobs"})
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
    confirmUnarchiveOrHideJob: function() {
      let self = this;
      this.$modal.show('dialog', {
          title: 'Confirm',
          text: 'Are you sure you want to mark this job as Active?',
          buttons: [
              {
                  title: '<div class="btn cb-delete">Archive</div>',
                  handler: () => {
                      this.unarchiveOrHideJob({ id: this.$route.params.id })
                      .then(() => {
                          this.$router.push({ name: "jobs"})
                          this.$toastr("info", "Job marked as Active", "Info");
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
    getTasks: function(params) {
      let data = {
        ...params,
        job: this.$route.params.id
      }
       this.getTaskByJob(data);
    },
    doAddRoles: function() {
      const promises = this.sharedRoles.map(sharedRole => this.shareJobToRole({ job: this.job, sharedTo: sharedRole.id }));
      Promise.all(promises).then(() => {
        this.$toastr("success", "Shared job to role" + (this.sharedTo.length === 1 ? "" : "s"), "success");
        this.sharedRoles = [];
        this.getJobById({ id: this.$route.params.id });
        this.getAllRoles({ job: this.$route.params.id }).then((response) => {
          this.jobRoles = response.data;
        });
        this.getAllRoles({ excludeJob: this.$route.params.id }).then((response) => {
          this.unsharedRoles = response.data;
        });
      });
    },
    confirmRemoveRole: function(role) {
      this.$modal.show('dialog', {
        title: 'Remove Role Access',
        text: `Are you sure you want to remove access for <b>${role.user.first_name} ${role.user.last_name}</b> on this job?`,
        buttons: [
          {
            title: '<div class="btn cb-delete">Remove</div>',
            handler: () => {
              this.unshareJobToRole({ job: this.job, sharedTo: role.id })
                .then(() => {
                  this.$toastr("info", "Company Removed!", "Info");
                  this.getJobById({ id: this.$route.params.id });
                  this.getAllRoles({ excludeJob: this.$route.params.id });
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
  },
  mounted: function() {
    this.$nextTick(function() {
      // Code that will run only after the
      // entire view has been rendered
    });
  },
  created() {
    this.getJobById({ id: this.$route.params.id });
    this.getAllRoles({ job: this.$route.params.id }).then((response) => {
      this.jobRoles = response.data;
    });
    this.getAllRoles({ excludeJob: this.$route.params.id }).then((response) => {
      this.unsharedRoles = response.data;
    });
    this.getAllRoles({});
    this.getTaskByJob({ job: this.$route.params.id });

    this.$root.$on('event-edit-job', this.goToUpdate);
    this.$root.$on('event-delete-job', this.confirmDeleteJob);
    this.$root.$on('event-archive-or-hide-job', this.confirmArchiveOrHideJob);
    this.$root.$on('event-unarchive-or-hide-job', this.confirmUnarchiveOrHideJob);
  },
  destroyed() {
    this.$root.$off('event-edit-job');
    this.$root.$off('event-delete-job');
  }
};
</script>

<style scoped>
  h3.task-details-title {
    margin: 0;
  }
</style>
