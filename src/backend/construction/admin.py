from django.contrib import admin
from construction import models
from reversion.admin import VersionAdmin


admin.site.register(models.Company, VersionAdmin)
admin.site.register(models.CompanyRole, VersionAdmin)
admin.site.register(models.Subdivision, VersionAdmin)
admin.site.register(models.Job, VersionAdmin)
admin.site.register(models.TaskCategory, VersionAdmin)
admin.site.register(models.TaskSubCategory, VersionAdmin)
admin.site.register(models.Task, VersionAdmin)
admin.site.register(models.Participation, VersionAdmin)
admin.site.register(models.Note, VersionAdmin)
admin.site.register(models.Document, VersionAdmin)
