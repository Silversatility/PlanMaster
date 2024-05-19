export default {
    addDocumentRequest(state) {
        state.loading = true;
    },
    addDocumentSuccess(state) {
        state.loading = false;
    },
    addDocumentFailure(state) {
        state.loading = false;
    },

    deleteDocumentRequest(state) {
        state.loading = true;
    },
    deleteDocumentSuccess(state) {
        state.loading = false;
    },
    deleteDocumentFailure(state) {
        state.loading = false;
    }
};
