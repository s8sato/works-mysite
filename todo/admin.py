from django.contrib import admin
from .models import Step, Task


# レコード表示機能
class StepAdmin(admin.ModelAdmin):
    list_display = ('pk',)
    # list_display_links = ()

# レコード表示機能
class TaskAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'title',
                    'start',
                    'expected_time',
                    'actual_time',
                    'deadline',
                    'client',
                    'is_done',
                    'note',
                    'initial_step',
                    'terminal_step',)
    # list_display_links = ()


admin.site.register(Step, StepAdmin)
admin.site.register(Task, TaskAdmin)
