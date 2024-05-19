import config from "../../config.json";

export default {
    loginAttempts: [],
    loginAttemptsKeywords: "",
    loginAttemptsOrdering: "",
    loginAttemptsCount: 0,
    loginAttemptsPageSize: config.PAGE_SIZE,
    loginAttemptsPageIndex: 1,
    loginAttemptsNumPages: 0,
};
