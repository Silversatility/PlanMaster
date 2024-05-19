export default {
    getRemindersRequest(state) {
        state.loading = true;
        state.reminders = [];
        state.remindersCount = 0;
        state.remindersPageIndex = 1;
        state.remindersNumPages = 0;
    },
    getRemindersSuccess(state, data) {
        state.loading = false;
        state.reminders = data.results;
        state.remindersKeywords = data.keywords;
        state.remindersOrdering = data.ordering;
        state.remindersCount = data.count;
        state.remindersPageIndex = data.page;
        state.remindersNumPages = Math.ceil(data.count / state.currentUser.settings.page_size);
    },
    getRemindersFailure(state) {
        state.loading = false;
        state.reminders = [];
        state.remindersCount = 0;
        state.remindersPageIndex = 1;
        state.remindersNumPages = 0;
    },

    getReminderByIdRequest(state) {
        state.loading = true;
        state.reminder = {};
    },
    getReminderByIdSuccess(state, data) {
        state.loading = false;
        state.reminder = data;
    },
    getReminderByIdFailure(state) {
        state.loading = false;
        state.reminder = {};
    },

    addReminderRequest(state) {
        state.loading = true;
    },
    addReminderSuccess(state) {
        state.loading = false;
    },
    addReminderFailure(state) {
        state.loading = false;
    },

    deleteReminderRequest(state) {
        state.loading = true;
    },
    deleteReminderSuccess(state, data) {
        state.loading = false;
        state.reminder = data;
    },
    deleteReminderFailure(state) {
        state.loading = false;
    },

    getAllReminderDaysRequest(state) {
        state.reminderDays = [];
    },

    getAllReminderDaysSuccess(state, data) {
        state.reminderDays = data;
    },

    getAllReminderDaysFailure(state) {
        state.reminderDays = [];
    }

};
