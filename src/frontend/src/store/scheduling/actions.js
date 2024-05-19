import axios from "axios";

export default {
    getAllDefaultReminders({ commit }) {
        commit("getAllDefaultRemindersRequest");
        let url = `/api/v1/default-reminders/?limit=0`;
        return axios
            .get(url)
            .then(function(response) {
                commit("getAllDefaultRemindersSuccess", response.data);
                return response;
            })
            .catch(function(error) {
                commit("getAllDefaultRemindersFailure", error);
                throw error;
            });
    },
    addDefaultReminder({ commit }, reminder) {
        commit("addDefaultReminderRequest");
        let url = `/api/v1/default-reminders/`;
        return axios
            .post(url, reminder)
            .then(function(response) {
                commit("addDefaultReminderSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("addDefaultReminderFailure", error.response.data);
                throw error.response.data;
            });
    },
    deleteDefaultReminder({ commit }, reminder) {
        commit("deleteDefaultReminderRequest");
        let url = `/api/v1/default-reminders/${reminder.id}/`;
        return axios
            .delete(url)
            .then(function(response) {
                commit("deleteDefaultReminderSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("deleteDefaultReminderFailure", error.response.data);
                throw error.response.data;
            });
    },
    updateShedule({ commit }, company) {
        commit("updateSheduleRequest");
        let url = `/api/v1/company/${company.id}/`;
        return axios
            .put(url, company)
            .then(function(response) {
                commit("updateSheduleSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("updateSheduleFailure", error.response.data);
                throw error.response.data;
            });
    },
    getAllDefaultReminderDays({ commit }, company) {
        commit("getAllDefaultReminderDaysRequest");
        let url = `/api/v1/default-reminders/?not_company=${company}`;
        return axios
            .options(url)
            .then(function(response) {
                commit(
                    "getAllDefaultReminderDaysSuccess",
                    response.data.actions.POST.reminder_days.choices
                );
                return response;
            })
            .catch(function(error) {
                commit("getAllDefaultReminderDaysFailure", error);
                throw error;
            });
    }
};
