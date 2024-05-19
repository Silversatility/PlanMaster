import axios from "axios";

export default {
    getAllSuperintendents({ commit }, { job = null, company = null, onlyInvited = false }) {
        commit("getAllSuperintendentsRequest");
        let url = `/api/v1/company-role/?role=superintendent&limit=0`;
        if (job) {
            url += `&job=${job}`;
        }
        if (company) {
            url += `&company=${company}`;
        }
        if (onlyInvited) {
          url += `&only_invited=${onlyInvited}`;
        }
        return axios
            .get(url)
            .then(function(response) {
                response.data.forEach(function(superintendent) {
                    superintendent.user_full_name = `${superintendent.user.first_name} ${superintendent.user.last_name} (${superintendent.company_name})`;
                });
                commit("getAllSuperintendentsSuccess", response.data);
                return response;
            })
            .catch(function(error) {
                commit("getAllSuperintendentsFailure", error);
                throw error;
            });
    }
};
