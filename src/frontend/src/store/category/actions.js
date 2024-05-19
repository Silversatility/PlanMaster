import axios from "axios";

export default {
    getAllCategories({ commit }) {
        commit("getAllCategoriesRequest");
        let url = `/api/v1/task_category/?limit=0`;
        return axios
            .get(url)
            .then(function(response) {
                commit("getAllCategoriesSuccess", response.data);
                return response;
            })
            .catch(function(error) {
                commit("getAllCategoriesFailure", error);
                throw error;
            });
    }
};
