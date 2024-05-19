<template>
  <header class="container-fluid nav-fluid component__nav_header">
    <v-dialog/>
    <div class="container">
      <nav class="nav">
      <router-link :to="{name: 'calendar'}">
        <img src="/dist/assets/images/header-logo.png" alt="logo" class="nav-logo">
      </router-link>
      <ul class="nav-ul">
        <router-link tag="li" :to="{name:'dashboard'}" class="nav-li">
          <a class="nav-a">Dashboard</a>
        </router-link>
        <router-link tag="li" :to="{name:'calendar'}" class="nav-li">
          <a class="nav-a">Calendar</a>
        </router-link>
        <router-link tag="li" :to="{name:'tasks'}" class="nav-li">
          <a class="nav-a">Tasks</a>
        </router-link>
        <router-link tag="li" :to="{name:'jobs'}" class="nav-li">
          <a class="nav-a">Jobs</a>
        </router-link>
        <router-link tag="li" :to="{name:'users'}" class="nav-li">
          <a class="nav-a">Users</a>
        </router-link>
        <router-link tag="li" :to="{name:'notifications'}" class="nav-li">
          <a class="nav-a">Notifications
            <NotificationBadge :count="headerNotificationsCount" />
          </a>
        </router-link>
        <li class="navbars">
          <div class="dropdown">
            <button @click="hamSpin" v-bind:class="{'is-active': isActive}" class="hamburger cb-ham-js hamburger--spin" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">
              <span class="hamburger-box navbars-a dropdown-toggle">
                <span class="hamburger-inner"></span>
              </span>
            </button>
            <ul class="dropdown-menu cb-dropdown-menu" aria-labelledby="dropdownMenu1">
              <li class="nav-li mobile-menu">
                <router-link class="nav-a" :to="{name:'dashboard'}">Dashboard</router-link>
              </li>
              <li class="nav-li mobile-menu">
                <router-link class="nav-a" :to="{name:'calendar'}">Calendar</router-link>
              </li>
              <li class="nav-li mobile-menu">
                <router-link class="nav-a" :to="{name:'tasks'}">Tasks</router-link>
              </li>
              <li class="nav-li mobile-menu">
                <router-link class="nav-a" :to="{name:'jobs'}">Jobs</router-link>
              </li>
              <li class="nav-li mobile-menu">
                <router-link class="nav-a" :to="{name:'users'}">Users</router-link>
              </li>
              <li class="nav-li mobile-menu">
                <router-link class="nav-a" :to="{name:'notifications'}">
                  Notification
                  <NotificationBadge :count="headerNotificationsCount" />
                </router-link>
              </li>
              <li class="dropdown-header">
                <b>{{ currentUser.user.full_name }}</b><br>
                {{ currentUser.active_role.user_types_display }}<br>
                {{ currentUser.active_role.company_name }}
              </li>
              <!-- <li role="separator" class="divider"></li>
              <li :class="{ 'disabled': (role.id == currentUser.active_role.id) }" v-for="role in currentUser.roles" :key="role.id">
                <a style="cursor: pointer;" v-if="role.id != currentUser.active_role.id" @click="changeCompanyRole(role)">{{ role.company_name }}</a>
                <a v-else> {{ role.company_name }} </a>
              </li>
              <li role="separator" class="divider"></li>
              <li>
                <router-link :to="{name:'companyroles'}">All Companies</router-link>
              </li> -->
              <li v-if=permission.isAdmin(currentUser)>
                <router-link :to="{name:'companyaccount'}">Company Account</router-link>
              </li>
              <li>
                <router-link :to="{name:'settings'}">User Settings</router-link>
              </li>
              <li>
                <a href="#" v-on:click.prevent="handleLogout()">Logout</a>
              </li>
            </ul>
          </div>
        </li>
      </ul>
    </nav>
    </div>
  </header>
</template>

<script>
import { mapState, mapActions } from "vuex";
import $ from "jquery"; // eslint-disable-line no-unused-vars
import bootstrap from "bootstrap3"; // eslint-disable-line no-unused-vars
import NotificationBadge from '@/components/NotificationBadge.vue';
import { permission } from "../router-helper"

export default {
    name: "Header",
    components: {
      NotificationBadge
    },
    data() {
        return {
            isActive: false,
            permission,
        };
    },
    computed: {
      ...mapState([
        'headerNotificationsCount',
        'currentUser',
      ])
    },
    methods: {
        hamSpin() {
            this.isActive = !this.isActive;
        },
        ...mapActions(["logout", "getHeaderNotificationsCount", 'switchCompany']),
        changeCompanyRole: function(role) {
          this.$modal.show('dialog', {
              title: 'Switch Company',
              text: `Are you sure you want to switch company to <b>${role.company_name}</b>?`,
              buttons: [
                  {
                      title: '<div class="btn cb-save-add">Switch</div>',
                      handler: () => {
                          this.$modal.hide('dialog');
                          this.switchCompany(role.id)
                            .then(() => {
                              this.trueHardReload()
                            })
                            .catch(() => {
                              this.$toastr("error", 'Switch Failed!', "error");
                            })
                      }
                  },
                  {
                      title: 'Cancel',
                  }
              ]
          });
        },
        handleLogout: function() {
            let self = this;
            this.logout()
                .then(function() {
                    self.$router.push({ name: "login" });
                })
                .catch(function() {
                    self.$toastr("error", "Logout failed", "error");
                    self.$router.push({ name: "login" });
                });
        }
    },
    created() {
      this.getHeaderNotificationsCount();
    },
};
</script>

<!-- "scoped" attribute limits CSS to this component only -->
<style scoped lang="scss">
.dropdown-menu>.disabled>a {
  background-color: #5090bb;
  color: white;
}
</style>
