export default {
    getAllCategoriesRequest(state) {
        state.categories = [];
    },

    getAllCategoriesSuccess(state, data) {
        state.categories = data;
    },

    getAllCategoriesFailure(state) {
        state.categories = [];
    }
};
