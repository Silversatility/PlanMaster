<template>
  <div class="mobile-sub-header">
    <div class="container">
      <section class="mobile-filter-section d-flex justify-content-start align-items-end">
        <div class="mr-3">
          <span class="select-title">Date</span>
          <article class="d-flex justify-content-between align-items-center">
            <select
              class="dates-select mr-2"
              v-model="selDate"
              @change="dateSelected(selDate.formatDate, selDate.actualDate)"
            >
              <option
                :value="{formatDate: selDate.formatDate, actualDate: selDate.actualDate}"
              >{{this.setDate.actualDate | dateFormat}}</option>
              <option
                v-for="(day,n) in weekDays"
                :key="n"
                :value="{formatDate: day.formatDate, actualDate: day.actualDate}"
              >{{day.calMonth}} {{day.calDate}}</option>
              <option :value="{formatDate: 'previous', actualDate: null}">Previous Week</option>
              <option :value="{formatDate: 'next', actualDate: null}">Next Week</option>
            </select>
          </article>
        </div>
        <div class="mr-3">
          <span class="select-title">Show By:</span>
          <select class="lot-select mr-2" v-model="showBy" @change="selectView()">
            <option value="lot">Lot #</option>
            <option value="address">Address</option>
          </select>
        </div>
        <div class="mr-3">
          <span class="select-title">Filter By:</span>
          <select class="lot-select mr-2" v-model="filterShowBy" @change="selectTaskView()">
            <option value="own">Own Tasks</option>
            <option value="all">All Tasks</option>
          </select>
        </div>
        <button class="add-task-btn-mobile btn" @click="addTask()">
          <i class="fa fa-plus-circle" aria-hidden="true"></i>
        </button>
      </section>
      <h3 class="mobile-title">Task Overview for {{setDate.formatDate}}</h3>
    </div>
  </div>
</template>

<script>
import moment from "moment";

export default {
  name: "MobileSubHeader",
  data() {
    return {
      selDate: {
        formatDate: this.setDate.formatDate,
        actualDate: this.setDate.actualDate
      },
      showBy: this.viewBy,
      filterShowBy: this.filterViewBy,
      dateShown: moment(this.setDate.actualDate).format("MMM DD")
    };
  },
  props: {
    selectedDate: Object,
    weekDays: Array,
    setDate: Object,
    viewBy: String,
    filterViewBy: String,
    showByLot: Boolean,
  },

  methods: {
    dateSelected(formatDate, actualDate) {
      if (formatDate === "next") {
        this.$parent.nextSevenDays();
      } else if (formatDate === "previous") {
        this.$parent.previousSevenDays();
      } else {
        this.$parent.dateSelected(formatDate, actualDate);
      }
    },

    nextSevenDays() {
      this.$parent.nextSevenDays();
    },

    previousSevenDays() {
      this.$parent.previousSevenDays();
    },

    addTask() {
      this.$parent.addTask();
    },

    selectView() {
      this.showBy === "lot"
        ? (this.$parent.showByLot = true)
        : (this.$parent.showByLot = false);
    },
    selectTaskView() {
      this.filterShowBy === "own"
        ? (this.$parent.filterTask('own'))
        : (this.$parent.filterTask('all'));
    }
  },

  filters: {
    dateFormat(a) {
      return moment.utc(a).format("MMM DD");
    }
  },
  components: {}
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/assets/styles/Dashboard/mobile-sub-header.scss";
</style>
