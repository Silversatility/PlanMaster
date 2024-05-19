<template>
  <div>
    <Header />

    <PageHeading text="Notifications List">
      <section class="notification-search-inputs">
        <div class="cf-full-search-div-job">
          <input
            type="text"
            class="form-control cf-list-search"
            v-model="keywords"
            v-on:input="search()"
            placeholder="Search by Task"
          />
          <button class="btn cf-full-search-button" @click="hasKeywords ? clearSearch() : search()">
                <i :class="[hasKeywords ? 'fa fa-remove cf-fa-search' : 'fa fa-search cf-fa-search']"></i>
              </button>
          <select
            v-model="filters.type"
            class="form-control cf-search cf-full-search"
            @change="search"
          >
            <option :value="false">All</option>
            <option value="1">General</option>
            <option value="2">Schedule</option>
            <option value="3">Invites</option>
          </select>
          <select
            v-model="filters.is_queued"
            class="form-control cf-search cf-full-search"
            @change="search"
          >
            <option value="all">All</option>
            <option :value="true">Pending</option>
            <option :value="false">Sent</option>
          </select>
        </div>
      </section>
    </PageHeading>

    <main class="main-fluid">
      <Table
          ref="Table"
          class="container"
          :fetch="getNotifications"
          :items="notifications"
          :count="notificationsCount"
          :pageSize="notificationsPageSize"
          :pageIndex="notificationsPageIndex"
          :numPages="notificationsNumPages"
          :keywords="keywords"
          :ordering="notificationsOrdering"
          :initialOrdering="ordering"
          :headers="headers"
      >
        <tr v-for="notification in notifications" v-bind:key="notification.id">
          <td><router-link v-bind:to="{name: 'task-detail', params: {id: notification.task}}">{{notification.task_name}}</router-link></td>
          <td v-if="notification.type_name == 'Invites Only'">
            <table class="table table-bordered add-job-table" style="margin: 0;">
              <thead>
                <tr>
                  <th>
                    {{ notification.type_name }}
                  </th>
                  <th>
                    Last Sent
                  </th>
                  <th>
                    Response
                  </th>
                </tr>
              </thead>
              <tbody>
                  <tr v-if="notification.key_participants.builder">
                    <td>
                      <span :class="`participant-status B ${notification.key_participants.builder.response_display.toLowerCase()}`">
                        {{ notification.key_participants.builder.participant_display }}
                      </span>
                    </td>
                    <td>
                      {{ notification.key_participants.builder.last_notification_timestamp | date("MM/DD/YYYY h:mm a")  }}
                    </td>
                    <td>
                      <template v-if="notification.key_participants.builder.response_timestamp">
                        {{ notification.key_participants.builder.response_timestamp | date("MM/DD/YYYY h:mm a") }}
                      </template>
                      <template v-else>
                        <i @click="sendAcknowledgement(notification.key_participants.builder.id)" class="fa fa-bell text-success" style="font-size:18px;cursor:pointer;" aria-hidden="true"></i>
                      </template>
                    </td>
                  </tr>
                  <tr v-if="notification.key_participants.subcontractor">
                    <td>
                      <span :class="`participant-status SC ${notification.key_participants.subcontractor.response_display.toLowerCase()}`">
                        {{ notification.key_participants.subcontractor.participant_display }}
                      </span>
                    </td>
                    <td>
                      {{ notification.key_participants.subcontractor.last_notification_timestamp | date("MM/DD/YYYY h:mm a")  }}
                    </td>
                    <td>
                      <template v-if="notification.key_participants.subcontractor.response_timestamp">
                        {{ notification.key_participants.subcontractor.response_timestamp | date("MM/DD/YYYY h:mm a") }}
                      </template>
                      <template v-else>
                        <i @click="sendAcknowledgement(notification.key_participants.subcontractor.id)" class="fa fa-bell text-success" style="font-size:18px;cursor:pointer;" aria-hidden="true"></i>
                      </template>
                    </td>
                  </tr>
                  <tr v-if="notification.key_participants.superintendent">
                    <td>
                      <span :class="`participant-status CR ${notification.key_participants.superintendent.response_display.toLowerCase()}`">
                        {{ notification.key_participants.superintendent.participant_display }}
                      </span>
                    </td>
                    <td>
                      {{ notification.key_participants.superintendent.last_notification_timestamp | date("MM/DD/YYYY h:mm a")  }}
                    </td>
                    <td>
                      <template v-if="notification.key_participants.superintendent.response_timestamp">
                        {{ notification.key_participants.superintendent.response_timestamp | date("MM/DD/YYYY h:mm a") }}
                      </template>
                      <template v-else>
                        <i @click="sendAcknowledgement(notification.key_participants.superintendent.id)" class="fa fa-bell text-success" style="font-size:18px;cursor:pointer;" aria-hidden="true"></i>
                      </template>
                    </td>
                  </tr>
              </tbody>
            </table>
          </td>
          <td v-else>
            {{notification.type_name}}
          </td>
          <td>
            <p v-if="notification.sent_timestamp">
              {{notification.sent_timestamp | date("MM/DD/YYYY h:mm a")}}
            </p>
            <p v-else>
              <i class="fa fa-bell text-success" style="font-size:18px;cursor:pointer;" @click="sendNotification(notification.task)" aria-hidden="true"></i>
            </p>
          </td>
          <td>{{notification.modified_timestamp | date("MM/DD/YYYY h:mm a")}}</td>
        </tr>
      </Table>
    </main>
    <Footer />
  </div>
