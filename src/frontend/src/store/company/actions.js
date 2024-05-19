import axios from "axios";

export default {
    getMatchedCompanies({ commit }, { search = null, email = null, mobile_number = null, first_name = null, last_name = null }) {
        commit("getMatchedCompaniesRequest");
        let url = `/api/v1/company/match/?limit=0&ordering=name`;
        if (search) {
            url += `&search=${search}`;
        }
        if (email) {
            url += `&email=${email}`;
        }
        if (mobile_number) {
            url += `&mobile_number=${mobile_number}`;
        }
        if (first_name) {
            url += `&first_name=${first_name}`;
        }
        if (last_name) {
            url += `&last_name=${last_name}`;
        }
        return axios
            .get(url)
            .then(function(response) {
                commit("getMatchedCompaniesSuccess", response.data);
                return response;
            })
            .catch(function(error) {
                commit("getMatchedCompaniesFailure", error);
                throw error;
            });
    },
    getAllCompanies({ commit }, { job = null, excludeJob = null, type = null }) {
        commit("getAllCompaniesRequest");
        let url = `/api/v1/company/?limit=0`;
        if (job) {
            url += `&job=${job}`;
        }
        if (excludeJob) {
            url += `&exclude_job=${excludeJob}`;
        }
        if (type) {
            url += `&type=${type}`;
        }
        return axios
            .get(url)
            .then(function(response) {
                commit("getAllCompaniesSuccess", response.data);
                return response;
            })
            .catch(function(error) {
                commit("getAllCompaniesFailure", error);
                throw error;
            });
    },
    getCompanyById({ commit }, id) {
        commit("getCompanyByIdRequest");
        let url = `/api/v1/company/${id}/`;
        return axios
            .get(url)
            .then(function(response) {
                commit("getCompanyByIdSuccess", response.data);
            })
            .catch(function(error) {
                throw commit("getCompanyByIdFailure", error);
            });
    },

    updateCompany({ commit }, company) {
        commit("updateCompanyRequest");
        let url = `/api/v1/company/${company.id}/`;
        return axios
            .put(url, company)
            .then(function(response) {
                commit("updateCompanySuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("updateCompanyFailure", error.response.data);
                throw error.response.data;
            });
    },

    createCompany({ commit }, company) {
      commit('createCompanyRequest')
      let url = `/api/v1/company/create-company-with-role/`
      return axios
        .post(url, company)
          .then(function(response) {
            commit('createCompanySuccess', response.data)
            return response.data
          })
          .catch(function(error) {
            commit('createCompanyFailure', error.response.data)
            throw error.response.data;
          })
    }
};
