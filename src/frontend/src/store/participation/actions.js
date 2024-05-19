import axios from "axios";

export default {
    addParticipation({ commit }, participation) {
        commit("addParticipationRequest");
        let url = `/api/v1/participation/`;
        return axios
            .post(url, participation)
            .then(function(response) {
                commit("addParticipationSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("addParticipationFailure", error.response.data);
                throw error.response.data;
            });
    },
    patchParticipation({ commit }, participation) {
        commit("patchParticipationRequest");
        let id = participation.id;
        let url = `/api/v1/participation/${id}/`;
        return axios
            .patch(url, participation)
            .then(function(response) {
                commit("patchParticipationSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("patchParticipationFailure", error.response.data);
                throw error.response.data;
            });
    }
};
