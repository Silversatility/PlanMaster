import axios from "axios";

export default {
    getAllSubdivisions({ commit }, { company = null }) {
        commit("getAllSubdivisionsRequest");
        let url = `/api/v1/subdivision/?limit=0`;
        if (company) {
            url += `&company=${company}`;
        }
        return axios
            .get(url)
            .then(function(response) {
                commit("getAllSubdivisionsSuccess", response.data);
                return response;
            })
            .catch(function(error) {
                commit("getAllSubdivisionsFailure", error);
                throw error;
            });
    }
};
