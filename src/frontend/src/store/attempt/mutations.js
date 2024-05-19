export default {
    getLoginAttemptsByUserRequest(state) {
        state.loading = true;
        state.loginAttempts = [];
        state.loginAttemptsCount = 0;
        state.loginAttemptsPageIndex = 1;
        state.loginAttemptsNumPages = 0;
    },

    getLoginAttemptsByUserSuccess(state, data) {
        state.loading = false;
        state.loginAttempts = data.results;
        state.loginAttemptsKeywords = data.keywords;
        state.loginAttemptsOrdering = data.ordering;
        state.loginAttemptsCount = data.count;
        state.loginAttemptsPageIndex = data.page;
        state.loginAttemptsNumPages = Math.ceil(data.count / state.currentUser.settings.page_size);
    },

    getLoginAttemptsByUserFailure(state) {
        state.loading = false;
        state.loginAttempts = [];
        state.loginAttemptsCount = 0;
        state.loginAttemptsPageIndex = 1;
        state.loginAttemptsNumPages = 0;
    }
};
