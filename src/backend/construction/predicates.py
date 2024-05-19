import rules


@rules.predicate
def is_admin_of_owning_contractor(user, obj):
    if obj is None:
        return (user.active_role.is_crew_leader or user.active_role.is_builder or user.active_role.is_admin)

    key_participants = obj.key_participants
    key_participants.pop('superintendent', None)
    return (
        obj.author == user or
        obj.job.owner.roles.filter(is_admin=True, user=user).exists() or
        obj.job.owner.roles.filter(is_crew_leader=True, user=user).exists() or
        obj.job.owner.roles.filter(is_builder=True, user=user).exists() or
        user in [participant.user for participant in key_participants.values() if participant]
    )


@rules.predicate
def is_admin_of_company(user, obj):
    return (
        obj.roles.filter(user=user, is_admin=True).exists()
    )


@rules.predicate
def is_admin(user, obj):
    return (user.active_role.is_admin)


@rules.predicate
def is_job_owner_or_creator(user, job):
    return (
        (job.owner and job.owner.roles.filter(user=user).exists()) or
        (job.created_by and job.created_by.roles.filter(user=user).exists())
    )


@rules.predicate
def is_admin_or_creator(user, obj):
    return (
        obj.job.owner.roles.filter(is_admin=True, user=user).exists() or obj.author == user
    )
