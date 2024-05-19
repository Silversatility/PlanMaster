<template>

  <div class="calendar-new-view">
    <div v-show="cbLoading" class="cb-loader"><img class="loader-gif" src="/dist/assets/images/gear.gif" alt="Loader"></div>
    <Header/>
    <section class="container-fluid main-fluid cf-fluid calendar">
      <div class="container">
        <section class="row search-section">
          <div class="col-lg-5 col-md-5">
            <span class="text-uppercase bold filter-by">filter by:</span>
            <button @click="filterTasks('builder')" :class="{cfBtnActive: userFilter === 'builder'}" class="btn cf-btn">
              Builder
            </button>
            <button @click="filterTasks('subcontractor')" :class="{cfBtnActive: userFilter === 'subcontractor'}" class="btn cf-btn">
              Subcontractor
            </button>
            <button @click="filterTasks('superintendent')" :class="{cfBtnActive: userFilter === 'superintendent'}" class="btn cf-btn">
              Crew / Flex
            </button>
            <button @click="filterTasks('job')" :class="{cfBtnActive: userFilter === 'job'}" class="btn cf-btn">
              Task
            </button>
          </div>
          <div class="col-lg-3 col-md-3">
            <button
              class="btn cf-btn pull-right"
              @click="filterTask('all')"
              :class="{cfBtnActive: !filterByOwnTask}"
            >All Tasks</button>
            <button
              class="btn cf-btn pull-right"
              @click="filterTask('own')"
              :class="{cfBtnActive: filterByOwnTask}"
            >Own Tasks</button>
          </div>
          <div class="col-lg-4 col-md-4" style="padding: 5px 0;">
            <v-select
              v-model="job"
              v-bind:options="jobs"
              label="location"
              class="form-control"
              :on-change="filterByJob"
              placeholder="All Jobs">
            </v-select>
          </div>
          <div class="col-lg-12 col-md-12" style="padding-left:0;">
            <div class="cf-search-div">
              <input type="text"
                v-model="keywords"
                v-on:input="searchTasks"
                class="form-control cf-search"
                placeholder="Search by Address, Subdivision, Job Name" />
              <button class="btn cf-search-btn" @click="hasKeywords ? clearSearch() : searchTasks()">
                <i :class="[hasKeywords ? 'fa fa-remove cf-fa-search' : 'fa fa-search cf-fa-search']"></i>
              </button>
            </div>
          </div>
          <MobileSubHeader
            :showBy="showBy"
            :filterBy="filterBy"
            :keywords="keywords"
            :hasKeywords="hasKeywords"
          />
        </section>
      </div>
    </section>
    <div class="container-fluid tasks grid-wrapper">
      <div class="container">
        <div class="row">
          <div class="col-md-12" id="calendarView">
            <full-calendar
              ref="calendar"
              :config="config"
              @event-render="eventRender"
              @event-resize="eventResize"
              @event-drop="eventDrop"
              @view-render="doSaveCalendarState"
            />
          </div>
        </div>
      </div>
    </div>
    <Footer/>
    <v-dialog />
  </div>
</template>

