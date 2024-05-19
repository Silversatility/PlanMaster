import axios from "axios";

export default {
  getActiveRole({ commit }) {
    commit("getActiveRoleRequest");
    return axios
      .get("/api/v1/company-role/active-role/")
      .then(function(response) {
        commit("getActiveRoleSuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("getActiveRoleFailure", error);
        throw error.response.data;
      });
  },
  getAllRoles({ commit }, { job = null, excludeJob = null }) {
    commit("getAllRolesRequest");
    let url = `/api/v1/company-role/?limit=0`;
    if (job) {
      url += `&job=${job}`;
    }
    if (excludeJob) {
      url += `&exclude_job=${excludeJob}`;
    }
    return axios
      .get(url)
      .then(function(response) {
        response.data.forEach(function(role) {
          role.user_full_name = `${role.user.full_name} (${role.company_name}: ${role.user_types_other_display})`;
        });
        commit("getAllRolesSuccess", response.data);
        return response;
      })
      .catch(function(error) {
        commit("getAllRolesFailure", error);
        throw error;
      });
  },
  getMyCompanyRoles(
    { commit, state },
    { page = 1, keywords = "", ordering = "" }
  ) {
    commit("getMyCompanyRolesRequest");
    let url = `/api/v1/company-role/mine/?limit=${
      state.currentUser.settings.page_size
    }&page=${page}`;
    if (keywords) {
      url = url + `&search=${keywords}`;
    }
    if (ordering) {
      if (ordering === "user_type") {
        url = url + `&order_by_user_type=true`;
      } else if (ordering === "-user_type") {
        url = url + `&order_by_user_type=false`;
      } else {
        url = url + `&ordering=${ordering}`;
      }
    }
    return axios
      .get(url)
      .then(function(response) {
        commit("getMyCompanyRolesSuccess", {
          ...response.data,
          page,
          keywords,
          ordering
        });
        return response.data;
      })
      .catch(function(error) {
        throw commit("getMyCompanyRolesFailure", error);
      });
  },
  getRoles({ commit, state }, { page = 1, keywords = "", ordering = "", onlyInvited = false }) {
    commit("getRolesRequest");
    let url = `/api/v1/company-role/?limit=${
      state.currentUser.settings.page_size
    }&page=${page}`;
    if (keywords) {
      url = url + `&search=${keywords}`;
    }
    if (ordering) {
      if (ordering === "user_type") {
        url = url + `&order_by_user_type=true`;
      } else if (ordering === "-user_type") {
        url = url + `&order_by_user_type=false`;
      } else {
        url = url + `&ordering=${ordering}`;
      }
    }
    if (onlyInvited) {
      url += `&only_invited=${onlyInvited}`;
    }
    return axios
      .get(url)
      .then(function(response) {
        commit("getRolesSuccess", {
          ...response.data,
          page,
          keywords,
          ordering
        });
        return response.data;
      })
      .catch(function(error) {
        commit("getRolesFailure", error);
      });
  },
  getRoleById({ commit }, { id }) {
    commit("getRoleByIdRequest");
    let url = `/api/v1/company-role/${id}/`;
    return axios
      .get(url)
      .then(function(response) {
        commit("getRoleByIdSuccess", response.data);
      })
      .catch(function(error) {
        commit("getRoleByIdFailure", error);
        throw error.response.data;
      });
  },
  addRole({ commit }, user) {
    commit("addRoleRequest");
    let url = `/api/v1/invite/`;
    return axios
      .post(url, user)
      .then(function(response) {
        commit("addRoleSuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("addRoleFailure", error.response.data);
        throw error.response.data;
      });
  },
  updateRole({ commit }, user) {
    commit("updateRoleRequest");
    let url = `/api/v1/company-role/${user.id}/`;
    return axios
      .patch(url, user)
      .then(function(response) {
        commit("updateRoleSuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("updateRoleFailure", error.response.data);
        throw error.response.data;
      });
  },
  deleteRole({ commit }, user) {
    commit("deleteRoleRequest");
    let url = `/api/v1/company-role/${user.id}/`;
    return axios
      .delete(url)
      .then(function(response) {
        commit("deleteRoleSuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("deleteRoleFailure", error.response.data);
        throw error.response.data;
      });
  },
  reinviteRole({ commit }, user) {
    commit("reinviteRoleRequest");
    let url = `/api/v1/reinvite/`;
    return axios
      .post(url, user)
      .then(function(response) {
        commit("reinviteRoleSuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("reinviteRoleFailure", error.response.data);
        throw error.response.data;
      });
  },
  switchCompany({ commit }, roleId) {
    commit("switchCompanyRequest");
    let url = `/api/v1/company-role/${roleId}/switch-company/`;
    return axios
      .patch(url)
      .then(function(response) {
        commit("switchCompanySuccess", response.data);
        return response.data;
      })
      .catch(function(error) {
        commit("switchCompanyFailure");
        throw error;
      });
  }
};
