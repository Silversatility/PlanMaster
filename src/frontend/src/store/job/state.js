import config from "../../config.json";

export default {
  matchedJobs: [],
  jobs: [],
  jobsKeywords: "",
  jobsOrdering: "",
  jobsCount: 0,
  jobsPageSize: config.PAGE_SIZE,
  jobsPageIndex: 1,
  jobsNumPages: 0,
  job: {}
};
