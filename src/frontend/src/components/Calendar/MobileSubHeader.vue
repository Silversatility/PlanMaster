<template>
  <div class="mobile-sub-header">
    <div class="container">
      <section class="mobile-filter-section d-flex justify-content-start align-items-end">
        <div class="mr-5">
          <span class="select-title">Filter By:</span>
          <select
            class="role-select-task ml-2"
            v-model="filterByRole"
            @change="selectViewByRole()"
          >
            <option value="builder">Builder</option>
            <option value="subcontractor">Subcontractor</option>
            <option value="superintendent">Crew / Flex</option>
            <option value="job">Task</option>
          </select>
        </div>
        <div class="mr-3">
          <select
            class="role-select ml-2"
            v-model="filterByTask"
            @change="selectViewByTask()"
          >
            <option value="own">Own Tasks</option>
            <option value="all">All Tasks</option>
          </select>
        </div>
      </section>
      <section class="mobile-filter-section d-flex justify-content-start align-items-end">
        <div class="mr-3">
          <div class="cf-search-div">
            <input type="text"
              v-model="filterByKeywords"
              v-on:input="selectViewByKeywords()"
              class="form-control cf-search"
              placeholder="Search by Address, Subdivision, Job Name" />
            <button class="btn cf-search-btn" @click="hasKeywords ? clearSearch() : searchTasks()">
              <i :class="[hasKeywords ? 'fa fa-remove cf-fa-search' : 'fa fa-search cf-fa-search']"></i>
            </button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import moment from "moment";

export default {
  name: "MobileSubHeader",
  data() {
    return {
      filterByRole: this.filterBy,
      filterByTask: this.showBy,
      filterByKeywords: this.keywords,
      showByKeyword: this.hasKeywords
    };
  },
  props: {
    filterBy: String,
    showBy: String,
    keywords: String,
    hasKeywords: Boolean
  },

  methods: {
    selectViewByRole() {
      if (this.filterByRole === "builder") {
        this.$parent.filterTasks('builder');
      } else if (this.filterByRole === "subcontractor") {
        this.$parent.filterTasks('subcontractor');
      } else if (this.filterByRole === "superintendent") {
        this.$parent.filterTasks('superintendent');
      } else if (this.filterByRole === "job") {
        this.$parent.filterTasks('job');
      }
    },
    selectViewByTask() {
      this.filterByTask === "own"
        ? (this.$parent.filterTask('own'))
        : (this.$parent.filterTask('all'));
    },
    selectViewByKeywords() {
      if (this.filterByKeywords) {
        this.searchTasks();
      } else {
        this.clearSearch();
      }
    },
    searchTasks() {
      this.$parent.keywords = this.filterByKeywords;
      this.$parent.searchTasks();
    },
    clearSearch() {
      this.filterByKeywords = '';
      this.$parent.keywords = '';
      this.$parent.clearSearch();
      this.searchTasks();
    }
  },
  components: {}
};
</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import "@/assets/styles/Calendar/mobile-sub-header.scss";
</style>
