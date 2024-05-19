<template>
  <div id="TaskDetailPage">
    <Header />

    <header class="container" style="padding: 0;">
      <div class="row" style="margin: 13px 0;">
        <div class="col-md-4 col-sm-12"><h1 class="page-title bold" style="margin: 13px 0;">Task Details</h1></div>
        <div class="col-md-2 col-sm-6 col-xs-12">
          <button
            v-if="
              permission.isAdmin(currentUser) ||
              permission.isBuilder(currentUser) ||
              permission.isCrewLeader(currentUser)
            "
            class="btn upload-btn"
            v-on:click="addTask()"
            style="float:none; margin: 0;"
          >
            <i class="fa fa-plus-circle" aria-hidden="true"></i>Add New Task
          </button>
        </div>
        <div class="col-md-6 col-sm-6 col-xs-12" style="margin: 5px 0;">
          <ButtonHeadingCommon :buttons="commonButtons" class="common-buttons"/>
        </div>
      </div>
    </header>

    <main class="container-fluid main-fluid add-job-fluid">
      <div class="container">
        <article class="row top-form-article">
          <div v-if="task.is_completed" class="col-sm-12 text-right" style="margin-bottom: 20px;">
            <h3 class="task-details-title bold" style="color: #1abc9c;">
              <i class="fa fa-check-circle cb-check-circle" aria-hidden="true"></i>
              Completed
            </h3>
          </div>

          <div class="col-sm-4">
            <div class="row task-details-row">
              <span class="task-details-label bold w-auto block">Task Name:</span>
              <h3
                class="task-details-title bold"
                :class="task | statusDisplay">
                {{task.name}}
              </h3>
            </div>
            <div class="row task-details-row">
              <span class="task-details-label bold w-auto block">Scheduling Info:</span>
              <p class="task-details-p">
                <span class="task-details-value block row">
                  <div class="col-xs-6">
                    Start Date:
                    <datepicker
                      placeholder="Start Date"
                      v-model="newTask.start_date"
                      name="start_date"
                      format="MM/dd/yyyy"
                      input-class="fill-vdp"
                      use-utc
                      :disabledDates = "{
                        days: task.job_data ? task.job_data.owner_non_working_days_in_day_of_week : []
                      }"
                      @input="tickScheduleEdited"
                    />
                  </div>
                  <div class="col-xs-6">
                    End Date:
                    <datepicker
                      placeholder="End Date"
                      v-model="newTask.end_date"
                      name="end_date"
                      format="MM/dd/yyyy"
                      input-class="fill-vdp"
                      use-utc
                      :disabledDates = "{
                        days: task.job_data ? task.job_data.owner_non_working_days_in_day_of_week : []
                      }"
                      @input="tickScheduleEdited"
                    />
                  </div>
                </span>
                <span class="task-details-value block row">
                  <div class="col-xs-6">
                    Start Time:
                    <timepicker
                      placeholder="Start Time"
                      class=""
                      format="hh:mm A"
                      :minute-interval="15"
                      hide-clear-button
                      v-model="startTime"
                      @input="tickScheduleEdited"
                    />
                  </div>
                  <div class="col-xs-6">
                    End Time:
                    <timepicker
                      placeholder="End Time"
                      class=""
                      format="hh:mm A"
                      :minute-interval="15"
                      hide-clear-button
                      v-model="endTime"
                      @input="tickScheduleEdited"
                    />
                  </div>
                </span>
                <span class="task-details-value block row">
                  <div class="col-xs-12">
                    <button
                      class="btn btn-common btn-primary"
                      style="width: 100%;"
                      @click="submitTaskSchedule"
                      :disabled="!scheduleEdited">
                      <i class="text-sm fa fa-check" aria-hidden="true"></i>
                      Save
                    </button>
                  </div>
                </span>
              </p>
            </div>
          </div>

          <div class="col-sm-4">
            <div class="row task-details-row">
              <span class="task-details-label bold w-auto block">Location:</span>
              <p class="task-details-p">
                   <span class="task-details-value w-auto block">
                       {{task && task.job_data && task.job_data.subdivision_name}}
                       <span>#{{task && task.job_data && task.job_data.lot_number}}</span>
                   </span>
                   <span class="task-details-value w-auto block">
                       {{task && task.job_data && task.job_data.street_address}}<br />
                       {{task && task.job_data && task.job_data.city + " " + task.job_data.state + " " + task.job_data.zip}}
                   </span>
               </p>
            </div>
          </div>

          <div class="col-sm-4">
            <div class="row task-details-row task-details-roles">
              <span class="task-details-label bold w-auto block">Roles:</span>

                <div class="row">
                  <div class="btn-group col-xs-12">
                    <span
                      v-if="!task.builder"
                      class="btn btn-primary h-auto b-r-4">
                      B
                    </span>
                    <button
                      v-if="task.builder"
                      type="button"
                      class="btn btn-primary dropdown-toggle h-auto b-r-4"
                      v-bind:class="getResponseClass('B')"
                      data-toggle="dropdown"
                      aria-haspopup="true"
                      aria-expanded="false">
                      B <span class="caret"></span>
                    </button>
                    <ul v-if="task.builder" class="dropdown-menu">
                      <li><a href="#" v-on:click.prevent="updateParticipationResponse('B', 1)" class="accepted-bg">Accepted</a></li>
                      <li><a href="#" v-on:click.prevent="updateParticipationResponse('B', 2)" class="rejected-bg">Rejected</a></li>
                      <li><a href="#" v-on:click.prevent="updateParticipationResponse('B', 3)" class="pending-bg">Pending</a></li>
                    </ul>
                    <span class="task-details-value block">{{task && task.builder_name}}</span>
                  </div>
                </div>
                <div class="row">
                  <div class="btn-group col-xs-12">
                    <span
                      v-if="!task.subcontractor"
                      class="btn btn-primary h-auto b-r-4">
                      SC
                    </span>
                    <button
                      v-if="task.subcontractor"
                      type="button"
                      class="btn btn-primary dropdown-toggle h-auto b-r-4"
                      v-bind:class="getResponseClass('SC')"
                      data-toggle="dropdown"
                      aria-haspopup="true"
                      aria-expanded="false">
                      SC <span class="caret"></span>
                    </button>
                    <ul v-if="task.subcontractor" class="dropdown-menu">
                      <li><a href="#" v-on:click.prevent="updateParticipationResponse('SC', 1)" class="accepted-bg">Accepted</a></li>
                      <li><a href="#" v-on:click.prevent="updateParticipationResponse('SC', 2)" class="rejected-bg">Rejected</a></li>
                      <li><a href="#" v-on:click.prevent="updateParticipationResponse('SC', 3)" class="pending-bg">Pending</a></li>
                    </ul>
                    <span class="task-details-value">{{task && task.subcontractor_data && task.subcontractor_data.user.first_name + " " + task.subcontractor_data.user.last_name}}
                    </span>
                  </div>
                </div>
                <div class="row">
                  <div class="btn-group col-xs-12">
                    <span
                      v-if="!task.superintendent"
                      class="btn btn-primary h-auto b-r-4">
                      CR
                    </span>
                    <button
                      v-if="task.superintendent"
                      type="button"
                      class="btn btn-primary dropdown-toggle h-auto b-r-4"
                      v-bind:class="getResponseClass('CR')"
                      data-toggle="dropdown"
                      aria-haspopup="true"
                      aria-expanded="false">
                      CR <span class="caret"></span>
                    </button>
                    <ul v-if="task.superintendent" class="dropdown-menu">
                      <li><a href="#" v-on:click.prevent="updateParticipationResponse('CR', 1)" class="accepted-bg">Accepted</a></li>
                      <li><a href="#" v-on:click.prevent="updateParticipationResponse('CR', 2)" class="rejected-bg">Rejected</a></li>
                      <li><a href="#" v-on:click.prevent="updateParticipationResponse('CR', 3)" class="pending-bg">Pending</a></li>
                    </ul>
                    <span class="task-details-value">{{task && task.superintendent_data && task.superintendent_data.user.first_name + " " + task.superintendent_data.user.last_name}}</span>
                  </div>
                </div>
            </div>
            <div class="row task-details-row">
              <span class="task-details-label bold w-auto block">Created By:</span>
              <p class="task-details-p">
                 <span class="task-details-value w-auto block">
                   {{task && task.author_display}}
                 </span>
               </p>
            </div>
          </div>
        </article>

        <DetailNotes id="TaskNotes" :notes="task.all_notes" category="task" />

        <DetailContacts
          id="TaskContacts"
          class="row form-article"
          :contacts="task.all_contacts"
          :roles="allRoles"
          category="task"
          titleText="Task Contacts"
        >
          <tr v-if="task.builder">
            <td>{{task.builder_data.user.full_name}}</td>
            <td>Builder</td>
            <td>Task</td>
            <td>
              <i :class="renderNotificationStatus(task.builder_data.user, 'email')"></i>
              {{task.builder_data.user.email}}
            </td>
            <td>
              <i :class="renderNotificationStatus(task.builder_data.user, 'text')"></i>
              {{task.builder_data.user.mobile_number_display}}
            </td>
            <td>
              <span class="table-action-buttons">
                <ButtonTableAction
                  icon="edit"
                  @click.native.prevent="gotToUserUpdate(task.builder_data.id)"
                />
                <ButtonTableAction
                  icon="delete disabled"
                />
              </span>
            </td>
          </tr>
          <tr v-if="task.subcontractor">
            <td>{{task.subcontractor_data.user.full_name}} {{task.subcontractor_data.user.id}}</td>
            <td>Subcontractor</td>
            <td>Task</td>
            <td>
              <i :class="renderNotificationStatus(task.subcontractor_data.user, 'email')"></i>
              {{task.subcontractor_data.user.email}}
            </td>
            <td>
              <i :class="renderNotificationStatus(task.subcontractor_data.user, 'text')"></i>
              {{task.subcontractor_data.user.mobile_number_display}}
            </td>
            <td>
              <span class="table-action-buttons">
                <ButtonTableAction
                  icon="edit"
                  @click.native.prevent="gotToUserUpdate(task.subcontractor_data.id)"
                />
                <ButtonTableAction
                  icon="delete disabled"
                />
              </span>
            </td>
          </tr>
          <tr v-if="task.superintendent">
            <td>{{task.superintendent_data.user.full_name}}</td>
            <td>Crew / Flex</td>
            <td>Task</td>
            <td>
              <i :class="renderNotificationStatus(task.superintendent_data.user, 'email')"></i>
              {{task.superintendent_data.user.email}}
            </td>
            <td>
              <i :class="renderNotificationStatus(task.superintendent_data.user, 'text')"></i>
              {{task.superintendent_data.user.mobile_number_display}}
            </td>
            <td>
              <span class="table-action-buttons">
                <ButtonTableAction
                  icon="edit"
                  @click.native.prevent="gotToUserUpdate(task.superintendent_data.id)"
                />
                <ButtonTableAction
                  icon="delete disabled"
                />
              </span>
            </td>
          </tr>
        </DetailContacts>

        <DetailDocuments :documents="task.documents" category="task" />
        <article class="row form-article">
          <h3 class="cb-h3 text-uppercas bold">Reminders:</h3>
          <div class="table-responsive">
              <table class="table table-bordered add-job-table">
                <thead>
                  <tr>
                    <th>Reminder</th>
                    <th>Sent?</th>
                    <th width="10%">Action</th>
                  </tr>
                </thead>
                <tbody>
                    <tr v-for="reminder in task.reminders" v-bind:key="reminder.id">
                      <td>{{reminder.reminder_days_display}}</td>
                      <td v-if="reminder.reminder_sent">{{ reminder.reminder_sent | date("MM/DD/YYYY") }}</td>
                      <td v-else>Not yet</td>
                      <td class="job-detail-task-edit">
                          <a href="" @click.prevent="confirmDeleteReminder(reminder)">
                              <h4>
                                  <i class="text-sm text-danger fa fa-trash" aria-hidden="true">
                                  </i>
                              </h4>
                          </a>
                      </td>
                    </tr>
                </tbody>
              </table>
            </div>

            <div class="form-group">
              <label class="cb-label bold">Add Reminder</label>
              <v-select
                v-model="newReminderDays"
                v-bind:options="filteredReminderDays"
                label="display_name"
                class="form-control cb-input mb-1">
                <template slot="option" slot-scope="option">
                  {{option.display_name}}
                </template>
              </v-select>
              <button class="btn upload-btn pull-right add-reminder" v-on:click="submitReminder()" :disabled="!this.newReminderDays">
                <i class="fa fa-plus-circle" aria-hidden="true"></i>Add Reminder
              </button>
            </div>
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
import DetailNotes from "@/components/Detail/Notes.vue";
import DetailContacts from "@/components/Detail/Contacts.vue";
import DetailDocuments from "@/components/Detail/Documents.vue";
import ButtonTableAction from '@/components/Button/TableAction.vue';
import ButtonHeadingCommon from "@/components/Button/HeadingCommon.vue";
import Footer from "@/components/Footer.vue";
import { mapState, mapActions } from "vuex";
import moment from "moment";
import { permission } from "../router-helper"

