import config from "../../config.json";

export default {
    loading: false,
    allRoles: [],
    roles: [],
    rolesKeywords: "",
    rolesOrdering: "",
    rolesCount: 0,
    rolesPageSize: config.PAGE_SIZE,
    rolesPageIndex: 1,
    rolesNumPages: 0,
    role: {},
};
