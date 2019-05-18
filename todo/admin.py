from django.contrib import admin
from .models import Task


# レコード表示機能
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'deadline')
    # list_display_links = ('message', 'created_at')


admin.site.register(Task, TaskAdmin)
