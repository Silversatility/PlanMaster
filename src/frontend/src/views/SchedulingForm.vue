<template>
  <div>
    <section class="container-fluid main-fluid cf-fluid schedule-editor-form">
      <h3 class="cb-h3 bold">Standard Workdays</h3>
      <div class="days-wrap d-flex justify-content-between align-items-center flex-wrap mb-5">
        <div>
          <input type="checkbox" class="cb-checkbox mr-2" v-model="newSchedule.monday" />
          <label class="cb-label">Monday</label>
        </div>
        <div>
          <input type="checkbox" class="cb-checkbox mr-2" v-model="newSchedule.tuesday" />
          <label class="cb-label">Tuesday</label>
        </div>
        <div>
          <input type="checkbox" class="cb-checkbox mr-2" v-model="newSchedule.wednesday" />
          <label class="cb-label">Wednesday</label>
        </div>
        <div>
          <input type="checkbox" class="cb-checkbox mr-2" v-model="newSchedule.thursday" />
          <label class="cb-label">Thursday</label>
        </div>
        <div>
          <input type="checkbox" class="cb-checkbox mr-2" v-model="newSchedule.friday" />
          <label class="cb-label">Friday</label>
        </div>
        <div>
          <input type="checkbox" class="cb-checkbox mr-2" v-model="newSchedule.saturday" />
          <label class="cb-label">Saturday</label>
        </div>
        <div>
          <input type="checkbox" class="cb-checkbox mr-2" v-model="newSchedule.sunday" />
          <label class="cb-label">Sunday</label>
        </div>
      </div>
      <div class="mb-4">
        <h3 class="cb-h3 bold">Standard Working Hours</h3>
      </div>
      <div id="Times" class="d-flex justify-content-start align-items-center flex-wrap">
        <div class="mr-5">
          <label class="cb-label block">Daily Start Time:</label>
          <timepicker
            class
            format="hh:mm a"
            :minute-interval="15"
            hide-clear-button
            v-model="startTime"
          />
        </div>
        <div>
          <label class="cb-label block">Daily End Time:</label>
          <timepicker
            class
            format="hh:mm a"
            :minute-interval="15"
            hide-clear-button
            v-model="endTime"
          />
        </div>
      </div>
      <button class="btn btn-common btn-primary mb-5" @click="saveScheduleDetails">Save</button>
      <h3 class="cb-h3 bold">Default Reminders</h3>
      <div>
        <div class="table-responsive">
          <table class="table table-bordered add-job-table">
            <thead>
              <tr>
                <th>
                  <a v-on:click.prevent="sort('task')">Reminder</a>
                </th>
                <th>
                  <a v-on:click.prevent="sort('type')">Action</a>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="reminder in reminders" v-bind:key="reminder.id">
                <td>{{reminder.reminder_days_display}}</td>
                <td>
                  <span class="table-action-buttons">
                    <ButtonTableAction
                      icon="delete"
                      @click.native.prevent="confirmDeleteReminder(reminder)"
                    />
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="d-flex justify-content-start">
        <div>
          <v-select
            name="reminder_dropdown"
            v-model="newReminder"
            label="display_name"
            v-bind:options="filteredReminderDays"
            class="form-control cb-input"
          ></v-select>
          <template slot="option" slot-scope="option">{{option.display_name}}</template>
        </div>
        <button class="btn cf-btn cb-input default" @click="submitDefaultReminder()">Add</button>
      </div>
    </section>
    <v-dialog />
  </div>
</template>

<script>
// @ is an alias to /src

import { mapState, mapActions } from "vuex";
import _ from "lodash";
import ButtonTableAction from "@/components/Button/TableAction.vue";

