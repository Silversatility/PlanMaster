<template>
  <div>
    <Header />
    <main class="main-fluid dashboard">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center">
          <section class="date-wrapper d-flex justify-content-between align-items-center">
            <i class="arrows fa fa-chevron-left pointer" @click="previousSevenDays()"></i>
            <div class="week-dates" v-for="(day,i) in weekDays" :key="i">
              <span class="day">{{day.calDay}}</span>
              <span
                class="date pointer"
                :class="{active: day.formatDate === setDate.formatDate }"
                @click="dateSelected(day.formatDate, day.actualDate)"
              >{{day.calDate}}</span>
            </div>
            <i class="arrows fa fa-chevron-right pointer" @click="nextSevenDays()"></i>
          </section>
          <button
            v-if="permission.isAdmin(currentUser) || permission.isBuilder(currentUser) || permission.isCrewLeader(currentUser)"
            class="add-task-btn btn"
            @click="addTask()">
            <i class="fa fa-plus-circle" aria-hidden="true"></i>Add task
          </button>
        </div>
      </div>
      <MobileSubHeader
        :selectedDate="selectedDate"
        :viewBy="viewBy"
        :filterViewBy="filterViewBy"
        :weekDays="weekDays"
        :setDate="setDate"
      />
      <section class="title-section mb-5">
        <div class="container">
          <article class="title d-flex justify-content-between align-items-center">
            <h3>Task Overview for {{setDate.formatDate}}</h3>
            <div class="show-by d-flex align-items-center">
              <span class="mr-3">Filter by:</span>
              <button
                class="filter-btn btn mr-3"
                @click="filterTask('own')"
                :class="{active: filterByOwnTask}"
              >Own Tasks</button>
              <button
                class="filter-btn btn address"
                @click="filterTask('all')"
                :class="{active: !filterByOwnTask}"
              >All Tasks</button>
            </div>
            <div class="show-by d-flex align-items-center">
              <span class="mr-3">Show by:</span>
              <button
                class="filter-btn btn mr-3"
                @click="showByLot = true"
                :class="{active: showByLot}"
              >Lot #</button>
              <button
                class="filter-btn btn address mr-3"
                @click="showByLot = false"
                :class="{active: !showByLot}"
              >Address</button>
            </div>
          </article>
        </div>
      </section>
      <section class="tasks">
        <div v-show="cbLoading" class="cb-loader">
          <img class="loader-gif" src="/dist/assets/images/gear.gif" alt="Loader" />
        </div>
        <div class="container">
          <div class="row">
            <div class="col-md-4">
              <TaskStatus
                status="Starting Today"
                @removeHeightLimit="showAllStartingTasks = !showAllStartingTasks"
                :numberOfTasks="startingToday.length"
                :showMore="showAllStartingTasks"
              />
              <section class="tasks-wrapper" :class="{handleHeight: showAllStartingTasks}">
                <Task
                  v-for="(task,i) in startingToday"
                  :id="task.id"
                  :key="i"
                  :lotNumber="'#'+task.lot_number"
                  :taskDesc="task.name"
                  :address="task.job_address"
                  :subdivision="task.job_data.subdivision_name"
                  :showBy="showByLot"
                />
              </section>
              <span
                class="bottom-blur"
                v-show="startingToday.length > 2 && showAllStartingTasks === false"
              ></span>
            </div>
            <div class="col-md-4">
              <TaskStatus
                status="In Progress"
                @removeHeightLimit="showAllProgressTasks = !showAllProgressTasks"
                :showMore="showAllProgressTasks"
                :numberOfTasks="inProgress.length"
              />
              <section class="tasks-wrapper" :class="{handleHeight: showAllProgressTasks}">
                <Task
                  v-for="(task,i) in inProgress"
                  :id="task.id"
                  :key="i"
                  :lotNumber="'#'+task.lot_number"
                  :taskDesc="task.name"
                  :address="task.job_address"
                  :subdivision="task.job_data.subdivision_name"
                  :showBy="showByLot"
                />
              </section>
              <span
                class="bottom-blur"
                v-show="inProgress.length > 2 && showAllProgressTasks === false"
              ></span>
            </div>
            <div class="col-md-4">
              <TaskStatus
                status="Finishing Today"
                @removeHeightLimit="showAllFinishingTasks = !showAllFinishingTasks"
                :showMore="showAllFinishingTasks"
                :numberOfTasks="finishingToday.length"
              />
              <section class="tasks-wrapper" :class="{handleHeight: showAllFinishingTasks}">
                <Task
                  v-for="(task,i) in finishingToday"
                  :id="task.id"
                  :key="i"
                  :lotNumber="'#'+task.lot_number"
                  :taskDesc="task.name"
                  :address="task.job_address"
                  :subdivision="task.job_data.subdivision_name"
                  :showBy="showByLot"
                />
              </section>
              <span
                class="bottom-blur"
                v-show="finishingToday.length > 2 && showAllFinishingTasks === false"
              ></span>
            </div>
          </div>
        </div>
      </section>
    </main>
    <Footer />
  </div>
</template>

<script>
// @ is an alias to /src
import Header from "@/components/Header.vue";
import Footer from "@/components/Footer.vue";
import Task from "@/components/Dashboard/Task.vue";
import TaskStatus from "@/components/Dashboard/TaskStatus.vue";
import MobileSubHeader from "@/components/Dashboard/MobileSubHeader.vue";

