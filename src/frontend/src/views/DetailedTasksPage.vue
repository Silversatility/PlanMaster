<template>
  <div class="detailed-tasks">
    <Modal name="print-loading" width="250px" height="125px" :clickToClose="false">
      <div class="panel panel-default" style="height: 100%">
        <div class="panel-heading" style="text-align: center">
          <h3 class="panel-title">Loading</h3>
        </div>
        <div class="panel-body" style="text-align: center">
          <p>Fetching print data</p>
          <div class="progress">
            <div
              class="progress-bar progress-bar-striped active"
              role="progressbar"
              aria-valuenow="100"
              aria-valuemin="0"
              aria-valuemax="100"
              style="width: 100%"
            ></div>
          </div>
        </div>
      </div>
    </Modal>
    <Header />
    <PageHeading text="Detailed Task List">
      <input
        type="text"
        class="form-control cf-list-search-detailed-tasks"
        style="flex: 3;"
        v-model="keywords"
        v-on:input="search()"
        placeholder="Search by Name, Address, Subdivision, Category, Sub Category, Subdivision, Lot Number, Street Address, City, State, ZIP, or any key participant's name"
      />
      <button class="btn cf-full-search-button-detailed-task mr-3" @click="hasKeywords ? clearSearch() : search()">
        <i :class="[hasKeywords ? 'fa fa-remove cf-fa-search' : 'fa fa-search cf-fa-search']"></i>
      </button>
      <datepicker
        v-model="startDate"
        class="form-control cf-search cf-full-search pull-right"
        style="flex: 1;"
        name="start_date"
        format="MM/dd/yyyy"
        input-class="fill-vdp"
        use-utc
        @input="selectStart()"
        placeholder="From"
        :clear-button="true"
      />
      <datepicker
        v-model="endDate"
        class="form-control cf-search cf-full-search pull-right"
        style="flex: 1;"
        name="end_date"
        format="MM/dd/yyyy"
        input-class="fill-vdp"
        use-utc
        @input="selectEnd()"
        placeholder="To"
        :clear-button="true"
      />
      <div class="d-flex justify-content-between align-items-center">
        <button
          class="btn upload-btn mr-3"
          v-on:click="$router.push({ name: 'tasks' })"
        >Back To Task List</button>
        <button class="btn upload-btn" v-on:click="printTasks()">
          <i class="fa fa-plus-circle" aria-hidden="true"></i>Print Data
        </button>
      </div>
    </PageHeading>
    <div class="container">
      <label class="cf-include-completed include-completed-label">
        <input
          type="checkbox"
          name="includeCompleted"
          v-model="filters.includeCompleted"
          class="cb-checkbox include-completed-checkbox"
          @change="$refs.Table.doFetch()"
        />
        <i title="Include Completed Tasks?" class="fa fa-check-circle cb-check-circle"></i>
        Include Completed Tasks
      </label>
    </div>
    <main class="main-fluid">
      <Table
        ref="Table"
        class="container-full"
        :fetch="getDetailedTasks"
        :items="detailedTasks"
        :count="detailedTasksCount"
        :pageSize="detailedTasksPageSize"
        :pageIndex="detailedTasksPageIndex"
        :numPages="detailedTasksNumPages"
        :keywords="keywords"
        :ordering="detailedTasksOrdering"
        :initialOrdering="ordering"
        :headers="headers"
        :filters="filters"
      >
        <tr
          v-for="task in detailedTasks"
          v-bind:key="task.id"
          :class="task.is_completed && 'completed'"
        >
          <td>#{{task.job_data.lot_number}}</td>
          <td>
            <router-link v-bind:to="{name: 'task-detail', params: {id: task.id}}" :class="task | statusDisplay">
              {{task.name}}
            </router-link>
          </td>
          <td>
            <span
              v-for="participant in task.participant_statuses"
              :class="`participant-status ${participant.status} ${participant.label}`"
              >
              {{getParticipantName(task, participant.label)}}
            </span>
          </td>
          <!-- <td>{{task.category_name}}</td>
          <td>{{task.subcategory_name}}</td> -->
          <td>{{task.start_date | date("MM/DD/YYYY", false)}}</td>
          <td>{{task.end_date | date("MM/DD/YYYY", false)}}</td>
          <td>{{task.between}}</td>
          <td>{{task.job_data.subdivision_name}} <br/> {{task.job_data.street_address}}</td>
          <td>{{task.job_data.city}}</td>
          <td>{{task.job_data.state}} {{task.job_data.zip}}</td>
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
import ButtonTableAction from "@/components/Button/TableAction.vue";

import { mapState, mapActions } from "vuex";
import moment from "moment";
import _ from "lodash";
import VueRangedatePicker from "vue-rangedate-picker";
import printJS from "print-js";

