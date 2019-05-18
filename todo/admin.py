from django.contrib import admin
from .models import Post


# レコード表示機能
class PostAdmin(admin.ModelAdmin):
    list_display = ('message', 'created_at')
    list_display_links = ('message', 'created_at')


admin.site.register(Post, PostAdmin)
