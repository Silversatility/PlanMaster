import axios from "axios";

export default {
    addNote({ commit }, note) {
        commit("addNoteRequest");
        let url = `/api/v1/note/`;
        return axios
            .post(url, note)
            .then(function(response) {
                commit("addNoteSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("addNoteFailure", error.response.data);
                throw error.response.data;
            });
    },
    updateNote({ commit }, note) {
        commit("updateNoteRequest");
        let url = `/api/v1/note/${note.id}/`;
        return axios
            .patch(url, note)
            .then(function(response) {
                commit("updateNoteSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("updateNoteFailure", error.response.data);
                throw error.response.data;
            });
    },
    deleteNote({ commit }, note) {
        commit("deleteNoteRequest");
        let url = `/api/v1/note/${note.id}/`;
        return axios
            .delete(url)
            .then(function(response) {
                commit("deleteNoteSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("deleteNoteFailure", error.response.data);
                throw error.response.data;
            });
    },
    translate({ commit }, data) {
        commit("translateRequest");
        let url = `/api/v1/note/translate/`;
        return axios
            .post(url, data)
            .then(function (response) {
                commit("translateSuccess", response.data);
                return response.data;
            })
            .catch(function (error) {
                commit("translateFailure", error.response.data);
                throw error.response.data;
            });
    },

};