import moment from "moment";
import { mapState, mapActions } from "vuex";
import { permission } from "../router-helper";

export default {
  name: "Dashboard",
  components: {
    Header,
    Footer,
    Task,
    TaskStatus,
    MobileSubHeader
  },
  data: function() {
    return {
      permission,
      weekDays: [],
      startDay: "",
      setDate: {
        formatDate: "",
        actualDate: ""
      },
      role: '',
      startingToday: [],
      inProgress: [],
      finishingToday: [],
      selectedDate: { formatDate: null, actualDate: null },
      filterByOwnTask: true,
      showByLot: true,
      viewBy: "lot",
      filterViewBy: "own",
      showAllStartingTasks: false,
      showAllProgressTasks: false,
      showAllFinishingTasks: false,
      cbLoading: false
    };
  },
  methods: {
    ...mapActions(["getTasksByRole"]),
    showWeek(firstDay) {
      let i, a;
      let day = firstDay;

      this.populateTasks({ isOwnTask: this.filterByOwnTask });
      this.weekDays = [];

      for (i = 0; i < 7; i++) {
        let obj = {};
        a = moment.utc(day);

        obj.calDay = a.format("dd");
        obj.calDate = a.format("DD");
        obj.calMonth = a.format("MMM");
        obj.actualDate = a;
        obj.formatDate = a.format("MMMM Do, YYYY");

        this.weekDays.push(obj);
        a = moment.utc(day.add(1, "days"));
      }
    },

    populateTasks({ isOwnTask = false }) {
      this.cbLoading = true;

      this.startingToday = [];
      this.finishingToday = [];
      this.inProgress = [];

      let tasksDate = moment.utc(this.setDate.actualDate).format("YYYY-MM-DD");
      let url = `/api/v1/task/?date=${tasksDate}&job_is_archived=false`;
      if (isOwnTask) {
        url += `&role=${this.currentUser.active_role.id}`;
      }
      this.$http
        .get(url)
        .then(response => {
          let i;

          let tasksArr = response.data.results.sort(function(a, b) {
            return Number(a.lot_number) - Number(b.lot_number);
          });

          for (i = 0; i < tasksArr.length; i++) {
            if (
              tasksArr[i].start_date ===
              moment.utc(this.setDate.actualDate).format("YYYY-MM-DD")
            ) {
              this.startingToday.push(tasksArr[i]);
            }

            if (
              tasksArr[i].end_date ===
              moment.utc(this.setDate.actualDate).format("YYYY-MM-DD")
            ) {
              this.finishingToday.push(tasksArr[i]);
            }

            let dateWithDashes = moment
              .utc(this.setDate.actualDate)
              .format("YYYY-MM-DD");

            if (
              moment
                .utc(this.setDate.actualDate)
                .isBetween(
                  tasksArr[i].start_date,
                  tasksArr[i].end_date,
                  null,
                  "[]"
                ) ||
              dateWithDashes === tasksArr[i].start_date ||
              dateWithDashes === tasksArr[i].end_date
            ) {
              this.inProgress.push(tasksArr[i]);
            }
          }

          this.cbLoading = false;
        })
        .catch(error => {
          this.$toastr("error", "Failed to load tasks", "Error");
          this.cbLoading = false;
        });
    },

    nextSevenDays() {
      let lastDayPreviousWeek = this.weekDays[6].actualDate;
      this.startDay = moment.utc(
        moment.utc(lastDayPreviousWeek).add(1, "days")
      );
      this.weekDays = [];
      this.showWeek(this.startDay);
    },

    previousSevenDays() {
      let firstDayPreviousWeek = this.weekDays[0].actualDate;
      this.startDay = moment.utc(firstDayPreviousWeek).subtract(7, "days");
      this.weekDays = [];
      this.showWeek(this.startDay);
    },

    dateSelected(formattedDate, momentDate) {
      this.setDate.formatDate = formattedDate;
      this.setDate.actualDate = momentDate;
      this.populateTasks({ isOwnTask: this.filterByOwnTask });
      this.saveSelectedDate(moment.utc(this.setDate.actualDate));
    },

    addTask() {
      this.$router.push({
        name: "add-task",
        query: {
          start_date: this.setDate.actualDate.format("YYYY-MM-DD"),
          end_date: this.setDate.actualDate.format("YYYY-MM-DD")
        }
      });
    },

    filterTask(filter) {
      if (filter === 'own') {
        this.filterByOwnTask = true;
        this.populateTasks({ isOwnTask: true });
      } else {
        this.filterByOwnTask = false;
        this.populateTasks({});
      }
    },

    ...mapActions(["saveSelectedDate"])
  },
  computed: {
    ...mapState(["currentUser", "previouslySelectedDate"])
  },
  mounted() {
    if (this.previouslySelectedDate.hasOwnProperty("_d")) {
      this.setDate.actualDate = this.previouslySelectedDate;
      this.setDate.formatDate = moment
        .utc(this.previouslySelectedDate)
        .format("MMMM Do, YYYY");
    } else {
      this.setDate.actualDate = moment.utc();
      this.setDate.formatDate = moment.utc().format("MMMM Do, YYYY");
    }

    this.showWeek(moment.utc(this.setDate.actualDate).startOf("week"));
  }
};
</script>

<style scoped lang="scss">
@import "@/assets/styles/Dashboard/dashboard.scss";
</style>
