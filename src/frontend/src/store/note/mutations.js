export default {
    addNoteRequest(state) {
        state.loading = true;
    },
    addNoteSuccess(state) {
        state.loading = false;
    },
    addNoteFailure(state) {
        state.loading = false;
    },

    updateNoteRequest(state) {
        state.loading = true;
    },
    updateNoteSuccess(state) {
        state.loading = false;
    },
    updateNoteFailure(state) {
        state.loading = false;
    },

    deleteNoteRequest(state) {
        state.loading = true;
    },
    deleteNoteSuccess(state, data) {
        state.loading = false;
        state.note = data;
    },
    deleteNoteFailure(state) {
        state.loading = false;
    },

    translateRequest(state) {
        state.loading = true;
    },
    translateSuccess(state) {
        state.loading = false;
    },
    translateFailure(state) {
        state.loading = false;
    },
};
