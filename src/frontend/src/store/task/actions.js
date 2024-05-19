import axios from "axios";

export default {
    getTasks({ commit, state }, { page = 1, keywords = "", ordering = "", status = false, filters = null, job_is_archived = false }) {
        commit("getTasksRequest");
        let url = `/api/v1/task/?limit=${state.currentUser.settings.page_size}&page=${page}`;
        if (keywords) {
            url = url + `&search=${keywords}`;
        }
        if (ordering) {
            url = url + `&ordering=${ordering}`;
        }
        if (status) {
            url = url + `&status=${status}`;
        }
        if (!job_is_archived) {
            url = url + `&job_is_archived=false`;
        }
        if (filters) {
          for (let [key, value] of Object.entries(filters)) {
            url += `&${key}=${value}`
          }
        }
        return axios
            .get(url)
            .then(function(response) {
                commit("getTasksSuccess", {
                    ...response.data,
                    page,
                    keywords,
                    ordering
                });
                return response.data;
            })
            .catch(function(error) {
                commit("getTasksFailure", error);
            });
    },
    getDetailedTasks({ commit, state }, { allItems = false, page = 1, keywords = "", ordering = "", status = false, filters = null, mutateState = true}) {
        if (mutateState) {
            commit("getDetailedTasksRequest");
        }
        let url = ''

        if (allItems) {
          url = `/api/v1/task/detailed/?limit=0&page=${page}`;
        } else {
          url = `/api/v1/task/detailed/?limit=${state.currentUser.settings.page_size}&page=${page}`;
        }


        if (keywords) {
            url = url + `&search=${keywords}`;
        }
        if (ordering) {
            url = url + `&ordering=${ordering}`;
        }
        if (status) {
            url = url + `&status=${status}`;
        }
        if (filters) {
            if (filters.includeCompleted === false) url = url + `&is_completed=false`;
            if (filters.start) url = url + `&start=${filters.start}`;
            if (filters.end) url = url + `&end=${filters.end}`;
        }

        return axios
            .get(url)
            .then(function(response) {
                if (mutateState) {
                    commit("getDetailedTasksSuccess", {
                        ...response.data,
                        page,
                        keywords,
                        ordering
                    });
                }
                return response.data
            })
            .catch(function(error) {
                if (mutateState) {
                    commit("getDetailedTasksFailure", error);
                }
            });
    },
    getTaskById({ commit }, { id }) {
        commit("getTaskByIdRequest");
        let url = `/api/v1/task/${id}/`;
        return axios
            .get(url)
            .then(function(response) {
                commit("getTaskByIdSuccess", response.data);
            })
            .catch(function(error) {
                throw commit("getTaskByIdFailure", error);
            });
    },
    getTaskByJob(
        { commit, state },
        { job, page = 1, keywords = "", ordering = "" }
    ) {
        commit("getTaskByJobRequest");
        let url = `/api/v1/task/?job=${job}&limit=${
            state.tasksPageSize
        }&page=${page}`;
        if (keywords) {
            url = url + `&search=${keywords}`;
        }
        if (ordering) {
            url = url + `&ordering=${ordering}`;
        }
        return axios
            .get(url)
            .then(function(response) {
                commit(
                    "getTaskByJobSuccess",
                    response.data,
                    page,
                    keywords,
                    ordering
                );
            })
            .catch(function(error) {
                commit("getTaskByJobFailure", error);
            });
    },
    getTasksByRole(
        { commit, state },
        { role, page = 1, keywords = "", ordering = "" }
    ) {
        commit("getTasksByRoleRequest");
        let url = role ? `/api/v1/task/?role=${role}&limit=${state.tasksPageSize}&page=${page}` : `/api/v1/task/?limit=${state.tasksPageSize}&page=${page}`;
        if (keywords) {
            url = url + `&search=${keywords}`;
        }
        if (ordering) {
            url = url + `&ordering=${ordering}`;
        }
        return axios
            .get(url)
            .then(function(response) {
                commit("getTasksByRoleSuccess", response.data, page, keywords, ordering);
            })
            .catch(function(error) {
                commit("getTasksByRoleFailure", error);
            });
    },
    getTaskNames({ commit, state }, { search = "" }) {
        commit("getTaskNamesRequest");
        let url = `/api/v1/task/names/?limit=0`;
        if (search) {
            url = url + `&search=${search}`;
        }
        return axios
            .get(url)
            .then(function(response) {
                commit("getTaskNamesSuccess", response.data);
            })
            .catch(function(error) {
                commit("getTaskNamesFailure", error);
            });
    },
    addTask({ commit }, task) {
        commit("addTaskRequest");
        let url = `/api/v1/task/`;
        if (task._alsoSendNotifications) {
            url = `/api/v1/task/create-and-send-notifications/`
        }

        return axios
            .post(url, task)
            .then(function(response) {
                commit("addTaskSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("addTaskFailure", error.response.data);
                throw error.response.data;
            });
    },
    updateTask({ commit }, task) {
        commit("updateTaskRequest");
        let url = `/api/v1/task/${task.id}/`;
        if (task._alsoSendNotifications) {
            url = `/api/v1/task/${task.id}/update-and-send-notifications/`
        }
        return axios
            .put(url, task)
            .then(function(response) {
                commit("updateTaskSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("updateTaskFailure", error.response.data);
                throw error.response.data;
            });
    },
    deleteTask({ commit }, task) {
        commit("deleteTaskRequest");
        let url = `/api/v1/task/${task.id}/`;
        return axios
            .delete(url)
            .then(function(response) {
                commit("deleteTaskSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("deleteTaskFailure", error.response.data);
                throw error.response.data;
            });
    },
    completeTask({ commit }, task) {
        commit("completeTaskRequest");
        let url = `/api/v1/task/${task.id}/complete/`;
        return axios
            .put(url)
            .then(function(response) {
                commit("completeTaskSuccess", response.data);
                return response.data;
            })
            .catch(function(error) {
                commit("completeTaskFailure", error.response.data);
                throw error.response.data;
            });
    },
    resetTask({commit}) {
      commit("resetTaskRequest");
    },
    persistTaskForm({ commit }, { task }) {
        commit("persistTaskFormSuccess", task);
    }
};