<script>
  import Vue from "vue";
  import vSelect from "vue-select";

  import VueGridLayout from "vue-grid-layout";
  import VueRangedatePicker from "vue-rangedate-picker";

  import FullCalendar from "vue-full-calendar";
  import "fullcalendar-scheduler";
  import "fullcalendar/dist/fullcalendar.min.css";
  import "fullcalendar-scheduler/dist/scheduler.min.css";


  Vue.use(FullCalendar);

  import Toastr from "vue-toastr";
  import moment from "moment";

  import $ from "jquery";
  import _ from "lodash";

  import Header from "@/components/Header.vue";
  import Footer from "@/components/Footer.vue";
  import MobileSubHeader from "@/components/Calendar/MobileSubHeader.vue";
  import axios from "axios";
  import VueAxios from "vue-axios";
  import {mapState, mapActions} from "vuex";
  import { permission } from "../router-helper"

  Vue.use(VueAxios, axios);

  var GridLayout = VueGridLayout.GridLayout;
  var GridItem = VueGridLayout.GridItem;

  export default {
    name: "Calendar",
    components: {
      Header,
      Footer,
      MobileSubHeader,
      GridItem,
      GridLayout,
      vSelect,
      VueRangedatePicker
    },
    computed: {
      ...mapState(["crewLeaderSettings", "calendarState", "currentUser", "jobs"])
    },
    methods: {
      ...mapActions([
        "getTasks",
        "getAllJobs",
        "getCalendarState",
        "saveCalendarState",
        "getHeaderNotificationsCount",
        "completeTask"
      ]),
      doSaveCalendarState: function() {
        let currentDate = $(this.$refs.calendar.$el).fullCalendar('getDate');

        this.saveCalendarState({
          keywords: this.keywords,
          role: this.userFilter,
          status: this.status,
          view: $(this.$refs.calendar.$el).fullCalendar('getView').type,
          date: currentDate,
          filter: this.filterByOwnTask,
        });
      },
      filterStatus: _.debounce(function() {
          this.$refs.calendar.$emit('refetch-events');
          $(this.$refs.calendar.$el).fullCalendar('refetchResources');
      }, 1000),
      eventRender(event, element, view) {
        let taskContent = '';
        let taskClass = '';
        this.cbLoading = true;

        const separator = '<i class="fa fa-circle"></i>';

        if (event.is_completed) {
          taskClass = 'color-gray completed';
        } else {
          if (event.status === 1) {
            taskClass = 'tentative';
          } else if (event.status === 3) {
            taskClass = 'scheduled';
          } else {
            taskClass = 'color-gray pending';
          }
        }

        if (event.hasPrevious) {
          taskClass  += ' has-previous'
          taskContent += '<div class="has-previous-container"><i class="fa fa-arrow-left"></i></div>'
        }
        if (event.hasFuture) {
          taskClass += ' has-future'
          taskContent += '<div class="has-future-container"><i class="fa fa-arrow-right"></i></div>'
        }

        let participants = '';
        $.each(event.participant_statuses, function (index, value) {
          participants += '<span class="crew-labels ' + value.status + '"></span>'
        });

        let titleClass = '';
        view.name === 'customWeek' ? titleClass = 'title' : titleClass = 'title-resource';

        taskContent += '<p class="cb-people">' + participants + '</p>';
        if (view.name === 'customWeek') {
          taskContent += '<i class="has-start-icon"></i>';
          taskContent += '<i class="has-end-icon"></i>';
        }
        // Line 1
        let line1 = '<span class="not-full-title"><p class="text-large title display-inline">';
        if (event.resourceName && (view.name === 'month' || this.userFilter === 'job')) {
          line1 += `${event.resourceName} ${separator} `;
        }

        if (event.start && event.end) {
          const wholeHours = event.start.format('mm')==='00' && event.end.format('mm')==='00';
          const startTime = wholeHours ? event.start.format('h a') : event.start.format('h:mm a');
          const endTime = wholeHours ? event.end.format('h a') : event.end.format('h:mm a');

          const sameMonth = moment.utc(event.start).format("MMM") === moment.utc(event.end).format("MMM")
          const startDate = moment.utc(event.start).format("MMM D");
          const endDate = sameMonth ? moment.utc(event.end).format("D") : moment.utc(event.end).format("MMM D");

          line1 += `${event.title} ${separator} ${startDate} – ${endDate} ${separator} ${startTime} – ${endTime}`;
        } else {
          line1 += `${event.title}`;
        }
        line1 += '</p></span>';

        taskContent += line1;

        let line2 = '<p class="text-small" style="margin-top:-5px">#' + event.lot_number;
        if (view.name === 'month' || this.userFilter !== 'job') {
          line2 += ` ${separator} ${event.job_address}`;
        }
        line2 += '</p>';

        taskContent += line2;


        taskContent += `<i class="fa fa-check-circle task-completed complete_${event.id} ${(event.has_queued_notification && permission.hasTaskPermission(this.currentUser, event)) ? '' : 'no-task-notification'}" aria-hidden="true"></i>`;

        if (event.has_queued_notification && permission.hasTaskPermission(this.currentUser, event)) {
          taskContent += '<i class="fa fa-bell task-notification send_' + event.id + '" aria-hidden="true"></i>';
        }

        taskContent += '<i class="fa fa-info-circle view-task-details info_' + event.id + '" aria-hidden="true"></i>';

        element.find('.fc-content').append(taskContent);
        element.find('.fc-content').addClass(taskClass);
        element.find('.fc-title').hide();
        element.find('.fc-time').hide();
        this.cbLoading = false;
      },
      eventResize: function (event, delta, revertFunc) {
        this.cbLoading = true;
        let url = "/api/v1/task/" + event.id + "/";
        let data = {
          start_date: event.start.format("YYYY-MM-DD"),
          end_date: event.end.format("YYYY-MM-DD"),
        };

        this.$http
          .patch(url, data)
          .then(response => {
            this.$toastr("success", "Task Updated", "Success!");
            this.$refs.calendar.$emit('refetch-events');
            this.getHeaderNotificationsCount();
            this.cbLoading = false;
          })
          .catch(error => {
            this.$toastr("error", "Task Update Failed", "Error");
            this.cbLoading = false;
          });
      },
      eventDrop: function (event, delta, revertFunc, jsEvent, ui, view) {
        this.cbLoading = true;
        let url = "/api/v1/task/" + event.id + "/";
        let data = {
          start_date: event.start ? event.start.format("YYYY-MM-DD") : null,
        };

        if (this.userFilter === 'subcontractor') {
          data.subcontractor = event.resourceId === 'unassigned' ? null : event.resourceId;
        } else if (this.userFilter === 'superintendent') {
          data.superintendent = event.resourceId === 'unassigned' ? null : event.resourceId;
        } else if (this.userFilter === 'builder') {
          data.builder = event.resourceId === 'unassigned' ? null : event.resourceId;
        } else if (this.userFilter === 'job') {
          data.job = event.resourceId;
        }
        if (permission.hasTaskPermission(this.currentUser, event)) {
          this.$http
            .patch(url, data)
            .then(response => {
              this.$toastr("success", "Task Updated", "Success!");
              this.$refs.calendar.$emit('refetch-events');
              this.cbLoading = false;
            })
            .catch(error => {
              revertFunc()
              if (error.response && error.response.data.non_field_errors) {
                this.$toastr("error", error.response.data.non_field_errors[0], "Error");
              } else {
                this.$toastr("error", "Task Update Failed", "Error");
              }
              this.$refs.calendar.$emit('refetch-events');
              this.cbLoading = false;
            });
        } else {
          revertFunc();
          this.$toastr("error", "Task Update Failed", "Error");
        }
      },

      searchTasks: _.debounce(function() {
        if (this.keywords) {
          this.hasKeywords = true;
        }
        this.$refs.calendar.$emit('refetch-events');
        // since vue-full-calendar doesn't catch "refetch-resources"
        $(this.$refs.calendar.$el).fullCalendar('refetchResources');
        this.doSaveCalendarState();
      }, 1000),
      clearSearch() {
        this.keywords = "";
        this.hasKeywords = false;
        this.searchTasks();
      },
      rangeSelect: function (start, end, jsEvent, view, resource) {
        let endDate = moment.utc(end).subtract(1, "days").format("dddd, MMMM Do, YYYY");
        let startDate = start.format("dddd, MMMM Do, YYYY");

        let taskEndDate = moment.utc(end).subtract(1, "days").format("YYYY-MM-DD");
        let taskStartDate = start.format("YYYY-MM-DD");

        let message = '';
        let query = {};

        if (startDate === endDate) {
          message = '<p class="text-center">Add a task on the following date?</p><p class="text-center"><b>' + startDate + '</b></p>';
        } else {
          message = '<p class="text-center">Add a task between the following dates?</p><p class="text-center"><b>' + startDate + '</b><br> to <br><b>' + endDate + '</b></p>';
        }
        resource ? query = {user: resource.realID, type: this.userFilter, start_date: taskStartDate, end_date: taskEndDate} :
          query = {start_date: taskStartDate, end_date: taskEndDate};
        this.$modal.show('dialog', {
          title: 'Confirm',
          text: message,
          buttons: [
              {
                  title: '<div class="btn cb-save-add">Add</div>',
                  handler: () => {
                    this.$router.push({
                      name: "add-task",
                      query: query
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
      filterTask(filter) {
        if (filter === 'own') {
          this.filterByOwnTask = true;
          this.saveCalendarState({ filter: this.filterByOwnTask });
          this.$refs.calendar.$emit('refetch-events');
          $(this.$refs.calendar.$el).fullCalendar('refetchResources');
        } else {
          this.filterByOwnTask = false;
          this.saveCalendarState({ filter: this.filterByOwnTask });
          this.$refs.calendar.$emit('refetch-events');
          $(this.$refs.calendar.$el).fullCalendar('refetchResources');
        }
      },
      filterTasks(role) {
        this.userFilter = role;
        this.saveCalendarState({ role: this.userFilter });
        this.$refs.calendar.$emit('refetch-events');
        $(this.$refs.calendar.$el).fullCalendar('refetchResources');
      },
      filterByJob(job) {
        this.job = job;
        this.saveCalendarState({ job: this.job });
        this.$refs.calendar.$emit('refetch-events');
        $(this.$refs.calendar.$el).fullCalendar('refetchResources');
        return this.job;
      },
      viewTask(id) {
        this.$router.push({
          name: "task-detail",
          params: {id: id}
        });
      },
      sendNotification(id) {
        this.cbLoading = true;
        this.$http
          .put(`/api/v1/task/${id}/send-notification/`)
          .then((response) => {
            if (
              response.data.notification_messages &&
              response.data.notification_messages.successful.roles.emails.length &&
              response.data.notification_messages.successful.roles.mobile_numbers.length
            ) {
              let successMessage = `
              <h5>Emails</h5>
              ${response.data.notification_messages.successful.roles.emails.join('<br>')}
              <h5>SMS</h5>
              ${response.data.notification_messages.successful.roles.mobile_numbers.join('<br>')}
              `
              this.$toastr("success", successMessage , "Notifications sent!");
            }
            if (
              response.data.notification_messages &&
              response.data.notification_messages.has_error
            ) {
              let errorMessage = `
              <h5>Emails</h5>
              ${response.data.notification_messages.unsuccessful.roles.emails.join('<br>')}
              <h5>SMS</h5>
              ${response.data.notification_messages.unsuccessful.roles.mobile_numbers.join('<br>')}
              `
              this.$toastr("error", errorMessage , "Notifications not sent!");
            }
            this.$refs.calendar.$emit('refetch-events');
            this.getHeaderNotificationsCount();
          })
          .catch((error) => {
            if (!error.response) {
              this.$toastr("error", "Notification not sent", "Error");
              this.cbLoading = false;
              return;
            }
            let failedMessages = error.response.data.failed_messages;
            let errorMessage = ``
            if (failedMessages.emails.length) {
              errorMessage += `<h5>Emails</h5>${failedMessages.emails.join('<br>')}`
            }
            if (failedMessages.mobile_numbers.length) {
              errorMessage += `<h5>SMS</h5>${failedMessages.mobile_numbers.join('<br>')}`
            }
            if (failedMessages.emails.length || failedMessages.mobile_numbers.length) {
              // this.$toastr("error", errorMessage , "Couldn't send the following");
              this.$refs.calendar.$emit('refetch-events');
              this.getHeaderNotificationsCount();
            } else {
              this.$toastr("error", "Notification not sent", "Error");
              this.cbLoading = false;
            }
          });
      },
      confirmCompleteTask: function(id) {
          let self = this;
          this.$modal.show('dialog', {
              title: 'Confirm',
              text: 'Are you sure you want to mark this task as Completed?',
              buttons: [
                  {
                      title: '<div class="btn cb-delete">Complete</div>',
                      handler: () => {
                          this.completeTask({ id: id })
                          .then(() => {
                              this.$refs.calendar.$emit('refetch-events');
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
    },
    data() {
      let self = this;
      return {
        showBy: "own",
        filterBy: "job",
        hasKeywords: false,
        keywords: "",
        job: null,
        status: null,
        role: "",
        ordering: "-start_date",
        cbLoading: false,
        userFilter: 'subcontractor',
        selectable: true,
        filterByOwnTask: false,
        config: {
          customButtons: {
            myCustomButton: {
              text: 'Print Calendar',
              click: () => {
                window.print();
              }
            }
          },
          eventDurationEditable: false,
          schedulerLicenseKey: "GPL-My-Project-Is-Open-Source",
          defaultView: "month",
          defaultDate: moment(),
          height: 600,
          firstDay: 0,
          handleWindowResize: false,
          resourceAreaWidth: "20%",
          editable: true,
          filterResourcesWithEvents: false,
          resourceRender: function (resourceObj, labelTds, bodyTds) {
            labelTds.find('.fc-expander-space').hide();
            if (self.userFilter !== 'job') {
              labelTds.find('.fc-cell-text').addClass('text-large').addClass('color-gray');
              labelTds.find('.fc-cell-content').append(
                '</br><span class="text-small color-gray">' + resourceObj.user_type_display + '</span>');
            } else {
              labelTds.find('.fc-cell-content').append(
                '<span class="text-medium color-gray" style="white-space: initial; display: block;">' + resourceObj.location + '</span>');
            }
          },
          views: {
            customWeek: {
              type: 'timelineWeek',
              duration: {weeks: 1},
              slotDuration: {days: 1}
            },
            day: {
              type: 'timelineDay',
              duration: {days: 1},
              slotDuration: {hours: 24}
            }
          },
          header: {
            left: "prev,next today, myCustomButton",
            center: "title",
            right: "day, customWeek, month",
          },
          buttonText: {
            today: 'Today',
            month: 'Month',
            week: 'Week',
            day: 'Day',
            list: 'List',
          },
          events: function (start, end, timezone, callback) {
            self.cbLoading = true;
            let url = "/api/v1/task/?limit=0&job_is_archived=false";
            if (self.keywords) {
              url += `&search=${self.keywords}`;
            }
            if (self.job) {
              url += `&job=${self.job.id}`;
            }
            if (self.status) {
              url += `&status=${self.status}`;
            }
            if (self.filterByOwnTask) {
              url += `&role=${self.currentUser.active_role.id}`;
            }
            if (start) {
              url += `&start=${start.format('YYYY-MM-DD')}`;
            }
            if (end) {
              url += `&end=${end.format('YYYY-MM-DD')}`;
            }
            self.$http
              .get(url)
              .then((response) => {
                const data = response.data;
                const newData = [];
                if(data.length === 0) {
                  self.$toastr("warning", "No records found!", "warning");
                }

                for (const task of data) {
                  // NOTE: most of moment.js methods mutates the original object
                  const durationInDays = moment(task.end_date).diff(moment(task.start_date), 'days') + 1
                  const nonWorkingDays = task.non_working_days_in_day_of_week || []

                  // startDate: this will serve as the start date of each working days/schedule block
                  // and will mutate when the loop creates a new schedule block
                  let startDate = moment(task.start_date)
                  for (let index of Array(durationInDays).keys()) {
                    // NOTE: "index" starts with 0 just so you know
                    // NOTE: format('d') Output: Day of Week | "0" "1" ... "5" "6" | "0" is Sunday

                    const today = moment(task.start_date).add(index, 'days')
                    if (nonWorkingDays.includes(parseInt(today.format('d')))) {
                      // if today is a non working day
                      // set startDate to tomorrow and continue
                      startDate = moment(task.start_date).add(index + 1, 'days')
                      continue
                    }

                    // lets check tomorrow
                    // we didn't use today.add because moment.add mutates the original object
                    const tomorrow = moment(task.start_date).add(index + 1, 'days')
                    if (nonWorkingDays.includes(parseInt(tomorrow.format('d')))) {
                      // if today is a working day, and tomorrow is a non working day
                      // 1. add a schedule block in newData using the start_date(startDate) to end_date(today)
                      // 2. set the startDate to the "today" inside the loop
                      // 3. continue
                      let newTask = Object.assign({}, task)
                      newTask.start_date = startDate.format('YYYY-MM-DD')
                      newTask.end_date = today.format('YYYY-MM-DD')
                      newTask.hasPrevious = (task.start_date == startDate.format('YYYY-MM-DD')) ? false : true
                      newTask.hasFuture = (task.end_date == today.format('YYYY-MM-DD')) ? false : true
                      newData.push(newTask)
                      startDate = moment(task.start_date).add(index, 'days')
                      continue
                    }

                    if (durationInDays == index + 1) {
                      // if today is a working day and the last day of the task
                      // add a schedule block in newData using the start_date(startDate) to end_date(today)
                      // no need to set the startDate to "today" since it is the last day already
                      // continue
                      let newTask = Object.assign({}, task)
                      newTask.start_date = startDate.format('YYYY-MM-DD')
                      newTask.end_date = today.format('YYYY-MM-DD')
                      newTask.hasPrevious = (task.start_date == startDate.format('YYYY-MM-DD')) ? false : true
                      newData.push(newTask)
                      continue
                    }
                    // if today is a working day, and tomorrow is a working day also
                    // just continue
                  } // END LOOP 1-1
                } // END LOOP 1
                $.each(newData, function (index, value) {
                  newData[index].title = value.name;
                  value.start_time ? newData[index].start = moment(value.start_date + ' ' + value.start_time, 'YYYY-MM-DD HH:mm').toDate() : newData[index].start = moment(value.start_date).toDate();
                  value.end_time ? newData[index].end = moment(value.end_date + ' ' + value.end_time, 'YYYY-MM-DD HH:mm').toDate() : newData[index].end = moment(value.end_date).toDate();
                  if (self.userFilter === 'subcontractor') {
                    newData[index].resourceId = value.subcontractor ? value.subcontractor : 'unassigned';
                    newData[index].resourceName = value.subcontractor_name;
                  } else if (self.userFilter === 'superintendent') {
                    newData[index].resourceId = value.superintendent ? value.superintendent : 'unassigned';
                    newData[index].resourceName = value.superintendent_name;
                  } else if (self.userFilter === 'builder') {
                    newData[index].resourceId = value.builder ? value.builder : 'unassigned';
                    newData[index].resourceName = value.builder_name;
                  } else if (self.userFilter === 'job') {
                    newData[index].resourceId = value.job;
                  }
                  newData[index].allDay = false;
                  newData[index].editable = permission.hasTaskPermission(self.currentUser, newData[index]);
                });
                callback(newData);
                self.cbLoading = false;
              })
              .catch(error => {
                self.$toastr("error", "Tasks Retrieval Failed", "Error");
                self.cbLoading = false;
              });
          },
          resourceLabelText: self.userFilter === 'job' ? "Job Name" : "Name",
          resourceOrder: 'first_name',
          resourceText: function (resource) {
            return resource.full_name
          },
          resources: function (callback) {
            self.cbLoading = true;
            let url = '';
            if (self.userFilter !== 'job') {
              url = "/api/v1/company-role/?limit=0";
              if (self.userFilter) {
                url += `&role=${self.userFilter}`;
              }
            } else {
              url = "/api/v1/job/?limit=0";
            }
            let user_type_display = '';
            if (self.userFilter === 'builder') {
              user_type_display = 'Builder'
            } else if (self.userFilter === 'subcontractor') {
              user_type_display = 'Subcontractor'
            } else if (self.userFilter === 'superintendent') {
              user_type_display = 'Crew / Flex'
            }
            self.$http.get(url).then(response => {
              let data = [];
              if (self.userFilter !== 'job') {
                data = response.data.map(role => {
                    role.full_name = role.user.first_name + ' ' + role.user.last_name;
                    role.first_name = role.user.first_name;
                    role.user_type_display = role.user_types_display;
                    role.realID = role.id;
                    return role;
                });
                data.unshift({
                  id: 'unassigned',
                  full_name: 'Unassigned Tasks',
                  first_name: '',
                  user_type_display: user_type_display
                });
              } else {
                data = response.data.map(user => {
                  user.realID = user.id;
                  return user;
                });
              }

              callback(data);
            })
            .catch(error => {
              this.$toastr("error", "Roles Retrieval Failed", "Error");
              this.cbLoading = false;
            });
          },

          eventAfterRender: function (event, element, view) {
            $(`.info_${event.id}`).on('click', () => { self.viewTask(event.id) });
            $(`.send_${event.id}`).on('click', () => { self.sendNotification(event.id) });
            $(`.complete_${event.id}`).on('click', () => { self.confirmCompleteTask(event.id) });
          },

          select: function (start, end, jsEvent, view, resource) {
            if (permission.isAdmin(self.currentUser) || permission.isBuilder(self.currentUser) || permission.isCrewLeader(self.currentUser)) {
              self.rangeSelect(start, end, jsEvent, view, resource);
            }
          }
        }
      };
  },
  created() {
      this.getAllJobs();

      this.$route.params.isNewTask ? this.config.defaultView == 'month' : this.config.defaultView = this.calendarState.view || 'month';
      this.job = this.calendarState.job;
      this.keywords = this.calendarState.keywords;
      if (this.keywords) {
        this.hasKeywords = true;
      }
      this.status = this.calendarState.status || null;
      this.config.defaultDate = moment(this.calendarState.date);
      this.userFilter = this.calendarState.role || 'subcontractor';
      this.filterByOwnTask = this.calendarState.filter;

      let contractorID = this.currentUser.active_role.company;
      let webSocketScheme = window.location.protocol == "https:" ? "wss://" : "ws://";
      let webSocket = new WebSocket(
          webSocketScheme +
          window.location.host +
          '/ws/calendar/' +
          contractorID +
          '/'
      );

      webSocket.onmessage = (response) => {
          let data = JSON.parse(response.data);
          let message = data['message'];
          let senderUserId = data['senderUserId'];
          if (message == "reload_calendar" && senderUserId != this.currentUser.user.id) {
            this.$refs.calendar.$emit('refetch-events');
            $(this.$refs.calendar.$el).fullCalendar('refetchResources');
          }
        };

      webSocket.onclose = (response) => {
          console.error('Web socket closed unexpectedly.');
      };
  }
};
</script>
<style scoped lang="scss">
@import "@/assets/styles/Calendar/calendar.scss";
</style>

<style lang="scss">
  $input-height: 50px;

  .search-section .dropdown {
    height: $input-height;
    border: thin #c5d0e3 solid;
    border-radius: 0;
    background: #FFF;
    margin-bottom: 10px;
    font-family: "montserratlight", sans-serif;
  }

  .divider-strip {
    background: #5499C7;
    width: 2px;
    height: 48px;
    margin-top: 5px;
    border-radius: 2px;
  }
  #calendarView {
    margin-bottom: 150px;
  }
  .has-previous {
    padding-left: 25px;
  }

  .has-previous-container {
    position: absolute;
    width: 25px;
    top: 40%;
    left: 5px;
  }

  .has-future {
    padding-right: 25px;
  }

  .has-future-container {
    position: absolute;
    width: 25px;
    top: 40%;
    right: 5px;
  }

  .fc-event {
    font-size: inherit;
    line-height: inherit;
    background-color: transparent;
    border: none;
  }

  .fc-content {
    border-radius: 5px;
  }

  .calendar-new-view .grid-wrapper {
    margin-top: 0;
    float: inherit;
  }

  .text-large {
    font-size: 16px;
    font-weight: 600;
  }

  .text-medium {
    font-size: 14px;
  }

  .text-small {
    font-size: 12px;
    padding-left: 5px;
  }

  .color-gray {
    color: #555
  }

  .calendar-new-view .view-task-details,
  .calendar-new-view .task-notification,
  .calendar-new-view .task-completed {
    margin: 5px 5px 0 5px;
  }

  .task-completed.no-task-notification {
    right: 23px;
  }

  .task-completed {
      font-size: 18px;
      color: #1abc9c;
      position: absolute;
      right: 48px;
      top: 2px;
  }

  .calendar-new-view .title {
    margin: -10px 5px -5px 5px;
  }

  .calendar-new-view .title-resource {
    margin: -10px 5px -5px 0;
  }

  .calendar-new-view .cb-people {
    margin: -2px 0 -5px 5px;
  }

  .calendar-new-view .crew-labels {
    width: 25px;
    height: 10px;
  }

  .fa-circle {
    font-size: 0.3em;
  }

  .display-inline {
    display: inline-block;
  }

  .fc-not-start .has-start-icon {
    content: "";
    position: absolute;
    border: 6px solid #000;
    border-top-color: transparent;
    border-bottom-color: transparent;
    opacity: .5;
    border-left: 0;
    left: 0
  }

  .fc-not-end .has-end-icon {
    content: "";
    position: absolute;
    border: 6px solid #000;
    border-top-color: transparent;
    border-bottom-color: transparent;
    opacity: .5;
    border-right: 0;
    left: 0;
  }

  .not-full-title {
    overflow: hidden;
    margin-right: 50px;
    display: block;
    text-overflow: ellipsis;
  }

  .main-fluid {
    padding-bottom: 13px;
  }

  .fc-ltr .fc-resource-area tr>* {
    overflow: hidden;
}

  @media (max-width: 768px) {
    .fc-left, .fc-right {
      margin-bottom: 10px;
    }

    .fc-center h2 {
      font-size: 24px;
    }

    .cf-btn {
      margin: 10px 3px;
      padding: 4px 4px;
      font-size: 12px;
    }

    .text-large {
      font-size: 14px;
      font-weight: 600;
    }
    .divider-strip {
      display: none;
    }
  }

  @media (max-width: 1024px) {
    .calendar-new-view .content-footer-fluid {
      position: inherit;
    }

    .cf-search {
      margin-left: -10px;
      width: 95%;
    }

    .cf-btn {
      padding: 2px 5px;
      font-size: 12px;
    }

    #calendar {
      margin-bottom: 30px;
    }
    .divider-strip {
      display: none;
    }
  }

  @media print {
    @page { size: landscape; }
    body * { visibility: hidden;}
    #calendarView * { visibility: visible; }
    .fc-scroller {
      overflow: visible !important;
      height: auto !important;
    }
    .fc td {
      border: 0;
    }
    .fc th {
      border-top: 1px solid black;
    }
    #calendarView {
      position: absolute;
      margin-top: -300px;
      top: 0;
      left: 0;
    }
  }
</style>
