import config from "../../config.json";

export default {
    documents: [],
    documentsKeywords: "",
    documentsOrdering: "",
    documentsCount: 0,
    documentsPageSize: config.PAGE_SIZE,
    documentsPageIndex: 1,
    documentsNumPages: 0,
    document: {}
};
