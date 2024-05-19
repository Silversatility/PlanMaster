export default {
    getAllCrewLeadersRequest(state) {
        state.crewLeaders = [];
    },

    getAllCrewLeadersSuccess(state, data) {
        state.crewLeaders = data;
    },

    getAllCrewLeadersFailure(state) {
        state.crewLeaders = [];
    },

    getCrewLeaderSettingsRequest(state) {
        state.crewLeaderSettings = {};
    },

    getCrewLeaderSettingsSuccess(state, data) {
        state.crewLeaderSettings = data;
        state.currentUser.settings.page_size = data.page_size;
    },

    getCrewLeaderSettingsFailure(state) {
        state.crewLeaderSettings = {};
    },

    updateCrewLeaderRequest(state) {
        state.loading = true;
    },

    updateCrewLeaderSuccess(state, data) {
        state.loading = false;
        state.crewLeader = data;
        state.currentUser.settings.page_size = data.page_size;
    },

    updateCrewLeaderFailure(state) {
        state.loading = false;
    }
};
