export default {
    getAllSuperintendentsRequest(state) {
        state.superintendents = [];
    },

    getAllSuperintendentsSuccess(state, data) {
        state.superintendents = data;
    },

    getAllSuperintendentsFailure(state) {
        state.superintendents = [];
    }
};
