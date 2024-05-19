import axios from "axios";

export default {
    getAllCrewLeaders({ commit }, { job = null, company = null }) {
        commit("getAllCrewLeadersRequest");
        let url = `/api/v1/company-role/?role=subcontractor&limit=0`;
        if (job) {
            url += `&job=${job}`;
        }
        if (company) {
            url += `&company=${company}`;
        }
        return axios
            .get(url)
            .then(function(response) {
                response.data.forEach(function(crewLeader) {
                    crewLeader.user_full_name = `${crewLeader.user.first_name} ${crewLeader.user.last_name} (${crewLeader.company_name})`;
                });
                commit("getAllCrewLeadersSuccess", response.data);
                return response;
            })
            .catch(function(error) {
                commit("getAllCrewLeadersFailure", error);
                throw error;
            });
    },

    getCrewLeaderSettings({ commit }) {
        commit("getCrewLeaderSettingsRequest");
        let url = `/api/v1/company-role/user_settings/`;
        return axios
            .get(url)
            .then(function(response) {
                commit("getCrewLeaderSettingsSuccess", response.data);
            })
            .catch(function(error) {
                commit("getCrewLeaderSettingsFailure", error);
                throw error.response.data;
            });
    },

    updateCrewLeader({ commit }, crewLeader) {
        commit("updateCrewLeaderRequest");
        let url = `/api/v1/company-role/${crewLeader.id}/`;
        return axios
            .patch(url, crewLeader)
            .then(function(response) {
                commit("updateCrewLeaderSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("updateCrewLeaderFailure", error.response.data);
                throw error.response.data;
            });
    },
};
