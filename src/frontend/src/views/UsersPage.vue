<template>
  <div>
    <Header />
    <PageHeading text="User List">
      <section class="notification-search-inputs mr-3">
        <div class="cf-full-search-div-job">
          <input
            type="text"
            class="form-control cf-list-search"
            v-model="keywords"
            v-on:input="search()"
            placeholder="Search by First Name, Last Name, Email or Mobile Number" />
          <button class="btn cf-full-search-button" @click="hasKeywords ? clearSearch() : search()">
            <i :class="[hasKeywords ? 'fa fa-remove cf-fa-search' : 'fa fa-search cf-fa-search']"></i>
          </button>
        </div>
      </section>
      <button v-if="permission.isAdmin(currentUser)" class="btn upload-btn" v-on:click="addUser()">
        <i class="fa fa-plus-circle" aria-hidden="true"></i>Invite User
      </button>
    </PageHeading>

    <main class="main-fluid">
      <Table
          ref="Table"
          class="container"
          :modelName='modelName'
          :createRouteName='createRouteName'
          :fetch="getOnlyInvitedRoles"
          :items="roles"
          :count="rolesCount"
          :pageSize="rolesPageSize"
          :pageIndex="rolesPageIndex"
          :numPages="rolesNumPages"
          :keywords="keywords"
          :ordering="rolesOrdering"
          :initialOrdering="ordering"
          :headers="headers"
      >
        <tr v-for="role in roles" v-bind:key="role.id">
           <td>{{role.company_name}}</td>
           <td>
             <router-link v-bind:to="{name: 'user-detail', params: {id: role.id}}">
               {{role.user.first_name}} {{role.user.last_name}}
             </router-link>
           </td>
           <td>
              <i v-if="role.user.email" :class="renderNotificationStatus(role.user, 'email')"></i>
              {{role.user.email}}
            </td>
           <td>
              <i v-if="role.user.mobile_number_display" :class="renderNotificationStatus(role.user, 'text')"></i>
              {{role.user.mobile_number_display}}
            </td>
           <td>{{role.user_types_display}}</td>
           <td class="cb-tick-td text-center">
             <i v-if="role.user.is_active" class="fa fa-check-circle cb-check-circle" aria-hidden="true"></i>
             <i v-else class="fa fa-ban cb-ban-icon" aria-hidden="true"></i>
           </td>
           <td class="cb-tick-td text-center">
             <i v-if="role.user.accepted" class="fa fa-check-circle cb-check-circle" aria-hidden="true"></i>
             <i v-else class="fa fa-ban cb-ban-icon" aria-hidden="true"></i>
           </td>
           <td class="cb-tick-td text-center">
             <i v-if="role.can_see_full_job" class="fa fa-check-circle cb-check-circle" aria-hidden="true"></i>
             <i v-else class="fa fa-ban cb-ban-icon" aria-hidden="true"></i>
           </td>
         </tr>
      </Table>
    </main>
    <Footer />
  </div>
</template>

<script>
// @ is an alias to /src
import Header from "@/components/Header.vue";
import PageHeading from "@/components/PageHeading.vue";
import Footer from "@/components/Footer.vue";
import Table from "@/components/Table.vue";
import ButtonTableAction from '@/components/Button/TableAction.vue';
import { permission } from "../router-helper"

import { mapState, mapActions } from "vuex";
import _ from "lodash";

export default {
    name: "RolesPage",
    components: {
        Header,
        PageHeading,
        Footer,
        Table,
        ButtonTableAction
    },
    data: function() {
        return {
            permission,
            hasKeywords: false,
            keywords: "",
            ordering: "company__name,user__first_name",
            modelName: 'User',
            createRouteName: 'add-user',
            headers: [
                {key: 'company__name', label: 'Company', sort: true},
                {key: 'user__first_name', label: 'Name', sort: true},
                {key: 'user__email', label: 'Email', sort: true},
                {key: 'user__mobile_number', label: 'Mobile Number', sort: true},
                {key: 'user_type', label: 'User Type', sort: true},
                {key: 'user__accepted', label: 'Accepted?', sort: false},
                {key: 'user__is_active', label: 'CrewBoss Access?', sort: false},
                {key: 'can_see_full_job', label: 'Related Tasks Access?', sort: false}
            ]
        };
    },
    computed: {
        ...mapState([
            "loading",
            "roles",
            "rolesCount",
            "rolesPageSize",
            "rolesPageIndex",
            "rolesOrdering",
            "rolesNumPages",
            "rolesKeywords",
            "currentUser"
        ])
    },
    methods: {
        ...mapActions([
          "getRoles"
        ]),
        getOnlyInvitedRoles: function(kwargs) {
          kwargs['onlyInvited'] = true;
          return this.getRoles(kwargs);
        },
        search: _.debounce(function() {
          this.keywords ? this.hasKeywords = true : ''
            this.$refs.Table.doFetch();
        }, 1000),
        clearSearch() {
          this.keywords = "";
          this.hasKeywords = false;
          this.search();
        },
        addUser: function() {
            this.$router.push({ name: "add-user" });
        },
        renderNotificationStatus: function(user, notification_type){
          return user[`enable_${notification_type}_notifications`] ? 'fa fa-bell text-success' : 'fa fa-bell-o text-danger';
        },
    },
    mounted() {
      this.keywords = this.rolesKeywords;
      this.keywords ? this.hasKeywords = true : ''
      this.$nextTick(() => {
        this.$refs.Table.doFetch();
      })
    }
};
</script>
<style scoped lang="scss">

.notification-search-inputs {
  width: 100%;
  flex: 1;
  input {
    position: static;
    margin: 0;
  }
  input {
    width: 96.5%;
  }
}

.notification-search-inputs-remove {
  width: 100%;
  flex: 1;
  input {
    position: static;
    margin: 0;
  }
  input {
    width: 75%;
  }
}

@media (max-width: 1080px) {
  .notification-search-inputs-remove {
    margin: 10px 0 0;
    input {
      width: 70%;
      margin-bottom: 13px;
    }
  }

  .upload-btn {
    margin-bottom: 10px;
  }
}

@media (max-width: 768px) {
  .notification-search-inputs-remove {
    margin: 10px 0 0;
  }

  .upload-btn {
    margin-bottom: 10px;
  }
}

@media (max-width: 425px) {
  .notification-search-inputs-remove {
    input {
      width: 100%;
      margin-bottom: 13px;
    }
  }
  button {
    width: 100% !important;
  }
}
</style>
