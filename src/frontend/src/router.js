import Vue from "vue";
import Router from "vue-router";
import LoginPage from "./views/LoginPage.vue";
import TasksPage from "./views/TasksPage.vue";
import DetailedTasksPage from "./views/DetailedTasksPage.vue";
import TaskForm from "./views/TaskForm.vue";
import TaskDetailPage from "./views/TaskDetailPage.vue";
import JobsPage from "./views/JobsPage.vue";
import JobForm from "./views/JobForm.vue";
import JobDetailPage from "./views/JobDetailPage.vue";
import UsersPage from "./views/UsersPage.vue";
import UserForm from "./views/UserForm.vue";
import UserDetailPage from "./views/UserDetailPage.vue";
import CrewStaffForm from "./views/CrewStaffForm.vue";
import CalendarNewPage from "./views/CalendarNewPage.vue";
import SettingsPage from "./views/SettingsPage.vue";
import NotificationsPage from "./views/NotificationsPage.vue";
import CompanyRoles from "./views/CompanyRoles.vue";
import CompanyForm from "./views/CompanyForm.vue";
import CompanyAccountPage from "./views/CompanyAccountPage.vue";
import Dashboard from "./views/Dashboard.vue";

import store from "./store/";
import { permission } from "./router-helper"
Vue.use(Router);

const router = new Router({
  routes: [
    {
      path: "/",
      name: "home",
      redirect: { name: "dashboard" }
    },
    {
      path: "/dashboard",
      name: "dashboard",
      component: Dashboard
      // beforeEnter: (to, from, next) => {
      //   console.log(window.OneSignal);
      //   console.log(typeof window.OneSignal);
      //   //if (window.OneSignal == undefined) {
      //     alert(1);
      //     //don't initialize onesignal twice
      //     if (store.state.currentUser !== null) { // check if user is logged in
      //       var OneSignal = window.OneSignal || [];
      //       OneSignal.push(function() {
      //         OneSignal.init({
      //           appId: "7c08da39-113b-481b-887b-ad9d092ea17b"
      //         });
      //       });

      //       console.log(typeof OneSignal);
      //     }
      //   //}
      //   next();
      // }
    },
    {
      path: "/login",
      name: "login",
      component: LoginPage
    },
    {
      path: "/tasks",
      name: "tasks",
      component: TasksPage
    },
    {
      path: "/detailed-tasks",
      name: "detailed-tasks",
      component: DetailedTasksPage
    },
    {
      path: "/add-task",
      name: "add-task",
      component: TaskForm,
      beforeEnter: (to, from, next) => {
        if (
          permission.isAdmin(store.state.currentUser) ||
          permission.isBuilder(store.state.currentUser) ||
          permission.isCrewLeader(store.state.currentUser)
        ) {
          return next()
        }
        return next(new Error('You have no permission to access this page'))
      }
    },
    {
      path: "/update-task/:id",
      name: "update-task",
      component: TaskForm,
      beforeEnter: (to, from, next) => {
        if (
          permission.isAdmin(store.state.currentUser) ||
          permission.isBuilder(store.state.currentUser) ||
          permission.isCrewLeader(store.state.currentUser)
        ) {
          return next()
        }
        return next(new Error('You have no permission to access this page'))
      }
    },
    {
      path: "/tasks/:id",
      name: "task-detail",
      component: TaskDetailPage
    },
    {
      path: "/jobs",
      name: "jobs",
      component: JobsPage
    },
    {
      path: "/add-job",
      name: "add-job",
      component: JobForm,
      beforeEnter: (to, from, next) => {
        if (permission.isAdmin(store.state.currentUser)) {
          return next()
        }
        return next(new Error('You have no permission to access this page'))
      }
    },
    {
      path: "/update-job/:id",
      name: "update-job",
      component: JobForm,
      beforeEnter: (to, from, next) => {
        if (permission.isAdmin(store.state.currentUser)) {
          return next()
        }
        return next(new Error('You have no permission to access this page'))
      }
    },
    {
      path: "/jobs/:id",
      name: "job-detail",
      component: JobDetailPage
    },
    {
      path: "/users",
      name: "users",
      component: UsersPage
    },
    {
      path: "/add-user",
      name: "add-user",
      component: UserForm,
      beforeEnter: (to, from, next) => {
        if (permission.isAdmin(store.state.currentUser)) {
          return next()
        }
        return next(new Error('You have no permission to access this page'))
      }
    },
    {
      path: "/update-user/:id",
      name: "update-user",
      component: UserForm,
      beforeEnter: (to, from, next) => {
        if (permission.isAdmin(store.state.currentUser)) {
          return next()
        }
        return next(new Error("You have no permission to access this page"))
      }
    },
    {
      path: "/users/:id",
      name: "user-detail",
      component: UserDetailPage
    },
    {
      path: "/add-crew-staff",
      name: "add-crew-staff",
      component: CrewStaffForm
    },
    {
      path: "/update-crew-staff/:id",
      name: "update-crew-staff",
      component: CrewStaffForm
    },
    {
      path: "/calendar",
      name: "calendar",
      component: CalendarNewPage
    },
    {
      path: "/notifications",
      name: "notifications",
      component: NotificationsPage
    },
    // {
    //   path: "/all-companies",
    //   name: "companyroles",
    //   component: CompanyRoles
    // },
    // {
    //   path: "/add-company",
    //   name: "add-company",
    //   component: CompanyForm,
    //   beforeEnter: (to, from, next) => {
    //     if (permission.isAdmin(store.state.currentUser)) {
    //       return next()
    //     }
    //     return next(new Error("You have no permission to access this page"))
    //   }
    // },
    {
      path: "/companyaccount",
      name: "companyaccount",
      component: CompanyAccountPage,
      beforeEnter: (to, from, next) => {
        if (permission.isAdmin(store.state.currentUser)) {
          return next()
        }
        return next(new Error("You have no permission to access this page"))
      }
    },
    {
      path: "/settings",
      name: "settings",
      component: SettingsPage
    },
    { path: "*", redirect: { name: "home" } }
  ]
});

router.beforeEach((to, from, next) => {
  if (to && to.name != "login" && store.state.currentUser === null) {
    return next({ name: "login" });
  }

  if (to && to.name === "login" && store.state.currentUser !== null) {
    return next({ name: "home" });
  }

  if (to && to.name === "login" && Vue.cookie.get("csrftoken")) {
    //return next({ name: "home" });
  }

  if (to.name != "login") {
    store.dispatch("getActiveRole");
  }

  next();
});

export default router;
