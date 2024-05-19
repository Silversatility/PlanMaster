from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberDescriptor, PhoneNumberField, to_python


class StrictPhoneNumberDescriptor(PhoneNumberDescriptor):
    """Stricter version rejects non-blank but malformed strings."""

    def __set__(self, instance, value):
        converted = to_python(value)
        if converted and not converted.national_number:
            raise ValueError(_('Invalid mobile number'))
        instance.__dict__[self.field.name] = converted


class StrictPhoneNumberField(PhoneNumberField):
    descriptor_class = StrictPhoneNumberDescriptor


# NOTE: Copied from https://gist.github.com/glarrain/5448253
class ValidateModelMixin(object):
    """Make :meth:`save` call :meth:`full_clean`.
    .. warning:
        This should be the left-most mixin/super-class of a model.
    Do you think Django models ``save`` method will validate all fields
    (i.e. call ``full_clean``) before saving or any time at all? Wrong!
    I discovered this awful truth when I couldn't understand why
    a model object with an email field (without `blank=True`) could be
    saved with an empty string as email address.
    More info:
    * "Why doesn't django's model.save() call full clean?"
        http://stackoverflow.com/questions/4441539/
    * "Model docs imply that ModelForm will call Model.full_clean(),
        but it won't."
        https://code.djangoproject.com/ticket/13100
    """

    def save(self, *args, **kwargs):
        """Call :meth:`full_clean` before saving."""
        self.full_clean()
        super(ValidateModelMixin, self).save(*args, **kwargs)
