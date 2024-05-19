export default {
    getAllStatesRequest(state) {
        state.states = [];
    },
    getAllStatesSuccess(state, data) {
        state.states = data;
    },
    getAllStatesFailure(state) {
        state.states = [];
    },

    saveCalendarRequest(state) {
        state.calendarState = {};
    },
    saveCalendarSuccess(state, data) {
        state.calendarState = data;
    }
};
