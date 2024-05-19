<template>
  <div>
    <section class="container-fluid main-fluid cf-fluid general-editor-form">
      <div>
        <h3 class="cb-h3 bold mb-5">General Account Settings</h3>
      </div>
      <div class="d-flex justify-content-start align-items-center mb-5">
        <label class="cb-label block mr-3">Reminder Time:</label>
        <div>
          <timepicker
            format="hh:mm a"
            :minute-interval="15"
            hide-clear-button
            v-model="companyReminderTime"
          />
        </div>
      </div>
      <div>
        <button class="btn btn-common btn-primary" @click="saveGeneralDetails">OK</button>
        <button class="btn btn-common btn-default" @click="close">Close</button>
      </div>
    </section>
  </div>
</template>

<script>
import { mapState, mapActions } from "vuex";
import _ from "lodash";

export default {
  name: "GeneralForm",
  components: {},
  data: function() {
    return {
      newGeneralSettings: {
        company_reminder_time: "00:00:00"
      }
    };
  },
  computed: {
    ...mapState(["crewLeaderSettings"]),
    companyReminderTime: {
      get() {
        return this.pickerTime(this.newGeneralSettings.company_reminder_time);
      },
      set(time) {
        this.newGeneralSettings.company_reminder_time = this.crewbossTime(time);
      }
    }
  },
  methods: {
    ...mapActions(["getCrewLeaderSettings", "updateCrewLeader"]),
    pickerTime(time) {
      if (time) {
        time = time.split(":");
        return {
          hh: (time[0] % 12).toString().padStart(2, "0"),
          mm: time[1],
          a: time[0] / 12 > 1 ? "pm" : "am"
        };
      }
      return time;
    },
    crewbossTime(time) {
      let hour = time.a == "am" ? time.hh : parseInt(time.hh) + 12;
      if (Number.isNaN(hour)) {
        return "00:00:00";
      }
      return `${hour}:${time.mm}:00`;
    },
    saveGeneralDetails: function() {
      let settings = this.newGeneralSettings;
      this.updateCrewLeader(settings)
        .then(() => {
          this.$toastr("info", "General settings updated", "info");
        })
        .catch(errors => {
          this.toastrErrors(errors);
        });
    },
    close() {
      this.$router.push({ name: "home" });
    }
  },
  created() {
    let self = this;
    this.getCrewLeaderSettings().then(data => {
      self.newGeneralSettings = {
        id: self.crewLeaderSettings.id,
        company_reminder_time: self.crewLeaderSettings.company_reminder_time
      };
    });
  }
};
</script>



<style lang="scss">
$input-height: 50px;
$padding-x: 12px;
.general-editor-form {
  .dropdown,
  .vdp-datepicker,
  .time-picker input.display-time,
  input {
    height: $input-height;
    border: thin #c5d0e3 solid;
    border-radius: 0;
    background: #fff;
    margin-bottom: 10px;
    font-family: "montserratlight", sans-serif;
  }
  .vdp-datepicker {
    padding: 0;
    input {
      padding: 15px $padding-x;
      margin: 0;
      width: 100%;
      height: 100%;
      border: 0;
    }
  }
  .time-picker {
    width: 100%;
    input.display-time {
      width: 100%;
      padding: 6px $padding-x;
      color: black;
    }
    .dropdown {
      width: 100%;
      top: 80%;
      .select-list {
        width: 100%;
        height: 100%;
      }
    }
  }
}
</style>
