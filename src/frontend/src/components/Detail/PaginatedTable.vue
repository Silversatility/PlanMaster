<template>
  <section>
    <div class="table-responsive">
      <table class="table table-bordered add-job-table">
        <thead>
          <tr>
            <th v-for="header in headers" :style="header.style">
              <template v-if="!header.hasOwnProperty('sort') || header.sort">
                <a v-on:click.prevent="sort(header.key)">
                  {{ header.label }}
                  <i class="fa" v-bind:class="iconClass(header.key)"></i>
                </a>
              </template>
              <template v-else>
                {{ header.label }}
              </template>
            </th>
          </tr>
        </thead>
        <tbody>
            <slot></slot>
        </tbody>
      </table>
    </div>
    <nav aria-label="Page navigation" class="text-center">
      <ul class="pagination">
        <li>
          <a href="#" v-on:click.prevent="getPreviousPage()" aria-label="Previous">
            <span aria-hidden="true">&laquo;</span>
          </a>
        </li>
        <li v-for="page in numPages" v-bind:key="page" v-bind:class="{active: page === pageIndex}">
          <a href="#" v-on:click.prevent="getPage(page)">{{page}}</a>
        </li>
        <li>
          <a href="#" v-on:click.prevent="getNextPage()" aria-label="Next">
            <span aria-hidden="true">&raquo;</span>
          </a>
        </li>
      </ul>
    </nav>
  </section>
</template>

<script>
import { mapState, mapActions } from "vuex";
export default {
    props: {
        fetch: Function,
        items: Array,
        count: Number,
        pageSize: Number,
        pageIndex: Number,
        numPages: Number,
        keywords: String,
        initialOrdering: String,
        headers: {
          type: Array,
          default: [
            {
              key: String,
              label: String,
              style: String,
              sort: Boolean
            }
          ]
        }
    },
    computed: {
      ...mapState([
        "loading"
      ]),
      ordering: function(){
        return this.initialOrdering;
      }
    },
    methods: {
        iconClass: function(order) {
            let className = "";
            if (this.ordering == order) {
                className = "fa-angle-up";
            }
            if (this.ordering == "-" + order) {
                className = "fa-angle-down";
            }
            return className;
        },
        doFetch: function(page) {
            this.fetch({
                page: page || 1,
                keywords: this.keywords,
                ordering: this.ordering
            });
        },
        sort: function(order) {
            if (this.ordering == order) {
                this.ordering = "-" + order;
            } else {
                this.ordering = order;
            }
            this.doFetch();
        },
        getPage: function(page) {
            if (page < 1 || page > this.numPages) {
                page = 1;
            }
            this.doFetch(page);
        },
        getPreviousPage: function() {
            let page = this.pageIndex - 1;
            if (page < 1) {
                page = 1;
            }
            this.doFetch(page);
        },
        getNextPage: function() {
            let page = this.pageIndex + 1;
            if (page > this.numPages) {
                page = this.numPages;
            }
            this.doFetch(page);
        },
    },
}
</script>
