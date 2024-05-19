export default {
    addParticipationRequest(state) {
        state.loading = true;
    },
    addParticipationSuccess(state) {
        state.loading = false;
    },
    addParticipationFailure(state) {
        state.loading = false;
    },

    patchParticipationRequest(state) {
        state.loading = true;
    },
    patchParticipationSuccess(state) {
        state.loading = false;
    },
    patchParticipationFailure(state) {
        state.loading = false;
    }
};
