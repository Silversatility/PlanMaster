export default {
    getAllRolesRequest(state) {
        state.allRoles = [];
    },
    getAllRolesSuccess(state, data) {
        state.allRoles = data;
    },
    getAllRolesFailure(state) {
        state.allRoles = [];
    },

    getMyCompanyRolesRequest(state) {
        state.loading = true;
        state.roles = [];
        state.rolesCount = 0;
        state.rolesPageIndex = 1;
        state.rolesNumPages = 0;
    },
    getMyCompanyRolesSuccess(state, data) {
        state.loading = false;
        state.roles = data.results;
        state.rolesKeywords = data.keywords;
        state.rolesOrdering = data.ordering;
        state.rolesCount = data.count;
        state.rolesPageIndex = data.page;
        state.rolesNumPages = Math.ceil(data.count / state.currentUser.settings.page_size);
    },
    getMyCompanyRolesFailure(state) {
        state.loading = false;
        state.roles = [];
        state.rolesCount = 0;
        state.rolesPageIndex = 1;
        state.rolesNumPages = 0;
    },

    getRolesRequest(state) {
        state.loading = true;
        state.roles = [];
        state.rolesCount = 0;
        state.rolesPageIndex = 1;
        state.rolesNumPages = 0;
    },
    getRolesSuccess(state, data) {
        state.loading = false;
        state.roles = data.results;
        state.rolesKeywords = data.keywords;
        state.rolesOrdering = data.ordering;
        state.rolesCount = data.count;
        state.rolesPageIndex = data.page;
        state.rolesNumPages = Math.ceil(data.count / state.currentUser.settings.page_size);
    },
    getRolesFailure(state) {
        state.loading = false;
        state.roles = [];
        state.rolesCount = 0;
        state.rolesPageIndex = 1;
        state.rolesNumPages = 0;
    },

    getRoleByIdRequest(state) {
        state.loading = true;
        state.role = {};
    },
    getRoleByIdSuccess(state, data) {
        state.loading = false;
        state.role = data;
    },
    getRoleByIdFailure(state) {
        state.loading = false;
        state.role = {};
    },

    addRoleRequest(state) {
        state.loading = true;
    },
    addRoleSuccess(state) {
        state.loading = false;
    },
    addRoleFailure(state) {
        state.loading = false;
    },

    updateRoleRequest(state) {
        state.loading = true;
    },
    updateRoleSuccess(state, data) {
        state.loading = false;
        state.role = data;
    },
    updateRoleFailure(state) {
        state.loading = false;
    },

    deleteRoleRequest(state) {
        state.loading = true;
    },
    deleteRoleSuccess(state, data) {
        state.loading = false;
        state.role = data;
    },
    deleteRoleFailure(state) {
        state.loading = false;
    },

    reinviteRoleRequest(state) {
        state.loading = true;
    },
    reinviteRoleSuccess(state) {
        state.loading = false;
    },
    reinviteRoleFailure(state) {
        state.loading = false;
    },

    getActiveRoleRequest(state) {
        state.loading = true;
    },
    getActiveRoleSuccess(state, data) {
        state.currentUser.active_role = data.active_role;
        state.loading = false;
    },
    getActiveRoleFailure(state) {
        state.loading = false;
    },
    switchCompanyRequest(state) {
        state.loading = true;
    },
    switchCompanySuccess(state, data) {
        state.currentUser.active_role = data.active_role;
        state.loading = false;
    },
    switchCompanyFailure(state) {
        state.loading = false;
    }
};
