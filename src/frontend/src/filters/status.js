function statusDisplay(task) {
  let className = 'status-icon';
  const status = task.status;

  if (task.is_completed) {
    return `${className} completed`;
  }

  switch (status) {
    case 1:
      return `${className} tentative`;
    case 3:
      return `${className} scheduled`;
    case 2:
    default:
      return `${className} pending`;
  }
}

export default {
  install(Vue) {
    Vue.filter("statusDisplay", statusDisplay);
  }
}
