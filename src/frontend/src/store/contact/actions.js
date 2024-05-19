import axios from "axios";

export default {
    addContact({ commit }, contact) {
        commit("addContactRequest");
        let url = `/api/v1/contact/`;
        return axios
            .post(url, contact)
            .then(function(response) {
                commit("addContactSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("addContactFailure", error.response.data);
                throw error.response.data;
            });
    },
    updateContact({ commit }, contact) {
        commit("updateContactRequest");
        let url = `/api/v1/contact/${contact.id}/`;
        return axios
            .patch(url, contact)
            .then(function(response) {
                commit("updateContactSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("updateContactFailure", error.response.data);
                throw error.response.data;
            });
    },
    deleteContact({ commit }, contact) {
        commit("deleteContactRequest");
        let url = `/api/v1/contact/${contact.id}/`;
        return axios
            .delete(url)
            .then(function(response) {
                commit("deleteContactSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("deleteContactFailure", error.response.data);
                throw error.response.data;
            });
    }
};
