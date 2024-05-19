import axios from "axios";

export default {
    saveSelectedDate({ commit }, selectedDate) {
      commit("saveDate", selectedDate );
    }
};
