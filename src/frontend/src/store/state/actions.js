import axios from "axios";

export default {
    getAllStates({ commit }) {
        commit("getAllStatesRequest");
        let url = `/api/v1/job/`;
        return axios
            .options(url)
            .then(function(response) {
                commit(
                    "getAllStatesSuccess",
                    response.data.actions.POST.state.choices
                );
                return response;
            })
            .catch(function(error) {
                commit("getAllStatesFailure", error);
                throw error;
            });
    },

    saveCalendarState({ commit }, keywords, role, status, view, filter, job) {
        commit("saveCalendarSuccess", keywords, role, status, view, filter, job);
    }
};
