import axios from "axios";

export default {
  getMatchedJobs({ commit }, { owner = null, search = null }) {
    commit("getMatchedJobsRequest");
    let url = `/api/v1/job/match/?limit=0&ordering=street_address`;
    if (owner) {
      url += `&owner=${owner}`;
    }
    if (search) {
      url += `&search=${search}`;
    }
    return axios
      .get(url)
      .then(function(response) {
        commit("getMatchedJobsSuccess", response.data);
        return response;
      })
      .catch(function(error) {
        commit("getMatchedJobsFailure", error);
        throw error;
      });
  },
  getAllJobs({ commit }) {
    commit("getAllJobsRequest");
    let url = `/api/v1/job/?limit=0`;
    return axios
      .get(url)
      .then(function(response) {
        commit("getAllJobsSuccess", response.data);
        return response;
      })
      .catch(function(error) {
        commit("getAllJobsFailure", error);
        throw error;
      });
  },
  getJobs(
    { commit, state },
    {
      page = 1,
      keywords = "",
      ordering = "",
      is_archived = false,
      filters = null
    }
  ) {
    commit("getJobsRequest");
    let url = `/api/v1/job/?limit=${
      state.currentUser.settings.page_size
    }&page=${page}`;
    if (keywords) {
      url = url + `&search=${keywords}`;
    }
    if (ordering) {
      url = url + `&ordering=${ordering}`;
    }
    if (is_archived) {
      url = url + `&is_archived=${is_archived}`;
    }
    if (filters) {
      for (let [key, value] of Object.entries(filters)) {
        url += `&${key}=${value}`;
      }
    }
    return axios
      .get(url)
      .then(function(response) {
        commit("getJobsSuccess", {
          ...response.data,
          page,
          keywords,
          ordering
        });
        return response.data;
      })
      .catch(function(error) {
        commit("getJobsFailure", error);
      });
  },
  getJobsByRole(
      { commit, state },
      { role, page = 1, keywords = "", ordering = "" }
  ) {
      commit("getJobsByRoleRequest");
      let url = `/api/v1/job/?roles=${role}&limit=${state.jobsPageSize}&page=${page}`;
      if (keywords) {
          url = url + `&search=${keywords}`;
      }
      if (ordering) {
          url = url + `&ordering=${ordering}`;
      }
      return axios
          .get(url)
          .then(function(response) {
              commit("getJobsByRoleSuccess", response.data, page, keywords, ordering);
          })
          .catch(function(error) {
              commit("getJobsByRoleFailure", error);
          });
  },
  getJobById({ commit }, { id }) {
    commit("getJobByIdRequest");
    let url = `/api/v1/job/${id}/`;
    return axios
      .get(url)
      .then(function(response) {
        commit("getJobByIdSuccess", response.data);
      })
      .catch(function(error) {
        commit("getJobByIdFailure", error);
      });
  },
  addJob({ commit }, job) {
    commit("addJobRequest");
    let url = `/api/v1/job/`;
    return axios
      .post(url, job)
      .then(function(response) {
        commit("addJobSuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("addJobFailure", error.response.data);
        throw error.response.data;
      });
  },
  updateJob({ commit }, job) {
    commit("updateJobRequest");
    let url = `/api/v1/job/${job.id}/`;
    return axios
      .put(url, job)
      .then(function(response) {
        commit("updateJobSuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("updateJobFailure", error.response.data);
        throw error.response.data;
      });
  },
  deleteJob({ commit }, job) {
    commit("deleteJobRequest");
    let url = `/api/v1/job/${job.id}/`;
    return axios
      .delete(url)
      .then(function(response) {
        commit("deleteJobSuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("deleteJobFailure", error.response.data);
        throw error.response.data;
      });
  },
  shareJobToRole({ commit }, { job, sharedTo }) {
    commit("shareJobToRoleRequest");
    let url = `/api/v1/job/${job.id}/share-role/`;
    return axios
      .put(url, { role: sharedTo })
      .then(function(response) {
        commit("shareJobToRoleSuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("shareJobToRoleFailure", error.response.data);
        throw error.response.data;
      });
  },
  unshareJobToRole({ commit }, { job, sharedTo }) {
    commit("unshareJobToRoleRequest");
    let url = `/api/v1/job/${job.id}/unshare-role/`;
    return axios
      .put(url, { role: sharedTo })
      .then(function(response) {
        commit("unshareJobToRoleSuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("unshareJobToRoleFailure", error.response.data);
        throw error.response.data;
      });
  },

  archiveOrHideJob({ commit }, job) {
    commit("archiveOrHideJobRequest");
    let url = `/api/v1/job/${job.id}/archive/`;
    return axios
      .put(url)
      .then(function(response) {
        commit("archiveOrHideJobSuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("archiveOrHideJobFailure", error.response.data);
        throw error.response.data;
      });
  },
  unarchiveOrHideJob({ commit }, job) {
    commit("unarchiveOrHideJobRequest");
    let url = `/api/v1/job/${job.id}/unarchive/`;
    return axios
      .put(url)
      .then(function(response) {
        commit("unarchiveOrHideJobSuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("unarchiveOrHideJobFailure", error.response.data);
        throw error.response.data;
      });
  }
};
