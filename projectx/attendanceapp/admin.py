from django.contrib import admin

from attendanceapp.models import Org, Indlist, Orgattendance, Userattendance
# Register your models here.

admin.site.register(Org)
admin.site.register(Indlist)
admin.site.register(Orgattendance)
admin.site.register(Userattendance)