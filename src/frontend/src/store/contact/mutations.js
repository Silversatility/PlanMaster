export default {
    addContactRequest(state) {
        state.loading = true;
    },
    addContactSuccess(state) {
        state.loading = false;
    },
    addContactFailure(state) {
        state.loading = false;
    },

    updateContactRequest(state) {
        state.loading = true;
    },
    updateContactSuccess(state) {
        state.loading = false;
    },
    updateContactFailure(state) {
        state.loading = false;
    },

    deleteContactRequest(state) {
        state.loading = true;
    },
    deleteContactSuccess(state) {
        state.loading = false;
    },
    deleteContactFailure(state) {
        state.loading = false;
    }
};
