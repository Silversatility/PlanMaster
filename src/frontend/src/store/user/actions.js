import axios from "axios";

export default {
    getAllUsers({ commit }) {
        commit("getAllUsersRequest");
        let url = `/api/v1/user/?limit=0`;
        return axios
            .get(url)
            .then(function(response) {
                commit("getAllUsersSuccess", response.data);
                return response;
            })
            .catch(function(error) {
                commit("getAllUsersFailure", error);
                throw error;
            });
    },
    getUsers({ commit, state }, { page = 1, keywords = "", ordering = "" }) {
        commit("getUsersRequest");
        let url = `/api/v1/user/?limit=${state.currentUser.settings.page_size}&page=${page}`;
        if (keywords) {
            url = url + `&search=${keywords}`;
        }
        if (ordering) {
            if (ordering === 'user_type') {
                url = url + `&order_by_user_type=true`;
            } else if (ordering === '-user_type') {
                url = url + `&order_by_user_type=false`;
            } else {
                url = url + `&ordering=${ordering}`;
            }
        }
        return axios
            .get(url)
            .then(function(response) {
                commit("getUsersSuccess", {
                    ...response.data,
                    page,
                    keywords,
                    ordering
                });
                return response.data;
            })
            .catch(function(error) {
                commit("getUsersFailure", error);
            });
    },
    getUserById({ commit }, { id }) {
        commit("getUserByIdRequest");
        let url = `/api/v1/user/${id}/`;
        return axios
            .get(url)
            .then(function(response) {
                commit("getUserByIdSuccess", response.data);
            })
            .catch(function(error) {
                commit("getUserByIdFailure", error);
                throw error.response.data;
            });
    },
    addUser({ commit }, user) {
        commit("addUserRequest");
        let url = `/api/v1/user/`;
        return axios
            .post(url, user)
            .then(function(response) {
                commit("addUserSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("addUserFailure", error.response.data);
                throw error.response.data;
            });
    },
    updateUser({ commit }, user) {
        commit("updateUserRequest");
        let url = `/api/v1/user/${user.id}/`;
        return axios
            .put(url, user)
            .then(function(response) {
                commit("updateUserSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("updateUserFailure", error.response.data);
                throw error.response.data;
            });
    },
    deleteUser({ commit }, user) {
        commit("deleteUserRequest");
        let url = `/api/v1/user/${user.id}/`;
        return axios
            .delete(url)
            .then(function(response) {
                commit("deleteUserSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("deleteUserFailure", error.response.data);
                throw error.response.data;
            });
    },
    login({ commit }, { email_or_mobile_number, password, ip_address }) {
        commit("loginRequest");
        let payload = JSON.stringify({ email_or_mobile_number, password, ip_address });
        return axios
            .post("/api/v1/login/", payload)
            .then(function(response) {
                commit("loginSuccess", response.data);
                return response;
            })
            .catch(function(error) {
                commit("loginFailure", error);
                throw error;
            });
    },
    logout({ commit }) {
        commit("logoutRequest");
        return axios
            .post("/api/v1/logout/")
            .then(function(response) {
                commit("logoutSuccess", response);
                return response;
            })
            .catch(function(error) {
                commit("logoutFailure", error);
                throw error;
            });
    },
    forgotPassword({ commit }, { email }) {
        commit("forgotPasswordRequest");
        let payload = JSON.stringify({ email });
        return axios
            .post("/api/v1/iforgot/", payload)
            .then(function(response) {
                commit("forgotPasswordSuccess", response.data);
                return response;
            })
            .catch(function(error) {
                commit("forgotPasswordFailure", error);
                throw error;
            });
    },
    inviteRole({ commit }, role) {
      commit("inviteRoleRequest");
      return axios
          .post("/api/v1/invite/", role)
          .then(function(response) {
              commit("inviteRoleSuccess", response.data);
              return response.data;
          })
          .catch(function(error) {
              commit("inviteRoleFailure", error);
              throw error.response.data;
          });
    },
    getIpAdress({ commit }) {
      commit("")
    }
};