import VueDropzone from 'vue2-dropzone';
import 'vue2-dropzone/dist/vue2Dropzone.min.css';

export default {
    name: "TaskDetailPage",
    components: {
        Header,
        PageHeading,
        DetailNotes,
        DetailContacts,
        DetailDocuments,
        ButtonTableAction,
        ButtonHeadingCommon,
        Footer,
        VueDropzone,
    },
    computed: {
        ...mapState([
          "loading",
          "allRoles",
          "task",
          "allUsers",
          "currentUser",
          "reminderDays"
        ]),
        commonButtons: function() {
          if (! this.task.id) {
            return []
          }
          if (!
            (
              this.permission.hasTaskPermission(this.currentUser, this.task)
            )
          ) {
            return [{ name: 'Go Back', type: 'return' },]
          }
          if (! this.permission.isAdminOrCreator(this.currentUser, this.task)) {
            return [
              { name: 'Go Back', type: 'return' },
              { name: 'Complete', type: 'complete', action: 'event-complete-task'},
              { name: 'Edit', type: 'edit', action: 'event-edit-task'}
            ]
          }
          return [
            { name: 'Go Back', type: 'return' },
            { name: 'Complete', type: 'complete', action: 'event-complete-task'},
            { name: 'Delete', type: 'delete', action: 'event-delete-task'},
            { name: 'Edit', type: 'edit', action: 'event-edit-task'}
          ]
        },
        noteButton: function(){
          return this.currentEditNote ? 'Save Note' : 'Add Note';
        },
        contactButton: function(){
          return this.currentEditContact ? 'Save Contact' : 'Add Contact';
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
    },
    data: function() {
        return {
            moment,
            permission,
            newNoteText: "",
            currentEditNote: null,
            currentEditContact: null,
            newContact: {
                name: "",
                email: "",
                mobile_number: "",
                enable_text_notifications: false,
                enable_email_notifications: false
            },
            dropzoneOptions: {
                url: this.submitDocuments,
                dictDefaultMessage: "Drop files or click to upload here."
            },
            newReminderDays: null,
            filteredReminderDays: [],
            newTask: {
              start_date: moment().toDate(),
              end_date: moment().toDate(),
              start_time: "09:00:00",
              end_time: "17:00:00",
            },
            scheduleEdited: false,
        };
    },
    methods: {
        ...mapActions([
            "getTaskById",
            "patchParticipation",
            "addNote",
            "updateNote",
            "addDocument",
            "addReminder",
            "addContact",
            "updateContact",
            "getAllUsers",
            "getAllReminderDays",
            "getAllRoles",
            "updateTask",
            "completeTask",
            "deleteTask",
            "deleteNote",
            "deleteContact",
            "deleteDocument",
            "deleteReminder"
        ]),
        submitTaskSchedule() {
          if (this.errors.any()) {
            return;
          }

          let task = {
            _alsoSendNotifications: true,
            start_date: this.newTask.start_date && moment.utc(this.newTask.start_date).format("YYYY-MM-DD"),
            end_date: this.newTask.end_date && moment.utc(this.newTask.end_date).format("YYYY-MM-DD"),
            start_time: this.newTask.start_time,
            end_time: this.newTask.end_time,

            is_completed: this.task.is_completed,
            name: this.task.name,
            job: this.task.job,
            subcontractor: this.task.subcontractor,
            superintendent: this.task.superintendent,
            builder: this.task.builder,
            category: this.task.category,
            subcategory: this.task.subcategory,
          }
          this.update(task);
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
              this.$router.replace({
                name: "task-detail",
                params: { id: this.$route.params.id }
              });
            })
            .catch(errors => {
              this.newTask._alsoSendNotifications = false
              this.toastrErrors(errors);
            });
        },
        renderNotificationStatus: function(user, notification_type){
          return user[`enable_${notification_type}_notifications`] ? 'fa fa-bell text-success' : 'fa fa-bell-o text-danger';
        },
        gotToUserUpdate: function(id){
          this.$router.push({
            name: "update-user",
            params: { id: id }
          });
        },
        confirmCompleteTask: function() {
            let self = this;
            this.$modal.show('dialog', {
                title: 'Confirm',
                text: 'Are you sure you want to mark this task as Completed?',
                buttons: [
                    {
                        title: '<div class="btn cb-delete">Complete</div>',
                        handler: () => {
                            this.completeTask({ id: this.$route.params.id })
                            .then(() => {
                                this.$router.push({ name: "tasks"})
                                this.$toastr("info", "Task marked as Completed!", "Info");
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
        confirmDeleteTask: function() {
            let self = this;
            this.$modal.show('dialog', {
                title: 'Confirm',
                text: 'Are you sure you want to delete this task?',
                buttons: [
                    {
                        title: '<div class="btn cb-delete">Delete</div>',
                        handler: () => {
                            this.deleteTask({ id: this.$route.params.id })
                            .then(() => {
                                this.$router.push({ name: "tasks"})
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
        confirmDeleteNote: function(note) {
            this.$modal.show('dialog', {
                title: 'Confirm',
                text: 'Are you sure you want to delete this note?',
                buttons: [
                    {
                        title: '<div class="btn cb-delete">Delete</div>',
                        handler: () => {
                            this.deleteNote({ id: note.id })
                                .then(() => {
                                    this.getTaskById({ id: this.$route.params.id });
                                    this.$toastr("info", "Note Deleted!", "Info");
                                })
                            this.$modal.hide('dialog');
                        }
                    },
                    {
                        title: 'Cancel',
                    }
                ]
            });
        },
        confirmDeleteDocument: function(document) {
            this.$modal.show('dialog', {
                title: 'Confirm',
                text: 'Are you sure you want to delete this document?',
                buttons: [
                    {
                        title: '<div class="btn cb-delete">Delete</div>',
                        handler: () => {
                            this.deleteDocument({ id: document.id })
                                .then(() => {
                                    this.getTaskById({ id: this.$route.params.id });
                                    this.$toastr("info", "Document Deleted!", "Info");
                                })
                            this.$modal.hide('dialog');
                        }
                    },
                    {
                        title: 'Cancel',
                    }
                ]
            });
        },
        confirmDeleteReminder: function(reminder) {
            this.$modal.show('dialog', {
                title: 'Confirm',
                text: 'Are you sure you want to delete this reminder?',
                buttons: [
                    {
                        title: '<div class="btn cb-delete">Delete</div>',
                        handler: () => {
                            this.deleteReminder({ id: reminder.id })
                                .then(() => {
                                    this.getTaskById({ id: this.$route.params.id }).then(() => {
                                        this.getAllReminderDays().then(() => {
                                            const existingReminderDays = this.task.reminders.map(reminder => reminder.reminder_days);
                                            this.filteredReminderDays = this.reminderDays.filter(day => !existingReminderDays.includes(day.value));
                                        });
                                    });
                                    this.$toastr("info", "Reminder Deleted!", "Info");
                                })
                            this.$modal.hide('dialog');
                        }
                    },
                    {
                        title: 'Cancel',
                    }
                ]
            });
        },
        editContactDetails: function(contact) {
          this.currentEditContact = contact;
          let gap = contact.name.indexOf(" ");
          this.newContact = {
              ...this.newContact,
              first_name: contact.name.slice(0,gap),
              last_name: contact.name.slice(gap),
              enable_email_notifications: contact.enable_email_notifications,
              enable_text_notifications: contact.enable_text_notifications,
              email: contact.email,
              mobile_number: contact.mobile_number,
              note: contact.note,
          };
        },
        confirmDeleteContact: function(contact) {
            this.$modal.show('dialog', {
                title: 'Confirm',
                text: 'Are you sure you want to delete this contact?',
                buttons: [
                    {
                        title: '<div class="btn cb-delete">Delete</div>',
                        handler: () => {
                            this.deleteContact({ id: contact.id })
                                .then(() => {
                                    this.editContactDetails = null;
                                    this.getTaskById({ id: this.$route.params.id });
                                    this.$toastr("info", "Contact Deleted!", "Info");
                                })
                            this.$modal.hide('dialog');
                        }
                    },
                    {
                        title: 'Cancel',
                    }
                ]
            });
        },
        addTask: function() {
            this.$router.push({ name: "add-task" });
        },
        goToUpdate: function() {
          this.$router.push({
            name: "update-task",
            params: { id: this.$route.params.id }
          });
        },
        getParticipation: function(label) {
            let participants = (this.task && this.task.participant_statuses) || [];
            return participants.reduce(function(participation, current) {
                if (current.label == label) {
                    return current;
                } else {
                    return participation;
                }
            }, null);
        },
        getResponseClass: function(label) {
            let participation = this.getParticipation(label);
            if (!participation) {
                return "not-applicable-bg";
            }
            if (participation.status == "accepted") {
                return "accepted-bg";
            }
            if (participation.status == "rejected") {
                return "rejected-bg";
            }
            if (participation.status == "pending") {
                return "pending-bg";
            }
            return "";
        },
        updateParticipationResponse: function(label, response) {
            let participation = this.getParticipation(label);
            if (!participation) {
                this.$toastr("error", "Not applicable", "error");
                return;
            }
            let payload = {
                id: participation.participation_id,
                response: response
            };
            let self = this;
            this.patchParticipation(payload)
                .then(function() {
                    self.getTaskById({ id: self.$route.params.id });
                    self.$toastr("info", "Participation updated", "info");
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
        },
        submitContact: function() {
            let self = this;
            let payload = Object.assign(this.newContact, {
                name: `${this.newContact.first_name} ${this.newContact.last_name}`,
                task: parseInt(this.$route.params.id, 10),
                created_timestamp: moment.utc().format(),
                modified_timestamp: moment.utc().format()
            });

            const submitSuccess = () => {
              self.newContact = {
                  name: "",
                  email: "",
                  mobile_number: "",
                  enable_text_notifications: false,
                  enable_email_notifications: false
              };
              self.getTaskById({ id: self.$route.params.id });
              self.$toastr("info", "Contact saved", "info");
              self.currentEditContact = null;
            }

            const submitFailure = (error) => {
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
            }

            if (this.currentEditContact) {
              payload = {
                ...payload,
                id: this.currentEditContact.id,
              }
              this.updateContact(payload)
                .then(function() {
                  submitSuccess();
                })
                .catch(function(error) {
                  submitFailure(error);
                })
            } else {
              this.addContact(payload)
                .then(function() {
                  submitSuccess();
                })
                .catch(function(error) {
                  submitFailure(error);
                });
            }
        },
        submitReminder: function() {
            let self = this;
            let payload = {
              task: parseInt(this.$route.params.id, 10),
              reminder_days: this.newReminderDays.value
            };
            this.addReminder(payload)
                .then(function() {
                    self.newReminderDays = null;
                    self.getTaskById({ id: self.$route.params.id }).then(() => {
                        self.getAllReminderDays().then(() => {
                            const existingReminderDays = self.task.reminders.map(reminder => reminder.reminder_days);
                            self.filteredReminderDays = self.reminderDays.filter(day => !existingReminderDays.includes(day.value));
                        });
                    });
                    self.$toastr("info", "Reminder saved", "info");
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
        },
        submitDocuments: function(file) {
            let self = this;
            let document = file[0];
            if (!document) {
                this.$toastr("error", "No file attached", "error");
                return;
            }
            let formData = new FormData();
            formData.append("filename", document);
            formData.append("task", parseInt(this.$route.params.id, 10));
            formData.append("created_timestamp", moment.utc().format());
            formData.append("modified_timestamp", moment.utc().format());

            this.addDocument(formData)
                .then(function() {
                    self.getTaskById({ id: self.$route.params.id });
                    self.$toastr("info", "Document saved", "info");
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
        },
        removeAllFiles: function() {
          this.$refs.vueDropzone.removeAllFiles();
        },
        editNote: function(note) {
          this.newNoteText = note.text;
          this.currentEditNote = note;
        },
        submitNote: function() {
          let self = this;
          let payload = {
              task: parseInt(this.$route.params.id, 10),
              text: this.newNoteText,
              created_timestamp: moment.utc().format(),
              modified_timestamp: moment.utc().format()
          };

          const submitSuccess = () => {
            self.newNoteText = "";
            this.currentEditNote = null;
            self.getTaskById({ id: self.$route.params.id });
            self.$toastr("info", "Note saved", "info");
          }

          const submitFailure = (error) => {
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
          }

          if (this.currentEditNote) {
            payload = {
              ...payload,
              created_timestamp: this.currentEditNote.created_timestamp,
              id: this.currentEditNote.id
            }
            this.updateNote(payload)
              .then(function() {
                submitSuccess()
              })
              .catch(function(error) {
                submitSuccess(error)
              });
          } else {
            this.addNote(payload)
              .then(function() {
                submitSuccess()
              })
              .catch(function(error) {
                submitSuccess(error)
              });
          }
        },
        cancel: function() {
            this.$router.push({ name: "tasks" });
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
      tickScheduleEdited() {
        this.scheduleEdited = true;
      },
    },

    mounted: function() {
        this.$nextTick(function() {
            // Code that will run only after the
            // entire view has been rendered
        });
    },
    created() {
      this.filteredReminderDays = this.reminderDays;
      this.getTaskById({ id: this.$route.params.id })
        .then(() => {
          if (this.task && this.task.reminders){
            this.getAllReminderDays().then(() => {
                const existingReminderDays = this.task.reminders.map(reminder => reminder.reminder_days);
                this.filteredReminderDays = this.reminderDays.filter(day => !existingReminderDays.includes(day.value));
            });
            this.newTask.start_date = this.task.start_date;
            this.newTask.end_date = this.task.end_date;
            this.newTask.start_time = this.task.start_time;
            this.newTask.end_time = this.task.end_time;
          }
        })
        .catch(() => {
          this.$router.push({ name: "tasks" });
        })
      this.getAllRoles({});
      this.getAllUsers();

      this.$root.$on('event-edit-task', this.goToUpdate);
      this.$root.$on('event-delete-task', this.confirmDeleteTask);
      this.$root.$on('event-complete-task', this.confirmCompleteTask);
    },
    destroyed() {
      this.$root.$off('event-edit-task');
      this.$root.$off('event-delete-task');
      this.$root.$off('event-complete-task');
    }
};
</script>

<style lang="scss">
  $input-height: 50px;
  $padding-x: 12px;

  .top-form-article {
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
  }

  .task-details-title {
    margin: 0;
  }

  .add-reminder {
    margin-bottom: 50px;
  }

  .common-buttons {
    float: right;
  }

  @media (max-width: 768px) {
  .common-buttons {
    justify-content: start;
  }
  }
</style>
