import config from "../../config.json";

export default {
    loading: false,
    notifications: [],
    notificationsKeywords: "",
    notificationsOrdering: "",
    notificationsFilters: { type: false, is_queued: true },
    notificationsCount: 0,
    notificationsPageSize: config.PAGE_SIZE,
    notificationsPageIndex: 1,
    notificationsNumPages: 0,
    notification: {},
    headerNotificationsCount: 0,
};
