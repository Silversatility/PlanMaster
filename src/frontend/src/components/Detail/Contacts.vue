<template>
  <article>
    <h3 class="cb-h3 bold">{{titleText}}:</h3>
    <div class="table-responsive">
      <table class="table table-bordered add-job-table">
        <thead>
          <tr>
            <th>Contact Name</th>
            <th>Note</th>
            <th>Type</th>
            <th>Email Address</th>
            <th>Mobile Number</th>
            <th class="action-column">Action</th>
          </tr>
        </thead>
        <tbody>
          <slot />
          <tr v-for="contact in contacts" v-bind:key="contact.id">
            <td v-if="contact.role">
              <router-link v-bind:to="{name: 'user-detail', params: {id: contact.role.id}}">
                {{contact.role.user.first_name}} {{contact.role.user.last_name}}
              </router-link>
            </td>
            <td v-else>
              {{contact.name}}
            </td>
            <td>{{contact.note}}</td>
            <td>{{contact.contact_type}}</td>
            <td>
              <i :class="renderNotificationStatus(contact, 'email')"></i>
              {{contact.role ? contact.role.user.email : contact.email}}
            </td>
            <td>
              <i :class="renderNotificationStatus(contact, 'text')"></i>
              {{contact.role ? contact.role.user.mobile_number_display : contact.mobile_number}}
            </td>
            <td v-if="contact.role">
              <!-- <DetailTableAction :actions="tableActions" /> -->
              <span class="table-action-buttons">
                <ButtonTableAction
                  icon="edit"
                  @click.native.prevent="gotToUserUpdate(contact.role.id)"
                />
                <ButtonTableAction
                  icon="delete disabled"
                />
              </span>
            </td>
            <td v-else>
              <span class="table-action-buttons">
                <ButtonTableAction
                  icon="edit"
                  @click.native.prevent="editContactDetails(contact)"
                />
                <ButtonTableAction
                  icon="delete"
                  @click.native.prevent="confirmDeleteContact(contact)"
                />
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="row">
      <div class="col-sm-12">
        <label class="cb-label">User</label>
        <v-select
          v-model="tempContactrole"
          v-bind:options="roles"
          label="user_full_name"
          placeholder="Select existing user or create a contact limited to this task"
          class="form-control cb-input"
          :on-change="setContact"
        >
        </v-select>
      </div>
    </div>

    <div id="editContactDetails" class="row add-contact">
      <div class="col-sm-6">
        <div class="row">
          <div class="col-xs-12 col-sm-6">
            <label class="cb-label required-label">First Name</label>
            <input
              :disabled="isSelected"
              type="text"
              name="contact_first_name"
              v-model="newContact.first_name"
              placeholder="Contact First Name"
              class="form-control cb-input" />
          </div>
          <div class="col-xs-12 col-sm-6">
            <label class="cb-label">Last Name</label>
            <input
              :disabled="isSelected"
              type="text"
              name="contact_last_name"
              v-model="newContact.last_name"
              placeholder="Contact Last Name"
              class="form-control cb-input" />
          </div>
        </div>
      </div>
      <div class="col-sm-6">
        <div class="row">
          <div class="col-xs-12 col-sm-6">
            <div class="notification-checkbox">
              <label class="cb-label block">
                <i :class="newContact.enable_email_notifications ? 'fa fa-bell' : 'fa fa-bell-o'"></i>
              </label>
              <input
                type="checkbox"
                name="is_active"
                v-model="newContact.enable_email_notifications"
                class="cb-checkbox add-contact-checkbox" />
            </div>
            <div class="notification-input">
              <label class="cb-label">Email Address</label>
              <input
                :disabled="isSelected"
                type="text"
                name="email"
                v-model="newContact.email"
                placeholder="Email address"
                class="form-control cb-input add-contact-email" />
            </div>
          </div>
          <div class="col-xs-12 col-sm-6">
            <div class="notification-checkbox">
              <label class="cb-label block">
                <i :class="newContact.enable_text_notifications ? 'fa fa-bell' : 'fa fa-bell-o'"></i>
              </label>
              <input
                type="checkbox"
                name="is_active"
                v-model="newContact.enable_text_notifications"
                class="cb-checkbox add-contact-checkbox" />
            </div>
            <div class="notification-input">
              <label class="cb-label">Mobile Number</label>
              <input
                :disabled="isSelected"
                type="text"
                name="mobile_number"
                v-model="newContact.mobile_number"
                placeholder="Mobile number"
                class="form-control cb-input add-contact-email" />
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-sm-9">
        <label class="cb-label">Note</label>
        <input
        type="text"
        name="note"
        v-model="newContact.note"
        placeholder="Note"
        maxlength="255"
        class="form-control cb-input" />
      </div>
      <div class="col-sm-3">
        <label class="cb-label hidden-label block">.</label>
        <button class="btn upload-btn pull-right" v-on:click="submitContact()">
          <i class="fa fa-plus-circle" aria-hidden="true"></i>{{contactButton}}
        </button>
      </div>
    </div>
  </article>
