class CompanyRoleFilterMixin:
    def get_queryset(self):
        if not self.request:
            return self.queryset.none()

        user = self.request.user
        role = self.request.role
        if user.is_superuser:
            return self.queryset

        if not role or not role.user_types:
            return self.queryset.none()

        queryset = self.queryset.none()
        for user_type in role.user_types:
            func_Q = self.company_role_filter.get(user_type, False)
            if func_Q is True:
                return self.queryset
            elif func_Q is False:
                queryset |= self.queryset.none()
            else:
                queryset |= self.queryset.filter(func_Q(role))

        return queryset.distinct()
