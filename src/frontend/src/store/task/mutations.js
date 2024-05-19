export default {
    getDetailedTasksRequest(state) {
        state.loading = true;
        state.detailedTasks = [];
        state.detailedTasksCount = 0;
        state.detailedTasksPageIndex = 1;
        state.detailedTasksNumPages = 0;
    },
    getDetailedTasksSuccess(state, data) {
        state.loading = false;
        state.detailedTasks = data.results;
        state.detailedTasksKeywords = data.keywords;
        state.detailedTasksOrdering = data.ordering;
        state.detailedTasksCount = data.count;
        state.detailedTasksPageIndex = data.page;
        state.detailedTasksNumPages = Math.ceil(data.count / state.currentUser.settings.page_size);
    },
    getDetailedTasksFailure(state) {
        state.loading = false;
        state.detailedTasks = [];
        state.detailedTasksCount = 0;
        state.detailedTasksPageIndex = 1;
        state.detailedTasksNumPages = 0;
    },
    getTasksRequest(state) {
        state.loading = true;
        state.tasks = [];
        state.tasksCount = 0;
        state.tasksPageIndex = 1;
        state.tasksNumPages = 0;
    },
    getTasksSuccess(state, data) {
        state.loading = false;
        state.tasks = data.results;
        state.tasksKeywords = data.keywords;
        state.tasksOrdering = data.ordering;
        state.tasksCount = data.count;
        state.tasksPageIndex = data.page;
        state.tasksNumPages = Math.ceil(data.count / state.currentUser.settings.page_size);
    },
    getTasksFailure(state) {
        state.loading = false;
        state.tasks = [];
        state.tasksCount = 0;
        state.tasksPageIndex = 1;
        state.tasksNumPages = 0;
    },

    getTaskByIdRequest(state) {
        state.loading = true;
        state.task = {};
    },
    getTaskByIdSuccess(state, data) {
        state.loading = false;
        state.task = data;
    },
    getTaskByIdFailure(state) {
        state.loading = false;
        state.task = {};
    },

    getTaskByJobRequest(state) {
        state.loading = true;
        state.tasks = [];
        state.tasksCount = 0;
        state.tasksPageIndex = 1;
        state.tasksNumPages = 0;
    },
    getTaskByJobSuccess(state, data) {
        state.loading = false;
        state.tasks = data.results;
        state.tasksKeywords = data.keywords;
        state.tasksOrdering = data.ordering;
        state.tasksCount = data.count;
        state.tasksPageIndex = data.page;
        state.tasksNumPages = Math.ceil(data.count / state.currentUser.settings.page_size);
    },
    getTaskByJobFailure(state) {
        state.loading = false;
        state.tasks = [];
        state.tasksCount = 0;
        state.tasksPageIndex = 1;
        state.tasksNumPages = 0;
    },

    getTasksByRoleRequest(state) {
        state.loading = true;
        state.tasks = [];
        state.tasksCount = 0;
        state.tasksPageIndex = 1;
        state.tasksNumPages = 0;
    },
    getTasksByRoleSuccess(state, data) {
        state.loading = false;
        state.tasks = data.results;
        state.tasksKeywords = data.keywords;
        state.tasksOrdering = data.ordering;
        state.tasksCount = data.count;
        state.tasksPageIndex = data.page;
        state.tasksNumPages = Math.ceil(data.count / state.currentUser.settings.page_size);
    },
    getTasksByRoleFailure(state) {
        state.loading = false;
        state.tasks = [];
        state.tasksCount = 0;
        state.tasksPageIndex = 1;
        state.tasksNumPages = 0;
    },

    getTaskNamesRequest(state) {
        state.loading = true;
        state.taskNames = [];
    },
    getTaskNamesSuccess(state, data) {
        state.loading = false;
        state.taskNames = data;
    },
    getTaskNamesFailure(state) {
        state.loading = false;
        state.taskNames = [];
    },

    addTaskRequest(state) {
        state.loading = true;
    },
    addTaskSuccess(state) {
        state.loading = false;
    },
    addTaskFailure(state) {
        state.loading = false;
    },

    updateTaskRequest(state) {
        state.loading = true;
    },
    updateTaskSuccess(state, data) {
        state.loading = false;
        state.task = data;
    },
    updateTaskFailure(state) {
        state.loading = false;
    },

    deleteTaskRequest(state) {
        state.loading = true;
    },
    deleteTaskSuccess(state, data) {
        state.loading = false;
        state.task = data;
    },
    deleteTaskFailure(state) {
        state.loading = false;
    },

    completeTaskRequest(state) {
        state.loading = true;
    },
    completeTaskSuccess(state, data) {
        state.loading = false;
        state.task = data;
    },
    completeTaskFailure(state) {
        state.loading = false;
    },

    resetTaskRequest(state) {
      state.task = {};
    },

    persistTaskFormRequest(state) {
        state.task = {};
    },
    persistTaskFormSuccess(state, data) {
      state.task = data;
    }

};
