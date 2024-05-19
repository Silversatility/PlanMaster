<template>
  <article id="DetailDocuments" class="row form-article">
    <h3 class="cb-h3 bold">Documents:</h3>
    <div class="table-responsive">
        <table class="table table-bordered add-job-table">
          <thead>
            <tr>
              <th>File Name</th>
              <th>File Type</th>
              <th>Date Added</th>
              <th class="action-column">Action</th>
            </tr>
          </thead>
          <tbody>
              <tr v-for="document in documents" v-bind:key="document.id">
                <td><a target="_blank" v-bind:href="document.filename">{{document.file_name}}</a></td>
                <td>{{document.file_type}}</td>
                <td>{{document.created_timestamp | date("MM/DD/YYYY h:mm a")}}</td>
                <td>
                  <span class="table-action-buttons">
                    <ButtonTableAction
                      icon="delete"
                      @click.native.prevent="confirmDeleteDocument(document)"
                    />
                  </span>
                </td>
              </tr>
          </tbody>
        </table>
      </div>

      <div class="row">
        <div class="col-md-12">
          <vue-dropzone
            ref="vueDropzone"
            id="dropzone"
            :options="dropzoneOptions">
          </vue-dropzone>
          <button @click="clearAllFiles" type="button" class="btn dropzone-bottom-btn">Clear list of recently uploaded files.</button>
        </div>
      </div>

  </article>
</template>

<script>
import ButtonTableAction from '@/components/Button/TableAction.vue';
import { mapState, mapActions } from "vuex";
import moment from "moment";
import VueDropzone from 'vue2-dropzone';
import 'vue2-dropzone/dist/vue2Dropzone.min.css';

export default {
  name: "DetailDocuments",
  components: {
    VueDropzone,
    ButtonTableAction
  },
  props: {
    documents: Array,
    category: String
  },
  computed: {
    ...mapState([
      "loading",
    ]),
  },
  data: function() {
    return {
      dropzoneOptions: {
        url: this.submitDocuments,
        dictDefaultMessage: "Drop files or click to upload here."
      },
    }
  },
  methods: {
    ...mapActions([
      "getJobById",
      "getTaskById",
      "addDocument",
      "deleteDocument",
    ]),
    getCategoryById: function(data){
      if (this.category == 'job'){
        this.getJobById(data);
      } else if (this.category == 'task'){
        this.getTaskById(data);
      }
    },
    clearAllFiles: function() {
      this.$refs.vueDropzone.removeAllFiles();
    },
    submitDocuments: function(file) {
      let self = this;
      let document = file[0];
      if (!document) {
        this.$toastr("error", "No file attached", "error");
        return;
      }
      let formData = new FormData();
      formData.append("filename", document);
      formData.append(this.category, parseInt(this.$route.params.id, 10));
      formData.append("created_timestamp", moment.utc().format());
      formData.append("modified_timestamp", moment.utc().format());

      this.addDocument(formData)
        .then(function() {
          self.getCategoryById({ id: self.$route.params.id });
          self.$toastr("info", "Document saved", "info");
        })
        .catch(function(error) {
          let message = "";
          for (var key in error) {
              let value = error[key];
              message +=
                  key +
                  " " +
                  (value.length ? value.join(", ") : value) +
                  "\n";
          }
          self.$toastr("error", message, "error");
        });
    },
    confirmDeleteDocument: function(document) {
      this.$modal.show('dialog', {
          title: 'Delete Document',
          text: `Are you sure you want to delete <b>${document.file_name}</b>?`,
          buttons: [
              {
                  title: '<div class="btn cb-delete">Delete</div>',
                  handler: () => {
                    this.deleteDocument({ id: document.id })
                      .then(() => {
                          this.getCategoryById({ id: this.$route.params.id });
                          this.$toastr("info", "Docmument Deleted!", "Info");
                      })
                    this.$modal.hide('dialog');
                  }
              },
              {
                  title: 'Cancel',
              }
          ]
      });
    },
  },
  created() {
    this.getCategoryById({ id: this.$route.params.id });
  }
}
</script>
