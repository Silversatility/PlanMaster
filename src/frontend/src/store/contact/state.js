import config from "../../config.json";

export default {
    contacts: [],
    contactsKeywords: "",
    contactsOrdering: "",
    contactsCount: 0,
    contactsPageSize: config.PAGE_SIZE,
    contactsPageIndex: 1,
    contactsNumPages: 0,
    contact: {}
};
