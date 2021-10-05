from django.contrib import admin


from .models import Eintrag, ListUser, ListSettings,ListUserFriendRequest, Category
# Register your models here.

class EintragAdmin(admin.ModelAdmin):
    list_display = ('category', 'author',)
    list_filter = ('category', 'author')
    search_fields = ['text']


admin.site.register(Eintrag, EintragAdmin)
admin.site.register(ListUser)
admin.site.register(ListSettings)
admin.site.register(ListUserFriendRequest)
admin.site.register(Category)