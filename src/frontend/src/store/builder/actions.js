import axios from "axios";

export default {
    getAllBuilders({ commit }, { job = null, company = null, onlyInvited = false }) {
        commit("getAllBuildersRequest");
        let url = `/api/v1/company-role/?role=builder&limit=0`;
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
                response.data.forEach(function(builder) {
                    builder.user_full_name = `${builder.user.first_name} ${builder.user.last_name} (${builder.company_name})`;
                });
                commit("getAllBuildersSuccess", response.data);
                return response;
            })
            .catch(function(error) {
                commit("getAllBuildersFailure", error);
                throw error;
            });
    }
};
