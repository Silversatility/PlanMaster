import Vue from "vue";
import Vuex from "vuex";
import VuexPersistence from "vuex-persist";

import loginAttemptState from "./attempt/state";
import userState from "./user/state";
import dashboardState from "./dashboard/state";
import roleState from "./role/state";
import categoryState from "./category/state";
import subcategoryState from "./subcategory/state";
import superintendentState from "./superintendent/state";
import jobState from "./job/state";
import contactState from "./contact/state";
import noteState from "./note/state";
import documentState from "./document/state";
import reminderState from "./reminder/state";
import builderState from "./builder/state";
import crewLeaderState from "./crewLeader/state";
import participationState from "./participation/state";
import taskState from "./task/state";
import subdivisionState from "./subdivision/state";
import companyState from "./company/state";
import notificationState from "./notification/state";
import subscriptionState from "./subscription/state";
import stateState from "./state/state";
import schedulingState from "./scheduling/state";

import loginAttemptMutations from "./attempt/mutations";
import userMutations from "./user/mutations";
import dashboardMutations from "./dashboard/mutations";
import roleMutations from "./role/mutations";
import categoryMutations from "./category/mutations";
import subcategoryMutations from "./subcategory/mutations";
import superintendentMutations from "./superintendent/mutations";
import jobMutations from "./job/mutations";
import contactMutations from "./contact/mutations";
import noteMutations from "./note/mutations";
import documentMutations from "./document/mutations";
import reminderMutations from "./reminder/mutations";
import builderMutations from "./builder/mutations";
import crewLeaderMutations from "./crewLeader/mutations";
import participationMutations from "./participation/mutations";
import taskMutations from "./task/mutations";
import subdivisionMutations from "./subdivision/mutations";
import companyMutations from "./company/mutations";
import notificationMutations from "./notification/mutations";
import subscriptionMutations from "./subscription/mutations";
import stateMutations from "./state/mutations";
import schedulingMutations from "./scheduling/mutations";

import loginAttemptActions from "./attempt/actions";
import userActions from "./user/actions";
import dashboardActions from "./dashboard/actions";
import roleActions from "./role/actions";
import categoryActions from "./category/actions";
import subcategoryActions from "./subcategory/actions";
import superintendentActions from "./superintendent/actions";
import jobActions from "./job/actions";
import contactActions from "./contact/actions";
import noteActions from "./note/actions";
import documentActions from "./document/actions";
import reminderActions from "./reminder/actions";
import builderActions from "./builder/actions";
import crewLeaderActions from "./crewLeader/actions";
import participationActions from "./participation/actions";
import taskActions from "./task/actions";
import subdivisionActions from "./subdivision/actions";
import companyActions from "./company/actions";
import notificationActions from "./notification/actions";
import subscriptionActions from "./subscription/actions";
import stateActions from "./state/actions";
import schedulingActions from "./scheduling/actions";


Vue.use(Vuex);

const vuexLocal = new VuexPersistence({
    storage: window.localStorage,
    reducer: state => {
        return {
            currentUser: state.currentUser,
            calendarState: state.calendarState
        };
    }
});

export default new Vuex.Store({
    state: {
        ...loginAttemptState,
        ...userState,
        ...dashboardState,
        ...roleState,
        ...categoryState,
        ...subcategoryState,
        ...superintendentState,
        ...jobState,
        ...contactState,
        ...noteState,
        ...documentState,
        ...reminderState,
        ...builderState,
        ...crewLeaderState,
        ...participationState,
        ...taskState,
        ...subdivisionState,
        ...companyState,
        ...notificationState,
        ...subscriptionState,
        ...stateState,
        ...schedulingState
    },
    mutations: {
        ...loginAttemptMutations,
        ...userMutations,
        ...dashboardMutations,
        ...roleMutations,
        ...categoryMutations,
        ...subcategoryMutations,
        ...superintendentMutations,
        ...jobMutations,
        ...contactMutations,
        ...noteMutations,
        ...documentMutations,
        ...reminderMutations,
        ...builderMutations,
        ...crewLeaderMutations,
        ...participationMutations,
        ...taskMutations,
        ...subdivisionMutations,
        ...companyMutations,
        ...notificationMutations,
        ...subscriptionMutations,
        ...stateMutations,
        ...schedulingMutations
    },
    actions: {
        ...loginAttemptActions,
        ...userActions,
        ...dashboardActions,
        ...roleActions,
        ...categoryActions,
        ...subcategoryActions,
        ...superintendentActions,
        ...jobActions,
        ...contactActions,
        ...noteActions,
        ...documentActions,
        ...reminderActions,
        ...builderActions,
        ...crewLeaderActions,
        ...participationActions,
        ...taskActions,
        ...subdivisionActions,
        ...companyActions,
        ...notificationActions,
        ...subscriptionActions,
        ...stateActions,
        ...schedulingActions
    },
    plugins: [vuexLocal.plugin]
});
