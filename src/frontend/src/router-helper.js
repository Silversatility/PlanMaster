const isAdmin = (currentUser) => (currentUser) ? currentUser.active_role.is_admin : false;
const isBuilder = (currentUser) => (currentUser) ? currentUser.active_role.is_builder : false;
const isCrewLeader = (currentUser) => (currentUser) ? currentUser.active_role.is_crew_leader : false;
const isSuperintendent = (currentUser) => (currentUser) ? currentUser.active_role.is_superintendent : false;
const isContact = (currentUser) => (currentUser) ? currentUser.active_role.is_contact : false;
const isAdminOrCreator = (currentUser, task)  => {
  return (task.author == currentUser.user.id || task.job_data.owner == currentUser.active_role.company && isAdmin(currentUser));
};
const hasTaskPermission = (currentUser, task) => {
  return (
    task.author == currentUser.user.id ||
    task.builder == currentUser.active_role.id ||
    task.subcontractor == currentUser.active_role.id ||
    (task.job_data.owner == currentUser.active_role.company && isAdmin(currentUser))
  );
};

const permission = {
  isAdmin,
  isBuilder,
  isCrewLeader,
  isSuperintendent,
  isContact,
  hasTaskPermission,
  isAdminOrCreator,
};

export { permission }
