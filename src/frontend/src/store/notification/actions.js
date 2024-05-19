import axios from "axios";

export default {
    getNotifications({ commit, state }, { page = 1, keywords = "", ordering = "", filters = { type: false, is_queued: true } }) {
        commit("getNotificationsRequest");
        let url = `/api/v1/notification-queue/?limit=${state.currentUser.settings.page_size}&page=${page}`;
        if (keywords) {
            url = url + `&search=${keywords}`;
        }
        if (ordering) {
            url = url + `&ordering=${ordering}`;
        }

        if (filters.type) {
          url = url + `&type=${filters.type}`;
        }

        if (filters.is_queued != 'all') {
          url = url + `&is_queued=${filters.is_queued}`;
        }

        return axios
            .get(url)
            .then(function(response) {
                commit("getNotificationsSuccess", {
                    ...response.data,
                    page,
                    keywords,
                    ordering
                });
                return response.data;
            })
            .catch(function(error) {
                commit("getNotificationsFailure", error);
            });
    },

    getHeaderNotificationsCount({ commit }) {
      commit('getHeaderNotificationsCountRequest');
      let self = this;
      return axios
        .get(`/api/v1/notification-queue/queued-count/`)
        .then(response => {
          commit("getHeaderNotificationsCountSuccess", response.data);
        })
        .catch((error) => {
          commit('getHeaderNotificationsCountFailure', error);
        });
    }
};
