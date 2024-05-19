import config from "../../config.json";

export default {
  loading: false,
  tasks: [],
  tasksKeywords: "",
  tasksOrdering: "",
  tasksCount: 0,
  tasksPageSize: config.PAGE_SIZE,
  tasksPageIndex: 1,
  tasksNumPages: 0,
  task: {},

  detailedTasks: [],
  detailedTasksKeywords: "",
  detailedTasksOrdering: "",
  detailedTasksCount: 0,
  detailedTasksPageSize: config.PAGE_SIZE,
  detailedTasksPageIndex: 1,
  detailedTasksNumPages: 0,

  taskNames: []
};
