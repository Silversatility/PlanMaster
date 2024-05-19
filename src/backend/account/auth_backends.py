from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


UserModel = get_user_model()


class EmailOrMobileNumberBackend(ModelBackend):
    """
    Copy of django.contrib.auth.backends.ModelBackend, accepting either email
    and mobile number instead of username
    """

    def authenticate(self, request, email=None, mobile_number=None, password=None, **kwargs):
        user = None
        try:
            if email:
                user = UserModel._default_manager.get(email__iexact=email)
            if mobile_number:
                user = UserModel._default_manager.get(mobile_number=mobile_number, is_active=True)
        except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
            pass

        if user:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        else:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
