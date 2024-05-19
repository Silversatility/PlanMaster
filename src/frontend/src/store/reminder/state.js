import config from "../../config.json";

export default {
    loading: false,
    reminders: [],
    remindersKeywords: "",
    remindersOrdering: "",
    remindersCount: 0,
    remindersPageSize: config.PAGE_SIZE,
    remindersPageIndex: 1,
    remindersNumPages: 0,
    reminder: {},
    reminderDays: []
};
