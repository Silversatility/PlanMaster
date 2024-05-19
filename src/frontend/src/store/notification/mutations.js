export default {
    getNotificationsRequest(state) {
        state.loading = true;
        state.notifications = [];
        state.notificationsCount = 0;
        state.notificationsPageIndex = 1;
        state.notificationsNumPages = 0;
    },
    getNotificationsSuccess(state, data) {
        state.loading = false;
        state.notifications = data.results;
        state.notificationsKeywords = data.keywords;
        state.notificationsOrdering = data.ordering;
        state.notificationsCount = data.count;
        state.notificationsPageIndex = data.page;
        state.notificationsNumPages = Math.ceil(data.count / state.currentUser.settings.page_size);
    },
    getNotificationsFailure(state) {
        state.loading = false;
        state.notifications = [];
        state.notificationsCount = 0;
        state.notificationsPageIndex = 1;
        state.notificationsNumPages = 0;
    },

    getHeaderNotificationsCountRequest(state) {
        state.loading = true;
          state.headerNotificationsCount = 0
    },
    getHeaderNotificationsCountSuccess(state, data) {
        state.loading = false;
        state.headerNotificationsCount = data.notification_count;
    },
    getHeaderNotificationsCountFailure(state) {
        state.loading = false;
        state.headerNotificationsCount = 0
    },
};
