export default {
    getAllDefaultRemindersRequest(state) {
        state.reminders = [];
    },
    getAllDefaultRemindersSuccess(state, data) {
        state.reminders = data;
    },
    getAllDefaultRemindersFailure(state) {
        state.reminders = [];
    },
    getAllDefaultReminderDaysRequest(state) {
        state.defaultReminderDays = [];
    },
    getAllDefaultReminderDaysSuccess(state, data) {
        state.defaultReminderDays = data;
    },
    getAllDefaultReminderDaysFailure(state) {
        state.defaultReminderDays = [];
    },
    addDefaultReminderRequest(state) {
        state.loading = true;
    },
    addDefaultReminderSuccess(state) {
        state.loading = false;
    },
    addDefaultReminderFailure(state) {
        state.loading = false;
    },
    deleteDefaultReminderRequest(state) {
        state.loading = true;
    },
    deleteDefaultReminderSuccess(state) {
        state.loading = false;
    },
    deleteDefaultReminderFailure(state) {
        state.loading = false;
    },
    updateSheduleRequest(state) {
        state.loading = true;
    },
    updateSheduleSuccess(state, data) {
        state.loading = false;
        state.schedule = data;
    },
    updateSheduleFailure(state) {
        state.loading = false;
    }
};