</template>

<script>
// @ is an alias to /src
import Header from "@/components/Header.vue";
import PageHeading from "@/components/PageHeading.vue";
import Footer from "@/components/Footer.vue";
import Table from "@/components/Table.vue";

import { mapState, mapActions } from "vuex";
import _ from "lodash";

export default {
    name: "NotificationsPage",
    components: {
        Header,
        PageHeading,
        Footer,
        Table
    },
    data: function() {
        return {
            cbLoading: false,
            keywords: "",
            hasKeywords: false,
            ordering: "task_name",
            filters: {
              type: false,
              is_queued: true,
            },
            headers: [
              {key: 'task_name', label: 'Task', sort: true},
              {key: 'type_name', label: 'Type', sort: true},
              {key: 'sent_timestamp', label: 'Sent', sort: true},
              {key: 'modified_timestamp', label: 'Modified', sort: true},
            ]
        };
    },
    computed: {
        ...mapState([
            "loading",
            "notifications",
            "notificationsCount",
            "notificationsPageSize",
            "notificationsPageIndex",
            "notificationsNumPages",
            "notificationsKeywords",
            "notificationsOrdering"
        ])
    },
    methods: {
        ...mapActions([
          "getNotifications",
          "getHeaderNotificationsCount"
        ]),
        sendAcknowledgement(participation_id) {
          this.$http
            .post(`/api/v1/participation/${participation_id}/send-acknowledgement/`)
              .then((response) => {
                this.$toastr("success", "Notification Sent", "Success!");
              })
              .catch((response) => {
                this.$toastr("error", "Notification not sent", "Error");
              })
              .finally(() => {
                this.$refs.Table.doFetch();
              })
        },
        sendNotification(id) {
          let self = this;
          this.cbLoading = true;
          this.$http
            .put(`/api/v1/task/${id}/send-notification/`)
            .then(response => {
              this.getNotifications({
                keywords: this.keywords,
                ordering: this.ordering,
                filters: this.filters,
              })
                .then((data) => {
                  self.cbLoading = false;
                  this.$toastr("success", "Notification Sent", "Success!");
                  this.getHeaderNotificationsCount();
                });
            })
            .catch((error) => {
              this.getNotifications({
                keywords: this.keywords,
                ordering: this.ordering,
                filters: this.filters,
              })
              .then((data) => {
                self.cbLoading = false;
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
                } else {
                  this.$toastr("error", "Notification not sent", "Error");
                }
                this.getHeaderNotificationsCount();
              });
            });
        },
        search: _.debounce(function() {
          this.keywords ? this.hasKeywords = true : this.filters.is_queued = null;
            this.$refs.Table.doFetch(1, this.filters);
        }, 1000),
        clearSearch() {
          this.keywords = "";
          this.hasKeywords = false;
          this.search();
        },
    },
    mounted() {
      this.keywords = this.notificationsKeywords;
      this.keywords ? this.hasKeywords = true : ''
      this.$nextTick(() => {
        this.$refs.Table.doFetch();
      })
    }
};
</script>

<style scoped lang="scss">
  .notification-search-inputs {
    width: 100%;
    flex: 1;
    input,
    select {
      position: static;
      margin: 0;
    }
    input {
      width: 50%;
    }
    select {
      width: 25%;
      background-image: none;
    }
  }

  @media (max-width: 768px) {
    .notification-search-inputs {
      margin: 10px 0 0;
    }
  }

  @media (max-width: 425px) {
    .notification-search-inputs {
      input {
        width: 100%;
        margin-bottom: 10px;
      }
      select {
        width: 50%;
      }
    }
  }
</style>
