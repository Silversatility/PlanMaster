export default {
    getAllSubcategoriesRequest(state) {
        state.subcategories = [];
    },

    getAllSubcategoriesSuccess(state, data) {
        state.subcategories = data;
    },

    getAllSubcategoriesFailure(state) {
        state.subcategories = [];
    }
};