export default {
  name: "DetailedTasksPage",
  components: {
    Header,
    PageHeading,
    Footer,
    Table,
    ButtonTableAction,
    VueRangedatePicker
  },
  data: function() {
    return {
      keywords: "",
      hasKeywords: false,
      ordering: "-start_date",
      headers: [
        { key: "job__lot_number", label: "Lot #", sort: true, style: 'min-width: 120px' },
        { key: "name", label: "Task Name", sort: true },
        { label: "Participants", sort: false },
        // { key: "category__name", label: "Category", sort: true },
        // { key: "subcategory__name", label: "Sub Category", sort: true },
        { key: "start_date", label: "Start Date", sort: true },
        { key: "end_date", label: "End Date", sort: true },
        { label: "Schedule", sort: false },
        { key: "job__subdivision__name", label: "Subdivision", sort: true },
        // { key: "job__street_address", label: "Street Address", sort: true },
        { key: "job__city", label: "City", sort: true },
        // { key: "job__state", label: "State", sort: true },
        { key: "job__zip", label: "State / ZIP", sort: true },
        { key: 'action', label: 'Action', sort: false },
      ],
      filters: { includeCompleted: false, start: null, end: null },
      startDate: null,
      endDate: null,
    };
  },
  computed: {
    ...mapState([
      "loading",
      "detailedTasks",
      "detailedTasksCount",
      "detailedTasksPageSize",
      "detailedTasksPageIndex",
      "detailedTasksOrdering",
      "detailedTasksNumPages",
      "detailedTasksKeywords"
    ])
  },
  methods: {
    ...mapActions(["getDetailedTasks", "deleteTask"]),
    search: _.debounce(function() {
      if (this.keywords) {
        this.hasKeywords = true;
      }
      this.$refs.Table.doFetch();
    }, 1000),
    clearSearch() {
      this.keywords = "";
      this.hasKeywords = false;
      this.search();
    },
    selectStart: function() {
      if (!this.startDate) this.filters.start = null;
      this.filters.start = moment(this.startDate).format('YYYY-MM-DD');
      this.$refs.Table.doFetch();
    },
    selectEnd: function() {
      if (!this.endDate) this.filters.end = null;
      this.filters.end = moment(this.endDate).format('YYYY-MM-DD');
      this.$refs.Table.doFetch();
    },
    printTasks: function() {
      this.$modal.show("print-loading");
      const params = {
        keywords: this.keywords,
        ordering: this.ordering,
        filters: this.filters,
        mutateState: false,
        allItems: true
      };
      this.getDetailedTasks(params)
        .then(data => {
          this.performPrint(data);
        })
        .catch(() => {
          this.$toastr("error", "Error fetching print data", "error");
        })
        .finally(() => {
          this.$modal.hide("print-loading");
        });
    },
    performPrint: function(data) {
      printJS({
        printable: data,
        type: "json",
        properties: [
          { field: "name", displayName: "Task Name" },
          { field: "start_date", displayName: "Start Date" },
          { field: "end_date", displayName: "End Date" },
          { field: "subcontractor_name", displayName: "Subcontractor" },
          { field: "superintendent_name", displayName: "Crew / Flex" },
          { field: "builder_name", displayName: "builder_name" },
          { field: "between", displayName: "Schedule" },
          { field: "job_data.subdivision_name", displayName: "Subdivision" },
          { field: "job_data.lot_number", displayName: "Lot Number" },
          { field: "job_data.street_address", displayName: "Street Address" },
          { field: "job_data.city", displayName: "City" },
          { field: "job_data.state", displayName: "State" },
          { field: "job_data.zip", displayName: "ZIP" }
        ],
        style: `
            -webkit-print-color-adjust:exact;
          `,
        gridHeaderStyle: `
            border: 1px solid #c5d0e3;
            vertical-align: middle;
            text-align: left;
            background: #e3eaf6;
          `,
        gridStyle: `
            border: 1px solid #c5d0e3;
            vertical-align: middle;
            text-align: left;
          `
      });
    },
    goToTaskView: function(task) {
      this.$router.push({
        name: "task-detail",
        params: { id: task.id }
      });
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
    }
  },
  mounted() {
    this.keywords = this.tasksKeywords;
    if (this.keywords) {
      this.hasKeywords = true;
    }
    this.$nextTick(() => {
      this.$refs.Table.doFetch();
    });
  }
};
</script>

<style lang="scss">
  $input-height: 50px;
  $padding-x: 12px;

  .detailed-tasks {
    .vdp-datepicker,
    .time-picker input.display-time,
    input {
      height: $input-height;
      border: thin #c5d0e3 solid;
      border-radius: 0;
      background: #FFF;
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
    .vdp-datepicker__clear-button {
      position: absolute;
      top: 10px;
      right: 10px;
      font-size: 20px;

      i { font-style: normal; }
    }
  }
</style>
