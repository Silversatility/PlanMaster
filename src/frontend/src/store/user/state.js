import config from "../../config.json";

export default {
    loading: false,
    allUsers: [],
    users: [],
    usersKeywords: "",
    usersOrdering: "",
    usersCount: 0,
    usersPageSize: config.PAGE_SIZE,
    usersPageIndex: 1,
    usersNumPages: 0,
    user: {},
    currentUser: null
};