</template>

<script>
// import DetailTableAction from '@/components/Detail/TableAction.vue';
import ButtonTableAction from '@/components/Button/TableAction.vue';
import { mapState, mapActions } from "vuex";
import moment from "moment";

export default {
  name: "DetailContacts",
  components: {
    ButtonTableAction
  },
  props: {
    titleText: {
      type: String,
      default: "Contacts"
    },
    contacts: Array,
    category: String,
    roles: Array
  },
  computed: {
    ...mapState([
      "loading",
    ]),
    contactButton: function(){
      return this.currentEditContact ? 'Save Contact' : 'Add Contact';
    },
  },
  data: function() {
    return {
      currentEditContact: null,
      isSelected: false,
      newContact: {
        first_name: "",
        last_name: "",
        email: "",
        mobile_number: "",
        enable_text_notifications: false,
        enable_email_notifications: false,
        role: null,
      },
      tempContactrole: {},
      // tableActions: [
      //   { type: 'edit', event: 'contactTableAction-edit' },
      //   { type: 'delete', event: 'contactTableAction-delete' }
      // ]
    }
  },
  methods: {
    ...mapActions([
      "getJobById",
      "getTaskById",
      "addContact",
      "updateContact",
      "deleteContact",
    ]),
    getCategoryById: function(data){
      if (this.category == 'job'){
        this.getJobById(data);
      } else if (this.category == 'task'){
        this.getTaskById(data);
      }
    },
    renderNotificationStatus: function(user, notification_type){
      return user[`enable_${notification_type}_notifications`] ? 'fa fa-bell text-success' : 'fa fa-bell-o text-danger';
    },
    gotToUserUpdate: function(id){
      console.log(id)
      this.$router.push({
        name: "update-user",
        params: { id: id }
      });
    },
    editContactDetails: function(contact) {
      this.currentEditContact = contact;
      let gap = contact.role ? '' : contact.name.indexOf(" ");
      this.newContact = {
          ...this.newContact,
          first_name: contact.role ? contact.role.user.first_name : contact.name.slice(0,gap),
          last_name: contact.role ? contact.role.user.last_name : contact.name.slice(gap),
          enable_email_notifications: contact.role ? contact.role.user.enable_email_notifications : contact.enable_email_notifications,
          enable_text_notifications:  contact.role ? contact.role.user.enable_text_notifications : contact.enable_text_notifications,
          email: contact.role ? contact.role.user.email : contact.email,
          mobile_number: contact.role ? contact.role.user.mobile_number : contact.mobile_number,
          note: contact.note,
          role: contact.role ? contact.role.id : null,
      };
    },
    setContact(role) {
      this.newContact.first_name = role.user.first_name;
      this.newContact.last_name = role.user.last_name;
      this.newContact.email = role.user.email;
      this.newContact.mobile_number = role.user.mobile_number_display;
      this.newContact.enable_email_notifications = role.user.enable_email_notifications;
      this.newContact.enable_text_notifications = role.user.enable_text_notifications;
      this.newContact.role = role.id;
      this.isSelected = true;
    },
    submitContact: function() {
        let self = this;
        let payload = Object.assign(this.newContact, {
            name: `${this.newContact.first_name} ${this.newContact.last_name}`,
            [this.category]: parseInt(this.$route.params.id, 10),
            created_timestamp: moment.utc().format(),
            modified_timestamp: moment.utc().format()
        });

        if (this.newContact.role) {
            payload.name = ''
            delete payload.email
            delete payload.mobile_number
        }

        const submitSuccess = () => {
          self.tempContactrole = {},
          self.newContact = {
            name: "",
            email: "",
            mobile_number: "",
            enable_text_notifications: false,
            enable_email_notifications: false,
            role: null,
          };
          self.getCategoryById({ id: self.$route.params.id });
          self.$toastr("info", "Contact saved", "info");
          self.currentEditContact = null;
          self.isSelected = false;
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

        if (this.currentEditContact) {
          payload = {
            ...payload,
            id: this.currentEditContact.id,
          }
          this.updateContact(payload)
            .then(function() {
              submitSuccess();
            })
            .catch(function(error) {
              submitFailure(error);
            })
        } else {
          this.addContact(payload)
            .then(function() {
              submitSuccess();
            })
            .catch(function(error) {
              submitFailure(error);
            });
        }
    },
    confirmDeleteContact: function(contact) {
      this.$modal.show('dialog', {
          title: 'Remove Contact',
          text: `Are you sure you want to remove <b>${contact.name}</b> from this ${this.category}?`,
          buttons: [
              {
                  title: '<div class="btn cb-delete">Remove</div>',
                  handler: () => {
                    this.deleteContact({ id: contact.id })
                      .then(() => {
                          this.getCategoryById({ id: this.$route.params.id });
                          this.$toastr("info", "Contact Removed!", "Info");
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
    // this.$root.$on('contactTableAction-edit', function({})
  }
}
</script>
