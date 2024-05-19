import axios from "axios";

export default {
    getLoginAttemptsByUser({ commit, state }, { user, page = 1 }) {
        commit("getLoginAttemptsByUserRequest");
        let url = `/api/v1/login-attempt/?limit=0&user=${user}&limit=${state.loginAttemptsPageSize}&page=${page}`
        return axios
            .get(url)
            .then(function(response) {
                commit("getLoginAttemptsByUserSuccess", response.data, page);
                return response;
            })
            .catch(function(error) {
                commit("getLoginAttemptsByUserFailure", error);
                throw error;
            });
    }
};
