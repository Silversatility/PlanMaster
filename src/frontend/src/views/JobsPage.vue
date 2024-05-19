<template>
  <div>
    <Header />
    <PageHeading text="Job List">
        <section class="notification-search-inputs mr-3">
          <div class="cf-full-search-div-job">
            <input
              type="text"
              class="form-control cf-list-search"
              v-model="keywords"
              v-on:input="search()"
              placeholder="Search by Address, Subdivision, Builder, Subcontractor or Crew" />
              <button class="btn cf-full-search-button" @click="hasKeywords ? clearSearch() : search()">
                <i :class="[hasKeywords ? 'fa fa-remove cf-fa-search' : 'fa fa-search cf-fa-search']"></i>
              </button>
                <select
                v-model="filters.is_archived"
                class="form-control cf-search cf-full-search pull-right"
                @change="search()"
              >
                <option value=false>Active</option>
                <option value=true>Archived or Hidden</option>
              </select>
            </div>
          </section>
      <button v-if="permission.isAdmin(currentUser)" class="btn upload-btn mr-2" v-on:click="addJob()">
        <i class="fa fa-plus-circle" aria-hidden="true"></i>Add New Job
      </button>
    </PageHeading>

    <main class="main-fluid">
      <Table
        ref="Table"
        class="container"
        :modelName='modelName'
        :createRouteName='createRouteName'
        :fetch="getJobs"
        :items="jobs"
        :count="jobsCount"
        :pageSize="jobsPageSize"
        :pageIndex="jobsPageIndex"
        :numPages="jobsNumPages"
        :keywords="keywords"
        :ordering="jobsOrdering"
        :initialOrdering="ordering"
        :headers="headers"
      >
        <tr v-for="job in jobs" v-bind:key="job.id">
          <td><router-link v-bind:to="{name: 'job-detail', params: {id: job.id}}">{{job.street_address}}</router-link></td>
          <td>{{job.subdivision_name}}</td>
          <td>#{{job.lot_number}}</td>
          <td>{{job.owner_name}}</td>
          <td>
            <span class="participant-status B">
              {{job.builder_name}}
            </span>
            <span class="participant-status SC">
              {{job.subcontractor_name}}
            </span>
            <span class="participant-status CR">
              {{job.superintendent_name}}
            </span>
          </td>
          <td>
            <span class="table-action-buttons">
              <a v-if="!job.is_archived && permission.isAdmin(currentUser)" @click="confirmArchiveOrHideJob(job)" href="#">
                <i class="text-success fa fa-archive" aria-hidden="true"></i>
              </a>
              <a v-if="job.is_archived && permission.isAdmin(currentUser)" @click="confirmUnarchiveOrHideJob(job)" href="#">
                <i class="text-success fa fa-undo" aria-hidden="true"></i>
              </a>
              <ButtonTableAction
                icon="view"
                @click.native.prevent="goToJobView(job)"
              />
              <ButtonTableAction
                v-if="currentUser.active_role.company === job.owner || currentUser.active_role.company === job.created_by"
                icon="edit"
                @click.native.prevent="goToJobEdit(job)"
              />
              <ButtonTableAction
                v-if="currentUser.active_role.company === job.owner || currentUser.active_role.company === job.created_by"
                icon="delete"
                @click.native.prevent="confirmDeleteJob(job)"
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
    name: "JobsPage",
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
            keywords: "",
            ordering: "street_address",
            modelName: 'Job',
            createRouteName: 'add-job',
            headers: [
                {key: 'street_address', label: 'Job Address', sort: true},
                {key: 'subdivision__name', label: 'Subdivision', sort: true},
                {key: 'lot_number', label: 'Lot #', sort: true},
                {key: 'owner__name', label: 'General Contractor', sort: true},
                {key: 'default_contacts', label: 'Default Contacts', sort: false},
                {key: 'action', label: 'Action', sort: false}
            ],
            filters: { is_archived: false },
        };
    },
    computed: {
        ...mapState([
            'currentUser',
            "loading",
            "jobs",
            "jobsCount",
            "jobsPageSize",
            "jobsPageIndex",
            "jobsOrdering",
            "jobsNumPages",
            "jobsKeywords"
        ])
    },
    methods: {
        ...mapActions([
          "archiveOrHideJob",
          "unarchiveOrHideJob",
          "getJobs",
          "deleteJob"
        ]),
        search: _.debounce(function() {
          this.keywords ? this.hasKeywords = true : ''
            this.$refs.Table.doFetch(1, this.filters);
        }, 1000),
        clearSearch() {
          this.keywords = "";
          this.search();
        },
        addJob: function() {
            this.$router.push({ name: "add-job" });
        },
        goToJobView: function(job) {
          this.$router.push({
            name: "job-detail",
            params: { id: job.id }
          });
        },
        goToJobEdit: function(job) {
          this.$router.push({
            name: "update-job",
            params: { id: job.id }
          });
        },
        confirmDeleteJob: function(job) {
          this.$modal.show('dialog', {
            title: 'Delete Job',
            text: `<p>Are you sure you want to delete this job?</p><b class="text-center block">${job.street_address}<br>${job.subdivision_name}<br>${job.lot_number}</b>`,
            buttons: [
              {
                title: '<div class="btn cb-delete">Delete</div>',
                handler: () => {
                  this.deleteJob({ id: job.id })
                    .then(() => {
                      this.$refs.Table.doFetch();
                      this.$toastr("info", "Job Deleted!", "Info");
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
        confirmArchiveOrHideJob: function(job) {
          let self = this;
          this.$modal.show('dialog', {
              title: 'Confirm',
              text: 'Are you sure you want to mark this job as Archived or Hidden?',
              buttons: [
                  {
                      title: '<div class="btn cb-delete">Archive</div>',
                      handler: () => {
                          this.archiveOrHideJob({ id: job.id })
                          .then(() => {
                              this.$refs.Table.doFetch(1, this.filters);
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
      confirmUnarchiveOrHideJob: function(job) {
          let self = this;
          this.$modal.show('dialog', {
              title: 'Confirm',
              text: 'Are you sure you want to mark this job as Active?',
              buttons: [
                  {
                      title: '<div class="btn cb-delete">Active</div>',
                      handler: () => {
                          this.unarchiveOrHideJob({ id: job.id })
                          .then(() => {
                              this.$refs.Table.doFetch(1, this.filters);
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
    },
    mounted() {
      this.keywords = this.jobsKeywords;
      this.keywords ? this.hasKeywords = true : ''
      this.$nextTick(() => {
        this.$refs.Table.doFetch(1, this.filters);
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
    width: 71%;
  }
  select {
    width: 25%;
    background-image: none;
  }
}

.notification-search-inputs-remove {
  width: 100%;
  flex: 1;
  input,
  select {
    position: static;
    margin: 0;
  }
  input {
    width: 75%;
  }
  select {
    width: 25%;
    background-image: none;
  }
}

@media (max-width: 1080px) {
  .notification-search-inputs-remove {
    margin: 10px 0 0;
    input {
      width: 70%;
      margin-bottom: 13px;
    }
  }

  .upload-btn {
    margin-bottom: 10px;
  }
}

@media (max-width: 768px) {
  .notification-search-inputs-remove {
    margin: 10px 0 0;
  }

  .upload-btn {
    margin-bottom: 10px;
  }
}

@media (max-width: 425px) {
  .notification-search-inputs-remove {
    input {
      width: 100%;
      margin-bottom: 13px;
    }
    select {
      width: 100%;
      margin-bottom: 13px;
    }
  }
  button {
    width: 100% !important;
  }
}
</style>
