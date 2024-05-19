<template>
  <article class="row form-article">
    <h3 class="cb-h3 bold">Notes:</h3>
    <div class="table-responsive">
      <table class="table table-bordered add-job-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Author</th>
            <th>English Text</th>
            <th>Spanish Text</th>
            <th class="action-column">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="note in notes" v-bind:key="note.id">
            <td>
              {{note.created_timestamp | date("MM/DD/YYYY")}}
              <br>
              {{note.created_timestamp | date("h:mm a")}}
            </td>
            <td>{{note.note_type}}</td>
            <td>{{note.author && note.author.first_name}} {{note.author && note.author.last_name}}</td>
            <td>{{note.text}}</td>
            <td>{{note.text_es}}</td>
            <td>
              <span class="table-action-buttons">
                <ButtonTableAction
                  icon="edit"
                  @click.native.prevent="editNote(note)"
                />
                <ButtonTableAction
                  icon="delete"
                  @click.native.prevent="confirmDeleteNote(note)"
                />
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="form-group cb-container-notes">
      <label class="cb-label-notes bold" style="display: block;">Add Notes</label>
      <textarea
        v-model="newEnglishNoteText"
        @input="triggerTranslate('to_es')"
        placeholder="English"
        class="form-control cb-input cb-textarea-notes" rows="3"></textarea>
      <textarea
        v-model="newSpanishNoteText"
        @input="triggerTranslate('to_en')"
        placeholder="Spanish"
        class="form-control cb-input cb-textarea-notes" rows="3"></textarea>
      <button class="btn upload-btn add-note-btn pull-right" v-on:click="submitNote()">
        <i class="fa fa-plus-circle" aria-hidden="true"></i>{{noteButton}}
      </button>
    </div>
  </article>
</template>

<script>
import ButtonTableAction from '@/components/Button/TableAction.vue';
import { mapState, mapActions } from "vuex";
import moment from "moment";
import _ from "lodash";

export default {
  name: "DetailNotes",
  components: {
    ButtonTableAction
  },
  props: {
    notes: Array,
    category: String
  },
  computed: {
    ...mapState([
      "loading",
    ]),
    noteButton: function(){
      return this.currentEditNote ? 'Save Note' : 'Add Note';
    },
  },
  data: function() {
    return {
      newEnglishNoteText: "",
      newSpanishNoteText: "",
      origIsEn: false,
      currentEditNote: null,
    }
  },
  methods: {
    ...mapActions([
      "getJobById",
      "getTaskById",
      "addNote",
      "updateNote",
      "deleteNote",
      "translate"
    ]),
    triggerTranslate: _.debounce(function(language) {
      let payload = {
        text: language == 'to_es' ? this.newEnglishNoteText : this.newSpanishNoteText,
        language: language
      }
      if (payload.text) {
        this.translate(payload)
        .then((response) => {
            if (language == 'to_es') {
              this.newSpanishNoteText = response.translated_text;
              this.origIsEn = true;
              return
            }
            this.newEnglishNoteText = response.translated_text;
            this.origIsEn = false;
          })
          .catch((response) => {
            this.$toastr("error", "error", "Error");
          })
      }
    }, 1000),

    getCategoryById: function(data){
      if (this.category == 'job'){
        this.getJobById(data);
      } else if (this.category == 'task'){
        this.getTaskById(data);
      }
    },
    editNote: function(note) {
      this.newEnglishNoteText = note.text;
      this.newSpanishNoteText = note.text_es;
      this.currentEditNote = note;
    },
    submitNote: function() {
      let self = this;
      let payload = {
          [this.category]: parseInt(this.$route.params.id, 10),
          text: this.newEnglishNoteText,
          text_es: this.newSpanishNoteText,
          orig_is_en: this.origIsEn,
          created_timestamp: moment.utc().format(),
          modified_timestamp: moment.utc().format()
      };
      const submitSuccess = () => {
        self.newEnglishNoteText = "";
        self.newSpanishNoteText = "";
        self.origIsEn = false;
        this.currentEditNote = null;
        self.getCategoryById({ id: self.$route.params.id });
        self.$toastr("info", "Note saved", "info");
      }

      const submitFailure = (error) => {
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
      }

      if (this.currentEditNote) {
        payload = {
          ...payload,
          created_timestamp: this.currentEditNote.created_timestamp,
          id: this.currentEditNote.id
        }
        this.updateNote(payload)
          .then(function() {
            submitSuccess()
          })
          .catch(function(error) {
            submitSuccess(error)
          });
      } else {
        this.addNote(payload)
          .then(function() {
            submitSuccess()
          })
          .catch(function(error) {
            submitSuccess(error)
          });
      }
    },
    confirmDeleteNote: function(note) {
      this.$modal.show('dialog', {
          title: 'Delete Note',
          text: `Are you sure you want to delete this note?<br><br><i>"${note.text}"<i>`,
          buttons: [
              {
                  title: '<div class="btn cb-delete">Delete</div>',
                  handler: () => {
                      this.deleteNote({ id: note.id })
                        .then(() => {
                            this.getCategoryById({ id: this.$route.params.id });
                            this.$toastr("info", "Note Deleted!", "Info");
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
