from django.contrib import admin
from account import models


class UserAdmin(admin.ModelAdmin):
    change_form_template = 'loginas/change_form.html'

# Register your models here.
admin.site.register(models.AuthToken)
admin.site.register(models.User, UserAdmin)
