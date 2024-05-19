<template>
  <div>
    <Header />
    <PageHeading text="Task List">
      <section class="notification-search-inputs mr-3">
        <div class="cf-full-search-div">
          <input
            type="text"
            class="form-control cf-list-search"
            v-model="keywords"
            v-on:input="search()"
            placeholder="Search by Name, Address, Subdivision or any key participant's name" />
            <button class="btn cf-full-search-button" @click="hasKeywords ? clearSearch() : search()">
              <i :class="[hasKeywords ? 'fa fa-remove cf-fa-search' : 'fa fa-search cf-fa-search']"></i>
            </button>
        </div>
        <select
          v-model="filters.status"
          class="form-control cf-search cf-full-search pull-right"
          @change="search()"
        >
          <option :value="null">Any Status</option>
          <option value="1">Open</option>
          <option value="2">Pending</option>
          <option value="3">Scheduled</option>
          <option value="is_completed">Completed</option>
        </select>
      </section>
      <div class="">
      <button class="btn upload-btn mr-2" v-on:click="detailedTasks()">
        Go To Detailed Task List
      </button>
      <button v-if="permission.isAdmin(currentUser) || permission.isBuilder(currentUser) || permission.isCrewLeader(currentUser)" class="btn upload-btn" v-on:click="addTask()">
        <i class="fa fa-plus-circle" aria-hidden="true"></i>Add New Task
      </button>
     </div>
    </PageHeading>
    <section class="container">
      <label class="include-completed-label">
        <input
          type="checkbox"
          name="includeCompleted"
          v-model="filters.includeCompleted"
          class="include-completed-checkbox cb-checkbox mr-4"
          @change="$refs.Table.doFetch()" /> <i title="Include Completed Tasks?" class="fa fa-check-circle cb-check-circle"></i> Include Completed Tasks
      </label>
    </section>
    <main class="main-fluid">
      <Table
          ref="Table"
          class="container"
          :modelName='modelName'
          :createRouteName='createRouteName'
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
        <tr v-for="task in tasks" v-bind:key="task.id" :class="task.is_completed && 'completed'">
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
                icon="complete"
                @click.native.prevent="confirmCompleteTask(task)"
              />
              <ButtonTableAction
                v-if="permission.isAdminOrCreator(currentUser, task)"
                icon="delete"
                @click.native.prevent="confirmDeleteTask(task)"
              />
            </span>
          </td>
        </tr>
      </Table>
    </main>

    <Footer />
    <v-dialog />
  </div>
</template>

<script>
// @ is an alias to /src
import Header from "@/components/Header.vue";
import PageHeading from "@/components/PageHeading.vue";
import Footer from "@/components/Footer.vue";
import Table from "@/components/Table.vue";
import ButtonTableAction from '@/components/Button/TableAction.vue';
import { permission } from "../router-helper"

import { mapState, mapActions } from "vuex";
import _ from "lodash";

export default {
    name: "TasksPage",
    components: {
        Header,
        PageHeading,
        Footer,
        Table,
        ButtonTableAction
    },
    data: function() {
        return {
            permission,
            hasKeywords: false,
            modelName: 'Task',
            createRouteName: 'add-task',
            keywords: "",
            ordering: "-start_date",
            headers: [
                {key: 'name', label: 'Task Name', sort: true},
                {key: 'start_date', label: 'Start Date', sort: true},
                {key: 'end_date', label: 'End Date', sort: true},
                {key: 'participants', label: 'Participants', sort: false},
                {key: 'action', label: 'Action', sort: false},
            ],
            filters: { status: null },
        };
    },
    computed: {
        ...mapState([
            "loading",
            "tasks",
            "tasksCount",
            "tasksPageSize",
            "tasksPageIndex",
            "tasksOrdering",
            "tasksNumPages",
            "tasksKeywords",
            "currentUser"
        ])
    },
    methods: {
      ...mapActions([
        "getTasks",
        "getTaskByJob",
        "completeTask",
        "deleteTask"
      ]),
      search: _.debounce(function() {
        this.keywords ? this.hasKeywords = true : ''
        this.$refs.Table.doFetch(1, this.filters);
      }, 1000),
      clearSearch() {
        this.keywords = "";
        this.hasKeywords = false;
        this.search();
      },
      detailedTasks: function() {
        this.$router.push({ name: "detailed-tasks" })
      },
      addTask: function() {
          this.$router.push({ name: "add-task" });
      },
      getParticipantName: function(task, label){
        switch (label) {
          case 'B':
            return task.builder_name ? task.builder_name : '(Not Assigned)';
          case 'SC':
            return task.subcontractor_name ? task.subcontractor_name : '(Not Assigned)';
          case 'CR':
            return task.superintendent_name ? task.superintendent_name : '(Not Assigned)';
          default:
            return '';
        }
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
      confirmCompleteTask: function(task) {
          let self = this;
          this.$modal.show('dialog', {
              title: 'Confirm',
              text: 'Are you sure you want to mark this task as Completed?',
              buttons: [
                  {
                      title: '<div class="btn cb-delete">Complete</div>',
                      handler: () => {
                          this.completeTask({ id: task.id })
                          .then(() => {
                              this.$refs.Table.doFetch();
                              this.$toastr("info", "Task marked as Completed!", "Info");
                          })
                          .catch(function(error) {
                              if (! Array.isArray(error)) {
                                self.$toastr('error', error.detail, 'error')
                              } else {
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
        this.$modal.show('dialog', {
          title: 'Delete Task',
          text: `Are you sure you want to delete the <b>${task.name}</b> task?`,
          buttons: [
            {
              title: '<div class="btn cb-delete">Delete</div>',
              handler: () => {
                this.deleteTask({ id: task.id })
                  .then(() => {
                    this.$refs.Table.doFetch();
                    this.$toastr("info", "Task Deleted!", "Info");
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
    },
    mounted() {
      this.keywords = this.tasksKeywords;
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
  height: 5%;
  flex: 1;
  input,
  select {
    position: static;
    margin: 0;
  }
  input {
    width: 95%;
  }
  select {
    width: 24%;
    background-image: none;
  }
}

@media (max-width: 1080px) {
  .notification-search-inputs {
    margin: 10px 0 0;
     input {
      width: 50%;
      margin-bottom: 10px;
    }
    select {
      width: 40%;
      margin-bottom: 10px;
    }
  }

  .upload-btn {
    margin-bottom: 10px;
  }
}

@media (max-width: 768px) {
  .notification-search-inputs {
    margin: 10px 0 0;
  }

  .upload-btn {
    margin-bottom: 10px;
  }
}

@media (max-width: 425px) {
  .notification-search-inputs {
    input {
      width: 100%;
      margin-bottom: 10px;
    }
    select {
      width: 100%;
      margin-bottom: 10px;
    }
  }
  button {
    width: 100% !important;
  }
}

</style>
