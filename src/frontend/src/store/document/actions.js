import axios from "axios";

export default {
    addDocument({ commit }, document) {
        commit("addDocumentRequest");
        let url = `/api/v1/document/`;
        return axios
            .post(url, document)
            .then(function(response) {
                commit("addDocumentSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("addDocumentFailure", error.response.data);
                throw error.response.data;
            });
    },
    deleteDocument({ commit }, document) {
        commit("deleteDocumentRequest");
        let url = `/api/v1/document/${document.id}/`;
        return axios
            .delete(url)
            .then(function(response) {
                commit("deleteDocumentSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("deleteDocumentFailure", error.response.data);
                throw error.response.data;
            });
    }
};
