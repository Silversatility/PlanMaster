export default {
    getAllBuildersRequest(state) {
        state.builders = [];
    },

    getAllBuildersSuccess(state, data) {
        state.builders = data;
    },

    getAllBuildersFailure(state) {
        state.builders = [];
    }
};