export default {
  name: "SchedulingForm",
  components: {
    ButtonTableAction
  },
  data: function() {
    return {
      activetab: 1,
      companyName: "",
      billingAddress: "",
      addressLine2: "",
      city: "",
      state: "",
      zipCode: "",
      newReminder: null,
      newSchedule: {},
      start_time: "8 am",
      end_time: "5 pm",
      filteredReminderDays: []
    };
  },
  computed: {
    ...mapState(["company", "reminders", "currentUser", "defaultReminderDays"]),
    startTime: {
      get() {
        return this.pickerTime(this.newSchedule.start_of_day);
      },
      set(time) {
        this.newSchedule.start_of_day = this.crewbossTime(time);
      }
    },
    endTime: {
      get() {
        return this.pickerTime(this.newSchedule.end_of_day);
      },
      set(time) {
        this.newSchedule.end_of_day = this.crewbossTime(time);
      }
    }
  },
  methods: {
    ...mapActions([
      "updateShedule",
      "getCompanyById",
      "getAllDefaultReminders",
      "getAllDefaultReminderDays",
      "deleteDefaultReminder",
      "addDefaultReminder"
    ]),
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
    saveScheduleDetails: function() {
      this.updateShedule(this.newSchedule)
        .then(() => {
          this.$toastr("info", "Schedule updated", "info");
        })
        .catch(errors => {
          this.toastrErrors(errors);
        });
    },
    submitDefaultReminder: function() {
      let self = this;
      let valid = true;
      if (!this.newReminder) {
        self.$toastr("error", "Select a reminder", "error");
        return;
      }
      this.reminders.forEach(function(reminder) {
        if (reminder.reminder_days == self.newReminder.value) {
          self.$toastr("error", "Reminder already exists", "error");
          valid = false;
        }
      });
      if (valid) {
        let payload = {
          reminder_days: this.newReminder.value,
          company: this.company.id
        };
        this.addDefaultReminder(payload)
          .then(() => {
            self.$toastr("info", "Reminder added", "info");
            self.newReminder = null;
            self.getAllDefaultReminders().then(() => {
              self.getAllDefaultReminderDays().then(() => {
                const existingReminderDays = self.reminders.map(
                  reminder => reminder.reminder_days
                );
                self.filteredReminderDays = self.defaultReminderDays.filter(
                  day => !existingReminderDays.includes(day.value)
                );
              });
            });
          })
          .catch(function(error) {
            let message = "";
            for (var key in error) {
              let value = error[key];
              message +=
                key + " " + (value.length ? value.join(", ") : value) + "\n";
            }
            self.$toastr("error", message, "error");
          });
      }
    },
    confirmDeleteReminder: function(reminder) {
      this.$modal.show("dialog", {
        title: "Confirm",
        text: "Are you sure you want to delete this reminder?",
        buttons: [
          {
            title: '<div class="btn cb-delete">Delete</div>',
            handler: () => {
              this.deleteDefaultReminder({ id: reminder.id }).then(() => {
                this.getAllDefaultReminders().then(() => {
                  this.getAllDefaultReminderDays().then(() => {
                    const existingReminderDays = this.reminders.map(
                      reminder => reminder.reminder_days
                    );
                    this.filteredReminderDays = this.defaultReminderDays.filter(
                      day => !existingReminderDays.includes(day.value)
                    );
                  });
                });
                this.$toastr("info", "Reminder Deleted!", "Info");
              });
              this.$modal.hide("dialog");
            }
          },
          {
            title: "Cancel"
          }
        ]
      });
    }
  },
  mounted() {
    this.getCompanyById(this.currentUser.active_role.company).then(() => {
      this.newSchedule = this.company;
      this.getAllDefaultReminders().then(() => {
        this.getAllDefaultReminderDays().then(() => {
          const existingReminderDays = this.reminders.map(
            reminder => reminder.reminder_days
          );
          this.filteredReminderDays = this.defaultReminderDays.filter(
            day => !existingReminderDays.includes(day.value)
          );
        });
      });
    });
  }
};
</script>


<style lang="scss">
$input-height: 50px;
$padding-x: 12px;
.schedule-editor-form {
  label {
    line-height: 1;
    margin-bottom: 10px;
    font-weight: normal;
  }
  .task-details-p {
    line-height: 50px;
    margin: 0;
  }
  .space-row {
    margin-top: 20px;
  }

  .days-wrap {
    input[type="checkbox"] {
      position: relative;
      top: 3px;
      width: 15px;
      height: 15px;
    }
  }
  .dropdown,
  .vdp-datepicker,
  .time-picker input.display-time,
  input[type="text"] {
    height: $input-height;
    border: thin #c5d0e3 solid;
    border-radius: 0;
    background: #fff;
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
      color: black;
    }
    .dropdown {
      width: 100%;
      top: 80%;
      .select-list {
        width: 100%;
        height: 100%;
      }
    }
  }
  .v-select {
    width: 200px;

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
    .vs__selected-options .selected-tag,
    input[type="search"] {
      height: auto;
      width: 100%;
      position: absolute;
      top: 0;
      left: 0;
    }
    input[type="search"]:focus {
      padding: 0;
      width: 100%;
    }
  }

  .cf-btn {
      height: 50px;
      margin: 0;
    }

  @media (max-width: 767px) {
    .space-row {
      margin-top: 0;
    }
  }
}
</style>
