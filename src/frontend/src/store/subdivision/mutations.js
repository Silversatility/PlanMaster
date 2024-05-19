export default {
    getAllSubdivisionsRequest(state) {
        state.subdivisions = [];
    },

    getAllSubdivisionsSuccess(state, data) {
        state.subdivisions = data;
    },

    getAllSubdivisionsFailure(state) {
        state.subdivisions = [];
    }
};
