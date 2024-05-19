import axios from "axios";

export default {
    getReminders({ commit, state }, { page = 1, keywords = "", ordering = "" }) {
        commit("getRemindersRequest");
        let url = `/api/v1/reminder/?limit=${state.currentUser.settings.page_size}&page=${page}`;
        if (keywords) {
            url = url + `&search=${keywords}`;
        }
        if (ordering) {
            url = url + `&ordering=${ordering}`;
        }
        return axios
            .get(url)
            .then(function(response) {
                commit("getRemindersSuccess", {
                    ...response.data,
                    page,
                    keywords,
                    ordering
                });
                return response.data;
            })
            .catch(function(error) {
                commit("getRemindersFailure", error);
            });
    },
    getReminderById({ commit }, { id }) {
        commit("getReminderByIdRequest");
        let url = `/api/v1/reminder/${id}/`;
        return axios
            .get(url)
            .then(function(response) {
                commit("getReminderByIdSuccess", response.data);
            })
            .catch(function(error) {
                commit("getReminderByIdFailure", error);
            });
    },
    addReminder({ commit }, reminder) {
        commit("addReminderRequest");
        let url = `/api/v1/reminder/`;
        return axios
            .post(url, reminder)
            .then(function(response) {
                commit("addReminderSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("addReminderFailure", error.response.data);
                throw error.response.data;
            });
    },
    deleteReminder({ commit }, reminder) {
        commit("deleteReminderRequest");
        let url = `/api/v1/reminder/${reminder.id}/`;
        return axios
            .delete(url)
            .then(function(response) {
                commit("deleteReminderSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("deleteReminderFailure", error.response.data);
                throw error.response.data;
            });
    },
    getAllReminderDays({ commit }) {
        commit("getAllReminderDaysRequest");
        let url = `/api/v1/reminder/`;
        return axios
            .options(url)
            .then(function(response) {
                commit(
                    "getAllReminderDaysSuccess",
                    response.data.actions.POST.reminder_days.choices
                );
                return response;
            })
            .catch(function(error) {
                commit("getAllReminderDaysFailure", error);
                throw error;
            });
    }
};
