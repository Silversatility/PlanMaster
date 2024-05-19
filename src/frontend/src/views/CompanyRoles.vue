<template>
  <div>
    <Header />
    <PageHeading text="All Company List">
      <input
        type="text"
        class="form-control cf-search cf-full-search"
        v-model="keywords"
        v-on:input="search()"
        placeholder="Searcy by Company" />
      <button v-if="permission.isAdmin(currentUser)" class="btn upload-btn" v-on:click="addCompanyRole()">
        <i class="fa fa-plus-circle" aria-hidden="true"></i>Add Company
      </button>
    </PageHeading>

    <main class="main-fluid">
      <Table
          ref="Table"
          class="container"
          :fetch="getMyCompanyRoles"
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
           <td>{{role.company == currentUser.active_role.company ? '' : role.company_name}}</td>
           <td>{{role.company == currentUser.active_role.company ? role.user_types_display : role.user_types_other_display}}</td>
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
import { permission } from "../router-helper"

import { mapState, mapActions } from "vuex";
import _ from "lodash";

export default {
    name: "CompanyRolesPage",
    components: {
        Header,
        PageHeading,
        Footer,
        Table
    },
    data: function() {
        return {
            permission,
            keywords: "",
            ordering: "company",
            headers: [
                {key: 'company', label: 'Company', sort: true},
                {key: 'user_type', label: 'User Type', sort: true},
            ]
        };
    },
    computed: {
        ...mapState([
            'currentUser',
            "loading",
            "roles",
            "rolesCount",
            "rolesPageSize",
            "rolesPageIndex",
            "rolesOrdering",
            "rolesNumPages",
            "rolesKeywords"
        ])
    },
    methods: {
        ...mapActions([
          "getMyCompanyRoles"
        ]),
        search: _.debounce(function() {
            this.$refs.Table.doFetch();
        }, 1000),
        addCompanyRole: function() {
            this.$router.push({ name: "add-company" });
        }
    },
    mounted() {
      this.keywords = this.rolesKeywords;
      this.$nextTick(() => {
        this.$refs.Table.doFetch();
      })
    }
};
</script>
