import axios from "axios";

export default {
    getAllSubcategories({ commit }, { categoryId }) {
        commit("getAllSubcategoriesRequest");
        let url = `/api/v1/task_subcategory/?limit=0&category=${categoryId}`;
        return axios
            .get(url)
            .then(function(response) {
                commit("getAllSubcategoriesSuccess", response.data);
                return response;
            })
            .catch(function(error) {
                commit("getAllSubcategoriesFailure", error);
                throw error;
            });
    }
};
