import moment from "moment";
import 'moment-timezone';

function dateFormat(date, format = "YYYY.MM.DD HH:mm:ss", localize = true) {
  if (!date) {
    return date;
  }

  if (typeof date === "string") {
    if (localize) {
      date = moment(date).tz(moment.tz.guess());
    } else {
      date = moment.utc(date);
    }
  }

  return date.format(format);
}

export default {
  install(Vue) {
    Vue.filter("date", dateFormat);
  }
};
