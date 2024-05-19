export default {
    getAllUsersRequest(state) {
        state.allUsers = [];
    },
    getAllUsersSuccess(state, data) {
        state.allUsers = data;
    },
    getAllUsersFailure(state) {
        state.allUsers = [];
    },

    getUsersRequest(state) {
        state.loading = true;
        state.users = [];
        state.usersCount = 0;
        state.usersPageIndex = 1;
        state.usersNumPages = 0;
    },
    getUsersSuccess(state, data) {
        state.loading = false;
        state.users = data.results;
        state.usersKeywords = data.keywords;
        state.usersOrdering = data.ordering;
        state.usersCount = data.count;
        state.usersPageIndex = data.page;
        state.usersNumPages = Math.ceil(data.count / state.currentUser.settings.page_size);
    },
    getUsersFailure(state) {
        state.loading = false;
        state.users = [];
        state.usersCount = 0;
        state.usersPageIndex = 1;
        state.usersNumPages = 0;
    },

    getUserByIdRequest(state) {
        state.loading = true;
        state.user = {};
    },
    getUserByIdSuccess(state, data) {
        state.loading = false;
        state.user = data;
    },
    getUserByIdFailure(state) {
        state.loading = false;
        state.user = {};
    },

    addUserRequest(state) {
        state.loading = true;
    },
    addUserSuccess(state) {
        state.loading = false;
    },
    addUserFailure(state) {
        state.loading = false;
    },

    updateUserRequest(state) {
        state.loading = true;
    },
    updateUserSuccess(state, data) {
        state.loading = false;
        state.user = data;
    },
    updateUserFailure(state) {
        state.loading = false;
    },

    deleteUserRequest(state) {
        state.loading = true;
    },
    deleteUserSuccess(state, data) {
        state.loading = false;
        state.user = data;
    },
    deleteUserFailure(state) {
        state.loading = false;
    },

    loginRequest(state) {
        state.loading = true;
        state.currentUser = null;
    },
    loginSuccess(state, data) {
        state.loading = false;
        state.currentUser = {
            user_type: data.user_type,
            session_key: data.session_key,
            settings: data.settings,
            active_role: data.active_role,
            user: data.user,
            roles: data.roles,
        };
    },
    loginFailure(state) {
        state.loading = false;
        state.currentUser = null;
    },

    logoutRequest(state) {
        state.loading = true;
    },
    logoutSuccess(state) {
        state.loading = false;
        state.currentUser = null;
    },
    logoutFailure(state) {
        state.loading = false;
        state.currentUser = null;
    },

    forgotPasswordRequest(state) {
        state.loading = true;
    },
    forgotPasswordSuccess(state) {
        state.loading = false;
    },
    forgotPasswordFailure(state) {
        state.loading = false;
    },

    inviteRoleRequest(state) {
        state.loading = true;
    },
    inviteRoleSuccess(state) {
        state.loading = false;
    },
    inviteRoleFailure(state) {
        state.loading = false;
    }
};
