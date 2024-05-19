export default {
  getMatchedJobsRequest(state) {
    state.matchedJobs = [];
  },
  getMatchedJobsSuccess(state, data) {
    state.matchedJobs = data;
  },
  getMatchedJobsFailure(state) {
    state.matchedJobs = [];
  },

  getAllJobsRequest(state) {
    state.jobs = [];
  },

  getAllJobsSuccess(state, data) {
    state.jobs = data;
  },

  getAllJobsFailure(state) {
    state.jobs = [];
  },

  getJobsRequest(state) {
    state.loading = true;
    state.jobs = [];
    state.jobsCount = 0;
    state.jobsPageIndex = 1;
    state.jobsNumPages = 0;
  },
  getJobsSuccess(state, data) {
    state.loading = false;
    state.jobs = data.results;
    state.jobsKeywords = data.keywords;
    state.jobsOrdering = data.ordering;
    state.jobsCount = data.count;
    state.jobsPageIndex = data.page;
    state.jobsNumPages = Math.ceil(
      data.count / state.currentUser.settings.page_size
    );
  },
  getJobsFailure(state) {
    state.loading = false;
    state.jobs = [];
    state.jobsCount = 0;
    state.jobsPageIndex = 1;
    state.jobsNumPages = 0;
  },

  getJobsByRoleRequest(state) {
    state.loading = true;
    state.jobs = [];
    state.jobsCount = 0;
    state.jobsPageIndex = 1;
    state.jobsNumPages = 0;
  },
  getJobsByRoleSuccess(state, data) {
    state.loading = false;
    state.jobs = data.results;
    state.jobsKeywords = data.keywords;
    state.jobsOrdering = data.ordering;
    state.jobsCount = data.count;
    state.jobsPageIndex = data.page;
    state.jobsNumPages = Math.ceil(
      data.count / state.currentUser.settings.page_size
    );
  },
  getJobsByRoleFailure(state) {
    state.loading = false;
    state.jobs = [];
    state.jobsCount = 0;
    state.jobsPageIndex = 1;
    state.jobsNumPages = 0;
  },

  getJobByIdRequest(state) {
    state.loading = true;
    state.job = {};
  },
  getJobByIdSuccess(state, data) {
    state.loading = false;
    state.job = data;
  },
  getJobByIdFailure(state) {
    state.loading = false;
    state.job = {};
  },

  addJobRequest(state) {
    state.loading = true;
  },
  addJobSuccess(state) {
    state.loading = false;
  },
  addJobFailure(state) {
    state.loading = false;
  },

  updateJobRequest(state) {
    state.loading = true;
  },
  updateJobSuccess(state, data) {
    state.loading = false;
    state.job = data;
  },
  updateJobFailure(state) {
    state.loading = false;
  },

  deleteJobRequest(state) {
    state.loading = true;
  },
  deleteJobSuccess(state, data) {
    state.loading = false;
    state.job = data;
  },
  deleteJobFailure(state) {
    state.loading = false;
  },

  shareJobToCompanyRequest(state) {
    state.loading = true;
  },
  shareJobToCompanySuccess(state, data) {
    state.loading = false;
  },
  shareJobToCompanyFailure(state) {
    state.loading = false;
  },
  unshareJobToCompanyRequest(state) {
    state.loading = true;
  },
  unshareJobToCompanySuccess(state, data) {
    state.loading = false;
  },
  unshareJobToCompanyFailure(state) {
    state.loading = false;
  },
  shareJobToRoleRequest(state) {
    state.loading = true;
  },
  shareJobToRoleSuccess(state, data) {
    state.loading = false;
  },
  shareJobToRoleFailure(state) {
    state.loading = false;
  },
  unshareJobToRoleRequest(state) {
    state.loading = true;
  },
  unshareJobToRoleSuccess(state, data) {
    state.loading = false;
  },
  unshareJobToRoleFailure(state) {
    state.loading = false;
  },

  archiveOrHideJobRequest(state) {
    state.loading = true;
  },
  archiveOrHideJobSuccess(state, data) {
    state.loading = false;
    state.job = data;
  },
  archiveOrHideJobFailure(state) {
    state.loading = false;
  },
  unarchiveOrHideJobRequest(state) {
    state.loading = true;
  },
  unarchiveOrHideJobSuccess(state, data) {
    state.loading = false;
    state.job = data;
  },
  unarchiveOrHideJobFailure(state) {
    state.loading = false;
  }
};
