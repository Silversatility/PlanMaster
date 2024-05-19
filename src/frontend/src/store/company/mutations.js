export default {
    getMatchedCompaniesRequest(state) {
        state.matchedCompanies = [];
    },
    getMatchedCompaniesSuccess(state, data) {
        state.matchedCompanies = data;
    },
    getMatchedCompaniesFailure(state) {
        state.matchedCompanies = [];
    },

    getAllCompaniesRequest(state) {
        state.companies = [];
        state.contractor = {};
    },
    getAllCompaniesSuccess(state, data) {
        state.companies = data;
        state.contractor = data[0];
    },
    getAllCompaniesFailure(state) {
        state.companies = [];
        state.contractor = {};
    },

    getCompanyByIdRequest(state) {
        state.loading = true;
        state.company = {};
    },
    getCompanyByIdSuccess(state, data) {
        state.loading = false;
        state.company = data;
    },
    getCompanyByIdFailure(state) {
        state.loading = false;
        state.company = {};
    },

    updateCompanyRequest(state) {
        state.loading = true;
    },
    updateCompanySuccess(state, data) {
        state.loading = false;
        state.company = data;
    },
    updateCompanyFailure(state) {
        state.loading = false;
    },

    createCompanyRequest(state) {
        state.loading = true;
    },
    createCompanySuccess(state, data) {
        state.loading = false;
        state.currentUser.roles = data.roles
    },
    createCompanyFailure(state) {
        state.loading = false;
    },
};
